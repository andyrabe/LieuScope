"""Le site et le pipeline doivent classer les zones exactement pareil.

Ce test lit le tableau TypeScript et le compare au tableau Python. Sans lui,
les deux listes divergeraient un jour sans que personne ne s'en aperçoive.
"""

from __future__ import annotations

import re
from pathlib import Path

from pipeline.common.tuiles import ZOOM_LCZ
from pipeline.common.verdict import CLASSES, ECHELLE

RACINE = Path(__file__).resolve().parents[2]
SOURCE_TS = RACINE / "src" / "lib" / "verdict" / "lcz.ts"
TUILES_TS = RACINE / "src" / "lib" / "verdict" / "tiles.ts"

LIGNE = re.compile(
    r"\{\s*code:\s*(\d+),\s*officiel:\s*'([^']+)',\s*libelle:\s*'([^']*)',\s*niveau:\s*'([^']+)'\s*\}"
)


def classes_du_site() -> list[tuple[int, str, str, str]]:
    texte = SOURCE_TS.read_text(encoding="utf-8")
    return [
        (int(code), officiel, libelle, niveau)
        for code, officiel, libelle, niveau in LIGNE.findall(texte)
    ]


def test_le_site_declare_bien_dix_sept_classes():
    assert len(classes_du_site()) == 17


def test_les_deux_tableaux_sont_identiques():
    cote_python = [(c.code, c.officiel, c.libelle, c.niveau) for c in CLASSES]
    assert classes_du_site() == cote_python


def test_la_meme_echelle_des_deux_cotes():
    texte = SOURCE_TS.read_text(encoding="utf-8")
    bloc = re.search(r"export const ECHELLE[^=]*=\s*\[(.*?)\]", texte, re.S)
    assert bloc is not None
    cote_site = tuple(re.findall(r"'([a-z_]+)'", bloc.group(1)))
    assert cote_site == ECHELLE


def test_le_meme_zoom_des_deux_cotes():
    """Un zoom différent ici et là-bas ferait chercher la donnée au mauvais endroit."""
    texte = TUILES_TS.read_text(encoding="utf-8")
    trouve = re.search(r"export const ZOOM_LCZ = (\d+);", texte)
    assert trouve is not None
    assert int(trouve.group(1)) == ZOOM_LCZ
