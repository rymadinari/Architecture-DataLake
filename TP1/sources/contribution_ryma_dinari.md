# Contribution individuelle — Ryma Dinari

Retail Intelligence Platform · TP Jour 1 · IPSSI · Mastère Développement, Data & IA

Mode de travail : projet réalisé seule. J'ai donc pris en charge l'ensemble des rôles prévus au §9.1 (référent métier, données, architecture et documentation).

## 1. Ma contribution au cadrage métier

Je suis partie des profils proposés dans l'énoncé (direction générale, direction commerciale, responsable de magasin, contrôleur de gestion, responsable des stocks, équipe Data). Pour chacun, j'ai cherché ce qu'il doit décider concrètement, plutôt que de lister des indicateurs « pour le principe ». J'ai ajouté un profil e-commerce / marketing, parce que le kit contient des données de navigation et des avis produits que personne d'autre n'aurait vraiment utilisés.

J'ai formulé 18 questions, chacune reliée à une décision et à une priorité, puis 13 indicateurs. Les plus importants pour moi sont le chiffre d'affaires net, le nombre de transactions et le panier moyen : c'est la base du pilotage, et ils sont calculables de façon fiable avec les données. J'ai fait attention à bien distinguer une ligne de vente d'une transaction : un ticket contient en moyenne 7,5 lignes, donc compter les lignes fausserait le panier moyen.

## 2. Les sources que j'ai examinées

J'ai parcouru les 36 fichiers du dossier `retail_project`, et plus en détail les ventes (`store_sales`, `web_sales`), les retours, le stock (`inventory`), les clics web (`web_clickstreams`) et les clients. La première chose qui m'a frappée, c'est que les fichiers n'ont pas d'en-tête : il faut connaître le schéma TPCx-BB pour savoir à quoi correspond chaque colonne. Ils utilisent le séparateur `|` et des fins de ligne au format Windows (CRLF).

J'ai aussi compris que le dossier `data_refresh/` est un petit lot qui vient compléter le lot principal : les ventes s'arrêtent au 13/12/2005 dans `data/` et le refresh couvre la fin du mois de décembre.

## 3. Les contrôles que j'ai réalisés

J'ai vérifié la structure des fichiers dans le terminal Linux. Par exemple, `store_sales.dat` contient 667 579 lignes, et toutes ont exactement 23 colonnes, donc aucune ligne n'est cassée. J'ai aussi mesuré les volumes : 978 Mio pour `data/`, 9,2 Mio pour `data_refresh/`, 36 fichiers au total. Les captures d'écran sont dans le dossier de preuves.

Les contrôles plus poussés (valeurs nulles, unicité des clés, correspondances entre tables, cohérence des montants) ont été faits avec un script Python et DuckDB. J'ai relu les résultats et je les ai intégrés au dossier. Les deux constats qui m'ont le plus surprise : le stock fait référence à 180 produits qui n'existent que dans le lot refresh, et 407 retours du refresh n'ont aucune vente d'origine.

## 4. Les décisions d'architecture auxquelles j'ai contribué

J'ai retenu un Data Lake organisé en trois zones. Bronze garde les fichiers tels qu'ils ont été reçus, Silver contient les données nettoyées et contrôlées, et Gold les données prêtes pour les indicateurs. Un Data Warehouse seul ne m'a pas paru suffisant : il ne conserve pas les données brutes, alors que plusieurs relations restent des hypothèses et qu'on pourrait devoir tout retraiter. J'ai quand même organisé la zone Gold en étoile, comme un entrepôt, pour que les KPI soient simples à calculer.

Delta Lake et HBase restent facultatifs, comme le prévoit le référentiel. Ils seraient intéressants plus tard, mais le socle n'en dépend pas. En local, l'architecture repose sur HDFS, NiFi et Spark ; dans le cloud, HDFS est remplacé par ADLS Gen2, et la gestion des accès passe par Entra ID, RBAC et ACL.

## 5. Les limites que j'ai identifiées

- Le jeu de données est synthétique : 74 % des ventes en magasin ont une marge négative et la remise moyenne est de 50 %. Les chiffres ne peuvent donc pas être lus comme une réalité métier.
- Les motifs de retour sont des chaînes de caractères aléatoires, on ne peut pas savoir pourquoi un produit est retourné.
- Les clics web n'ont ni type d'événement ni session : on ne peut pas reconstruire un parcours vue → panier → achat.
- Les dates de promotion vont de 1901 à 2199, donc on ne peut pas mesurer l'effet réel d'une promotion.
- La version du kit n'est pas communiquée, et les noms de colonnes viennent du schéma de référence, pas des fichiers.

## 6. Ce que je retiens / difficultés rencontrées

Ce que je retiens surtout, c'est qu'une donnée disponible n'est pas forcément exploitable : il faut vérifier colonne par colonne avant de construire un indicateur. La principale difficulté a été de travailler sans en-tête ni documentation fournie avec le kit.