import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { CLASSES_LCZ, ECHELLE, verdictLcz } from '../src/lib/verdict/lcz.js';
import { chercheLcz, codeAuPoint } from '../src/lib/verdict/lookup.js';
import { ZOOM_LCZ, tileOf } from '../src/lib/verdict/tiles.js';
import type { FeatureCollection, LczProperties, Tile } from '../src/lib/verdict/types.js';

const SOURCE = { producteur: 'Cerema', millesime: '2022' };

const tuile = JSON.parse(
  readFileSync(fileURLToPath(new URL('./fixtures/tuile-exemple.json', import.meta.url)), 'utf8'),
) as FeatureCollection<LczProperties>;

describe('classes et niveaux', () => {
  it('couvre les dix-sept classes officielles', () => {
    expect(CLASSES_LCZ).toHaveLength(17);
    expect(new Set(CLASSES_LCZ.map((c) => c.code)).size).toBe(17);
    expect(new Set(CLASSES_LCZ.map((c) => c.officiel)).size).toBe(17);
  });

  it('range chaque classe sur l’échelle', () => {
    for (const classe of CLASSES_LCZ) {
      expect(ECHELLE).toContain(classe.niveau);
    }
  });

  it('donne un verdict complet pour le bâti compact', () => {
    const verdict = verdictLcz(2, SOURCE);
    expect(verdict).toBeDefined();
    expect(verdict?.niveau).toBe('tres_elevee');
    expect(verdict?.rang).toBe(4);
    expect(verdict?.rangMax).toBe(4);
    expect(verdict?.classeCode).toBe('2');
    expect(verdict?.source).toBe('Source : Cerema, 2022');
    expect(verdict?.signifie.length).toBeGreaterThan(20);
    expect(verdict?.neDitPas.length).toBeGreaterThan(20);
  });

  it('classe les arbres denses en sensibilité faible', () => {
    expect(verdictLcz(11, SOURCE)?.niveau).toBe('faible');
    expect(verdictLcz(11, SOURCE)?.rang).toBe(1);
  });

  it('ne dit jamais « danger », « toxique » ni « à fuir »', () => {
    const interdits = /danger|toxique|à fuir/i;
    for (const classe of CLASSES_LCZ) {
      const verdict = verdictLcz(classe.code, SOURCE);
      expect(verdict).toBeDefined();
      expect(interdits.test(`${verdict?.phrase} ${verdict?.signifie} ${verdict?.neDitPas}`)).toBe(false);
    }
  });

  it('rend undefined pour un code inconnu', () => {
    expect(verdictLcz(99, SOURCE)).toBeUndefined();
  });
});

describe('zone au point', () => {
  it('trouve la zone de bâti compact', () => {
    expect(codeAuPoint({ lon: 4.83, lat: 45.765 }, tuile)).toBe(2);
  });

  it('ignore le trou du polygone', () => {
    expect(codeAuPoint({ lon: 4.815, lat: 45.765 }, tuile)).toBeUndefined();
  });

  it('trouve la zone boisée du multipolygone', () => {
    expect(codeAuPoint({ lon: 4.87, lat: 45.765 }, tuile)).toBe(11);
  });
});

describe('recherche complète', () => {
  const point = { lon: 4.83, lat: 45.765 };
  const tuileDuPoint = tileOf(point, ZOOM_LCZ);

  const chargeur = (dispo: ReadonlyArray<Tile>) => async (t: Tile) =>
    dispo.some((d) => d.x === t.x && d.y === t.y && d.z === t.z) ? tuile : null;

  it('trouve le code quand la tuile existe', async () => {
    const resultat = await chercheLcz(point, chargeur([tuileDuPoint]));
    expect(resultat).toEqual({ trouve: true, code: 2 });
  });

  it('dit « hors couverture » quand aucune tuile n’existe', async () => {
    const resultat = await chercheLcz(point, chargeur([]));
    expect(resultat).toEqual({ trouve: false, raison: 'hors_couverture' });
  });

  it('dit « hors zone » quand la tuile existe mais ne couvre pas le point', async () => {
    const dehors = { lon: 4.9999, lat: 45.99 };
    const resultat = await chercheLcz(dehors, async () => tuile);
    expect(resultat).toEqual({ trouve: false, raison: 'hors_zone' });
  });

  it('ne réclame pas les voisines quand la tuile du point répond', async () => {
    const demandees: Tile[] = [];
    await chercheLcz(point, async (t) => {
      demandees.push(t);
      return tuile;
    });
    expect(demandees).toHaveLength(1);
  });
});
