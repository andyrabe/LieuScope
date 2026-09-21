import { describe, expect, it } from 'vitest';
import {
  ZOOM_LCZ,
  tileBounds,
  tileNeighbourhood,
  tileOf,
  tilePath,
} from '../src/lib/verdict/tiles.js';
import { pointInBbox } from '../src/lib/verdict/geometry.js';

const BELLECOUR = { lon: 4.83223, lat: 45.75778 };

describe('tuile d’un point', () => {
  it('place l’origine au centre de la grille au zoom 1', () => {
    expect(tileOf({ lon: 0, lat: 0 }, 1)).toEqual({ z: 1, x: 1, y: 1 });
  });

  it('n’a qu’une seule tuile au zoom 0', () => {
    expect(tileOf({ lon: 4.83, lat: 45.75 }, 0)).toEqual({ z: 0, x: 0, y: 0 });
  });

  it('rend une tuile dont l’emprise contient le point', () => {
    const tuile = tileOf(BELLECOUR, ZOOM_LCZ);
    expect(pointInBbox(BELLECOUR, tileBounds(tuile))).toBe(true);
  });

  it('respecte les bornes de la grille aux pôles', () => {
    const tuile = tileOf({ lon: 179.9, lat: 89 }, 5);
    expect(tuile.x).toBeLessThan(32);
    expect(tuile.y).toBeGreaterThanOrEqual(0);
    expect(tuile.y).toBeLessThan(32);
  });
});

describe('voisinage', () => {
  it('rend neuf tuiles, celle du point en premier', () => {
    const tuiles = tileNeighbourhood(BELLECOUR, ZOOM_LCZ);
    expect(tuiles).toHaveLength(9);
    expect(tuiles[0]).toEqual(tileOf(BELLECOUR, ZOOM_LCZ));
  });

  it('ne sort pas de la grille près du pôle nord', () => {
    const tuiles = tileNeighbourhood({ lon: 0, lat: 85 }, 2);
    expect(tuiles.every((t) => t.y >= 0 && t.y < 4)).toBe(true);
  });
});

describe('chemin de tuile', () => {
  it('suit la forme couche/z/x/y.json', () => {
    expect(tilePath('lcz', { z: 12, x: 2074, y: 1409 })).toBe('lcz/12/2074/1409.json');
  });
});
