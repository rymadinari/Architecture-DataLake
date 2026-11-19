# Comment ranger les données dans Azure (ADLS Gen2) et à quoi sert le HNS (J4-08, UC-07 étapes 2 et 3)

État : **prévu, pas créé** (parcours B).

Je reprends le rangement que j'ai vraiment utilisé dans HDFS au TP2 (`/retail-lake/...`) et mes règles de nommage du TP2. Comme ça, pour passer à Azure, seul le début du chemin change.

## 1. Le rangement prévu

Compte de stockage `stretailintelfrc01` (avec HNS) · conteneur `retail-intelligence`

```
retail-intelligence/
├── raw/                    fichiers reçus, jamais modifiés
│   └── tpcxbb/<domaine>/<table>/lot=<initial|refresh>/date_reception=<AAAA-MM-JJ>/<fichier>.dat
│       ex. raw/tpcxbb/ventes/store_sales/lot=initial/date_reception=2026-11-16/store_sales.dat
├── bronze/                 mêmes données en Parquet, avec les noms de colonnes, sans nettoyage
│   └── tpcxbb/<domaine>/<table>/lot=<lot>/
├── silver/                 données nettoyées (résultats du TP3)
│   ├── ventes/sales/
│   ├── produits/products/
│   ├── magasins/stores/
│   └── referentiel/dates/
├── gold/                   données prêtes pour les décisions
│   ├── indicateurs/ventes_magasin_mois/       (TP3)
│   ├── indicateurs/ventes_categorie_annee/    (TP3)
│   └── analyses/kpi/, analyses/ventes_par_magasin/ ...   (résultats du TP4)
├── quality/
│   ├── rapports/controles_qualite_<AAAAMMJJ>.csv
│   └── quarantine/<domaine>/<table>/   lignes mises de côté, jamais supprimées
├── complementaire/         données qui ne viennent pas de TPCx-BB (aucune pour l'instant), à part
└── documentation/          dictionnaires, liste des données, d'où elles viennent
```

Pour lire un dossier avec Spark, on écrirait :
`abfss://retail-intelligence@stretailintelfrc01.dfs.core.windows.net/silver/ventes/sales`

Correspondance avec mes dossiers actuels :

| Sur mon PC (utilisé) | Dans Azure (prévu) |
|---|---|
| HDFS `/retail-lake/raw/tpcxbb/initial/store_sales/store_sales.dat` | `raw/tpcxbb/ventes/store_sales/lot=initial/date_reception=2026-11-16/store_sales.dat` |
| `~/TP3/data/silver/sales/` | `silver/ventes/sales/` |
| `~/TP3/data/gold/ventes_magasin_mois/` | `gold/indicateurs/ventes_magasin_mois/` |
| `~/TP3/preuves/controles_qualite.csv` | `quality/rapports/controles_qualite_20261118.csv` |
| `~/TP4/resultats/kpi.csv` | `gold/analyses/kpi/kpi.csv` |

## 2. Chaque zone en détail

### raw/
- **À quoi elle sert** : garder une preuve de ce qu'on a reçu.
- **Ce qu'on y met** : les fichiers `.dat` tels qu'ils sont arrivés.
- **Qui écrit** : seulement Data Factory (le service qui copie les fichiers). **Qui lit** : l'équipe data.
- **Règles de nom** : le lot et la date de réception sont dans les noms de dossiers. On ne change **jamais** le nom du fichier.
- **Combien de temps on garde** : on ne modifie et ne supprime rien. On note une empreinte (un code unique qui change si le fichier change) à l'arrivée. On garde longtemps, et on passe en stockage moins cher après 90 jours.

### bronze/
- **À quoi elle sert** : rendre les données lisibles sans les changer.
- **Ce qu'on y met** : des fichiers Parquet avec les noms de colonnes, plus le lot, la date de réception et le fichier d'origine.
- **Qui** : Spark (l'équipe data).
- **Règles de nom** : `<domaine>/<table>/lot=<lot>/`. Les noms de fichiers `part-*.parquet` sont choisis par Spark.
- **Combien de temps** : on peut le vider et le refaire à partir de `raw/`.

### silver/
- **À quoi elle sert** : avoir des données propres et fiables.
- **Ce qu'on y met** : des tables avec les bons types, nettoyées, et des liens entre tables vérifiés.
- **Qui écrit** : Spark. **Qui lit** : l'équipe data, et certains analystes.
- **Règles de nom** : `<domaine>/<table>/`, en minuscules, sans accents.
- **Combien de temps** : chaque ligne garde le fichier d'origine et la date du traitement. Le dossier est remplacé à chaque recalcul (pas d'historique sans Iceberg ou Delta).

