"""Rapport de contrôle et vérification des adresses témoins."""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import Point, shape

from pipeline.common.tuiles import tuile_du_point
from pipeline.common.verdict import PAR_CODE


def verdict_au_point(lon: float, lat: float, dossier: Path, zoom: int) -> tuple[str | None, str | None]:
    """Refait, côté pipeline, ce que le navigateur fera : la tuile, puis le point."""
    tuile = tuile_du_point(lon, lat, zoom)
    fichier = dossier / tuile.chemin
    if not fichier.exists():
        return None, None
    collection = json.loads(fichier.read_text(encoding="utf-8"))
    point = Point(lon, lat)
    for feature in collection["features"]:
        if shape(feature["geometry"]).contains(point):
            classe = PAR_CODE.get(int(feature["properties"]["c"]))
            if classe is not None:
                return classe.niveau, classe.officiel
    return None, None


def verifie_les_temoins(chemin: Path, dossier: Path, zoom: int) -> list[dict]:
    """Compare le verdict obtenu à l'attente notée dans data/temoins.json."""
    if not chemin.exists():
        return []
    fiche = json.loads(chemin.read_text(encoding="utf-8"))
    resultats: list[dict] = []
    for temoin in fiche.get("temoins", []):
        obtenu, classe = verdict_au_point(temoin["lon"], temoin["lat"], dossier, zoom)
        attendu = temoin.get("attendu")
        resultats.append(
            {
                "nom": temoin["nom"],
                "attendu": attendu,
                "obtenu": obtenu,
                "classe": classe,
                "confirme": bool(temoin.get("confirme", False)),
                "ecart": obtenu != attendu,
            }
        )
    return resultats


def ecris_le_rapport(
    cible: Path,
    *,
    jeu,
    ressource,
    meta: dict,
    total_brut: int,
    retenues: int,
    manquantes: int,
    emprise: tuple[float, float, float, float],
    poids: dict[str, int],
    communes: list[dict],
    temoins: list[dict],
    colonne_classe: str,
) -> None:
    total_octets = sum(poids.values())
    plus_lourde = max(poids.items(), key=lambda p: p[1], default=("aucune", 0))
    part_manquante = manquantes / total_brut * 100 if total_brut else 0.0

    lignes = [
        "# Rapport — zones climatiques locales",
        "",
        f"Aire traitée : **{meta['aire']}**. Exécution du {meta['telecharge']}.",
        "",
        "## Source",
        "",
        f"- Jeu : {jeu.titre} (`{jeu.identifiant}`)",
        f"- Producteur : {jeu.producteur}",
        f"- Licence : {jeu.licence}",
        f"- Millésime retenu : {meta['millesime']} (le jeu a été mis à jour le {jeu.millesime})",
        f"- Ressource : {ressource.titre} ({ressource.format})",
        f"- Page : {jeu.page}",
        "",
        "## Objets",
        "",
        f"- Objets lus : {total_brut}",
        f"- Objets retenus : {retenues}",
        f"- Classes illisibles écartées : {manquantes} ({part_manquante:.1f} %)",
        f"- Colonne des classes : `{colonne_classe}`",
        f"- Emprise (ouest, sud, est, nord) : {emprise[0]:.4f}, {emprise[1]:.4f}, {emprise[2]:.4f}, {emprise[3]:.4f}",
        "",
        "## Sorties",
        "",
        f"- Tuiles écrites : {len(poids)} (zoom {meta['zoom']})",
        f"- Poids total : {total_octets / 1024 / 1024:.1f} Mo",
        f"- Tuile la plus lourde : `{plus_lourde[0]}`, {plus_lourde[1] / 1024:.0f} Ko (budget 300 Ko)",
        f"- Communes décrites : {len(communes)}",
        "",
        "## Adresses témoins",
        "",
    ]

    if not temoins:
        lignes.append("Aucun témoin défini dans `data/temoins.json`.")
    else:
        lignes += [
            "| Adresse | Attendu | Obtenu | Classe | Verdict |",
            "| --- | --- | --- | --- | --- |",
        ]
        for temoin in temoins:
            if not temoin["ecart"]:
                etat = "conforme"
            elif temoin["confirme"]:
                etat = "**ÉCART — mise en ligne bloquée**"
            else:
                etat = "écart, attente non confirmée"
            lignes.append(
                f"| {temoin['nom']} | {temoin['attendu'] or '—'} | "
                f"{temoin['obtenu'] or 'hors zone'} | {temoin['classe'] or '—'} | {etat} |"
            )
        lignes += [
            "",
            "Tant qu'un témoin porte `\"confirme\": false`, l'écart est signalé mais "
            "ne bloque pas : l'attente vient de Claude, pas encore du terrain.",
        ]

    if poids and plus_lourde[1] > 300 * 1024:
        lignes += [
            "",
            "## Attention",
            "",
            f"La tuile `{plus_lourde[0]}` dépasse le budget de 300 Ko. "
            "Augmentez `--simplification`, ou montez d'un zoom.",
        ]

    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text("\n".join(lignes) + "\n", encoding="utf-8")
