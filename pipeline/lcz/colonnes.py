"""Repérage des colonnes utiles dans le fichier du producteur.

Le nom exact des colonnes n'est pas garanti d'une version à l'autre du jeu :
on cherche parmi des noms plausibles, et on s'arrête net si rien ne convient,
plutôt que de deviner et de publier un verdict faux.
"""

from __future__ import annotations

from collections.abc import Iterable

from pipeline.common.source import sans_accent
from pipeline.common.verdict import code_interne

NOMS_CLASSE = (
    "lcz",
    "lcz_class",
    "classe_lcz",
    "classe",
    "code_lcz",
    "lcz_code",
    "zone_climatique",
    "typo",
)
NOMS_INSEE = ("insee_com", "code_insee", "insee", "codgeo", "com_code", "codecommune")
NOMS_COMMUNE = ("nom_com", "commune", "nom_commune", "libgeo", "com_nom", "nom")


def _trouve(colonnes: Iterable[str], candidats: tuple[str, ...]) -> str | None:
    index = {sans_accent(str(c)).replace(" ", "_"): str(c) for c in colonnes}
    for candidat in candidats:
        if candidat in index:
            return index[candidat]
    return None


def colonne_classe(donnees) -> str:
    """Colonne qui porte la classe de zone."""
    trouvee = _trouve(donnees.columns, NOMS_CLASSE)
    if trouvee is not None and _majorite_lisible(donnees[trouvee]):
        return trouvee
    # Dernier recours : la colonne dont les valeurs se traduisent le mieux.
    meilleure, score_max = None, 0.0
    for colonne in donnees.columns:
        if colonne == donnees.geometry.name:
            continue
        score = _part_lisible(donnees[colonne])
        if score > score_max:
            meilleure, score_max = str(colonne), score
    if meilleure is not None and score_max >= 0.9:
        return meilleure
    raise SystemExit(
        "Impossible de repérer la colonne des classes de zone.\n"
        f"Colonnes présentes : {', '.join(str(c) for c in donnees.columns)}\n"
        "Ajoutez son nom dans pipeline/lcz/colonnes.py (NOMS_CLASSE)."
    )


def colonne_insee(donnees) -> str | None:
    return _trouve(donnees.columns, NOMS_INSEE)


def colonne_commune(donnees) -> str | None:
    return _trouve(donnees.columns, NOMS_COMMUNE)


def _part_lisible(serie) -> float:
    echantillon = serie.dropna().head(500)
    if len(echantillon) == 0:
        return 0.0
    lisibles = sum(1 for valeur in echantillon if code_interne(valeur) is not None)
    return lisibles / len(echantillon)


def _majorite_lisible(serie) -> bool:
    return _part_lisible(serie) >= 0.9
