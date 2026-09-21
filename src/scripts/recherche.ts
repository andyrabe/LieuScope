import { cherche, type Suggestion } from '../lib/geocode.js';
import { chargeMeta, chargeurTuile } from '../lib/donnees.js';
import { chercheLcz } from '../lib/verdict/lookup.js';
import { COULEUR_NIVEAU, verdictLcz } from '../lib/verdict/lcz.js';
import type { Point, Verdict } from '../lib/verdict/types.js';

const BASE = import.meta.env.BASE_URL;
const charge = chargeurTuile(BASE);

const champ = document.getElementById('adresse') as HTMLInputElement | null;
const liste = document.getElementById('suggestions') as HTMLUListElement | null;
const message = document.getElementById('message') as HTMLParagraphElement | null;
const bloc = document.getElementById('verdict') as HTMLElement | null;
const zoneCarte = document.getElementById('carte-zone');

if (champ !== null && liste !== null && message !== null && bloc !== null) {
  brancheChamp(champ, liste);
  void depuisLUrl(champ);
}

/* ---------------------------------------------------------------- saisie */

function brancheChamp(champ: HTMLInputElement, liste: HTMLUListElement): void {
  let suggestions: Suggestion[] = [];
  let actif = -1;
  let minuteur: ReturnType<typeof setTimeout> | undefined;
  let requete: AbortController | undefined;

  champ.addEventListener('input', () => {
    if (minuteur !== undefined) clearTimeout(minuteur);
    const texte = champ.value;
    minuteur = setTimeout(() => void propose(texte), 250);
  });

  champ.addEventListener('keydown', (evenement) => {
    if (suggestions.length === 0) return;
    if (evenement.key === 'ArrowDown') {
      evenement.preventDefault();
      surligne(Math.min(actif + 1, suggestions.length - 1));
    } else if (evenement.key === 'ArrowUp') {
      evenement.preventDefault();
      surligne(Math.max(actif - 1, 0));
    } else if (evenement.key === 'Enter') {
      const choisi = suggestions[actif === -1 ? 0 : actif];
      if (choisi !== undefined) {
        evenement.preventDefault();
        void choisis(choisi);
      }
    } else if (evenement.key === 'Escape') {
      vide();
    }
  });

  liste.addEventListener('click', (evenement) => {
    const cible = (evenement.target as HTMLElement).closest('li');
    if (cible === null) return;
    const choisi = suggestions[Number(cible.dataset['index'])];
    if (choisi !== undefined) void choisis(choisi);
  });

  async function propose(texte: string): Promise<void> {
    if (texte.trim().length < 3) {
      vide();
      return;
    }
    requete?.abort();
    requete = new AbortController();
    try {
      suggestions = await cherche(texte, { signal: requete.signal });
      dessineListe();
    } catch (erreur) {
      if (erreur instanceof Error && erreur.name === 'AbortError') return;
      dis("La recherche d'adresse est momentanément indisponible. Réessayez dans un instant.");
    }
  }

  function dessineListe(): void {
    liste.replaceChildren();
    suggestions.forEach((suggestion, index) => {
      const element = document.createElement('li');
      element.id = `suggestion-${index}`;
      element.dataset['index'] = String(index);
      element.setAttribute('role', 'option');
      element.setAttribute('aria-selected', 'false');
      // textContent, jamais innerHTML : rien d'externe n'est injecté en HTML.
      element.textContent = suggestion.libelle;
      liste.append(element);
    });
    actif = -1;
    champ.setAttribute('aria-expanded', suggestions.length > 0 ? 'true' : 'false');
  }

  function surligne(index: number): void {
    actif = index;
    [...liste.children].forEach((element, i) => {
      element.setAttribute('aria-selected', i === index ? 'true' : 'false');
    });
    champ.setAttribute('aria-activedescendant', `suggestion-${index}`);
  }

  function vide(): void {
    suggestions = [];
    actif = -1;
    liste.replaceChildren();
    champ.setAttribute('aria-expanded', 'false');
    champ.removeAttribute('aria-activedescendant');
  }

  async function choisis(suggestion: Suggestion): Promise<void> {
    champ.value = suggestion.libelle;
    vide();
    retiensDansLUrl(suggestion);
    await affiche({ lon: suggestion.lon, lat: suggestion.lat }, suggestion.libelle);
  }
}

