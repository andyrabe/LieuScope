"""Découpe en tuiles : on vérifie le chemin complet, sans rien télécharger."""

from __future__ import annotations

import json

import pytest
from shapely.geometry import box, shape

from pipeline.common.tuiles import ZOOM_LCZ, emprise_tuile, tuile_du_point
from pipeline.lcz.decoupe import arrondis, ecris_les_tuiles, range_par_tuile
from pipeline.lcz.rapport import verdict_au_point

BELLECOUR = (4.83223, 45.75778)


def test_arrondi_a_cinq_decimales():
    geometrie = {"type": "Point", "coordinates": [4.832234567, 45.757781234]}
    assert arrondis(geometrie)["coordinates"] == [4.83223, 45.75778]


def test_une_zone_tient_dans_sa_tuile():
    tuile = tuile_du_point(*BELLECOUR, ZOOM_LCZ)
    ouest, sud, est, nord = emprise_tuile(tuile)
    petite = box(
        ouest + (est - ouest) * 0.4,
        sud + (nord - sud) * 0.4,
        ouest + (est - ouest) * 0.6,
        sud + (nord - sud) * 0.6,
    )
    par_tuile = range_par_tuile([(petite, 2)], ZOOM_LCZ)
    assert list(par_tuile) == [tuile]


def test_une_zone_a_cheval_est_decoupee_dans_chaque_tuile():
    tuile = tuile_du_point(*BELLECOUR, ZOOM_LCZ)
    ouest, sud, est, nord = emprise_tuile(tuile)
    largeur = est - ouest
    hauteur = nord - sud
    a_cheval = box(
        est - largeur * 0.1, sud + hauteur * 0.1, est + largeur * 0.1, nord - hauteur * 0.1
    )
    par_tuile = range_par_tuile([(a_cheval, 5)], ZOOM_LCZ)
    assert len(par_tuile) == 2
    assert all(len(features) == 1 for features in par_tuile.values())
    # Chaque morceau reste dans sa tuile, et les deux recollés font le tout.
    # L'arrondi à 5 décimales a lieu après la découpe : un morceau peut
    # dépasser du bord d'environ un mètre, ce qui ne change aucun verdict.
    ARRONDI = 2e-5
    total = 0.0
    for t, features in par_tuile.items():
        cadre = box(*emprise_tuile(t))
        morceau = shape(features[0]["geometry"])
        assert morceau.difference(cadre.buffer(ARRONDI)).is_empty
        total += morceau.area
    # Même tolérance côté surface : arrondir les sommets d'une zone de cette
    # taille à cinq décimales en déplace le contour de quelques pour mille.
    assert total == pytest.approx(a_cheval.area, rel=5e-3)


def test_ecriture_puis_relecture_au_point(tmp_path):
    tuile = tuile_du_point(*BELLECOUR, ZOOM_LCZ)
    ouest, sud, est, nord = emprise_tuile(tuile)
    zone = box(ouest + 0.001, sud + 0.001, est - 0.001, nord - 0.001)

    par_tuile = range_par_tuile([(zone, 2)], ZOOM_LCZ)
    poids = ecris_les_tuiles(par_tuile, tmp_path)

    fichier = tmp_path / tuile.chemin
    assert fichier.exists()
    assert poids[tuile.chemin] == len(fichier.read_text(encoding="utf-8").encode("utf-8"))

    contenu = json.loads(fichier.read_text(encoding="utf-8"))
    assert contenu["type"] == "FeatureCollection"
    assert contenu["features"][0]["properties"] == {"c": 2}

    niveau, classe = verdict_au_point(*BELLECOUR, tmp_path, ZOOM_LCZ)
    assert (niveau, classe) == ("tres_elevee", "2")


def test_hors_couverture(tmp_path):
    assert verdict_au_point(2.35, 48.85, tmp_path, ZOOM_LCZ) == (None, None)


def test_le_json_est_minifie(tmp_path):
    tuile = tuile_du_point(*BELLECOUR, ZOOM_LCZ)
    ouest, sud, est, nord = emprise_tuile(tuile)
    zone = box(ouest + 0.001, sud + 0.001, est - 0.001, nord - 0.001)
    ecris_les_tuiles(range_par_tuile([(zone, 2)], ZOOM_LCZ), tmp_path)
    contenu = (tmp_path / tuile.chemin).read_text(encoding="utf-8")
    assert ", " not in contenu and '": ' not in contenu and "\n" not in contenu
