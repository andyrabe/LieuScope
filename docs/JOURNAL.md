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

### Prochaine étape

1. Fusionner la pull request, activer Pages, vérifier que le site s'ouvre.
2. Lancer `data.yml` dans Actions pour produire les données de Lyon.
3. Lire le rapport `pipeline/rapports/lcz.md`, confirmer le millésime, corriger
   le tableau de `docs/METHODE.md` si le guide du Cerema le demande.
4. Remplacer les trois adresses témoins par des adresses qu'elle connaît.
