# Questions de recul (§15)

**1. Pourquoi vérifier la granularité avant de calculer un KPI ?**
La granularité, c'est ce que représente une ligne. Il faut la connaître pour savoir ce qu'on additionne ou ce qu'on compte. Dans `silver/sales`, une ligne est un produit dans un ticket. Dans `gold/ventes_magasin_mois`, une ligne est un magasin pour un mois. Si je divisais le chiffre d'affaires par le nombre de lignes pour avoir le panier moyen, je trouverais 1 723 au lieu de 12 913. C'est aussi pour ça que je recompte les tickets dans le Silver, au lieu d'additionner les tickets de chaque mois du Gold.

**2. Différence entre un nombre de lignes et un nombre de transactions ?**
Une transaction, c'est un ticket de caisse. Un ticket contient plusieurs produits, donc plusieurs lignes. Chez moi : 667 579 lignes pour 89 100 tickets (environ 7,5 produits par ticket). Et encore autre chose pour les articles : 33 755 474. Pour compter les tickets, il faut compter les numéros de ticket **différents** (`countDistinct`), pas les lignes.

**3. Quelles limites ai-je rencontrées dans les données ?**
Les données sont inventées par un programme : ventes réparties presque au hasard, pas de saisons, montants pas réalistes (environ 379 articles par ticket). En plus :
- 74 % des ventes sont à perte ;
- décembre 2005 n'a que 13 jours ;
- les surfaces des magasins sont fausses ;
- le nombre d'employés est donné une seule fois pour 5 ans ;
- la devise n'est pas indiquée ;
- seules les ventes en magasin ont été nettoyées au TP3.

**4. Quels indicateurs je n'ai pas pu calculer, et pourquoi ?**
- La marge (K6) : possible, mais pas fiable.
- Le chiffre d'affaires par m² : les surfaces sont fausses.
- Les remises (K5) : pas réalistes, et la table des promotions n'a pas été nettoyée.
- Les retours (K8), les stocks (K9), les clics web (K10), les avis (K12) : ces tables n'ont pas été nettoyées au TP3.
- La rentabilité (K13) : il n'y a pas de coûts dans les données.

Je n'ai pas non plus pu comparer magasin et site web (Q7).

**5. Comment j'ai vérifié que mes résultats sont justes ?**
- Le chiffre d'affaires total est le même dans le Silver et dans les deux tables Gold (1 150 529 586,37). Le notebook s'arrête avec une erreur si ce n'est pas le cas.
- Le total est le même quand on regarde par ligne ou par ticket.
- Il n'y a pas de doublon dans les tables Gold.
- Un ticket appartient toujours à un seul magasin.
- K1, K2, K3 et K4 sont exactement les mêmes que ceux calculés au TP1 avec un autre outil (DuckDB).
- Les parts des catégories font bien 100 %.

**6. Différence entre un constat et une cause ?**
Un constat dit ce qu'on voit : « Germantown a le meilleur chiffre d'affaires par employé ». Une cause dit pourquoi : « parce qu'il est mieux géré ». Pour dire ça, il faudrait d'abord éliminer les autres explications (taille, ville, clients, prix…). Ici, Germantown est surtout le magasin qui a le moins d'employés : c'est le calcul lui-même qui le met premier.

**7. Pourquoi dire que les données sont inventées ?**
Pour que personne ne croie que ce sont de vrais résultats et ne prenne de décision dessus. Un panier moyen de 12 900 ou l'absence de pic à Noël viennent du programme qui a inventé les données, pas de vrais clients. Je l'écris donc sous chaque graphique et au début des conclusions.

**8. Quel est le rôle d'ADLS Gen2 dans mon architecture ?**
C'est l'endroit où on rangerait les données dans Azure. Il remplacerait HDFS (TP2) et le disque de mon PC (TP3). Il contiendrait toutes les zones (raw, bronze, silver, gold, quality) dans un conteneur, avec des droits par dossier. Il ne calcule rien : Spark et SQL viennent y lire et y écrire.

**9. À quoi sert le HNS ?**
Il donne de vrais dossiers au lieu de simples noms de fichiers. Grâce à lui, renommer ou supprimer un dossier se fait en une seule fois, sans risque de le laisser à moitié fait. C'est important pour Spark, qui écrit dans un dossier temporaire puis le renomme. Il permet aussi de mettre des droits sur chaque dossier. Sans lui, impossible de donner `gold/` aux analystes sans leur ouvrir aussi `raw/`.

**10. Différence entre RBAC et ACL ?**
Le RBAC donne un rôle sur une ressource entière (tout le compte, tout le conteneur) : c'est large. Les ACL donnent des droits lire / écrire / ouvrir sur un dossier ou un fichier précis : c'est précis. Azure regarde d'abord le RBAC ; s'il dit oui, il ne regarde pas les ACL. C'est pour ça que je ne donne pas de grand rôle sur les données, et que je gère les accès avec les ACL.

**11. Quand Azure Data Factory serait-il utile ?**
Pour automatiser ce que je fais à la main : copier chaque nouveau lot de fichiers dans `raw/` (comme NiFi au TP2), puis lancer les étapes dans l'ordre (Silver → Gold → contrôles → analyses), chaque jour ou dès qu'un fichier arrive. Il prévient aussi s'il y a une erreur. Pour un seul lot traité une seule fois, ce n'est pas nécessaire.

**12. À quoi pourrait servir Synapse Analytics ?**
À tout réunir au même endroit :
- mes notebooks PySpark, qui tourneraient sur des machines louées à la demande au lieu de mon PC (qui n'a que 2 Go de mémoire pour Spark) ;
- un SQL pour que les analystes interrogent directement les fichiers de `gold/` ;
- le lien avec Power BI.

**13. Qu'est-ce qui a vraiment été mis en place, et qu'est-ce qui reste théorique ?**
Vraiment mis en place :
- les fichiers TPCx-BB sur mon PC ;
- HDFS et NiFi (TP2) ;
- Spark sur mon PC, et les fichiers Parquet Silver et Gold (TP3) ;
- JupyterLab, Pandas, Matplotlib, le notebook et les graphiques (TP4).

Théorique :
- toute la partie Azure (ADLS Gen2, Entra ID, RBAC, ACL, Data Factory, Synapse, Power BI) ;
- MinIO, Iceberg, le catalogue, Trino, Airflow et Superset.

**14. Quels seraient les principaux risques de coût ou de sécurité dans la vraie vie ?**
Côté coût :
- laisser des machines Spark allumées ;
- faire des requêtes SQL sur de gros fichiers bruts au lieu des petits fichiers Parquet ;
- oublier des ressources (adresses IP, disques) qui coûtent même sans servir.

Solutions : un budget avec alertes, l'arrêt automatique des machines, et un seul groupe de ressources pour tout supprimer d'un coup.

Côté sécurité :
- publier une clé du compte de stockage dans Git ;
- laisser un conteneur ouvert au public ;
- donner trop de droits « pour aller plus vite » ;
- laisser les analystes voir des données clients non anonymisées.

Solutions : Entra ID et les identités managées (sans mot de passe), Key Vault pour les secrets, des droits par dossier et la trace de qui accède à quoi.
