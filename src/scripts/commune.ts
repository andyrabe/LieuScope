import { chargeurTuile } from '../lib/donnees.js';

/**
 * Affiche la carte d'une commune : les mêmes îlots que sur la page d'accueil,
 * mais centrés sur la commune et sans repère, le centre géométrique n'étant
 * l'adresse de personne.
 */
const zone = document.getElementById('carte-zone');
const lon = Number(zone?.dataset['lon']);
const lat = Number(zone?.dataset['lat']);

if (zone !== null && Number.isFinite(lon) && Number.isFinite(lat)) {
  void (async () => {
    try {
      const { montreCarte } = await import('./carte.js');
      await montreCarte({ lon, lat }, chargeurTuile(import.meta.env.BASE_URL), {
        zoom: 12,
        marqueur: false,
      });
    } catch {
      // Sans carte, le reste de la page garde tout son sens.
      zone.hidden = true;
    }
  })();
}
