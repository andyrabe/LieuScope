"""Prépare la couche « chaleur » pour une aire urbaine.

    python -m pipeline.lcz --aire "Lyon"

Le traitement est relançable sans effet de bord : il écrase sa propre sortie et
ne touche à rien d'autre. Il écrit un rapport dans pipeline/rapports/lcz.md.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

import geopandas

from pipeline.common.source import (
    lis_le_jeu,
    ressource_de_l_aire,
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


def main() -> int:
    arguments = lis_les_arguments()
    dossier = Path(arguments.sortie)

    print(f"Jeu {JEU} sur data.gouv.fr…")
    jeu = lis_le_jeu(JEU)
    ressource = ressource_de_l_aire(jeu, arguments.aire)
    print(f"Ressource retenue : {ressource.titre} ({ressource.format})")
    fichier = telecharge(ressource)
    print(f"Fichier local : {fichier.name}")

    zones = geopandas.read_file(chemin_lisible(fichier))
    total_brut = len(zones)
    print(f"{total_brut} objets lus.")

    classe = colonne_classe(zones)
    insee = colonne_insee(zones)
    nom_commune = colonne_commune(zones)
    print(f"Colonne des classes : {classe}")

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
    metres["geometry"] = metres.geometry.simplify(
        arguments.simplification, preserve_topology=True
    )
    zones = metres.to_crs("EPSG:4326")
    zones = zones[~zones.geometry.is_empty & zones.geometry.notna()].copy()

    communes = repartition_par_commune(zones, surfaces, insee, nom_commune)

    if dossier.exists():
        shutil.rmtree(dossier)
    dossier.mkdir(parents=True, exist_ok=True)

    par_tuile = range_par_tuile(
        zip(zones.geometry, zones["code_lcz"], strict=True), arguments.zoom
    )
    poids = ecris_les_tuiles(par_tuile, dossier)
    print(f"{len(poids)} tuiles écrites, la plus lourde fait {max(poids.values(), default=0) / 1024:.0f} Ko.")

    meta = {
        "couche": "lcz",
        "zoom": arguments.zoom,
        "aire": arguments.aire,
        "producteur": jeu.producteur,
        "millesime": jeu.millesime,
        "telecharge": date.today().isoformat(),
        "licence": jeu.licence,
        "url": jeu.page,
    }
    ecris_json(dossier / "meta.json", meta)
    ecris_json(
        dossier / "communes.json",
        {"aire": arguments.aire, "millesime": jeu.millesime, "communes": communes},
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
        centre = groupe.geometry.union_all().centroid
        resultat.append(
            {
                "insee": str(valeur) if insee is not None else "",
                "nom": libelle,
                "slug": slug(libelle),
                "centre": [round(centre.x, 5), round(centre.y, 5)],
                "parts": parts,
                "dominante": dominante,
            }
        )
    return sorted(resultat, key=lambda commune: commune["nom"])


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
        default=8.0,
        help="Tolérance de simplification des contours, en mètres.",
    )
    analyseur.add_argument("--sortie", default=str(SORTIE), help="Dossier de sortie.")
    return analyseur.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
