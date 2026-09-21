"""Communes couvertes par une aire, d'après le CSV publié par le Cerema.

Le jeu des zones climatiques ne dit pas à quelle commune appartient chaque
îlot. En revanche le Cerema publie, à côté, un fichier qui liste toutes les
communes de France avec l'aire qui les couvre et la part couverte. C'est de là
que vient la liste des pages par commune.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from pipeline.common.geocodage import centre_de_la_commune
from pipeline.common.source import sans_accent, slug


@dataclass(frozen=True)
class Commune:
    insee: str
    nom: str
    slug: str
    population: int | None
    couverture: float
    departement: str
    region: str
    centre: tuple[float, float] | None


def _nombre(texte: str | None) -> float:
    if not texte:
        return 0.0
    try:
        return float(texte.replace(",", ".").strip())
    except ValueError:
        return 0.0


def _entier(texte: str | None) -> int | None:
    if not texte:
        return None
    try:
        return int(float(texte.replace(",", ".").strip()))
    except ValueError:
        return None


def part_de_l_aire(detail: str, aire: str) -> float:
    """Part de la commune couverte par cette aire, lue dans « Lyon = 100.00 % »."""
    cherche = sans_accent(aire)
    for morceau in detail.split(","):
        nom, _, valeur = morceau.partition("=")
        if sans_accent(nom) != cherche:
            continue
        trouve = re.search(r"[\d.,]+", valeur)
        return _nombre(trouve.group(0)) if trouve else 0.0
    return 0.0


def lis_le_csv(chemin: Path, aire: str) -> list[dict[str, str]]:
    """Lignes du CSV qui concernent l'aire demandée."""
    with chemin.open(encoding="utf-8-sig", errors="replace", newline="") as lecture:
        table = csv.DictReader(lecture, delimiter=";")
        return [
            ligne
            for ligne in table
            if part_de_l_aire(str(ligne.get("detail_couverture_lcz") or ""), aire) > 0
        ]


def communes_de_l_aire(chemin: Path, aire: str, *, situe: bool = True) -> tuple[list[Commune], int]:
    """Communes couvertes par l'aire, situées sur la carte. Renvoie aussi le nombre d'échecs.

    Une commune qu'on ne sait pas situer est écartée : une page qui pointe au
    mauvais endroit serait pire que pas de page du tout.
    """
    retenues: list[Commune] = []
    echecs = 0
    for ligne in lis_le_csv(chemin, aire):
        insee = str(ligne.get("insee_commune") or "").strip()
        nom = str(ligne.get("commune") or "").strip()
        if not insee or not nom:
            echecs += 1
            continue
        centre = centre_de_la_commune(nom, insee) if situe else None
        if situe and centre is None:
            echecs += 1
            continue
        retenues.append(
            Commune(
                insee=insee,
                nom=nom,
                slug=slug(f"{nom}-{insee}"),
                population=_entier(ligne.get("population")),
                couverture=round(
                    part_de_l_aire(str(ligne.get("detail_couverture_lcz") or ""), aire), 1
                ),
                departement=str(ligne.get("departement") or "").strip(),
                region=str(ligne.get("region") or "").strip(),
                centre=centre,
            )
        )
    retenues.sort(key=lambda commune: sans_accent(commune.nom))
    return retenues, echecs
