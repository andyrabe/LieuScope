import { describe, expect, it } from 'vitest';
import {
  bbox,
  distanceM,
  pointInBbox,
  pointInGeometry,
  pointInPolygon,
  pointInRing,
} from '../src/lib/verdict/geometry.js';
import type { MultiPolygonGeometry, Ring } from '../src/lib/verdict/types.js';

const CARRE: Ring = [
  [0, 0],
  [10, 0],
  [10, 10],
  [0, 10],
  [0, 0],
];

describe('point dans un anneau', () => {
  it('trouve un point au centre', () => {
    expect(pointInRing({ lon: 5, lat: 5 }, CARRE)).toBe(true);
  });

  it('rejette un point à l’extérieur', () => {
    expect(pointInRing({ lon: 15, lat: 5 }, CARRE)).toBe(false);
  });

  it('accepte un point posé sur le bord', () => {
    expect(pointInRing({ lon: 0, lat: 5 }, CARRE)).toBe(true);
    expect(pointInRing({ lon: 10, lat: 10 }, CARRE)).toBe(true);
  });

  it('rejette un anneau dégénéré', () => {
    expect(pointInRing({ lon: 1, lat: 1 }, [[0, 0], [1, 1]])).toBe(false);
  });
});

describe('point dans un polygone à trou', () => {
  const avecTrou = [
    CARRE,
    [
      [4, 4],
      [6, 4],
      [6, 6],
      [4, 6],
      [4, 4],
    ],
  ] as const;

  it('exclut le trou', () => {
    expect(pointInPolygon({ lon: 5, lat: 5 }, avecTrou)).toBe(false);
  });

  it('garde le reste du polygone', () => {
    expect(pointInPolygon({ lon: 2, lat: 2 }, avecTrou)).toBe(true);
  });
});

describe('multipolygone', () => {
  const secondCarre: Ring = [
    [20, 20],
    [30, 20],
    [30, 30],
    [20, 30],
    [20, 20],
  ];
  const multi: MultiPolygonGeometry = {
    type: 'MultiPolygon',
    coordinates: [[CARRE], [secondCarre]],
  };

  it('trouve le point dans la seconde partie', () => {
    expect(pointInGeometry({ lon: 25, lat: 25 }, multi)).toBe(true);
  });

  it('rejette un point entre les deux parties', () => {
    expect(pointInGeometry({ lon: 15, lat: 15 }, multi)).toBe(false);
  });
});

describe('emprise', () => {
  it('encadre le polygone', () => {
    expect(bbox({ type: 'Polygon', coordinates: [CARRE] })).toEqual([0, 0, 10, 10]);
  });

  it('sert de test rapide', () => {
    expect(pointInBbox({ lon: 5, lat: 5 }, [0, 0, 10, 10])).toBe(true);
    expect(pointInBbox({ lon: 11, lat: 5 }, [0, 0, 10, 10])).toBe(false);
  });
});

describe('distance', () => {
  it('donne environ 392 km entre Paris et Lyon', () => {
    const paris = { lon: 2.3522, lat: 48.8566 };
    const lyon = { lon: 4.8357, lat: 45.764 };
    expect(distanceM(paris, lyon) / 1000).toBeCloseTo(391.5, 1);
  });

  it('est nulle pour un point sur lui-même', () => {
    expect(distanceM({ lon: 4.8, lat: 45.7 }, { lon: 4.8, lat: 45.7 })).toBe(0);
  });
});
