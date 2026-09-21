// Copie la feuille de style de MapLibre dans public/, pour la charger seulement
// au moment où la carte s'affiche. Importée en module, elle serait liée dans le
// <head> de toutes les pages et bloquerait l'affichage de l'accueil.
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const source = join('node_modules', 'maplibre-gl', 'dist', 'maplibre-gl.css');
const cible = join('public', 'carte', 'maplibre-gl.css');

mkdirSync(dirname(cible), { recursive: true });
copyFileSync(source, cible);
console.log(`Feuille de style de la carte copiée dans ${cible}`);
