<!-- POUR VOUS : 1. Ce fichier doit rester à la racine du dépôt, sous le nom exact CLAUDE.md.
2. Dans une session Claude Code, tapez /context : CLAUDE.md doit apparaître sous « Memory files ».
3. Quand Claude Code refait deux fois la même erreur, dites-lui : « ajoute une règle dans CLAUDE.md ».
4. Gardez ce fichier sous 200 lignes : au-delà, il est moins bien suivi. -->

# LieuScope : consignes du projet

## Le projet en bref

- Site grand public, en français, pensé pour le téléphone. On saisit une adresse ou le nom d'un lieu ; en cinq secondes on obtient un verdict clair, la carte qui le justifie, et les sources.
- Un seul moteur, trois questions : (1) la chaleur dans ma rue, c'est l'étape en cours ; (2) l'école, la crèche ou l'EHPAD de mes proches et ce qui les entoure ; (3) le bruit à mon adresse.
- La valeur vient du croisement de bases publiques à l'échelle du lieu (un point dans une zone, une distance à une source). Afficher une base sur une carte ne vaut rien : des dizaines de sites le font déjà.
- But : l'audience la plus large possible. La simplicité passe avant l'exhaustivité.

## La personne avec qui tu travailles

- Elle ne sait pas coder et ne lira pas le code. Tu es le responsable technique : tu tranches les détails techniques dans le cadre ci-dessous, et tu expliques en français simple.
- Réponds toujours en français. Explique chaque terme technique en une phrase la première fois.
- Elle vérifie le résultat sur son téléphone, sur le site en ligne. Ne lui demande jamais de lancer une commande, de lire un journal d'erreurs ou de modifier un fichier. Seule exception : un réglage dans l'interface de GitHub ou du vendeur de nom de domaine ; guide-la alors clic par clic.
- Une seule question à la fois, et seulement si la réponse change ce que tu construis. Sinon, prends l'option la plus simple et dis-le.

## Contraintes non négociables

- Outils disponibles : GitHub Pro (dépôt, Actions, Pages, Releases), Claude Pro (toi), et un nom de domaine qui sera acheté plus tard. Rien d'autre.
- Aucun autre service, même gratuit : ni Vercel, Netlify, Cloudflare, Supabase, Firebase, Mapbox ou Google Maps, ni clé d'API, ni compte à créer. Si un service te paraît indispensable, arrête-toi et explique pourquoi ; la décision lui revient.
- Aucune dépense. Sont autorisés les services publics gratuits et sans clé : Géoplateforme de l'IGN, data.gouv.fr et ses API.
- Pas de serveur, pas de base de données, pas de comptes, pas d'envoi d'e-mails. Tout ce qui en demanderait est reporté à l'étape 6.

## Architecture imposée

- Site 100 % statique sur GitHub Pages, déployé par GitHub Actions à chaque mise à jour de `main`.
- Les calculs lourds se font hors ligne dans `pipeline/` (Python). Le navigateur se limite à : géocoder l'adresse, télécharger 1 à 9 petits fichiers autour du point, tester « point dans polygone » ou une distance, afficher.
- Données de verdict découpées en petits fichiers par tuile, à zoom fixe par couche (ex. `data/lcz/12/2074/1409.json`), servis en simples requêtes GET. Un polygone à cheval est copié dans chaque tuile qu'il touche. Choisis le zoom pour que chaque fichier pèse moins de 300 Ko.
- GeoJSON minifié, 5 décimales, attributs inutiles supprimés, sortie en WGS84. Si le poids dépasse le budget : simplifier les géométries, puis passer à un format binaire.
- Pas de PMTiles sur le chemin critique : les requêtes partielles servies par GitHub Pages posent un problème connu avec Firefox. PMTiles seulement pour un affichage secondaire, après test sur Firefox, Safari et Chrome.
- Étape 1 : les fichiers de la ville pilote (moins de 50 Mo) sont versionnés dans `public/data/`. Dès l'extension nationale : `data.yml` publie les données en pièce jointe d'une Release GitHub, et `deploy.yml` les télécharge avant de construire le site.
- Le pipeline tourne à l'identique en local et dans GitHub Actions (`workflow_dispatch`). Si ton environnement n'a pas accès à une source, lance-le dans Actions.

## Limites de GitHub à surveiller

- Site publié : 1 Go maximum. Déploiement : 10 minutes maximum. Bande passante : environ 100 Go par mois (limite souple).
- Actions : 3 000 minutes par mois si le dépôt est privé ; pas de décompte sur un dépôt public. Git refuse tout fichier de plus de 100 Mo.
- Budget de poids : la CI échoue si `dist/` dépasse 700 Mo. Une page par commune, oui ; une page par établissement, non, tant que le budget ne le permet pas.
- Pages n'est pas fait pour vendre ni pour héberger un service payant. Un site d'information gratuit convient ; toute idée de publicité ou de vente se rediscute avec elle.
- Si une limite approche : préviens, propose des options, ne migre rien sans son accord.

