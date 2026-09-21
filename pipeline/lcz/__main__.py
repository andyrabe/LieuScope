"""Prépare la couche « chaleur » pour une aire urbaine.

    python -m pipeline.lcz --aire "Lyon"

Le traitement est relançable sans effet de bord : il écrase sa propre sortie et
ne touche à rien d'autre. Il écrit un rapport dans pipeline/rapports/lcz.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from datetime import date
from pathlib import Path

import geopandas

from pipeline.common.source import (
    lis_le_jeu,
    millesime_de_la_ressource,
    ressource_de_l_aire,
    ressource_des_communes,
    slug,
    telecharge,
)
from pipeline.common.tuiles import ZOOM_LCZ
from pipeline.common.verdict import PAR_CODE, code_interne
from pipeline.lcz import JEU
from pipeline.lcz.colonnes import colonne_classe, colonne_commune, colonne_insee
from pipeline.lcz.decoupe import ecris_les_tuiles, range_par_tuile
from pipeline.lcz.rapport import ecris_le_rapport, verifie_les_temoins

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "public" / "data" / "lcz"
#: Lambert-93 : le système projeté officiel en France, en mètres.
LAMBERT93 = "EPSG:2154"


def etape(titre: str, depuis: float) -> float:
    """Affiche le temps passé : sans cela, une exécution longue est aveugle."""
    maintenant = time.monotonic()
    print(f"[{maintenant - depuis:6.1f} s] {titre}", flush=True)
    return maintenant


def main() -> int:
    debut = time.monotonic()
    arguments = lis_les_arguments()
    dossier = Path(arguments.sortie)

    print(f"Jeu {JEU} sur data.gouv.fr…")
    jeu = lis_le_jeu(JEU)
    ressource = ressource_de_l_aire(jeu, arguments.aire)
    print(f"Ressource retenue : {ressource.titre} ({ressource.format})", flush=True)
    fichier = telecharge(ressource)
    etape(f"Fichier local : {fichier.name}", debut)
    zones = geopandas.read_file(chemin_lisible(fichier))
    total_brut = len(zones)
    colonnes = [str(c) for c in zones.columns]
    etape(f"{total_brut} objets lus ; colonnes : {', '.join(colonnes)}", debut)

    classe = colonne_classe(zones)
    insee = colonne_insee(zones)
    nom_commune = colonne_commune(zones)
    print(f"Colonne des classes : {classe}", flush=True)

    zones["code_lcz"] = zones[classe].map(code_interne)
    manquantes = int(zones["code_lcz"].isna().sum())
    zones = zones[zones["code_lcz"].notna()].copy()
    zones["code_lcz"] = zones["code_lcz"].astype(int)

    if zones.crs is None:
        raise SystemExit(
            "Le fichier ne déclare pas de système de coordonnées : "
            "impossible de le reprojeter sans risque."
        )

    metres = zones.to_crs(LAMBERT93)
    surfaces = metres.geometry.area

    # Les communes se calculent sur les zones d'origine : la fusion ci-dessous
    # efface le rattachement communal.
    communes = repartition_par_commune(
        zones.to_crs("EPSG:4326"), surfaces, insee, nom_commune
    )
    etape(f"{len(communes)} communes décrites", debut)

    # Le jeu vient d'une image satellite : des milliers de petites zones
    # voisines portent la même classe et se touchent. Les fusionner d'abord
    # supprime toutes leurs frontières communes, ce qui allège énormément la
    # sortie ; on simplifie ensuite les contours qui restent.
    fusion = metres.dissolve(by="code_lcz", as_index=False).explode(ignore_index=True)
    etape(f"{len(fusion)} zones après fusion des voisines de même classe", debut)
    fusion["geometry"] = fusion.geometry.simplify(
        arguments.simplification, preserve_topology=True
    )
    zones = fusion.to_crs("EPSG:4326")
    zones = zones[~zones.geometry.is_empty & zones.geometry.notna()].copy()
    etape("Simplification et reprojection terminées", debut)

    if dossier.exists():
        shutil.rmtree(dossier)
    dossier.mkdir(parents=True, exist_ok=True)

    par_tuile = range_par_tuile(
        zip(zones.geometry, zones["code_lcz"], strict=True), arguments.zoom
    )
    etape(f"{len(par_tuile)} tuiles préparées", debut)
    poids = ecris_les_tuiles(par_tuile, dossier)
    etape(
        f"{len(poids)} tuiles écrites, {sum(poids.values()) / 1024 / 1024:.1f} Mo au "
        f"total, la plus lourde fait {max(poids.values(), default=0) / 1024:.0f} Ko",
        debut,
    )

    apercu_communes = inspecte_les_communes(jeu)
    millesime = millesime_de_la_ressource(ressource, jeu)
    meta = {
        "couche": "lcz",
        "zoom": arguments.zoom,
        "aire": arguments.aire,
        "producteur": jeu.producteur,
        "millesime": millesime,
        "telecharge": date.today().isoformat(),
        "licence": jeu.licence,
        "url": jeu.page,
    }
    ecris_json(dossier / "meta.json", meta)
    ecris_json(
        dossier / "communes.json",
        {"aire": arguments.aire, "millesime": millesime, "communes": communes},
    )

    temoins = verifie_les_temoins(RACINE / "data" / "temoins.json", dossier, arguments.zoom)
    ecris_le_rapport(
        RACINE / "pipeline" / "rapports" / "lcz.md",
        jeu=jeu,
        ressource=ressource,
        meta=meta,
        total_brut=total_brut,
        retenues=len(zones),
        manquantes=manquantes,
        emprise=tuple(zones.total_bounds),
        poids=poids,
        communes=communes,
        temoins=temoins,
        colonne_classe=classe,
        colonnes=colonnes,
        apercu_communes=apercu_communes,
    )

    ecarts = [t for t in temoins if t["ecart"] and t["confirme"]]
    if ecarts:
        noms = ", ".join(t["nom"] for t in ecarts)
        print(f"ÉCHEC : témoin(s) en écart : {noms}. La mise en ligne est bloquée.")
        return 1
    print("Terminé. Rapport : pipeline/rapports/lcz.md")
    return 0


def repartition_par_commune(zones, surfaces, insee: str | None, nom: str | None) -> list[dict]:
    """Part de chaque niveau de sensibilité dans chaque commune, en pourcents.

    Le jeu ne porte pas toujours le rattachement communal : dans ce cas la liste
    est vide, et aucune page de commune n'est construite. Mieux vaut pas de page
    qu'une page vide.
    """
    if insee is None and nom is None:
        return []
    cle = insee or nom
    travail = zones.copy()
    travail["surface"] = surfaces.reindex(travail.index)
    travail["niveau"] = travail["code_lcz"].map(lambda c: PAR_CODE[c].niveau)

    resultat: list[dict] = []
    for valeur, groupe in travail.groupby(cle):
        totale = float(groupe["surface"].sum())
        if totale <= 0:
            continue
        parts = {
            str(niveau): round(float(part["surface"].sum()) / totale * 100)
            for niveau, part in groupe.groupby("niveau")
        }
        dominante = max(parts, key=lambda n: parts[n])
        libelle = str(groupe[nom].iloc[0]) if nom is not None else str(valeur)
        # Centre de l'emprise de la commune : fusionner toutes ses zones pour
        # en prendre le centroïde exact coûterait des minutes pour un point qui
        # ne sert qu'à centrer une carte.
        ouest, sud, est, nord = groupe.total_bounds
        resultat.append(
            {
                "insee": str(valeur) if insee is not None else "",
                "nom": libelle,
                "slug": slug(libelle),
                "centre": [round((ouest + est) / 2, 5), round((sud + nord) / 2, 5)],
                "parts": parts,
                "dominante": dominante,
            }
        )
    return sorted(resultat, key=lambda commune: commune["nom"])


def inspecte_les_communes(jeu) -> str:
    """Regarde ce que contient le CSV des communes couvertes, s'il existe.

    Le jeu du Cerema ne rattache pas ses zones à une commune. Ce fichier est la
    piste la plus simple pour construire une page par commune : on relève ce
    qu'il contient avant d'écrire quoi que ce soit.
    """
    ressource = ressource_des_communes(jeu)
    if ressource is None:
        return "aucune ressource « communes » dans le jeu"
    try:
        fichier = telecharge(ressource)
        with fichier.open(encoding="utf-8-sig", errors="replace", newline="") as lecture:
            table = list(csv.DictReader(lecture, delimiter=";"))
    except Exception as souci:  # noqa: BLE001 — diagnostic, jamais bloquant
        return f"lecture impossible ({souci})"
    if not table:
        return f"`{ressource.titre}` — fichier vide"

    couvertes = [
        ligne
        for ligne in table
        if (ligne.get("couverture_lcz") or "0").replace(",", ".").strip() not in {"", "0", "0.00"}
    ]
    exemple = couvertes[0] if couvertes else table[0]
    detail = str(exemple.get("detail_couverture_lcz", ""))
    return (
        f"`{ressource.titre}` — {len(table)} communes, dont {len(couvertes)} couvertes.\n"
        f"  - Colonnes : `{', '.join(table[0].keys())}`\n"
        f"  - Exemple couvert : `{exemple.get('commune')}` "
        f"({exemple.get('insee_commune')}), couverture `{exemple.get('couverture_lcz')}`\n"
        f"  - Détail de cette commune : `{detail[:400]}`"
    )


def chemin_lisible(fichier: Path) -> str:
    """GeoPandas sait lire dans une archive zip sans la décompresser."""
    return f"zip://{fichier}" if fichier.suffix.lower() == ".zip" else str(fichier)


def ecris_json(cible: Path, contenu: object) -> None:
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text(
        json.dumps(contenu, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )


def lis_les_arguments() -> argparse.Namespace:
    analyseur = argparse.ArgumentParser(
        prog="python -m pipeline.lcz",
        description="Prépare les zones climatiques locales d'une aire urbaine.",
    )
    analyseur.add_argument("--aire", required=True, help="Nom de l'aire urbaine, ex. « Lyon ».")
    analyseur.add_argument("--zoom", type=int, default=ZOOM_LCZ, help="Zoom des tuiles de données.")
    analyseur.add_argument(
        "--simplification",
        type=float,
        default=40.0,
        help="Tolérance de simplification des contours, en mètres.",
    )
    analyseur.add_argument("--sortie", default=str(SORTIE), help="Dossier de sortie.")
    return analyseur.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
