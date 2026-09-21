/**
 * Géocodage : transformer un texte saisi en coordonnées.
 * On utilise le service de la Géoplateforme de l'IGN, sans clé.
 * Doc : https://geoservices.ign.fr/documentation/services/services-geoplateforme/geocodage
 * L'adresse saisie ne part que vers ce service et n'est enregistrée nulle part.
 */

const BASE = 'https://data.geopf.fr/geocodage';

export interface Suggestion {
  /** Libellé complet à afficher, ex. « 12 rue de la Paix, 69003 Lyon ». */
  libelle: string;
  lon: number;
  lat: number;
  /** Nom de la commune. */
  commune: string;
  /** Code INSEE de la commune, quand le service le fournit. */
  codeInsee: string | undefined;
}

interface ReponseGeocodage {
  type?: string;
  features?: ReadonlyArray<{
    geometry?: { type?: string; coordinates?: ReadonlyArray<number> };
    properties?: Record<string, unknown>;
  }>;
}

/** Cherche des adresses et des lieux correspondant au texte saisi. */
export async function cherche(
  texte: string,
  options: { limite?: number; signal?: AbortSignal } = {},
): Promise<Suggestion[]> {
  const requete = texte.trim();
  if (requete.length < 3) return [];
  const url = new URL(`${BASE}/search`);
  url.searchParams.set('q', requete);
  url.searchParams.set('index', 'address,poi');
  url.searchParams.set('limit', String(options.limite ?? 7));
  url.searchParams.set('returntruegeometry', 'false');

  const reponse = await fetch(url, { signal: options.signal });
  if (!reponse.ok) {
    throw new Error(`Géocodage indisponible (${reponse.status})`);
  }
  const donnees = (await reponse.json()) as ReponseGeocodage;
  return (donnees.features ?? []).flatMap(versSuggestion);
}

function versSuggestion(feature: {
  geometry?: { type?: string; coordinates?: ReadonlyArray<number> };
  properties?: Record<string, unknown>;
}): Suggestion[] {
  const coordonnees = feature.geometry?.coordinates;
  const lon = coordonnees?.[0];
  const lat = coordonnees?.[1];
  if (typeof lon !== 'number' || typeof lat !== 'number') return [];
  const props = feature.properties ?? {};
  const libelle = texte(props, ['label', 'toponym', 'name', 'fulltext']);
  if (libelle === undefined) return [];
  const commune = texte(props, ['city', 'commune', 'municipality']) ?? '';
  const codeInsee = texte(props, ['citycode', 'inseeCode', 'insee']);
  return [{ libelle, lon, lat, commune, codeInsee }];
}

function texte(
  props: Record<string, unknown>,
  cles: ReadonlyArray<string>,
): string | undefined {
  for (const cle of cles) {
    const valeur = props[cle];
    if (typeof valeur === 'string' && valeur.length > 0) return valeur;
    if (Array.isArray(valeur)) {
      const premier = valeur[0];
      if (typeof premier === 'string' && premier.length > 0) return premier;
    }
  }
  return undefined;
}
