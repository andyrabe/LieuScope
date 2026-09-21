"""Lecture du CSV des communes couvertes. Aucun accès réseau : on passe
« situe=False », le géocodage étant testé sur le terrain, pas ici.
"""

from __future__ import annotations

import pytest

from pipeline.lcz.communes import communes_de_l_aire, part_de_l_aire

CSV = """commune;insee_commune;population;surface_ha;couverture_lcz;detail_couverture_lcz;epci;siren_epci;departement;insee_departement;region;insee_region
L'Abergement-Clémenciat;01001;779;3260;0.00;[hors couverture];CC de la Dombes;200069193;Ain;01;Auvergne-Rhône-Alpes;84
Ambérieux-en-Dombes;01005;1700;1600;100.00;Lyon = 100.00 %;CC Dombes;200069193;Ain;01;Auvergne-Rhône-Alpes;84
Villeurbanne;69266;156929;1450;100.00;Lyon = 100.00 %;Métropole de Lyon;200046977;Rhône;69;Auvergne-Rhône-Alpes;84
Vienne;38544;29306;2300;62.50;Lyon = 40.00 %, Grenoble = 22.50 %;CA ViennAgglo;243800984;Isère;38;Auvergne-Rhône-Alpes;84
Échirolles;38151;36485;800;100.00;Grenoble = 100.00 %;Grenoble-Alpes Métropole;200040715;Isère;38;Auvergne-Rhône-Alpes;84
Sans code;;100;10;100.00;Lyon = 100.00 %;X;1;Rhône;69;ARA;84
"""


@pytest.fixture
def fichier(tmp_path):
    chemin = tmp_path / "communes.csv"
    chemin.write_text(CSV, encoding="utf-8")
    return chemin


def test_part_de_l_aire_simple():
    assert part_de_l_aire("Lyon = 100.00 %", "Lyon") == 100.0


def test_part_de_l_aire_parmi_plusieurs():
    detail = "Lyon = 40.00 %, Grenoble = 22.50 %"
    assert part_de_l_aire(detail, "Lyon") == 40.0
    assert part_de_l_aire(detail, "Grenoble") == 22.5


def test_part_de_l_aire_ignore_les_accents_et_la_casse():
    assert part_de_l_aire("Saint-Étienne = 75.00 %", "saint etienne") == 75.0


def test_part_de_l_aire_absente():
    assert part_de_l_aire("[hors couverture]", "Lyon") == 0.0
    assert part_de_l_aire("Grenoble = 100.00 %", "Lyon") == 0.0


def test_ne_garde_que_les_communes_de_l_aire(fichier):
    communes, _ = communes_de_l_aire(fichier, "Lyon", situe=False)
    noms = [c.nom for c in communes]
    assert "Échirolles" not in noms
    assert "L'Abergement-Clémenciat" not in noms
    assert {"Ambérieux-en-Dombes", "Villeurbanne", "Vienne"} <= set(noms)


def test_ecarte_une_ligne_sans_code_insee(fichier):
    communes, echecs = communes_de_l_aire(fichier, "Lyon", situe=False)
    assert echecs == 1
    assert all(c.insee for c in communes)


def test_retient_la_part_de_cette_aire_seulement(fichier):
    communes, _ = communes_de_l_aire(fichier, "Lyon", situe=False)
    vienne = next(c for c in communes if c.nom == "Vienne")
    assert vienne.couverture == 40.0


def test_champs_utiles_a_la_page(fichier):
    communes, _ = communes_de_l_aire(fichier, "Lyon", situe=False)
    villeurbanne = next(c for c in communes if c.nom == "Villeurbanne")
    assert villeurbanne.insee == "69266"
    assert villeurbanne.population == 156929
    assert villeurbanne.departement == "Rhône"
    assert villeurbanne.region == "Auvergne-Rhône-Alpes"
    assert villeurbanne.slug == "villeurbanne-69266"


def test_tri_alphabetique_sans_accent(fichier):
    communes, _ = communes_de_l_aire(fichier, "Lyon", situe=False)
    noms = [c.nom for c in communes]
    assert noms == sorted(noms, key=lambda n: n.lower().replace("é", "e").replace("è", "e"))
