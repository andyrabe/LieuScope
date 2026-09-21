# Journal du projet

Le journal est la seule mémoire fiable du projet : la mémoire automatique de
Claude Code ne suit pas d'une machine à l'autre. La séance la plus récente est
en haut.

---

## 21 septembre 2026 — mise en place et couche chaleur

### Fait

- Squelette complet du site : Astro 7.3.3 en sortie statique, TypeScript 6
  strict, CSS simple à variables, aucun framework d'interface.
- Logique de verdict dans `src/lib/verdict/`, pure et couverte par des tests :
  tuile d'un point (`tiles.ts`), point dans polygone avec trous (`geometry.ts`),
  classes et niveaux (`lcz.ts`), recherche de la zone (`lookup.ts`).
- Champ d'adresse avec autocomplétion sur le géocodage de la Géoplateforme,
  navigation au clavier, résultat en texte avant la carte, lien partageable.
- Carte MapLibre 6 chargée seulement après le verdict, fond Plan IGN sans clé,
  repli Etalab, attribution visible, légende écrite (la couleur ne porte jamais
  seule l'information).
- Pages « Méthode » (publiée telle quelle depuis `docs/METHODE.md`), « Sources
  et mentions légales », « Communes couvertes », page 404.
- Pipeline `pipeline/lcz/` en Python : téléchargement du jeu Cerema, sélection
  de l'aire pilote, simplification, arrondi à 5 décimales, découpe en tuiles
  au zoom 12, métadonnées, rapport de contrôle et vérification des témoins.
- Trois ateliers GitHub Actions : `ci.yml` (types, tests, construction, poids),
  `deploy.yml` (publication sur Pages à chaque `main`), `data.yml` (exécution du
  pipeline à la demande).

### Décidé

- **Ville pilote : Lyon.** Aire urbaine couverte par le jeu, assez grande pour
  montrer tous les cas (centre compact, parcs, industrie, périurbain). Facile à
  changer : un seul paramètre, `--aire`, dans `data.yml`.
- **Dépôt privé** (constaté après coup : j'avais d'abord écrit « public » par
  erreur). Conséquence à surveiller : les minutes d'Actions sont décomptées
  (3 000 par mois), et chaque exécution du pipeline en consomme. Le passage en
  public reste recommandé ; c'est un réglage dans Settings du dépôt.
- **Licence MIT**, nom **LieuScope**, adresse provisoire
  `https://andyrabe.github.io/LieuScope/`.
- **Quatre niveaux de sensibilité** plutôt que cinq : au-delà, les libellés se
  ressemblent trop pour être utiles. Le tableau complet est dans
  `docs/METHODE.md`.
- **Zoom 12 pour les tuiles de données** : à Lyon une tuile fait environ 7 km de
  côté, ce qui tient largement sous les 300 Ko une fois les géométries
  simplifiées. À revoir si une tuile dépasse le budget.
- **Pas de PMTiles**, comme prévu par les consignes.

### Bloqué

- L'environnement de développement n'a pas accès à `data.gouv.fr` ni à
  `data.geopf.fr` : impossible de télécharger le jeu Cerema ou d'essayer le
  géocodage ici. Le pipeline a donc été écrit pour tourner **dans GitHub
  Actions** (`data.yml`, bouton « Run workflow »), exactement comme prévu par
  les consignes. Tant qu'il n'a pas tourné, `public/data/lcz/` est vide et le
  site affiche « les données ne sont pas encore publiées ».

### Mise en ligne, ce qui a bloqué

- Pages n'était pas activé : `deploy.yml` l'active désormais lui-même
  (`enablement: true`), sans réglage manuel.
- La première publication a échoué sans journal, en une seconde.
  Cause trouvée : l'environnement `github-pages` n'autorise les mises en ligne
  que depuis la **branche par défaut** du dépôt, et celle-ci est encore
  `claude/validation-automatique-etapes-870mpp`, pas `main`. `deploy.yml`
  accepte donc les deux pour l'instant ; à ramener à `main` seul dès que la
  branche par défaut aura été changée.
- Publication réussie le 21 septembre à 00:39 depuis la branche par défaut.
  Je n'ai pas pu ouvrir `andyrabe.github.io` moi-même : ce domaine est bloqué
  depuis mon environnement. À vérifier sur téléphone.
- L'API ne me laisse ni déclencher un atelier (« Run workflow »), ni changer la
  branche par défaut, ni changer la visibilité du dépôt : 403 à chaque fois.

### Ajouté dans la foulée

- `deploy.yml` active GitHub Pages lui-même (`enablement: true`) : plus besoin
  d'aller le régler dans les Settings du dépôt.
- `data.yml` se lance aussi en poussant une branche `lancer/donnees-…`, car
  l'API ne m'autorise pas à déclencher un atelier à la main. L'aire traitée est
  alors celle de `data/aire-pilote.txt`.

### Première exécution réelle du pipeline, et ce qu'elle a appris

Le pipeline a tourné dans Actions en 5 min 26 s et a bien trouvé le bon fichier
(`lcz-spot-2022-lyon.zip`, millésime 2022), la bonne colonne de classes (`lcz`)
et 81 048 zones. Mais les sorties étaient très au-dessus du budget :
**110 tuiles, la plus lourde à 6,9 Mo** (budget : 300 Ko) et **656 Mo au total**
(limite pour des données versionnées : 50 Mo). Le garde-fou de `data.yml` a
arrêté la suite, donc rien n'a été proposé à la fusion.

Cause : le jeu est dérivé d'une image satellite. Une même classe y est découpée
en milliers de petites zones accolées, aux contours en escalier. Trois
corrections, dans cet ordre :

1. **Fusion des zones voisines de même classe** avant tout le reste : leurs
   frontières communes disparaissent.
2. **Simplification portée de 8 à 40 mètres.** À l'échelle d'un îlot, ce détail
   ne dit rien de plus.
3. **Découpe des zones au bord de la tuile** au lieu de les recopier entières,
   et **zoom des tuiles porté de 12 à 14**. Sans la découpe, la fusion aurait eu
   l'effet inverse : une grande zone fusionnée aurait été recopiée entière dans
   chacune des dizaines de tuiles qu'elle touche.

Le zoom doit être identique côté site et côté pipeline ; un test le vérifie
désormais (`test_le_meme_zoom_des_deux_cotes`), comme il vérifiait déjà que les
dix-sept classes sont décrites pareil des deux côtés.

### Deuxième exécution : le budget de poids est tenu, trois défauts trouvés

La fusion et la découpe au bord des tuiles font passer le poids total de
**656 Mo à 30,3 Mo**, soit vingt fois moins, sans rien changer aux verdicts.
81 048 zones lues, 63 561 après fusion. Trois défauts restaient :

1. **`data.yml` imposait `--zoom 12 --simplification 8` en dur**, ce qui
   écrasait silencieusement les valeurs du pipeline (14 et 40). Les données ont
   donc été écrites au zoom 12 alors que le site cherche au zoom 14 : il
   n'aurait rien trouvé. L'atelier ne fixe plus ces valeurs ; elles vivent dans
   le pipeline, à un seul endroit.
2. **La tuile la plus lourde faisait 861 Ko**, au-dessus du budget de 300 Ko.
   C'est ce que le zoom 14 corrige.
3. **Le millésime affiché était `2026-07-21`**, la date de dernière
   modification de la fiche data.gouv.fr, pas celle de la donnée. Le nom du
   fichier la porte (`lcz-spot-2022-lyon.zip`) : on la lit là, avec la date de
   fiche en repli.

Autres constats de ce rapport :

- **Aucune colonne de rattachement communal** dans le jeu : `communes.json` est
  vide et aucune page de commune n'est construite. Il faudra croiser avec un
  découpage administratif à l'étape 2.
- **Les ateliers n'ont pas le droit d'ouvrir une pull request** sur ce dépôt
  (« GitHub Actions is not permitted to create or approve pull requests »). La
  branche de données est bien poussée ; la pull request s'ouvre à la main.
- **Deux témoins sur trois sont en écart**, et c'est instructif : Place
  Bellecour ressort en classe E (revêtement imperméable) et non en bâti
  compact — le point tombe sur l'esplanade elle-même, pas sur les immeubles.
  Ces attentes venaient de moi, pas du terrain : elles ne bloquent pas, et
  elles sont à revoir avec elle.

### Troisième exécution : bon du premier coup, et mise en ligne réussie

| | Obtenu | Budget |
| --- | --- | --- |
| Poids total | 23,5 Mo | 50 Mo |
| Tuile la plus lourde | 100 Ko | 300 Ko |
| Tuiles écrites | 1 416 (zoom 14) | — |
| Classes illisibles | 0 | — |
| Millésime affiché | 2022 | — |

Pull request #1 ouverte à la main (les ateliers n'ont pas le droit d'en créer
sur ce dépôt), fusionnée par elle le 21 septembre à 01:03.

**La mise en ligne depuis `main` a alors échoué**, alors que la construction
était verte : l'environnement `github-pages` refuse toute publication qui ne
vient pas de la branche par défaut, et celle-ci est encore la branche de
travail. Contournement appliqué : reporter le commit de fusion sur la branche
par défaut, en avance rapide. Publication réussie à 02:10.

Ce réglage n'est donc plus cosmétique : **tant que la branche par défaut n'est
pas `main`, chaque fusion demandera cette manœuvre.** Une fois le réglage fait,
retirer la branche de travail des déclencheurs de `deploy.yml`.

### Prochaine étape

1. **Elle** : vérifier sur téléphone qu'une adresse lyonnaise donne bien un
   verdict, et qu'une adresse hors aire le dit nettement.
2. **Elle** : donner trois adresses qu'elle connaît avec le verdict attendu,
   pour remplacer les témoins posés par Claude et passer `"confirme": true`.
3. **Elle** : passer la branche par défaut à `main`, et le dépôt en public.
4. Relire le guide utilisateur et le guide technique du Cerema, puis corriger
   le tableau des niveaux de `docs/METHODE.md` si nécessaire.
5. Vérifier Firefox, Safari et Chrome, puis poser l'étiquette `v0.1`.
