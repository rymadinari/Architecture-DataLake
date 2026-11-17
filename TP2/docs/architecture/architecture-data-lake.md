# Arborescence du Data Lake (UC-03, étape 3)

## Arborescence créée dans HDFS

```
/retail-lake/
├── raw/                     données reçues, jamais modifiées
│   ├── tpcxbb/
│   │   ├── initial/         lot principal (dossier data/ du kit), un sous-dossier par table
│   │   │   ├── store_sales/store_sales.dat
│   │   │   ├── web_sales/web_sales.dat
│   │   │   └── ... (23 tables)
│   │   └── refresh/         lot d'ajout (dossier data_refresh/ du kit), 11 tables
│   └── nifi/                fichiers déposés automatiquement par le flux NiFi (UC-04)
├── bronze/
│   └── tpcxbb/              (vide au Jour 2) données brutes mises dans un format lisible
├── silver/                  (vide au Jour 2) données nettoyées et contrôlées
├── gold/                    (vide au Jour 2) données prêtes pour les indicateurs
├── quality/                 (vide au Jour 2) rapports de contrôle qualité
└── logs/                    journaux des traitements
```

Seules les zones `raw/` sont remplies au Jour 2. Les autres sont créées vides : elles seront remplies au Jour 3 avec Spark.

## Lien avec l'architecture du Jour 1

Au Jour 1, j'avais prévu trois zones (Bronze, Silver, Gold) et une quarantaine, avec des chemins en `/datalake/...`. Pour le Jour 2, je suis l'arborescence proposée par le TP (`/retail-lake/...`), qui ajoute une zone **Raw** avant Bronze. C'est un changement de nom de dossier, la logique ne change pas.

| Jour 1 | Jour 2 | Remarque |
|---|---|---|
| `/datalake/bronze` (fichiers d'origine) | `/retail-lake/raw` | Au Jour 1, Bronze contenait les fichiers tels quels. C'est maintenant le rôle de Raw. |
| — | `/retail-lake/bronze` | Nouvelle étape : les mêmes données mais avec des noms de colonnes, toujours sans nettoyage. |
| `/datalake/silver` | `/retail-lake/silver` | Identique. |
| `/datalake/gold` | `/retail-lake/gold` | Identique. |
| `/datalake/quarantine` | `/retail-lake/quality` | Les lignes rejetées et les rapports qualité seront rangés ici. |
| — | `/retail-lake/logs` | Ajouté pour séparer les journaux des données. |

## Pourquoi cette organisation

**Pourquoi garder les données sources ?**
Si on se trompe dans un nettoyage ou si on change une règle (par exemple un nom de colonne qu'on avait mal deviné au Jour 1), on peut tout refaire à partir des fichiers d'origine. Ça sert aussi de preuve de ce qu'on a reçu.

**Différence entre Raw et Bronze**
- Raw = le fichier exactement comme il est arrivé (`.dat`, séparateur `|`, pas d'en-tête, fins de ligne Windows). On n'y touche jamais.
- Bronze = les mêmes données mais lisibles par les outils : noms de colonnes ajoutés, format Parquet, colonnes techniques (lot, date de réception, fichier d'origine). Pas encore de nettoyage.

**Rôle de Silver et Gold**
- Silver : données propres (bons types, doublons retirés, liens entre tables vérifiés, clients rendus anonymes).
- Gold : tables prêtes pour les indicateurs du Jour 1 (CA, panier moyen, taux de retour…), organisées en étoile.

**Pourquoi séparer données, qualité et journaux**
- On ne mélange pas les données métier avec des fichiers techniques : un analyste qui lit `gold/` ne tombe pas sur un rapport d'erreur.
- On peut donner des droits différents : les métiers lisent `gold/`, l'équipe data lit `quality/` et `logs/`.
- On peut supprimer les vieux journaux sans risquer de toucher aux données.

**Comment la provenance est conservée**
- Le chemin dit déjà beaucoup : source (`tpcxbb`), lot (`initial` ou `refresh`), table (nom du dossier).
- Le nom du fichier d'origine est gardé tel quel.
- Une empreinte SHA-256 de chaque fichier est calculée avant et après le dépôt (`preuves/j2/hdfs/verif_stockage.csv`) : elle prouve que le fichier n'a pas changé.
- Pour les fichiers déposés par NiFi, l'historique (provenance) de NiFi garde la date, le nom et le parcours de chaque fichier (`docs/ingestion/provenance.md`).
- Les dépôts NiFi vont dans `raw/nifi/`, séparé du dépôt manuel, pour ne jamais écraser le premier dépôt.

## Schéma des deux méthodes de dépôt

```
                 Fichiers du kit retail_project (disque local)
                                   │
                        Inspection et inventaire
                    (docs/ingestion/inventaire-sources.md)
                     ┌─────────────┴──────────────┐
                     ▼                            ▼
       UC-03 : hdfs dfs -put (manuel)     UC-04 : flux NiFi (automatique)
       script depot_hdfs.sh               GetFile ──success──▶ PutHDFS
                     │                            │
                     ▼                            ▼
       /retail-lake/raw/tpcxbb/           /retail-lake/raw/nifi/
            initial/ et refresh/
```
