import type { ChargeurTuile } from './verdict/lookup.js';
import type { SourceLcz } from './verdict/lcz.js';
import type { FeatureCollection, LczProperties, Tile } from './verdict/types.js';
import { tilePath } from './verdict/tiles.js';

/** Métadonnées écrites par le pipeline à côté des tuiles. */
export interface MetaLcz extends SourceLcz {
  couche: string;
  zoom: number;
  aire: string;
  /** Date de téléchargement de la source, au format AAAA-MM-JJ. */
  telecharge: string;
  licence: string;
  url: string;
}

/** Racine des données servies, en tenant compte du sous-dossier du site. */
export function racineDonnees(base: string): string {
  const propre = base.endsWith('/') ? base.slice(0, -1) : base;
  return `${propre}/data`;
}

/** Crée un chargeur de tuiles qui garde en mémoire ce qu'il a déjà lu. */
export function chargeurTuile(base: string): ChargeurTuile {
  const racine = racineDonnees(base);
  const cache = new Map<string, FeatureCollection<LczProperties> | null>();
  return async (tuile: Tile) => {
    const chemin = tilePath('lcz', tuile);
    const enCache = cache.get(chemin);
    if (enCache !== undefined) return enCache;
    let resultat: FeatureCollection<LczProperties> | null = null;
    try {
      const reponse = await fetch(`${racine}/${chemin}`);
      if (reponse.ok) {
        resultat = (await reponse.json()) as FeatureCollection<LczProperties>;
      }
    } catch {
      resultat = null;
    }
    cache.set(chemin, resultat);
    return resultat;
  };
}

/** Lit les métadonnées de la couche. Renvoie null si les données manquent. */
export async function chargeMeta(base: string): Promise<MetaLcz | null> {
  try {
    const reponse = await fetch(`${racineDonnees(base)}/lcz/meta.json`);
    if (!reponse.ok) return null;
    return (await reponse.json()) as MetaLcz;
  } catch {
    return null;
  }
}
