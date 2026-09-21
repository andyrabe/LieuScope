# Rapport — zones climatiques locales

Aire traitée : **Lyon**. Exécution du 2026-09-21.

## Source

- Jeu : Cartographie des Zones Climatiques Locales (LCZ) des 93 territoires de plus de 50 000 habitants en France (`6641c562e5acdb35c0e6051d`)
- Producteur : Cerema
- Licence : lov2
- Millésime retenu : 2022 (le jeu a été mis à jour le 2026-07-21)
- Ressource : lcz-spot-2022-lyon.zip (zip)
- Page : https://www.data.gouv.fr/datasets/cartographie-des-zones-climatiques-locales-lcz-des-93-territoires-de-plus-de-50-000-habitants-en-france

## Objets

- Objets lus : 81048
- Objets retenus : 63561
- Classes illisibles écartées : 0 (0.0 %)
- Colonne des classes : `lcz`
- Colonnes présentes dans le fichier du producteur : `identifier`, `hre`, `are`, `bur`, `ror`, `bsr`, `war`, `ver`, `vhr`, `lcz`, `lcz_int`, `geometry`
- Emprise (ouest, sud, est, nord) : 4.4294, 45.3964, 5.3833, 46.1136

## Sorties

- Tuiles écrites : 1416 (zoom 14)
- Poids total : 23.5 Mo
- Tuile la plus lourde : `14/8412/5844.json`, 100 Ko (budget 300 Ko)
- Communes décrites : 0

## Piste pour les pages par commune

- CSV des communes couvertes : `Couverture LCZ par commune` — 34955 communes, dont 15321 couvertes.
  - Colonnes : `commune, insee_commune, population, surface_ha, couverture_lcz, detail_couverture_lcz, epci, siren_epci, departement, insee_departement, region, insee_region`
  - Exemple couvert : `Ambérieux-en-Dombes` (01005), couverture `100.00`
  - Détail de cette commune : `Lyon = 100.00 %`

## Adresses témoins

| Adresse | Attendu | Obtenu | Classe | Verdict |
| --- | --- | --- | --- | --- |
| Place Bellecour, Lyon 2e | tres_elevee | elevee | E | écart, attente non confirmée |
| Parc de la Tête d'Or, Lyon 6e | faible | faible | A | conforme |
| Quartier pavillonnaire, Sainte-Foy-lès-Lyon | moderee | faible | A | écart, attente non confirmée |

Tant qu'un témoin porte `"confirme": false`, l'écart est signalé mais ne bloque pas : l'attente vient de Claude, pas encore du terrain.
