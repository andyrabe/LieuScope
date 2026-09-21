import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import type { NiveauCle } from './verdict/types.js';

/** Une commune couverte, telle que le pipeline la décrit. */
export interface Commune {
  insee: string;
  nom: string;
  slug: string;
  /** Centre approximatif [longitude, latitude], pour le lien vers la carte. */
  centre: [number, number];
  /** Part de la surface de la commune par niveau de sensibilité, en pourcents. */
  parts: Partial<Record<NiveauCle, number>>;
  /** Niveau le plus représenté. */
  dominante: NiveauCle;
}

export interface Couverture {
  aire: string;
  millesime: string;
  communes: Commune[];
}

const CHEMIN = fileURLToPath(new URL('../../public/data/lcz/communes.json', import.meta.url));

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
