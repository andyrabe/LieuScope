import type { Point, Tile } from './types.js';

/**
 * Zoom fixe de la couche « zones climatiques locales ».
 * Choisi pour que chaque fichier de tuile reste bien sous 300 Ko.
 */
export const ZOOM_LCZ = 12;

/** Nombre de tuiles par côté à un zoom donné. */
export function tileCount(z: number): number {
  return 2 ** z;
}

/** Tuile XYZ qui contient un point. */
export function tileOf(point: Point, z: number): Tile {
  const n = tileCount(z);
  const lat = clamp(point.lat, -85.05112878, 85.05112878);
  const lonNorm = ((point.lon + 180) % 360 + 360) % 360 / 360;
  const latRad = (lat * Math.PI) / 180;
  const yNorm =
    (1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2;
  const x = clampInt(Math.floor(lonNorm * n), n);
  const y = clampInt(Math.floor(yNorm * n), n);
  return { z, x, y };
}

/** Coin nord-ouest d'une tuile, en WGS84. */
export function tileTopLeft(tile: Tile): Point {
  const n = tileCount(tile.z);
  const lon = (tile.x / n) * 360 - 180;
  const latRad = Math.atan(Math.sinh(Math.PI * (1 - (2 * tile.y) / n)));
  return { lon, lat: (latRad * 180) / Math.PI };
}

/** Emprise d'une tuile : [ouest, sud, est, nord]. */
export function tileBounds(tile: Tile): [number, number, number, number] {
  const nw = tileTopLeft(tile);
  const se = tileTopLeft({ z: tile.z, x: tile.x + 1, y: tile.y + 1 });
  return [nw.lon, se.lat, se.lon, nw.lat];
}

/**
 * La tuile du point et ses huit voisines.
 * On les interroge toutes : un point près d'un bord doit trouver la zone d'à côté.
 */
export function tileNeighbourhood(point: Point, z: number): Tile[] {
  const centre = tileOf(point, z);
  const n = tileCount(z);
  const tiles: Tile[] = [];
  for (let dy = -1; dy <= 1; dy += 1) {
    for (let dx = -1; dx <= 1; dx += 1) {
      const y = centre.y + dy;
      if (y < 0 || y >= n) continue;
      const x = (((centre.x + dx) % n) + n) % n;
      tiles.push({ z, x, y });
    }
  }
  // La tuile du point d'abord : c'est presque toujours la bonne.
  tiles.sort((a, b) => distanceRang(a, centre) - distanceRang(b, centre));
  return tiles;
}

function distanceRang(a: Tile, b: Tile): number {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

/** Chemin du fichier d'une tuile, relatif à la racine des données. */
export function tilePath(couche: string, tile: Tile): string {
  return `${couche}/${tile.z}/${tile.x}/${tile.y}.json`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function clampInt(value: number, n: number): number {
  return Math.min(Math.max(value, 0), n - 1);
}
