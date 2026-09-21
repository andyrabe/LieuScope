# Feuille de route

Mise à jour : 21 septembre 2026. Étape en cours : **étape 1**.

## Étape 0 — mise en place ✔ (code prêt, reste un clic côté GitHub)

- [x] Décisions : ville pilote **Lyon**, dépôt **public**, nom **LieuScope**, licence **MIT**.
- [x] Squelette Astro en sortie statique, TypeScript strict, CSS à variables.
- [x] `deploy.yml` (construction et publication sur GitHub Pages à chaque `main`).
- [x] `ci.yml` (types, tests, construction, contrôle de poids sur chaque PR).
- [x] `data.yml` (exécution du pipeline dans Actions, `workflow_dispatch`).
- [x] JOURNAL, ROADMAP, MÉTHODE, SOURCES, `.gitignore`, LICENSE.
- [ ] **À faire par elle** : activer Pages (Settings → Pages → Source : GitHub Actions).
- [ ] Terminé quand le site s'ouvre sur son téléphone.

## Étape 1 — la chaleur sur la ville pilote (en cours)

- [x] Logique de verdict pure et testée : tuile d'un point, point dans polygone, distance.
- [x] Champ d'adresse avec autocomplétion (géocodage Géoplateforme, sans clé).
- [x] Verdict en texte avant la carte, lien partageable, balises Open Graph.
- [x] Carte MapLibre chargée en différé, avec légende et attribution.
- [x] Pages « Méthode », « Sources et mentions légales », « Communes couvertes ».
- [x] Pipeline `pipeline/lcz/` : téléchargement, découpe en tuiles, rapport, témoins.
- [ ] **Bloqué ici** : exécuter `data.yml` dans Actions pour produire `public/data/lcz/`
      (data.gouv.fr est inaccessible depuis l'environnement de développement).
- [ ] Confirmer le millésime du jeu Cerema et le noter dans `data/SOURCES.md`.
- [ ] Relire le guide utilisateur et le guide technique du Cerema, corriger le
      tableau de `docs/METHODE.md` si nécessaire.
- [ ] Remplacer les trois adresses témoins par des adresses qu'elle connaît, et
      inscrire le verdict attendu dans `data/temoins.json`.
- [ ] Vérifier sur téléphone : les trois témoins, le hors zone, Firefox, Safari, Chrome.
- [ ] Vérifier le budget : accueil sous 150 Ko hors carte, `dist/` sous 700 Mo.
- [ ] Étiquette `v0.1`.

## Étape 2 — toutes les aires urbaines

Une page par commune, couches de points (sols pollués, sites industriels
classés, accidents de la route). Les données passent en pièce jointe d'une
Release GitHub : `data.yml` publie, `deploy.yml` télécharge avant de construire.

## Étape 3 — écoles, crèches, EHPAD

Fiches d'établissements à partir des données officielles du lieu, hygiène de la
cantine (Alim'confiance, résultats de moins d'un an), expositions calculées à
l'étape 2.

## Étape 4 — le bruit

Jeu national du Cerema d'abord, puis Grand Paris, aéroports, agglomérations.

## Étape 5 — campagne chaleur avant l'été

Un indicateur maison par ville, justifié dans `docs/METHODE.md`.

## Étape 6 — suivre un lieu par alertes

Demandera un service en plus (envoi d'e-mails). Décision à prendre avec elle le
moment venu ; rien n'est engagé avant.
