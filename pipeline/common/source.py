"""Accès aux jeux de données publics de data.gouv.fr, sans clé ni compte."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import requests

API = "https://www.data.gouv.fr/api/1"
#: Une année à quatre chiffres, telle qu'elle apparaît dans un nom de fichier.
ANNEE = re.compile(r"(?:19|20)\d{2}")
RACINE = Path(__file__).resolve().parents[2]
DOSSIER_BRUT = RACINE / "data" / "brut"


@dataclass(frozen=True)
class Ressource:
    titre: str
    url: str
    format: str
    taille: int | None


@dataclass(frozen=True)
class Jeu:
    identifiant: str
    titre: str
    producteur: str
    licence: str
    page: str
    millesime: str
    ressources: tuple[Ressource, ...]


def sans_accent(texte: str) -> str:
    """« Saint-Étienne » et « saint etienne » doivent se rejoindre."""
    normalise = unicodedata.normalize("NFD", texte)
    sans = "".join(c for c in normalise if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", sans.lower()).strip()


def slug(texte: str) -> str:
    normalise = unicodedata.normalize("NFD", texte)
    sans = "".join(c for c in normalise if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", sans.lower()).strip("-")


def lis_le_jeu(identifiant: str, *, delai: int = 60) -> Jeu:
    """Lit la fiche d'un jeu sur data.gouv.fr."""
    reponse = requests.get(f"{API}/datasets/{identifiant}/", timeout=delai)
    reponse.raise_for_status()
    fiche = reponse.json()
    organisation = fiche.get("organization") or {}
    millesime = str(fiche.get("last_modified") or fiche.get("created_at") or "")[:10]
    ressources = tuple(
        Ressource(
            titre=str(r.get("title") or ""),
            url=str(r.get("url") or ""),
            format=str(r.get("format") or "").lower(),
            taille=r.get("filesize"),
        )
        for r in fiche.get("resources", [])
        if r.get("url")
    )
    return Jeu(
        identifiant=identifiant,
        titre=str(fiche.get("title") or ""),
        producteur=str(organisation.get("name") or "Cerema"),
        licence=str(fiche.get("license") or "inconnue"),
        page=str(fiche.get("page") or f"https://www.data.gouv.fr/fr/datasets/{identifiant}/"),
        millesime=millesime,
        ressources=ressources,
    )


def ressource_de_l_aire(jeu: Jeu, aire: str) -> Ressource:
    """Trouve la ressource qui correspond à l'aire urbaine demandée."""
    cherche = sans_accent(aire)
    candidates = [
        r
        for r in jeu.ressources
        if cherche in sans_accent(r.titre) or cherche in sans_accent(r.url)
    ]
    geo = [r for r in candidates if r.format not in {"csv", "pdf", "html", "txt", "json"}]
    retenues = geo or candidates
    if not retenues:
        titres = "\n  ".join(sorted(r.titre for r in jeu.ressources)[:40])
        raise SystemExit(
            f"Aucune ressource ne correspond à l'aire « {aire} ».\n"
            f"Ressources disponibles (40 premières) :\n  {titres}"
        )
    # La plus grosse est le fichier de données, pas une notice.
    return max(retenues, key=lambda r: r.taille or 0)


def ressource_des_communes(jeu: Jeu) -> Ressource | None:
    """Le CSV des communes couvertes, s'il est publié."""
    for ressource in jeu.ressources:
        if ressource.format == "csv" and "commune" in sans_accent(ressource.titre):
            return ressource
    return None


def telecharge(ressource: Ressource, *, delai: int = 300) -> Path:
    """Télécharge une ressource dans data/brut/, une seule fois."""
    DOSSIER_BRUT.mkdir(parents=True, exist_ok=True)
    nom = ressource.url.rsplit("/", 1)[-1].split("?")[0] or f"{slug(ressource.titre)}.dat"
    cible = DOSSIER_BRUT / nom
    if cible.exists() and cible.stat().st_size > 0:
        return cible
    provisoire = cible.with_suffix(cible.suffix + ".partiel")
    with requests.get(ressource.url, stream=True, timeout=delai) as reponse:
        reponse.raise_for_status()
        with provisoire.open("wb") as fichier:
            for morceau in reponse.iter_content(chunk_size=1 << 20):
                fichier.write(morceau)
    provisoire.replace(cible)
    return cible


def millesime_de_la_ressource(ressource: Ressource, jeu: Jeu) -> str:
    """Millésime de la donnée elle-même, pas de sa mise en ligne.

    Le nom du fichier le porte presque toujours (« lcz-spot-2022-lyon.zip ») ;
    la date de dernière modification du jeu, elle, change à chaque correction
    de fiche et afficherait une année fausse à côté du verdict.
    """
    for texte in (ressource.titre, ressource.url):
        trouve = ANNEE.search(texte)
        if trouve is not None:
            return trouve.group(0)
    return jeu.millesime[:4] if jeu.millesime else "millésime inconnu"
