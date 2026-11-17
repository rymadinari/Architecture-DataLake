# Convention de nommage des dossiers et des fichiers (activité complémentaire CO-02)

Une **convention de nommage**, c'est une règle commune pour nommer les dossiers et les fichiers. Le but : qu'en lisant juste un chemin, n'importe qui de l'équipe sache ce qu'il y a dedans, sans devoir ouvrir le fichier ni chercher dans la documentation.

## 1. Ce que le nom doit dire

Le TP demande qu'on puisse retrouver cinq informations. Voici où je les ai placées :

| Information | Où on la lit | Exemple |
|---|---|---|
| La source (d'où viennent les données) | 3ᵉ niveau du chemin | `tpcxbb` |
| Le domaine métier (de quoi ça parle) | 4ᵉ niveau du chemin | `ventes` |
| Le lot (la livraison) | dossier `lot=` | `lot=initial` ou `lot=refresh` |
| La date de réception | dossier `date_reception=` | `date_reception=2026-11-16` |
| Le type de données | la zone (1ᵉʳ niveau) et l'extension du fichier | `raw/…/store_sales.dat` |

J'ai aussi ajouté le nom de la table (`store_sales`), parce que c'est ce qu'on cherche le plus souvent.

## 2. La règle que j'ai choisie

```
/retail-lake/<zone>/<source>/<domaine>/<table>/lot=<lot>/date_reception=<année-mois-jour>/<fichier>
```

Par exemple, pour les ventes en magasin du lot principal :

```
/retail-lake/raw/tpcxbb/ventes/store_sales/lot=initial/date_reception=2026-11-16/store_sales.dat
```

On lit de gauche à droite : zone Raw, source TPCx-BB, domaine ventes, table store_sales, lot initial, reçu le 16 novembre 2026.

### Les règles d'écriture

1. **Tout en minuscules, avec `_` entre les mots.** C'est déjà la façon dont sont nommées les tables TPCx-BB (`store_sales`, `web_returns`), donc je garde la même habitude.
2. **Pas d'accents, pas d'espaces, pas de caractères spéciaux.** J'ai eu le problème pendant le TP : `hdfs dfs -stat` affichait `??` à la place des accents (erreur n°4 dans `docs/operations/erreurs-et-corrections.md`). J'écris donc `referentiel` et pas `référentiel`.
3. **Les dates s'écrivent année-mois-jour** (`2026-11-16`). Dans ce sens, les dossiers se rangent tout seuls dans l'ordre chronologique quand on fait un `ls`.
4. **Les dossiers `lot=` et `date_reception=` s'écrivent `nom=valeur`.** Spark, qu'on utilisera au Jour 3, comprend cette écriture : il transforme le nom du dossier en colonne. On pourra donc lire seulement le lot `refresh` sans parcourir tout le reste. On appelle ce découpage une **partition**.
5. **Dans Raw, on ne renomme jamais le fichier reçu.** `store_sales.dat` reste `store_sales.dat`. Si on le renommait, on perdrait le lien avec le fichier d'origine du kit. Tout ce que j'ajoute (domaine, lot, date) va dans les dossiers, pas dans le nom du fichier.
6. **Dans Bronze, Silver et Gold, c'est Spark qui nomme les fichiers** (`part-00000-….parquet`). On les laisse comme ça : ce sont les dossiers qui donnent les informations.
7. **Pour les journaux et les rapports qualité**, le nom indique le traitement, la table, puis la date et l'heure. Par exemple :
   - `logs/ingestion/depot_hdfs_store_sales_20261116T143000.log`
   - `quality/tpcxbb/ventes/store_sales/controle_colonnes_20261118T100000.csv`

### Les domaines métier

Je suis partie de la liste des domaines du §8.1 de l'énoncé. J'ai regroupé certaines tables pour ne pas avoir des domaines avec une seule petite table dedans.

| Domaine | Tables TPCx-BB |
|---|---|
| `ventes` | `store_sales`, `web_sales` |
| `retours` | `store_returns`, `web_returns`, `reason` |
| `produits` | `item`, `item_marketprices`, `promotion` |
| `clients` | `customer`, `customer_address`, `customer_demographics`, `household_demographics`, `income_band` |
| `magasins` | `store`, `warehouse`, `ship_mode` |
| `stocks` | `inventory` |
| `web` | `web_clickstreams`, `web_page`, `web_site` |
| `avis` | `product_reviews` |
| `referentiel` | `date_dim`, `time_dim` |

## 3. Pourquoi ce choix

**On sait d'où vient un fichier rien qu'en lisant son chemin.**
C'est une première trace de la provenance. Elle complète les deux autres que j'ai déjà mises en place : l'empreinte SHA-256 de chaque fichier et l'historique de NiFi.

**On évite d'écraser un fichier.**
Si le même fichier arrive deux jours différents, il va dans deux dossiers `date_reception=` différents. Si par erreur il arrive deux fois le même jour, le dépôt est refusé : PutHDFS est réglé sur `fail`, et mon script `depot_hdfs.sh` vérifie si le fichier existe déjà avant de le déposer.

**On peut donner des droits par domaine.**
Par exemple, le dossier `clients/` contient des données personnelles (noms, e-mails). On peut en limiter l'accès sans toucher aux ventes ou aux produits.

**Ça prépare le Jour 3.**
Grâce aux dossiers `lot=` et `date_reception=`, Spark lira directement le lot et la date comme des colonnes, sans qu'on ait à les recopier dans les données.

**On suit une table d'une zone à l'autre facilement.**
Le chemin reste le même partout, seul le premier mot change : `raw/…` → `bronze/…` → `silver/…`.

## 4. Ce qui existe déjà dans HDFS

L'arborescence que j'ai créée au Jour 2 (voir `architecture-data-lake.md`) respecte déjà une partie de la règle : la source, le lot et la table sont dans le chemin, et le nom du fichier d'origine est gardé. Il manque surtout le domaine et la date.

| Chemin actuel | Chemin avec la convention | Ce qui manque |
|---|---|---|
| `raw/tpcxbb/initial/store_sales/store_sales.dat` | `raw/tpcxbb/ventes/store_sales/lot=initial/date_reception=2026-11-16/store_sales.dat` | domaine, date |
| `raw/tpcxbb/refresh/web_returns/web_returns.dat` | `raw/tpcxbb/retours/web_returns/lot=refresh/date_reception=2026-11-16/web_returns.dat` | domaine, date |
| `raw/nifi/ship_mode.dat` (test NiFi de l'étape 9) | `raw/nifi/tpcxbb/magasins/ship_mode/lot=test/date_reception=2026-11-17/ship_mode.dat` | source, domaine, table, lot, date |

**J'ai choisi de ne pas déplacer les fichiers déjà déposés.** Mes preuves (`verif_stockage.csv`, la provenance NiFi) indiquent leur chemin actuel. Si je les déplaçais, ces preuves ne correspondraient plus à rien. La règle s'applique donc aux prochains dépôts. Pour les données existantes, la réorganisation se fera naturellement au Jour 3, au passage en Bronze, puisque les données seront de toute façon réécrites.

## 5. Comment je l'appliquerais

**Dans le script de dépôt manuel** (`depot_hdfs.sh`) : trouver le domaine de la table grâce au tableau ci-dessus, prendre la date du jour avec `date +%F`, puis déposer le fichier dans `…/<domaine>/<table>/lot=<lot>/date_reception=<date>/`.

**Dans le flux NiFi** : on ajouterait un processeur UpdateAttribute entre GetFile et PutHDFS. Il colle des informations à chaque fichier : la source, le domaine, la table et le lot. Dans NiFi, ces informations s'appellent des **attributs**. Il suffirait ensuite de changer le dossier de destination de PutHDFS pour qu'il utilise ces attributs :

```
/retail-lake/raw/nifi/${source.systeme}/${domaine}/${table}/lot=${lot}/date_reception=${now():format('yyyy-MM-dd')}
```

`${...}` veut dire « remplacer par la valeur de l'attribut ». `now():format('yyyy-MM-dd')` donne la date du jour.

## 6. Les limites

- **Le domaine d'une table, c'est un choix.** Par exemple, `promotion` aurait aussi pu aller dans `ventes`. Pour ne pas hésiter à chaque fois, c'est le tableau du §2 qui décide.
- **La date de réception, c'est la date du dépôt dans HDFS**, pas la date à laquelle les données ont été créées. TPCx-BB ne donne pas cette information.
- **Le kit n'a pas de numéro de version.** La seule notion de version que j'ai, c'est `initial` et `refresh`. Si le formateur envoie une nouvelle livraison, je l'appellerai `lot=refresh_2`.
- **Les chemins deviennent longs.** Ce n'est pas un problème pour HDFS, mais c'est moins agréable à taper dans le terminal.
