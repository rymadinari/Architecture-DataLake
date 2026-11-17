# Inventaire des fichiers TPCx-BB utilisés (§8.2 et §8.3)

Les tailles, nombres de lignes et nombres de colonnes ont été mesurés sur les fichiers eux-mêmes (inventaire du Jour 1, `TP1/.../preuves/inventaire_fichiers.csv`), puis contrôlés à nouveau après le dépôt dans HDFS (`preuves/j2/hdfs/verif_stockage.csv`).

## Informations communes à tous les fichiers

| Information | Valeur constatée |
|---|---|
| Chemin local | `~/TP1/retail_project/data/<table>/<table>.dat` et `~/TP1/retail_project/data_refresh/<table>/<table>.dat` |
| Format | Texte délimité par `|`, **sans ligne d'en-tête**, fins de ligne Windows (CRLF), valeur vide = valeur manquante. Ce n'est ni du CSV classique, ni du JSON, ni du Parquet. |
| Types | Pas de types dans le fichier (c'est du texte). Types déduits au Jour 1 : nombres entiers pour les clés (`*_sk`), décimaux pour les montants, dates `AAAA-MM-JJ`, texte. |
| Noms des colonnes | Absents des fichiers. Repris du schéma officiel TPCx-BB au Jour 1 (statut : déduit). |
| Provenance | Kit `retail_project`, fourni par le formateur via Teams le 16/11/2026. Version non communiquée. Données synthétiques TPCx-BB. |
| Lisibilité | Tous les fichiers s'ouvrent et se lisent (`head`, `wc -l`). |

## Matrice d'inventaire — lot principal (`data/`, déposé dans `raw/tpcxbb/initial/`)

| Fichier | Format | Taille | Lignes | Colonnes | Observations |
|---|---|---|---|---|---|
| `store_sales.dat` | `.dat` délimité `|` | 92,8 Mo | 667 579 | 23 | Ventes magasin. 74 % des lignes ont une marge négative (données inventées). |
| `web_sales.dat` | `.dat` délimité `|` | 133,8 Mo | 668 052 | 34 | Ventes web. |
| `store_returns.dat` | `.dat` délimité `|` | 4,3 Mo | 37 902 | 20 | Retours magasin. |
| `web_returns.dat` | `.dat` délimité `|` | 5,4 Mo | 38 487 | 24 | Retours web. |
| `inventory.dat` | `.dat` délimité `|` | 424,9 Mo | 23 255 100 | 4 | Plus gros fichier : 4 blocs HDFS (voir CO-01). |
| `web_clickstreams.dat` | `.dat` délimité `|` | 178,7 Mo | 6 770 550 | 6 | Clics. Pas de type d'action ni de session. |
| `product_reviews.dat` | `.dat` délimité `|` | 56,4 Mo | 89 991 | 8 | Avis clients, avec texte libre. |
| `customer.dat` | `.dat` délimité `|` | 13,3 Mo | 99 000 | 18 | Données personnelles (inventées) : nom, e-mail… |
| `customer_address.dat` | `.dat` délimité `|` | 5,4 Mo | 49 500 | 13 | |
| `customer_demographics.dat` | `.dat` délimité `|` | 77,8 Mo | 1 920 800 | 9 | |
| `household_demographics.dat` | `.dat` délimité `|` | 0,16 Mo | 7 200 | 5 | |
| `income_band.dat` | `.dat` délimité `|` | 327 o | 20 | 3 | |
| `item.dat` | `.dat` délimité `|` | 6,8 Mo | 17 820 | 22 | Produits. |
| `item_marketprices.dat` | `.dat` délimité `|` | 4,2 Mo | 89 100 | 6 | Prix concurrents. |
| `promotion.dat` | `.dat` délimité `|` | 46 Ko | 300 | 19 | Dates de promotion entre 1901 et 2199 (anomalie). |
| `store.dat` | `.dat` délimité `|` | 3,4 Ko | 12 | 29 | 12 magasins. |
| `warehouse.dat` | `.dat` délimité `|` | 584 o | 5 | 14 | Fichier du premier test NiFi (étape 9). |
| `date_dim.dat` | `.dat` délimité `|` | 15,4 Mo | 109 573 | 28 | `d_holiday` vaut Y partout (inutilisable). |
| `time_dim.dat` | `.dat` délimité `|` | 5,1 Mo | 86 400 | 10 | |
| `reason.dat` | `.dat` délimité `|` | 3,1 Ko | 35 | 3 | Motifs illisibles (lettres au hasard). |
| `ship_mode.dat` | `.dat` délimité `|` | 1,2 Ko | 20 | 6 | Fichier du deuxième test NiFi (étape 9). |
| `web_page.dat` | `.dat` délimité `|` | 8 Ko | 60 | 14 | |
| `web_site.dat` | `.dat` délimité `|` | 8,8 Ko | 30 | 26 | |

## Matrice d'inventaire — lot d'ajout (`data_refresh/`, déposé dans `raw/tpcxbb/refresh/`)

| Fichier | Format | Taille | Lignes | Colonnes | Observations |
|---|---|---|---|---|---|
| `store_sales.dat` | `.dat` délimité `|` | 0,92 Mo | 6 632 | 23 | Ventes du 13/12 au 31/12/2005. Utilisé comme second fichier de test NiFi. |
| `web_sales.dat` | `.dat` délimité `|` | 1,4 Mo | 6 879 | 34 | |
| `store_returns.dat` | `.dat` délimité `|` | 49 Ko | 426 | 20 | 407 retours sans vente correspondante. |
| `web_returns.dat` | `.dat` délimité `|` | 56 Ko | 400 | 24 | |
| `inventory.dat` | `.dat` délimité `|` | 4,3 Mo | 234 900 | 4 | |
| `web_clickstreams.dat` | `.dat` délimité `|` | 1,8 Mo | 68 988 | 6 | |
| `product_reviews.dat` | `.dat` délimité `|` | 0,57 Mo | 909 | 8 | |
| `customer.dat` | `.dat` délimité `|` | 0,13 Mo | 1 000 | 18 | |
| `customer_address.dat` | `.dat` délimité `|` | 55 Ko | 500 | 13 | |
| `item.dat` | `.dat` délimité `|` | 69 Ko | 180 | 22 | 180 nouveaux produits, absents du lot principal. |
| `item_marketprices.dat` | `.dat` délimité `|` | 43 Ko | 900 | 6 | |

## Fichiers non déposés

| Fichier | Raison |
|---|---|
| `item_marketprices_audit.csv` (dans `data/` et `data_refresh/`) | Ce sont des rapports du générateur de données, pas des données métier. Ils restent dans le kit local. |

Aucun faux fichier TPCx-BB n'a été créé. Les fichiers de test NiFi sont des **copies** de fichiers réels du kit (voir `docs/ingestion/flux-nifi.md`).
