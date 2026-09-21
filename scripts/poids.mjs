// Contrôle de poids : la CI échoue si le site construit dépasse le budget.
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const DIST = 'dist';
const BUDGET_TOTAL_MO = 700;
const BUDGET_TUILE_KO = 300;
const BUDGET_ACCUEIL_KO = 150; // hors carte : HTML + CSS + scripts de la page

if (!existsSync(DIST)) {
  console.error('dist/ est absent : lancez d’abord « npm run build ».');
  process.exit(1);
}

let total = 0;
const tuilesLourdes = [];

function parcours(dossier) {
  for (const entree of readdirSync(dossier, { withFileTypes: true })) {
    const chemin = join(dossier, entree.name);
    if (entree.isDirectory()) {
      parcours(chemin);
      continue;
    }
    const taille = statSync(chemin).size;
    total += taille;
    if (chemin.includes(join('data', 'lcz')) && chemin.endsWith('.json')) {
      if (taille > BUDGET_TUILE_KO * 1024) {
        tuilesLourdes.push([chemin, taille]);
      }
    }
  }
}

parcours(DIST);

const accueil = poidsAccueil();
const totalMo = total / 1024 / 1024;

console.log(`Poids total de dist/ : ${totalMo.toFixed(1)} Mo (budget ${BUDGET_TOTAL_MO} Mo)`);
console.log(`Page d’accueil hors carte : ${(accueil / 1024).toFixed(1)} Ko (budget ${BUDGET_ACCUEIL_KO} Ko)`);

let echec = false;

if (totalMo > BUDGET_TOTAL_MO) {
  console.error(`Budget dépassé : dist/ pèse ${totalMo.toFixed(1)} Mo.`);
  echec = true;
}
if (tuilesLourdes.length > 0) {
  console.error(`${tuilesLourdes.length} tuile(s) au-dessus de ${BUDGET_TUILE_KO} Ko :`);
  for (const [chemin, taille] of tuilesLourdes.slice(0, 5)) {
    console.error(`  ${chemin} — ${(taille / 1024).toFixed(0)} Ko`);
  }
  console.error('Simplifiez davantage les géométries ou montez d’un zoom.');
  echec = true;
}
if (accueil > BUDGET_ACCUEIL_KO * 1024) {
  console.error(`La page d’accueil dépasse ${BUDGET_ACCUEIL_KO} Ko hors carte.`);
  echec = true;
}

process.exit(echec ? 1 : 0);

/** HTML de l’accueil, plus les fichiers CSS et JS qu’il charge (hors carte). */
function poidsAccueil() {
  const html = join(DIST, 'index.html');
  if (!existsSync(html)) return 0;
  let poids = statSync(html).size;
  const dossierAstro = join(DIST, '_astro');
  if (!existsSync(dossierAstro)) return poids;
  const contenu = readFileSync(html, 'utf8');
  for (const fichier of readdirSync(dossierAstro, { withFileTypes: true })) {
    if (!fichier.isFile()) continue;
    if (!contenu.includes(fichier.name)) continue;
    poids += statSync(join(dossierAstro, fichier.name)).size;
  }
  return poids;
}
