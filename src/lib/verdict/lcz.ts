import type { NiveauCle, Verdict } from './types.js';

/**
 * Les zones climatiques locales (« local climate zones ») décrivent la forme
 * d'un îlot urbain : hauteur et densité du bâti, part de végétation, de sol nu
 * ou d'eau. Les dix-sept classes ci-dessous sont celles du producteur.
 */
export interface ClasseLcz {
  /** Code numérique utilisé dans nos fichiers de données. */
  code: number;
  /** Code officiel : « 1 » à « 10 » pour le bâti, « A » à « G » pour les sols. */
  officiel: string;
  /** Libellé officiel, en français. */
  libelle: string;
  /** Niveau de sensibilité retenu (voir docs/METHODE.md). */
  niveau: NiveauCle;
}

export const CLASSES_LCZ: ReadonlyArray<ClasseLcz> = [
  { code: 1, officiel: '1', libelle: 'Bâti compact de grande hauteur', niveau: 'tres_elevee' },
  { code: 2, officiel: '2', libelle: 'Bâti compact de hauteur moyenne', niveau: 'tres_elevee' },
  { code: 3, officiel: '3', libelle: 'Bâti compact de faible hauteur', niveau: 'tres_elevee' },
  { code: 4, officiel: '4', libelle: 'Bâti ouvert de grande hauteur', niveau: 'elevee' },
  { code: 5, officiel: '5', libelle: 'Bâti ouvert de hauteur moyenne', niveau: 'elevee' },
  { code: 6, officiel: '6', libelle: 'Bâti ouvert de faible hauteur', niveau: 'moderee' },
  { code: 7, officiel: '7', libelle: 'Bâti léger de faible hauteur', niveau: 'elevee' },
  { code: 8, officiel: '8', libelle: 'Grand bâti de faible hauteur', niveau: 'elevee' },
  { code: 9, officiel: '9', libelle: 'Bâti très dispersé', niveau: 'moderee' },
  { code: 10, officiel: '10', libelle: 'Industrie lourde', niveau: 'tres_elevee' },
  { code: 11, officiel: 'A', libelle: 'Arbres denses', niveau: 'faible' },
  { code: 12, officiel: 'B', libelle: 'Arbres épars', niveau: 'faible' },
  { code: 13, officiel: 'C', libelle: 'Broussailles, arbustes', niveau: 'moderee' },
  { code: 14, officiel: 'D', libelle: 'Végétation basse', niveau: 'moderee' },
  { code: 15, officiel: 'E', libelle: 'Roche ou revêtement imperméable', niveau: 'elevee' },
  { code: 16, officiel: 'F', libelle: 'Sol nu, sable', niveau: 'moderee' },
  { code: 17, officiel: 'G', libelle: 'Eau', niveau: 'faible' },
];

const PAR_CODE = new Map(CLASSES_LCZ.map((classe) => [classe.code, classe]));

export function classeLcz(code: number): ClasseLcz | undefined {
  return PAR_CODE.get(code);
}

/** L'échelle de sensibilité, du plus faible au plus fort. */
export const ECHELLE: ReadonlyArray<NiveauCle> = [
  'faible',
  'moderee',
  'elevee',
  'tres_elevee',
];

export const LIBELLE_NIVEAU: Readonly<Record<NiveauCle, string>> = {
  faible: 'faible',
  moderee: 'modérée',
  elevee: 'élevée',
  tres_elevee: 'très élevée',
};

/** Couleur du niveau. Elle ne porte jamais seule l'information. */
export const COULEUR_NIVEAU: Readonly<Record<NiveauCle, string>> = {
  faible: '#1b7f5a',
  moderee: '#8a6d1f',
  elevee: '#a3531b',
  tres_elevee: '#8f2727',
};

const SIGNIFIE: Readonly<Record<NiveauCle, string>> = {
  faible:
    "La forme de cet îlot — végétation, eau ou bâti très aéré — limite l'accumulation de chaleur. Les nuits d'été y restent en général plus fraîches qu'au centre de la ville.",
  moderee:
    "Cet îlot mêle bâti aéré et surfaces perméables. Il chauffe moins que les quartiers denses, mais plus que les parcs et les zones boisées.",
  elevee:
    "Les surfaces minérales dominent et la ventilation reste limitée. Par forte chaleur, l'îlot restitue la nuit une partie de ce qu'il a emmagasiné le jour.",
  tres_elevee:
    "Bâti serré ou activité industrielle : peu d'air circule, peu d'eau s'évapore. Ce sont les configurations où la chaleur nocturne se maintient le plus longtemps.",
};

const PHRASE: Readonly<Record<NiveauCle, string>> = {
  faible: 'Sensibilité faible à la surchauffe.',
  moderee: 'Sensibilité modérée à la surchauffe.',
  elevee: 'Sensibilité élevée à la surchauffe.',
  tres_elevee: 'Sensibilité très élevée à la surchauffe.',
};

const NE_DIT_PAS =
  "Ce n'est pas une température mesurée, ni un avis sur un logement : un appartement bien isolé, traversant ou ombragé peut rester confortable dans un îlot sensible, et l'inverse existe aussi. La zone décrit l'îlot autour de l'adresse, pas le bâtiment.";

/** Informations de source à afficher, lues dans les métadonnées du pipeline. */
export interface SourceLcz {
  producteur: string;
  millesime: string;
}

export function texteSource(source: SourceLcz): string {
  return `Source : ${source.producteur}, ${source.millesime}`;
}

/** Construit le verdict affichable à partir du code de classe. */
export function verdictLcz(code: number, source: SourceLcz): Verdict | undefined {
  const classe = classeLcz(code);
  if (classe === undefined) return undefined;
  const rang = ECHELLE.indexOf(classe.niveau) + 1;
  return {
    couche: 'lcz',
    niveau: classe.niveau,
    rang,
    rangMax: ECHELLE.length,
    phrase: PHRASE[classe.niveau],
    classe: classe.libelle,
    classeCode: classe.officiel,
    signifie: SIGNIFIE[classe.niveau],
    neDitPas: NE_DIT_PAS,
    source: texteSource(source),
  };
}
