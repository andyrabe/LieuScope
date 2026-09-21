# Sources de données

Une ligne par jeu utilisé. Rien n'est mis en ligne sans licence claire.

## Zones climatiques locales (étape 1)

| Champ | Valeur |
| --- | --- |
| Nom | Zones climatiques locales (*local climate zones*) des aires urbaines françaises |
| Producteur | Cerema |
| Page du jeu | https://www.data.gouv.fr/fr/datasets/6641c562e5acdb35c0e6051d/ |
| Identifiant | `6641c562e5acdb35c0e6051d` |
| Licence | Licence Ouverte (Etalab) |
| Millésime | **2022** (fichier `lcz-spot-2022-lyon.zip`) |
| Date de téléchargement | 21 septembre 2026 |
| Fréquence de mise à jour | ponctuelle ; à revérifier à chaque campagne |
| Champs utilisés | la classe de zone (code 1 à 10 et A à G) et la géométrie |
| Limites connues | décrit la forme d'un îlot, pas une température mesurée ; ne couvre que les aires urbaines du jeu ; l'échelle est l'îlot, pas le bâtiment ; **ne porte aucun rattachement communal**, d'où l'absence de pages par commune à l'étape 1 |

Mention affichée à côté de la donnée : « Source : Cerema, 2022 ».

Les valeurs marquées « à confirmer » sont remplies par le pipeline dans
`public/data/lcz/meta.json` et reprises telles quelles par le site ; elles
doivent être recopiées ici à la première exécution réussie.

## Géocodage (service, pas un jeu de données)

| Champ | Valeur |
| --- | --- |
| Nom | Service de géocodage de la Géoplateforme |
| Producteur | IGN |
| Documentation | https://geoservices.ign.fr/documentation/services/services-geoplateforme/geocodage |
| Clé d'API | aucune |
| Limite | environ 50 requêtes par seconde et par adresse IP |
| Usage | transformer le texte saisi en coordonnées, côté navigateur uniquement |

`api-adresse.data.gouv.fr` n'est pas utilisée : elle est décommissionnée depuis
fin janvier 2026.

## Fond de carte

| Champ | Valeur |
| --- | --- |
| Nom | Plan IGN, tuiles vectorielles |
| Producteur | IGN — Géoplateforme |
| Style | https://data.geopf.fr/annexes/ressources/vectorTiles/styles/PLAN.IGN/standard.json |
| Clé d'API | aucune |
| Repli | fond OpenMapTiles d'Etalab |

## Jeux écartés pour l'instant

- **DVF (valeurs foncières)** : à ne pas utiliser sans en reparler, ses
  conditions interdisent l'indexation par les moteurs de recherche.
- **Alim'confiance** : prévu à l'étape 3, avec retrait de tout résultat de plus
  d'un an.
