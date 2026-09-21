"""Classes de zones climatiques locales et niveaux de sensibilité.

Ce tableau doit rester identique à celui du site (`src/lib/verdict/lcz.ts`).
Le test `pipeline/tests/test_coherence.py` le vérifie à chaque exécution.
"""

from __future__ import annotations

from dataclasses import dataclass

#: L'échelle, du plus faible au plus fort.
ECHELLE = ("faible", "moderee", "elevee", "tres_elevee")


@dataclass(frozen=True)
class ClasseLcz:
    code: int
    officiel: str
    libelle: str
    niveau: str


CLASSES: tuple[ClasseLcz, ...] = (
    ClasseLcz(1, "1", "Bâti compact de grande hauteur", "tres_elevee"),
    ClasseLcz(2, "2", "Bâti compact de hauteur moyenne", "tres_elevee"),
    ClasseLcz(3, "3", "Bâti compact de faible hauteur", "tres_elevee"),
    ClasseLcz(4, "4", "Bâti ouvert de grande hauteur", "elevee"),
    ClasseLcz(5, "5", "Bâti ouvert de hauteur moyenne", "elevee"),
    ClasseLcz(6, "6", "Bâti ouvert de faible hauteur", "moderee"),
    ClasseLcz(7, "7", "Bâti léger de faible hauteur", "elevee"),
    ClasseLcz(8, "8", "Grand bâti de faible hauteur", "elevee"),
    ClasseLcz(9, "9", "Bâti très dispersé", "moderee"),
    ClasseLcz(10, "10", "Industrie lourde", "tres_elevee"),
    ClasseLcz(11, "A", "Arbres denses", "faible"),
    ClasseLcz(12, "B", "Arbres épars", "faible"),
    ClasseLcz(13, "C", "Broussailles, arbustes", "moderee"),
    ClasseLcz(14, "D", "Végétation basse", "moderee"),
    ClasseLcz(15, "E", "Roche ou revêtement imperméable", "elevee"),
    ClasseLcz(16, "F", "Sol nu, sable", "moderee"),
    ClasseLcz(17, "G", "Eau", "faible"),
)

PAR_CODE = {classe.code: classe for classe in CLASSES}
PAR_OFFICIEL = {classe.officiel: classe for classe in CLASSES}


def code_interne(valeur: object) -> int | None:
    """Traduit la valeur brute du producteur en code interne de 1 à 17.

    Le jeu peut noter les classes « 1 » à « 10 » et « A » à « G », ou bien
    « LCZ 2 », ou encore 101 à 107 pour les couvertures du sol : on accepte ces
    trois écritures et on refuse tout le reste, plutôt que de deviner.
    """
    if valeur is None:
        return None
    texte = str(valeur).strip().upper()
    if not texte or texte in {"NAN", "NONE", "NULL", "0", "-9999"}:
        return None
    texte = texte.removeprefix("LCZ").strip().lstrip("_-").strip()

    if texte in PAR_OFFICIEL:
        return PAR_OFFICIEL[texte].code
    if texte.isdigit():
        entier = int(texte)
        if 1 <= entier <= 10:
            return entier
        # Certains fichiers numérotent les couvertures du sol de 101 à 107,
        # d'autres de 11 à 17 : les deux tombent sur A à G dans cet ordre.
        if 101 <= entier <= 107:
            return entier - 101 + 11
        if 11 <= entier <= 17:
            return entier
    if len(texte) == 1 and "A" <= texte <= "G":
        return PAR_OFFICIEL[texte].code
    return None


def niveau_du_code(code: int) -> str | None:
    classe = PAR_CODE.get(code)
    return None if classe is None else classe.niveau
