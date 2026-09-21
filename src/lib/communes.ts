import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

/** Une commune couverte, telle que le pipeline la décrit. */
export interface Commune {
  /** Code INSEE, qui identifie la commune sans ambiguïté. */
  insee: string;
  nom: string;
  /** Identifiant d'adresse web, ex. « villeurbanne-69266 ». */
  slug: string;
  /** Population légale, quand le producteur la donne. */
  population: number | null;
  /** Part de la commune couverte par les données, en pourcents. */
  couverture: number;
  departement: string;
  region: string;
  /** Centre de la commune [longitude, latitude], pour centrer la carte. */
  centre: number[];
}

export interface Couverture {
  aire: string;
  millesime: string;
  communes: Commune[];
}

// Chemin depuis la racine du projet, pas depuis ce fichier : à la
// construction, ce module s'exécute depuis dist/ et un chemin relatif à
// lui-même pointe à côté. L'erreur est muette — aucune page ne serait
// construite — d'où le contrôle ajouté dans scripts/poids.mjs.
const DONNEES = join(process.cwd(), 'public', 'data', 'lcz');
const CHEMIN = join(DONNEES, 'communes.json');
const CHEMIN_META = join(DONNEES, 'meta.json');

/** Ce que le pipeline a publié : l'aire traitée, ou null si rien n'est en ligne. */
export function aireEnLigne(): { aire: string; millesime: string } | null {
  if (!existsSync(CHEMIN_META)) return null;
  try {
    const meta = JSON.parse(readFileSync(CHEMIN_META, 'utf8')) as {
      aire?: string;
      millesime?: string;
    };
    if (meta.aire === undefined) return null;
    return { aire: meta.aire, millesime: meta.millesime ?? '' };
  } catch {
    return null;
  }
}

/**
 * Lit la liste des communes couvertes, écrite par le pipeline.
 * Tant que le pipeline n'a pas tourné, la liste est vide : aucune page
 * de commune n'est alors construite, plutôt qu'une page vide.
 */
export function couverture(): Couverture {
  if (!existsSync(CHEMIN)) return { aire: '', millesime: '', communes: [] };
  try {
    const brut = JSON.parse(readFileSync(CHEMIN, 'utf8')) as Partial<Couverture>;
    return {
      aire: brut.aire ?? '',
      millesime: brut.millesime ?? '',
      communes: brut.communes ?? [],
    };
  } catch {
    return { aire: '', millesime: '', communes: [] };
  }
}
