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


#: Types de géométrie qu'une découpe peut produire et qu'on sait servir.
SURFACIQUES = {"Polygon", "MultiPolygon"}


def range_par_tuile(zones, zoom: int) -> dict[Tuile, list[dict]]:
    """Range chaque zone dans les tuiles qu'elle touche, découpée à leur bord.

    Une zone à cheval est présente dans chaque tuile qu'elle touche, mais
    seulement pour la part qui y tombe. Recopier la zone entière dans chaque
    tuile ferait exploser le poids dès qu'une zone est grande, sans rien
    changer au résultat : le test « point dans polygone » donne la même réponse.
    """
    par_tuile: dict[Tuile, list[dict]] = defaultdict(list)
    emprises: dict[Tuile, object] = {}
    for geometrie, code in zones:
        ouest, sud, est, nord = geometrie.bounds
        candidates = tuiles_de_l_emprise(ouest, sud, est, nord, zoom)
        for tuile in candidates:
            if len(candidates) == 1:
                # La zone tient dans une seule tuile : rien à découper.
                part = geometrie
            else:
                cadre = emprises.get(tuile)
                if cadre is None:
                    cadre = box(*emprise_tuile(tuile))
                    emprises[tuile] = cadre
                if not geometrie.intersects(cadre):
                    continue
                part = geometrie.intersection(cadre)
            if part.is_empty or part.geom_type not in SURFACIQUES:
                # Un simple contact au bord donne un point ou une ligne :
                # rien à afficher, rien à tester.
                continue
            par_tuile[tuile].append(
                {
                    "type": "Feature",
                    "properties": {"c": int(code)},
                    "geometry": arrondis(mapping(part)),
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