/* --------------------------------------------------------------- verdict */

async function affiche(point: Point, libelle: string): Promise<void> {
  if (bloc === null) return;
  dis('Recherche en cours…');
  const [resultat, meta] = await Promise.all([
    chercheLcz(point, charge),
    chargeMeta(BASE),
  ]);

  if (meta === null) {
    dis("Les données de la ville pilote ne sont pas encore publiées sur ce site. Revenez bientôt.");
    return;
  }
  if (!resultat.trouve) {
    dis(
      resultat.raison === 'hors_couverture'
        ? `Cette adresse est en dehors de la zone couverte aujourd'hui (${meta.aire}). Nous ne donnons pas de verdict par défaut.`
        : "Aucune zone climatique locale ne couvre exactement ce point : il peut s'agir d'un plan d'eau ou d'une limite de zone. Essayez une adresse voisine.",
    );
    return;
  }

  const verdict = verdictLcz(resultat.code, meta);
  if (verdict === undefined) {
    dis('Cette zone porte un code que nous ne savons pas encore interpréter.');
    return;
  }

  if (message !== null) message.hidden = true;
  dessineVerdict(bloc, verdict, libelle);
  void afficheCarte(point);
}

function dessineVerdict(bloc: HTMLElement, verdict: Verdict, adresse: string): void {
  const pleines = '●'.repeat(verdict.rang);
  const vides = '○'.repeat(verdict.rangMax - verdict.rang);
  remplis('verdict-adresse', adresse);
  remplis('verdict-phrase', verdict.phrase);
  remplis('verdict-jauge', `Niveau ${verdict.rang} sur ${verdict.rangMax} — ${pleines}${vides}`);
  remplis('verdict-classe', `Zone climatique locale ${verdict.classeCode} : ${verdict.classe}.`);
  remplis('verdict-signifie', verdict.signifie);
  remplis('verdict-ne-dit-pas', verdict.neDitPas);
  remplis('verdict-source', verdict.source);
  bloc.style.setProperty('--niveau', COULEUR_NIVEAU[verdict.niveau]);
  bloc.hidden = false;
}

function remplis(id: string, texte: string): void {
  const element = document.getElementById(id);
  if (element !== null) element.textContent = texte;
}

function dis(texte: string): void {
  if (message !== null) {
    message.textContent = texte;
    message.hidden = false;
  }
  if (bloc !== null) bloc.hidden = true;
  if (zoneCarte !== null) zoneCarte.hidden = true;
}

/* ----------------------------------------------------------------- carte */

async function afficheCarte(point: Point): Promise<void> {
  if (zoneCarte === null) return;
  zoneCarte.hidden = false;
  try {
    const { montreCarte } = await import('./carte.js');
    await montreCarte(point, charge);
  } catch {
    // Sans carte, le verdict reste lisible : on masque simplement le bloc.
    zoneCarte.hidden = true;
  }
}

/* ------------------------------------------------------- lien partageable */

function retiensDansLUrl(suggestion: Suggestion): void {
  const url = new URL(window.location.href);
  url.searchParams.set('a', suggestion.libelle);
  url.searchParams.set('lon', suggestion.lon.toFixed(6));
  url.searchParams.set('lat', suggestion.lat.toFixed(6));
  window.history.replaceState(null, '', url);
}

async function depuisLUrl(champ: HTMLInputElement): Promise<void> {
  const params = new URLSearchParams(window.location.search);
  const lon = Number(params.get('lon'));
  const lat = Number(params.get('lat'));
  const libelle = params.get('a');
  if (libelle === null || !Number.isFinite(lon) || !Number.isFinite(lat)) return;
  if (lon < -180 || lon > 180 || lat < -90 || lat > 90) return;
  champ.value = libelle;
  await affiche({ lon, lat }, libelle);
}
