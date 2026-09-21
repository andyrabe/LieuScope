// Copie dans public/ les fichiers de MapLibre que la construction n'embarque pas.
//
// 1. La feuille de style : importée en module, elle serait liée dans le <head>
//    de toutes les pages et retarderait l'affichage du verdict.
// 2. Le « worker » : MapLibre fait tout son calcul de tuiles dans un fil
//    d'exécution séparé, qu'il charge par une adresse calculée à l'exécution.
//    L'outil de construction ne peut pas la deviner, donc il n'embarque pas le
//    fichier : la carte s'ouvre alors vide, sans rien dessiner ni signaler.
//    On le copie nous-mêmes et on indique son adresse à MapLibre (carte.ts).
//
// Les deux fichiers du worker sont renommés en .js : un fil d'exécution de
// module est refusé par le navigateur si le serveur annonce un type autre que
// JavaScript, et .js est le seul suffixe que tout hébergeur sert correctement.
// Le worker importe son voisin : on récrit donc aussi ce nom dans son code.
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const SOURCE = join('node_modules', 'maplibre-gl', 'dist');
const CIBLE = join('public', 'carte');
const ANCIEN_VOISIN = './maplibre-gl-shared.mjs';
const NOUVEAU_VOISIN = './maplibre-gl-shared.js';

mkdirSync(CIBLE, { recursive: true });

copyFileSync(join(SOURCE, 'maplibre-gl.css'), join(CIBLE, 'maplibre-gl.css'));
copyFileSync(join(SOURCE, 'maplibre-gl-shared.mjs'), join(CIBLE, 'maplibre-gl-shared.js'));

const worker = readFileSync(join(SOURCE, 'maplibre-gl-worker.mjs'), 'utf8');
if (!worker.includes(ANCIEN_VOISIN)) {
  console.error(
    `Le worker de MapLibre n'importe plus « ${ANCIEN_VOISIN} ». Vérifiez ce qu'il` +
      ' importe désormais et mettez ce script à jour, sinon la carte restera vide.',
  );
  process.exit(1);
}
writeFileSync(
  join(CIBLE, 'maplibre-gl-worker.js'),
  worker.replaceAll(ANCIEN_VOISIN, NOUVEAU_VOISIN),
);

console.log(`Fichiers de la carte copiés dans ${CIBLE}.`);
