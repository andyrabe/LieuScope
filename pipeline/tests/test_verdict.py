import pytest

from pipeline.common.verdict import CLASSES, ECHELLE, PAR_CODE, code_interne, niveau_du_code


def test_dix_sept_classes():
    assert len(CLASSES) == 17
    assert len({c.code for c in CLASSES}) == 17
    assert len({c.officiel for c in CLASSES}) == 17


def test_chaque_classe_est_sur_l_echelle():
    assert all(classe.niveau in ECHELLE for classe in CLASSES)


@pytest.mark.parametrize(
    ("brut", "attendu"),
    [
        ("1", 1),
        (10, 10),
        ("LCZ 2", 2),
        ("lcz_3", 3),
        ("A", 11),
        ("g", 17),
        (11, 11),
        (101, 11),
        (107, 17),
    ],
)
def test_ecritures_acceptees(brut, attendu):
    assert code_interne(brut) == attendu


@pytest.mark.parametrize("brut", [None, "", "  ", "NaN", 0, -9999, "Z", "42", "inconnu"])
def test_ecritures_refusees(brut):
    assert code_interne(brut) is None


def test_niveau_du_code():
    assert niveau_du_code(2) == "tres_elevee"
    assert niveau_du_code(11) == "faible"
    assert niveau_du_code(99) is None


def test_industrie_lourde_est_au_maximum():
    assert PAR_CODE[10].niveau == ECHELLE[-1]


def test_millesime_lu_dans_le_nom_du_fichier():
    """Le nom du fichier porte l'année de la donnée ; la fiche porte celle de sa mise à jour."""
    from pipeline.common.source import Jeu, Ressource, millesime_de_la_ressource

    jeu = Jeu(
        identifiant="x",
        titre="t",
        producteur="Cerema",
        licence="lov2",
        page="https://example.org",
        millesime="2026-07-21",
        ressources=(),
    )
    spot = Ressource("LCZ SPOT 2022 Lyon", "https://ex.org/lcz-spot-2022-lyon.zip", "zip", 1)
    assert millesime_de_la_ressource(spot, jeu) == "2022"

    sans_annee = Ressource("LCZ Lyon", "https://ex.org/lcz-lyon.zip", "zip", 1)
    assert millesime_de_la_ressource(sans_annee, jeu) == "2026"

    muet = Jeu("x", "t", "Cerema", "lov2", "https://ex.org", "", ())
    assert millesime_de_la_ressource(sans_annee, muet) == "millésime inconnu"