## Pile technique

- Astro en sortie statique, TypeScript strict, CSS simple à variables. Pas de framework d'interface sans nécessité démontrée.
- Carte : MapLibre GL JS, chargé en différé après le verdict.
- Fond de carte : tuiles vectorielles Plan IGN de la Géoplateforme, sans clé (style `https://data.geopf.fr/annexes/ressources/vectorTiles/styles/PLAN.IGN/standard.json` ; si la source déclare `scheme: tms`, passe-la en `xyz`). Repli : le fond OpenMapTiles d'Etalab. Attribution toujours visible.
- Adresse : API de géocodage de la Géoplateforme (50 requêtes par seconde et par IP). Doc : https://geoservices.ign.fr/documentation/services/services-geoplateforme/geocodage. N'utilise jamais `api-adresse.data.gouv.fr`, décommissionnée fin janvier 2026.
- Pipeline : Python 3.12, DuckDB avec l'extension spatiale, GeoPandas, dépendances figées. Tests : Vitest côté site, pytest côté pipeline.
- Prends les versions stables actuelles et fige-les. Pour Astro, MapLibre et GitHub Actions, vérifie la documentation officielle plutôt que ta mémoire.
- Avant d'ajouter une dépendance : utile, maintenue, licence libre, légère. Trente lignes de code valent mieux qu'une bibliothèque.

## Organisation du dépôt

- `src/` le site ; `src/lib/verdict/` la logique de verdict, pure et testée ; `public/data/` les données servies.
- `pipeline/<couche>/` un dossier par source ; `pipeline/rapports/` les rapports de contrôle.
- `data/brut/` les téléchargements (ignoré par git) ; `data/SOURCES.md` ; `data/temoins.json`.
- `docs/JOURNAL.md`, `docs/ROADMAP.md`, `docs/METHODE.md` ; `.github/workflows/deploy.yml` et `data.yml`.

## Commandes

- `npm run dev`, `npm run build`, `npm run preview`
- `npm run check` (types et lint), `npm test`, `npm run poids` (taille de `dist/`)
- `python -m pipeline.lcz --aire "<nom>"`, `pytest pipeline`

## Méthode de travail, à chaque session

1. Commence par lire `docs/JOURNAL.md` et `docs/ROADMAP.md`. Ne relis pas tout le dépôt.
2. Avant de coder, annonce en 3 à 5 lignes ce que tu vas faire et comment elle pourra le vérifier. Pour un changement important, passe par le mode plan.
3. Un seul objectif par session, petit, qui finit en ligne.
4. Avant de dire « terminé » : `npm run check && npm test && npm run build` passent, tu as déroulé toi-même le parcours avec une adresse témoin, et le déploiement est vert si tu peux le consulter.
5. En fin de session, mets à jour JOURNAL (fait, décidé, prochaine étape) et ROADMAP. Puis résume en français simple : ce qui a changé, comment le vérifier au téléphone (adresse du site et geste à faire), ce qui vient ensuite.
6. Après deux échecs sur la même erreur : arrête, explique simplement, propose deux options.

Ta mémoire automatique ne suit pas d'une machine ou d'un environnement à l'autre : `docs/JOURNAL.md` est la seule mémoire fiable du projet.

## Git et déploiement

- Petits commits fréquents, message en français à l'impératif (« Ajoute le champ d'adresse »). Code et identifiants en anglais, commentaires en français.
- `main` est ce qui est en ligne. En local : commit puis push sur `main` après les vérifications. Dans Claude Code sur le web : une branche et une pull request ; dis-lui quelle PR fusionner et ce que cela met en ligne.
- Jamais de `push --force`, jamais de réécriture d'historique, jamais de secret dans le dépôt. Pour annuler : `git revert`.
- Pose une étiquette de version à chaque étape de la feuille de route (`v0.1`, `v0.2`…).
- Sans nom de domaine : règle `site` et `base` d'Astro pour `https://<compte>.github.io/<depot>/`. Quand le domaine arrive : `public/CNAME`, `base: '/'`, HTTPS forcé, et guide-la pour les réglages DNS en suivant la documentation GitHub Pages.

## Données : règles

