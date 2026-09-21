"""Découpe des zones en petits fichiers par tuile, et écriture du GeoJSON."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from shapely.geometry import box, mapping

from pipeline.common.tuiles import Tuile, emprise_tuile, tuiles_de_l_emprise

#: Cinq décimales, soit environ un mètre : inutile d'en garder davantage.
DECIMALES = 5


def arrondis(valeur):
    """Arrondit toutes les coordonnées d'une géométrie GeoJSON."""
    if isinstance(valeur, bool):
        return valeur
    if isinstance(valeur, (int, float)):
        return round(float(valeur), DECIMALES)
    if isinstance(valeur, (list, tuple)):
        return [arrondis(element) for element in valeur]
    if isinstance(valeur, dict):
        return {cle: arrondis(element) for cle, element in valeur.items()}
    return valeur


def range_par_tuile(zones, zoom: int) -> dict[Tuile, list[dict]]:
    """Range chaque zone dans toutes les tuiles qu'elle touche.

    Une zone à cheval est recopiée entière dans chaque tuile : c'est le prix à
    payer pour que le navigateur n'ait qu'un seul petit fichier à lire.
    """
    par_tuile: dict[Tuile, list[dict]] = defaultdict(list)
    for geometrie, code in zones:
        ouest, sud, est, nord = geometrie.bounds
        for tuile in tuiles_de_l_emprise(ouest, sud, est, nord, zoom):
            if not geometrie.intersects(box(*emprise_tuile(tuile))):
                continue
            par_tuile[tuile].append(
                {
                    "type": "Feature",
                    "properties": {"c": int(code)},
                    "geometry": arrondis(mapping(geometrie)),
                }
            )
    return dict(par_tuile)


def ecris_les_tuiles(par_tuile: dict[Tuile, list[dict]], dossier: Path) -> dict[str, int]:
    """Écrit un fichier GeoJSON minifié par tuile. Renvoie les poids en octets."""
    poids: dict[str, int] = {}
    for tuile, features in par_tuile.items():
        cible = dossier / tuile.chemin
        cible.parent.mkdir(parents=True, exist_ok=True)
        contenu = json.dumps(
            {"type": "FeatureCollection", "features": features},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        cible.write_text(contenu, encoding="utf-8")
        poids[tuile.chemin] = len(contenu.encode("utf-8"))
    return poids
