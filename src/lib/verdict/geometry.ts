import type {
  AreaGeometry,
  MultiPolygonCoords,
  Point,
  PolygonCoords,
  Ring,
} from './types.js';

/**
 * Point dans un anneau, par la méthode du lancer de rayon.
 * Un point posé exactement sur le bord est considéré dedans.
 */
export function pointInRing(point: Point, ring: Ring): boolean {
  if (ring.length < 3) return false;
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i, i += 1) {
    const a = ring[i];
    const b = ring[j];
    if (a === undefined || b === undefined) continue;
    const [xi, yi] = a;
    const [xj, yj] = b;
    if (onSegment(point, a, b)) return true;
    const intersecte =
      yi > point.lat !== yj > point.lat &&
      point.lon < ((xj - xi) * (point.lat - yi)) / (yj - yi) + xi;
    if (intersecte) inside = !inside;
  }
  return inside;
}

function onSegment(
  p: Point,
  a: readonly [number, number],
  b: readonly [number, number],
): boolean {
  const [ax, ay] = a;
  const [bx, by] = b;
  const longueur = (bx - ax) ** 2 + (by - ay) ** 2;
  // Un anneau fermé répète son premier point : ce segment de longueur nulle
  // ne contient que ce point-là, et surtout pas tout le plan.
  if (longueur === 0) return p.lon === ax && p.lat === ay;
  const croix = (bx - ax) * (p.lat - ay) - (by - ay) * (p.lon - ax);
  if (Math.abs(croix) > 1e-12) return false;
  const produit = (p.lon - ax) * (bx - ax) + (p.lat - ay) * (by - ay);
  if (produit < 0) return false;
  return produit <= longueur;
}

/** Point dans un polygone : dans l'anneau extérieur et dans aucun trou. */
export function pointInPolygon(point: Point, coords: PolygonCoords): boolean {
  const exterieur = coords[0];
  if (exterieur === undefined || !pointInRing(point, exterieur)) return false;
  for (let i = 1; i < coords.length; i += 1) {
    const trou = coords[i];
    if (trou !== undefined && pointInRing(point, trou)) return false;
  }
  return true;
}

/** Point dans l'un des polygones d'un multipolygone. */
export function pointInMultiPolygon(
  point: Point,
  coords: MultiPolygonCoords,
): boolean {
  return coords.some((polygone) => pointInPolygon(point, polygone));
}

/** Point dans une géométrie surfacique GeoJSON. */
export function pointInGeometry(point: Point, geometry: AreaGeometry): boolean {
  return geometry.type === 'Polygon'
    ? pointInPolygon(point, geometry.coordinates)
    : pointInMultiPolygon(point, geometry.coordinates);
}

/** Emprise d'une géométrie : [ouest, sud, est, nord]. */
export function bbox(geometry: AreaGeometry): [number, number, number, number] {
  let ouest = Infinity;
  let sud = Infinity;
  let est = -Infinity;
  let nord = -Infinity;
  const polygones: MultiPolygonCoords =
    geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
  for (const polygone of polygones) {
    for (const anneau of polygone) {
      for (const sommet of anneau) {
        const [x, y] = sommet;
        if (x < ouest) ouest = x;
        if (x > est) est = x;
        if (y < sud) sud = y;
        if (y > nord) nord = y;
      }
    }
  }
  return [ouest, sud, est, nord];
}

/** Test rapide : le point est-il dans l'emprise ? Évite les calculs inutiles. */
export function pointInBbox(
  point: Point,
  box: readonly [number, number, number, number],
): boolean {
  const [ouest, sud, est, nord] = box;
  return (
    point.lon >= ouest && point.lon <= est && point.lat >= sud && point.lat <= nord
  );
}

const RAYON_TERRE_M = 6371008.8;

/** Distance en mètres entre deux points, formule de haversine. */
export function distanceM(a: Point, b: Point): number {
  const phi1 = (a.lat * Math.PI) / 180;
  const phi2 = (b.lat * Math.PI) / 180;
  const dPhi = phi2 - phi1;
  const dLambda = ((b.lon - a.lon) * Math.PI) / 180;
  const h =
    Math.sin(dPhi / 2) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(dLambda / 2) ** 2;
  return 2 * RAYON_TERRE_M * Math.asin(Math.min(1, Math.sqrt(h)));
}
