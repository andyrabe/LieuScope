# Rapport — zones climatiques locales

Aire traitée : **Lyon**. Exécution du 2026-09-21.

## Source

- Jeu : Cartographie des Zones Climatiques Locales (LCZ) des 93 territoires de plus de 50 000 habitants en France (`6641c562e5acdb35c0e6051d`)
- Producteur : Cerema
- Licence : lov2
- Millésime retenu : 2026-07-21
- Ressource : lcz-spot-2022-lyon.zip (zip)
- Page : https://www.data.gouv.fr/datasets/cartographie-des-zones-climatiques-locales-lcz-des-93-territoires-de-plus-de-50-000-habitants-en-france

## Objets

- Objets lus : 81048
- Objets retenus : 63561
- Classes illisibles écartées : 0 (0.0 %)
- Colonne des classes : `lcz`
- Emprise (ouest, sud, est, nord) : 4.4294, 45.3964, 5.3835, 46.1136

## Sorties

- Tuiles écrites : 110 (zoom 12)
- Poids total : 30.3 Mo
- Tuile la plus lourde : `12/2102/1460.json`, 861 Ko (budget 300 Ko)
- Communes décrites : 0

## Adresses témoins

| Adresse | Attendu | Obtenu | Classe | Verdict |
| --- | --- | --- | --- | --- |
| Place Bellecour, Lyon 2e | tres_elevee | elevee | E | écart, attente non confirmée |
| Parc de la Tête d'Or, Lyon 6e | faible | faible | A | conforme |
| Quartier pavillonnaire, Sainte-Foy-lès-Lyon | moderee | faible | A | écart, attente non confirmée |

Tant qu'un témoin porte `"confirme": false`, l'écart est signalé mais ne bloque pas : l'attente vient de Claude, pas encore du terrain.

## Attention

La tuile `12/2102/1460.json` dépasse le budget de 300 Ko. Augmentez `--simplification`, ou montez d'un zoom.
