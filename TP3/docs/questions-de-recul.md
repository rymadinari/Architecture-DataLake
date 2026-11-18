# Questions de recul (§11)

**1. Pourquoi vérifier les schémas avant de transformer ?**
Parce que les fichiers n'ont pas d'en-tête et que tout y est du texte. Si je me trompe de colonne ou de type, mes calculs sont faux sans que Spark ne dise rien. Par exemple, une somme sur une colonne de texte mal convertie donne des nulls. J'ai donc vérifié le nombre de colonnes et que chaque valeur rentre dans son type avant de nettoyer.

**2. Différence entre donnée brute, Silver et Gold ?**
La donnée brute, c'est le fichier tel qu'on l'a reçu (`store_sales.dat`), on n'y touche pas. Le Silver, c'est la même donnée mais propre : bons types, espaces enlevés, colonnes inutiles retirées, avec sa provenance. Le Gold, c'est une donnée calculée pour répondre à une question, par exemple le CA par magasin et par mois.

**3. Pourquoi connaître la granularité avant d'agréger ?**
Pour savoir ce qu'on compte. Dans mes ventes, une ligne n'est pas un ticket mais une ligne de ticket. Si j'avais compté les lignes comme des tickets, j'aurais trouvé 667 579 tickets au lieu de 89 100, et un panier moyen faux. C'est pour ça que j'utilise `countDistinct` sur le numéro de ticket.

**4. Risques d'une jointure sur une clé supposée ?**
Perdre des lignes (si des clés n'ont pas de correspondance) ou en dupliquer (si la clé n'est pas unique de l'autre côté). Les totaux seraient alors faux. J'ai vérifié qu'il n'y avait aucun orphelin et que les clés étaient uniques dans les tables de référence, puis que le nombre de lignes était le même avant et après la jointure.

**5. Pourquoi ne pas supprimer automatiquement les valeurs atypiques ?**
Parce qu'une valeur bizarre peut être vraie. Dans mes données, les ventes à 0 € peuvent être des produits offerts, et les doublons (ticket, produit) sont de vraies ventes avec des prix différents. Les supprimer aurait faussé le CA. Je les ai gardées et documentées.

**6. Quels contrôles vérifient la cohérence d'un jeu transformé ?**
Comparer le nombre de lignes avant et après, vérifier que les totaux restent égaux (CA Gold = CA Silver), contrôler les clés (unicité, pas d'orphelins), les valeurs obligatoires, les types, et des règles métier (quantité entre 1 et 100, net payé = montant − coupon). C'est ce que fait le notebook 04.

**7. Pourquoi Parquet est adapté à l'analyse ?**
Il range les données par colonne, les compresse et garde les types. Pour calculer un CA, Spark ne lit que la colonne utile. Chez moi, les ventes passent de 88,5 Mo en texte à 42 Mo en Parquet, et la somme du CA est 4 à 5 fois plus rapide.

**8. Pourquoi Parquet seul n'est pas une table transactionnelle ?**
Un dossier Parquet, c'est juste des fichiers. Si une écriture plante au milieu, il peut rester des fichiers à moitié écrits, deux personnes peuvent écrire en même temps, et on ne peut pas revenir à une version précédente. Des formats comme Delta Lake, Iceberg ou Hudi ajoutent un journal des transactions par-dessus les fichiers Parquet pour avoir ces garanties.

**9. Quand une base NoSQL peut compléter un Data Lake ?**
Quand on a besoin de retrouver très vite une information précise à partir d'une clé, par exemple la fiche d'un produit ou l'historique d'un client pour une application. Le Data Lake et Parquet sont faits pour analyser beaucoup de lignes d'un coup, pas pour lire ou modifier une seule ligne rapidement.

**10. Limites des données TPCx-BB pour interpréter les résultats ?**
Ce sont des données inventées par un générateur : les ventes sont réparties presque au hasard (les 12 magasins sont à 5 % d'écart), 74 % des marges sont négatives, le panier moyen est d'environ 13 000 €, les textes sont aléatoires et certaines colonnes sont incohérentes (dates de fermeture, `d_holiday`). En plus, 2005 s'arrête au 13 décembre dans le lot principal. Les résultats montrent que la chaîne de traitement fonctionne, mais ils ne disent rien d'une vraie enseigne.