### gold/
- **À quoi elle sert** : répondre aux questions métier.
- **Ce qu'on y met** : des totaux et des indicateurs (Parquet), et des tableaux CSV.
- **Qui écrit** : Spark. **Qui lit** : les analystes, SQL, Power BI.
- **Règles de nom** : `indicateurs/<sujet>_<niveau>/` et `analyses/<sujet>/`.
- **Combien de temps** : chaque table est expliquée dans `documentation/`. On vérifie que le total Gold est égal au total Silver.

### quality/
- **À quoi elle sert** : prouver la qualité et mettre de côté les lignes refusées.
- **Ce qu'on y met** : les rapports de contrôle et les lignes en quarantaine.
- **Qui** : l'équipe data ; le responsable data peut lire les rapports.
- **Règles de nom** : `controles_qualite_<AAAAMMJJ>.csv`.
- **Combien de temps** : rapports gardés au moins 1 an ; la quarantaine n'est jamais vidée automatiquement.

### complementaire/
- **À quoi elle sert** : séparer ce qui ne vient pas de TPCx-BB.
- **Ce qu'on y met** : fichiers JSON, journaux inventés… (vide pour l'instant).
- **Règles** : `<source>/<domaine>/`. Ces données sont toujours marquées comme « complémentaires », jamais mélangées avec `tpcxbb/`.

### documentation/
- **À quoi elle sert** : savoir ce qu'il y a dans le lac de données.
- **Ce qu'on y met** : les dictionnaires, les listes de données, l'origine des données.
- **Qui** : tout le monde peut lire. Les documents sont aussi gardés dans Git.

## 3. À quoi sert le HNS (étape 3)

**HNS** veut dire *Hierarchical Namespace*, en français « espace de noms hiérarchique ».

**Sans HNS**, il n'y a pas de vrais dossiers. Un fichier `silver/ventes/sales/part-0.parquet` est juste un fichier dont le **nom contient des `/`**. Les « dossiers » qu'on voit ne sont qu'un affichage.

**Avec HNS** (c'est ce qu'on appelle ADLS Gen2), il y a de **vrais dossiers**, comme sur un PC ou dans HDFS.

| | Sans HNS | Avec HNS | Pourquoi c'est utile pour moi |
|---|---|---|---|
| Dossiers | Faux dossiers (juste une partie du nom) | Vrais dossiers | Mes zones raw → gold sont de vrais dossiers qu'on peut gérer |
| Renommer un dossier | Il faut copier **chaque** fichier puis le supprimer : c'est lent, et si ça plante au milieu, la moitié est déplacée | **Une seule opération**, instantanée, tout ou rien | Spark écrit d'abord dans un dossier temporaire, puis le renomme : avec HNS c'est rapide et sûr |
| Supprimer un dossier | Supprimer chaque fichier un par un | Une seule opération | Refaire vite un dossier Gold |
| Lister un dossier | Chercher parmi tous les noms | Lecture directe du dossier | Spark lit plus vite les dossiers comme `lot=initial` |
| Droits d'accès | Sur tout le compte ou tout le conteneur | Droits **par dossier et par fichier** (ACL) ; les nouveaux fichiers reçoivent automatiquement les droits de leur dossier | Donner `gold/` aux analystes sans leur ouvrir `raw/` |
| Avec Spark | Ancien chemin `wasbs://` | Chemin `abfss://`, prévu pour Spark | Mes notebooks marchent en changeant juste le chemin |

À savoir :
- le HNS s'active **quand on crée** le compte. On peut l'activer plus tard, mais on ne peut plus jamais revenir en arrière ;
- quelques options du stockage classique ne marchent pas avec le HNS : il faut vérifier le jour où on le crée.

Le stockage sans HNS reste bien pour des fichiers qu'on ne range jamais autrement (sauvegardes, images). Pour un lac de données en zones avec Spark, le HNS est nécessaire.

## 4. Mise en place (étape 4)

**Pas faite dans Azure** (pas d'accès). Ce qu'on aurait fait (ressources, étapes, contrôles, commandes) est expliqué dans `simulation-azure.md`.
