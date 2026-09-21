"""Prépare la couche « chaleur » pour une aire urbaine.

    python -m pipeline.lcz --aire "Lyon"

Le traitement est relançable sans effet de bord : il écrase sa propre sortie et
ne touche à rien d'autre. Il écrit un rapport dans pipeline/rapports/lcz.md.
"""

from __future__ import annotations

import argparse
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
    telecharge,
)
from pipeline.common.tuiles import ZOOM_LCZ
from pipeline.common.verdict import code_interne
from pipeline.lcz import JEU
from pipeline.lcz.colonnes import colonne_classe
from pipeline.lcz.communes import communes_de_l_aire
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

    communes, communes_ecartees = lis_les_communes(jeu, arguments.aire)
    etape(f"{len(communes)} communes retenues, {communes_ecartees} écartées", debut)

    metres = zones.to_crs(LAMBERT93)
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
        {
            "aire": arguments.aire,
            "millesime": millesime,
            "communes": [vars(commune) | {"centre": list(commune.centre or [])} for commune in communes],
        },
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
        communes_ecartees=communes_ecartees,
    )

    ecarts = [t for t in temoins if t["ecart"] and t["confirme"]]
    if ecarts:
        noms = ", ".join(t["nom"] for t in ecarts)
        print(f"ÉCHEC : témoin(s) en écart : {noms}. La mise en ligne est bloquée.")
        return 1
    print("Terminé. Rapport : pipeline/rapports/lcz.md")
    return 0


def lis_les_communes(jeu, aire: str) -> tuple[list, int]:
    """Communes couvertes par l'aire, d'après le CSV publié à côté du jeu.

    Le fichier des zones ne porte aucun rattachement communal : c'est ce CSV,
    publié par le même producteur, qui dit quelle commune est couverte par
    quelle aire.
    """
    ressource = ressource_des_communes(jeu)
    if ressource is None:
        print("Aucun CSV de communes dans le jeu : aucune page de commune.", flush=True)
        return [], 0
    return communes_de_l_aire(telecharge(ressource), aire)


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
