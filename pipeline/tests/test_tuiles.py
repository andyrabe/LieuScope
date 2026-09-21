import math

from pipeline.common.tuiles import (
    ZOOM_LCZ,
    Tuile,
    emprise_tuile,
    tuile_du_point,
    tuiles_de_l_emprise,
)

BELLECOUR = (4.83223, 45.75778)


def test_origine_au_zoom_1():
    assert tuile_du_point(0, 0, 1) == Tuile(1, 1, 1)


def test_une_seule_tuile_au_zoom_0():
    assert tuile_du_point(4.83, 45.75, 0) == Tuile(0, 0, 0)


def test_emprise_contient_le_point():
    tuile = tuile_du_point(*BELLECOUR, ZOOM_LCZ)
    ouest, sud, est, nord = emprise_tuile(tuile)
    assert ouest <= BELLECOUR[0] <= est
    assert sud <= BELLECOUR[1] <= nord


def test_chemin_de_tuile():
    assert Tuile(12, 2074, 1409).chemin == "12/2074/1409.json"


def test_emprise_petite_couvre_au_moins_une_tuile():
    tuiles = tuiles_de_l_emprise(4.80, 45.74, 4.86, 45.78, ZOOM_LCZ)
    assert tuile_du_point(*BELLECOUR, ZOOM_LCZ) in tuiles


def test_tuile_reste_dans_la_grille_pres_du_pole():
    tuile = tuile_du_point(179.9, 89.0, 5)
    assert 0 <= tuile.x < 2**5
    assert 0 <= tuile.y < 2**5


def test_meme_resultat_que_le_site():
    """Le site calcule la tuile avec la même formule : on la refait ici."""
    lon, lat = BELLECOUR
    n = 2**ZOOM_LCZ
    attendu_x = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    attendu_y = int(
        (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n
    )
    tuile = tuile_du_point(lon, lat, ZOOM_LCZ)
    assert (tuile.x, tuile.y) == (attendu_x, attendu_y)
