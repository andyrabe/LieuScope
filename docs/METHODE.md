# Méthode

Cette page explique ce que LieuScope calcule, à partir de quoi, et ce que le
résultat ne dit pas. Elle est publiée telle quelle : ce que vous lisez ici est
exactement ce qui sert à produire les verdicts.

## D'où vient le résultat

1. Votre adresse est envoyée au service de géocodage de l'IGN (Géoplateforme),
   qui la transforme en un point (une longitude et une latitude). Elle n'est
   enregistrée nulle part.
2. Le site télécharge le petit fichier de données qui couvre ce point, et
   regarde dans quelle zone il tombe.
3. La classe de cette zone est traduite en une phrase, un niveau, et une source.

Tout le calcul se fait dans votre navigateur. Il n'y a ni serveur, ni compte,
ni traceur.

## La donnée utilisée : les zones climatiques locales

Les zones climatiques locales (*local climate zones*) sont une classification
scientifique des îlots urbains, proposée par Stewart et Oke en 2012. Elle décrit
la **forme** d'un îlot : hauteur et densité du bâti, part de végétation, de sol
nu ou d'eau, matériaux dominants.

Dix-sept classes existent : dix pour le bâti (numérotées de 1 à 10) et sept pour
les couvertures du sol (notées de A à G). Nous reprenons ces classes telles que
le producteur les publie, sans les modifier ni les regrouper dans la donnée.

Le jeu utilisé est celui du **Cerema**, publié sur data.gouv.fr (jeu
`6641c562e5acdb35c0e6051d`), sous Licence Ouverte. Le millésime exact et la date
de téléchargement sont affichés à côté de chaque résultat et détaillés dans
`data/SOURCES.md`.

## Le passage de la classe au niveau de sensibilité

La classe officielle décrit une forme urbaine ; elle ne donne pas de note. Pour
rester lisible, LieuScope range les dix-sept classes sur une échelle de quatre
niveaux de **sensibilité potentielle à la surchauffe**. Ce classement est un
choix de LieuScope, pas une donnée du producteur. Le voici en entier :

| Niveau | Classes concernées |
| --- | --- |
| Sensibilité faible | A (arbres denses), B (arbres épars), G (eau) |
| Sensibilité modérée | 6 (bâti ouvert de faible hauteur), 9 (bâti très dispersé), C (broussailles), D (végétation basse), F (sol nu, sable) |
| Sensibilité élevée | 4 et 5 (bâti ouvert de grande et moyenne hauteur), 7 (bâti léger), 8 (grand bâti de faible hauteur), E (roche ou revêtement imperméable) |
| Sensibilité très élevée | 1, 2 et 3 (bâti compact), 10 (industrie lourde) |

Le raisonnement, en une phrase par famille :

- **Bâti compact (1, 2, 3)** : les rues étroites piègent la chaleur émise le
  jour et la restituent la nuit ; l'air circule peu et l'eau s'évapore peu.
- **Industrie lourde (10)** : surfaces minérales, très peu de végétation, et
  chaleur produite sur place.
- **Bâti ouvert (4, 5), grand bâti bas (8), bâti léger (7), surfaces revêtues
  (E)** : le minéral domine, mais l'air circule mieux que dans le bâti compact.
- **Bâti pavillonnaire et dispersé (6, 9), végétation basse et sol nu (C, D,
  F)** : une part notable du sol reste perméable, le refroidissement nocturne
  fonctionne mieux.
- **Arbres et eau (A, B, G)** : ombrage et évaporation limitent nettement
  l'accumulation de chaleur.

**À revalider.** Ce classement a été établi à partir de la définition des
classes. Il doit être confronté au guide utilisateur et au guide technique
publiés par le Cerema avec le jeu de données ; toute correction issue de cette
lecture remplacera le tableau ci-dessus, et sera notée dans `docs/JOURNAL.md`.

## Ce que le résultat ne dit pas

- Ce n'est **pas une température mesurée**. Aucun thermomètre n'intervient.
- Ce n'est **pas un avis sur un logement**. Un appartement isolé, traversant ou
  ombragé peut rester confortable dans un îlot sensible ; l'inverse existe.
- La zone décrit **l'îlot autour de l'adresse**, à l'échelle de quelques
  centaines de mètres, pas le bâtiment ni la parcelle.
- Hors des aires couvertes par le jeu de données, LieuScope le dit et ne donne
  **aucun verdict par défaut**.

## Comment les données sont préparées

Le pipeline `pipeline/lcz/` télécharge le fichier de l'aire urbaine pilote
publié par le Cerema, puis :

1. **fusionne les zones voisines de même classe.** Le jeu est dérivé d'une image
   satellite : une même classe y est découpée en milliers de petites zones
   accolées. Les fusionner efface leurs frontières communes, qui ne portaient
   aucune information ;
2. **simplifie les contours** avec une tolérance de 40 mètres. La zone décrit un
   îlot de quelques centaines de mètres : ce niveau de détail suffit, et il évite
   de faire télécharger des contours en escalier hérités de la grille de
   l'image ;
3. **arrondit les coordonnées à cinq décimales**, soit environ un mètre ;
4. **découpe le résultat en petits fichiers par tuile, au zoom 14.** Une zone à
   cheval sur deux tuiles est présente dans chacune, mais seulement pour la part
   qui y tombe : la découper au bord évite de recopier une grande zone en entier
   dans chaque tuile, sans changer le résultat du test « point dans polygone ».

Ces choix visent un budget précis : chaque fichier téléchargé par le navigateur
doit peser moins de 300 Ko.

Chaque exécution écrit un rapport dans `pipeline/rapports/lcz.md` : nombre de
zones, valeurs manquantes, emprise, poids des fichiers, et verdict obtenu pour
chaque adresse témoin. Un écart sur un témoin bloque la mise en ligne.
