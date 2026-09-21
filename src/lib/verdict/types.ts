/** Types partagés de la logique de verdict. */

/** Un point en WGS84 (longitude, latitude), en degrés. */
export interface Point {
  lon: number;
  lat: number;
}

/** Coordonnées d'une tuile XYZ (celles des fonds de carte usuels). */
export interface Tile {
  z: number;
  x: number;
  y: number;
}

/** Anneau d'un polygone : liste de [lon, lat]. Le premier point est répété à la fin. */
export type Ring = ReadonlyArray<readonly [number, number]>;

/** Polygone GeoJSON : anneau extérieur, puis trous éventuels. */
export type PolygonCoords = ReadonlyArray<Ring>;

/** MultiPolygone GeoJSON. */
export type MultiPolygonCoords = ReadonlyArray<PolygonCoords>;

export interface PolygonGeometry {
  type: 'Polygon';
  coordinates: PolygonCoords;
}

export interface MultiPolygonGeometry {
  type: 'MultiPolygon';
  coordinates: MultiPolygonCoords;
}

export type AreaGeometry = PolygonGeometry | MultiPolygonGeometry;

export interface Feature<P> {
  type: 'Feature';
  geometry: AreaGeometry;
  properties: P;
}

export interface FeatureCollection<P> {
  type: 'FeatureCollection';
  features: ReadonlyArray<Feature<P>>;
}

/** Propriétés d'une zone climatique locale dans nos tuiles de données. */
export interface LczProperties {
  /** Code de la classe, de 1 à 17 (voir lcz.ts). */
  c: number;
}

/** Les cinq niveaux possibles d'un verdict. Ici la couche chaleur en utilise quatre. */
export type NiveauCle = 'faible' | 'moderee' | 'elevee' | 'tres_elevee';

/** Un verdict affichable, tel qu'attendu par l'interface. */
export interface Verdict {
  /** Identifiant de la couche, ex. « lcz ». */
  couche: string;
  /** Niveau retenu. */
  niveau: NiveauCle;
  /** Rang du niveau, de 1 (le plus faible) au nombre de niveaux. */
  rang: number;
  /** Nombre total de niveaux de l'échelle. */
  rangMax: number;
  /** La phrase de verdict, courte. */
  phrase: string;
  /** Classe officielle du producteur, reprise telle quelle. */
  classe: string;
  /** Code de la classe officielle. */
  classeCode: string;
  /** Ce que cela veut dire. */
  signifie: string;
  /** Ce que cela ne dit pas. */
  neDitPas: string;
  /** Source et millésime, à afficher à côté de la donnée. */
  source: string;
}
