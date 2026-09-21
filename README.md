# LieuScope

Un site d'information gratuit, en français, qui dit en une phrase ce que les
bases publiques racontent sur un lieu. Première question traitée : **la chaleur
dans votre rue**, à partir des zones climatiques locales du Cerema.

Le site est entièrement statique, hébergé sur GitHub Pages. Il n'y a ni serveur,
ni base de données, ni compte, ni cookie, ni mesure d'audience. L'adresse saisie
part uniquement vers le service de géocodage de l'IGN, le temps de la recherche.

## Comment ça marche

1. `pipeline/` (Python) télécharge les données publiques, les simplifie et les
   découpe en petits fichiers par tuile, hors ligne.
2. `src/` (Astro, TypeScript) affiche le site. Le navigateur géocode l'adresse,
   télécharge un à neuf petits fichiers autour du point, teste « point dans
   polygone », et affiche le verdict puis la carte.

## Commandes

```
npm run dev        # site en local
npm run build      # construire dans dist/
npm run preview    # relire dist/
npm run check      # types
npm test           # tests du site
npm run poids      # contrôle du budget de poids

python -m pipeline.lcz --aire "Lyon"   # préparer les données d'une aire urbaine
pytest pipeline                        # tests du pipeline
```

Le pipeline tourne aussi dans GitHub Actions, de deux façons :

- onglet **Actions** → **Préparer les données** → **Run workflow** ;
- ou en poussant une branche dont le nom commence par `lancer/donnees-`. L'aire
  traitée est alors celle notée dans `data/aire-pilote.txt`.

Dans les deux cas, l'atelier ouvre une pull request avec les données produites
et son rapport de contrôle. Rien ne part en ligne sans cette pull request.

## Documents

- `CLAUDE.md` — les consignes du projet.
- `docs/JOURNAL.md` — la mémoire du projet, séance par séance.
- `docs/ROADMAP.md` — la feuille de route.
- `docs/METHODE.md` — la méthode, publiée telle quelle sur le site.
- `data/SOURCES.md` — les jeux de données, leurs licences et leurs limites.

## Licence

Code sous licence MIT. Les données restent sous la licence de leur producteur,
citée à côté de chaque résultat.