- Avant d'utiliser un jeu : vérifie producteur, licence, millésime, fréquence de mise à jour, et lis sa documentation. Consigne-le dans `data/SOURCES.md` (nom, producteur, URL, licence, date de téléchargement, champs utilisés, limites connues). Pas de jeu sans licence claire. Pas d'aspiration de site quand un jeu ouvert existe.
- Si le serveur MCP de data.gouv.fr est branché (`https://mcp.data.gouv.fr/mcp`), sers-t'en pour chercher et inspecter les jeux.
- Chaque pipeline est relançable sans effet de bord et écrit un rapport `pipeline/rapports/<couche>.md` : nombre d'objets, part de valeurs manquantes, emprise, poids des sorties, et verdict obtenu pour chaque adresse de `data/temoins.json` (des adresses qu'elle connaît). Un écart sur un témoin bloque la mise en ligne.
- Étape 1 : zones climatiques locales du Cerema, jeu `6641c562e5acdb35c0e6051d` sur data.gouv.fr. Un fichier par aire urbaine, plus un CSV des communes couvertes. Lis le guide utilisateur et le guide technique avant de définir les verdicts.
- Licence Ouverte : affiche « Source : producteur, millésime » à côté de chaque donnée. Alim'confiance : retire tout résultat de plus d'un an. DVF : ne l'utilise pas sans en reparler, ses conditions interdisent l'indexation par les moteurs de recherche.
- Aucune donnée personnelle. Pas de cookie, pas de traceur, pas d'outil de mesure d'audience sans son accord. L'adresse saisie ne part que vers le géocodage de l'IGN et n'est enregistrée nulle part.

## Verdicts et textes

- Un verdict = une phrase simple, un niveau parmi 3 à 5, « ce que cela veut dire », « ce que cela ne dit pas », la source et sa date.
- Reprends les classes officielles du producteur. Tout seuil ou score maison est justifié dans `docs/METHODE.md`, publiée telle quelle sur la page « Méthode » du site.
- Vocabulaire : « sensibilité », « exposition potentielle ». Jamais « danger », « toxique », « à fuir ». Une zone climatique locale indique une sensibilité potentielle d'un îlot à la surchauffe : ni une température mesurée, ni un avis sur un logement.
- Adresse hors des aires couvertes : dis-le nettement, sans verdict par défaut.
- Aucun conseil commercial, aucun lien sponsorisé. Vouvoiement, phrases courtes, français courant.

## Interface

- Mobile d'abord (360 px), utilisable d'une main. À l'accueil : un champ d'adresse avec autocomplétion, et rien d'autre avant lui.
- Le verdict s'affiche en texte avant la carte et reste compréhensible sans elle. Une couleur ne porte jamais seule une information.
- Accessibilité : contrastes AA, navigation au clavier, libellés explicites, mouvement réduit respecté.
- Performance : page d'accueil sous 150 Ko hors carte, aucune ressource externe bloquante.
- Chaque verdict a une adresse web partageable et des balises Open Graph.
- Référencement : une page statique par commune couverte, avec un texte propre à la commune, `sitemap.xml`, et aucune page vide.
- N'injecte jamais une donnée externe dans la page sans l'échapper.

## Tests et qualité

- La logique de verdict (tuile d'un point, point dans polygone, distance) est couverte par des tests unitaires, avec de petits fichiers d'exemple dans `tests/fixtures/`.
- La CI enchaîne `check`, `test`, `build` et le contrôle de poids. Rien ne se déploie si l'un échoue.

## Économie de contexte

- L'abonnement Claude Pro a des limites d'usage : chaque lecture inutile en consomme. Jamais de `cat` sur un fichier de données. Utilise `head -c 2000`, `wc -l`, `ogrinfo -so`, ou DuckDB avec `DESCRIBE` et `LIMIT 5`.
- Développe sur la ville pilote, jamais sur la France entière en interactif.
- Redirige les sorties longues (npm, pip, journaux) vers un fichier et n'en lis que la fin.
- Si la session s'allonge ou change de sujet : mets le JOURNAL à jour et propose d'en ouvrir une nouvelle.

## Feuille de route

- **Étape 0, mise en place.** Ville pilote, trois adresses témoins, dépôt public ou privé, nom du projet. Squelette Astro, `deploy.yml`, page d'accueil provisoire, JOURNAL, ROADMAP, SOURCES, `.gitignore`, LICENSE (MIT, à confirmer). Activer Pages (Settings, Pages, Source : GitHub Actions). Terminé quand le site s'ouvre sur son téléphone.
- **Étape 1, la chaleur sur la ville pilote.** Pipeline des zones climatiques de l'aire pilote, champ d'adresse, verdict, carte locale avec légende, pages « Méthode » et « Sources et mentions légales ». Terminé quand les trois témoins donnent le verdict attendu sur téléphone, que le hors zone est géré, que Firefox, Safari et Chrome fonctionnent, et que poids et performance tiennent le budget.
- **Étape 2** : toutes les aires urbaines, une page par commune, couches de points (sols pollués, sites industriels classés, accidents de la route). Données en Release.
- **Étape 3** : fiches écoles, crèches et EHPAD (données officielles du lieu, hygiène de la cantine, expositions calculées à l'étape 2).
- **Étape 4** : le bruit (jeu national du Cerema d'abord, puis Grand Paris, aéroports, agglomérations).
- **Étape 5** : campagne chaleur avant l'été, avec un indicateur maison par ville.
- **Étape 6** : suivre un lieu par alertes. Demandera un service en plus : décision à prendre avec elle le moment venu.

## Étape en cours

Étape 1 (la chaleur sur la ville pilote). Mets cette ligne à jour à chaque changement d'étape.
