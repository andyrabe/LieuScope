import type { ChargeurTuile } from '../lib/verdict/lookup.js';
import { ZOOM_LCZ, tileNeighbourhood } from '../lib/verdict/tiles.js';
import { CLASSES_LCZ, COULEUR_NIVEAU } from '../lib/verdict/lcz.js';
import type { Feature, LczProperties, Point } from '../lib/verdict/types.js';

/** Style du fond de carte : Plan IGN de la Géoplateforme, sans clé. */
const STYLE_IGN =
  'https://data.geopf.fr/annexes/ressources/vectorTiles/styles/PLAN.IGN/standard.json';
/** Repli si la Géoplateforme ne répond pas : fond OpenMapTiles d'Etalab. */
const STYLE_REPLI = 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json';

const ATTRIBUTION = 'Fond de carte : IGN — Géoplateforme | Zones climatiques locales : Cerema';

let carte: import('maplibre-gl').Map | undefined;

/**
 * Charge la feuille de style de MapLibre au dernier moment. Importée comme un
 * module, elle serait liée dans le <head> et retarderait l'affichage du verdict.
 */
function poseFeuilleDeStyle(): void {
  const href = `${import.meta.env.BASE_URL.replace(/\/$/, '')}/carte/maplibre-gl.css`;
  if (document.querySelector(`link[href="${href}"]`) !== null) return;
  const lien = document.createElement('link');
  lien.rel = 'stylesheet';
  lien.href = href;
  document.head.append(lien);
}

export async function montreCarte(point: Point, charge: ChargeurTuile): Promise<void> {
  poseFeuilleDeStyle();
  const maplibre = await import('maplibre-gl');
  const conteneur = document.getElementById('carte');
  if (conteneur === null) return;

  const zones = await collecteZones(point, charge);
  const style = await chargeStyle();

  if (carte === undefined) {
    carte = new maplibre.Map({
      container: conteneur,
      style,
      center: [point.lon, point.lat],
      zoom: 14,
      attributionControl: { compact: false, customAttribution: ATTRIBUTION },
    });
    carte.addControl(new maplibre.NavigationControl({ showCompass: false }), 'top-right');
    await new Promise<void>((resoudre) => {
      carte?.on('load', () => resoudre());
    });
  } else {
    carte.setCenter([point.lon, point.lat]);
    carte.setZoom(14);
  }

  poseZones(carte, zones, point);
  carte.resize();
}

/** Rassemble les zones des tuiles autour du point, pour les dessiner. */
async function collecteZones(
  point: Point,
  charge: ChargeurTuile,
): Promise<Array<Feature<LczProperties>>> {
  const tuiles = tileNeighbourhood(point, ZOOM_LCZ);
  const collections = await Promise.all(tuiles.map((tuile) => charge(tuile)));
  return collections.flatMap((collection) =>
    collection === null ? [] : [...collection.features],
  );
}

function poseZones(
  carte: import('maplibre-gl').Map,
  zones: Array<Feature<LczProperties>>,
  point: Point,
): void {
  const donnees = {
    type: 'FeatureCollection' as const,
    features: zones.map((zone) => ({
      type: 'Feature' as const,
      geometry: zone.geometry,
      properties: { couleur: couleurDeCode(zone.properties.c) },
    })),
  };

  const source = carte.getSource('lcz');
  if (source !== undefined && 'setData' in source) {
    (source as import('maplibre-gl').GeoJSONSource).setData(donnees);
  } else {
    carte.addSource('lcz', { type: 'geojson', data: donnees });
    carte.addLayer({
      id: 'lcz-remplissage',
      type: 'fill',
      source: 'lcz',
      paint: { 'fill-color': ['get', 'couleur'], 'fill-opacity': 0.45 },
    });
    carte.addLayer({
      id: 'lcz-contour',
      type: 'line',
      source: 'lcz',
      paint: { 'line-color': ['get', 'couleur'], 'line-width': 1 },
    });
  }

  const marqueur = {
    type: 'FeatureCollection' as const,
    features: [
      {
        type: 'Feature' as const,
        geometry: { type: 'Point' as const, coordinates: [point.lon, point.lat] },
        properties: {},
      },
    ],
  };
  const sourcePoint = carte.getSource('adresse');
  if (sourcePoint !== undefined && 'setData' in sourcePoint) {
    (sourcePoint as import('maplibre-gl').GeoJSONSource).setData(marqueur);
  } else {
    carte.addSource('adresse', { type: 'geojson', data: marqueur });
    carte.addLayer({
      id: 'adresse-point',
      type: 'circle',
      source: 'adresse',
      paint: {
        'circle-radius': 7,
        'circle-color': '#111111',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 3,
      },
    });
  }
}

function couleurDeCode(code: number): string {
  const classe = CLASSES_LCZ.find((c) => c.code === code);
  return classe === undefined ? '#808080' : COULEUR_NIVEAU[classe.niveau];
}

/**
 * Charge le style, et corrige le cas connu où la source déclare `scheme: tms` :
 * MapLibre attend l'ordre xyz.
 */
async function chargeStyle(): Promise<import('maplibre-gl').StyleSpecification> {
  for (const url of [STYLE_IGN, STYLE_REPLI]) {
    try {
      const reponse = await fetch(url);
      if (!reponse.ok) continue;
      const style = (await reponse.json()) as import('maplibre-gl').StyleSpecification;
      for (const source of Object.values(style.sources ?? {})) {
        if (
          typeof source === 'object' &&
          source !== null &&
          'scheme' in source &&
          source.scheme === 'tms'
        ) {
          (source as { scheme?: string }).scheme = 'xyz';
        }
      }
      return style;
    } catch {
      continue;
    }
  }
  throw new Error('Aucun fond de carte disponible');
}
