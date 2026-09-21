import { bbox, pointInBbox, pointInGeometry } from './geometry.js';
import { ZOOM_LCZ, tileNeighbourhood, tileOf } from './tiles.js';
import type {
  FeatureCollection,
  LczProperties,
  Point,
  Tile,
} from './types.js';

/**
 * Charge le fichier d'une tuile. Renvoie null si la tuile n'existe pas :
 * c'est le cas normal hors des aires couvertes.
 */
export type ChargeurTuile = (
  tile: Tile,
) => Promise<FeatureCollection<LczProperties> | null>;

export type ResultatLcz =
  | { trouve: true; code: number }
  /** Aucune tuile de données autour du point : l'adresse n'est pas couverte. */
  | { trouve: false; raison: 'hors_couverture' }
  /** Des tuiles existent, mais aucune zone ne contient exactement le point. */
  | { trouve: false; raison: 'hors_zone' };

/**
 * Cherche la zone climatique locale qui contient le point.
 * On regarde la tuile du point, puis au besoin ses voisines : une adresse
 * posée sur un bord doit trouver la zone d'à côté.
 */
export async function chercheLcz(
  point: Point,
  charge: ChargeurTuile,
  zoom: number = ZOOM_LCZ,
): Promise<ResultatLcz> {
  const tuiles = tileNeighbourhood(point, zoom);
  const centre = tileOf(point, zoom);
  let uneTuileExiste = false;

  for (const tuile of tuiles) {
    // On ne descend chez les voisines que si la tuile du point n'a rien donné.
    const collection = await charge(tuile);
    if (collection === null) continue;
    uneTuileExiste = true;
    const code = codeAuPoint(point, collection);
    if (code !== undefined) return { trouve: true, code };
    if (tuile.x === centre.x && tuile.y === centre.y) {
      // La tuile du point existe et ne contient pas le point : inutile
      // d'interroger les voisines, leurs zones sont ailleurs.
      return { trouve: false, raison: 'hors_zone' };
    }
  }

  return {
    trouve: false,
    raison: uneTuileExiste ? 'hors_zone' : 'hors_couverture',
  };
}

/** Code de la première zone qui contient le point, s'il y en a une. */
export function codeAuPoint(
  point: Point,
  collection: FeatureCollection<LczProperties>,
): number | undefined {
  for (const feature of collection.features) {
    if (!pointInBbox(point, bbox(feature.geometry))) continue;
    if (pointInGeometry(point, feature.geometry)) return feature.properties.c;
  }
  return undefined;
}
