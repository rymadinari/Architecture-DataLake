# Dépôt et vérification du stockage HDFS (UC-03, étapes 2, 4 et 5)

## 1. Commandes HDFS testées (étape 2)

Fichier complet avec les commandes, leurs résultats et les erreurs : `preuves/j2/hdfs/01_decouverte_commandes.txt`.

| Opération demandée | Commande | Résultat |
|---|---|---|
| État du système | `hdfs dfsadmin -safemode get` / `hdfs dfsadmin -report` | Safe mode OFF, 1 DataNode vivant |
| Infos sur les nœuds | `hdfs dfsadmin -report` | `127.0.0.1:9866`, 136 Go configurés, 37 Go libres |
| Lister les répertoires | `hdfs dfs -ls /` | Vide au départ |
| Créer un répertoire | `hdfs dfs -mkdir -p /retail-lake` | OK (avant : `No such file or directory`) |
| Vérifier les permissions | `hdfs dfs -ls -d /retail-lake`, `hdfs dfs -stat "%u %g %A"` | Propriétaire `rymadinari`, groupe `supergroup`, droits `rwxr-xr-x` |
| Taille des données | `hdfs dfs -du -h`, `hdfs dfs -df -h /`, `hdfs dfs -count -q -h` | 0 au départ, 37,4 Go disponibles |

## 2. Dépôt (étape 4)

Script : `ingestion/scripts/depot_hdfs.sh` (journal : `preuves/j2/hdfs/depot_hdfs.log`).

Avant le dépôt, j'ai vérifié pour chaque fichier le chemin local, le nom, le format, la taille, la structure et la lisibilité. Tout est dans `docs/ingestion/inventaire-sources.md`.

J'ai déposé **les 34 fichiers de données du kit**, et pas seulement un :

| Lot | Dossier local | Destination HDFS | Fichiers | Taille |
|---|---|---|---|---|
| Principal | `~/TP1/retail_project/data/` | `/retail-lake/raw/tpcxbb/initial/<table>/` | 23 | 977,0 Mo |
| Ajout | `~/TP1/retail_project/data_refresh/` | `/retail-lake/raw/tpcxbb/refresh/<table>/` | 11 | 9,0 Mo |

Commande utilisée pour chaque fichier, par exemple :
```bash
hdfs dfs -put ~/TP1/retail_project/data/store_sales/store_sales.dat /retail-lake/raw/tpcxbb/initial/store_sales/
```
Le script ne remplace jamais un fichier existant : il vérifie d'abord avec `hdfs dfs -test -e`.

## 3. Vérification du stockage (étape 5)

Preuves : `preuves/j2/hdfs/verif_stockage.csv` (une ligne par fichier), `verif_stockage.log`, `03_controles_stockage.txt`, `02_arborescence_finale.txt`.

### Méthode utilisée

Pour **chacun des 34 fichiers** (`tests/hdfs/verif_stockage.sh`) :
1. taille locale (`stat`) comparée à la taille dans HDFS (`hdfs dfs -stat %b`) ;
2. empreinte **SHA-256** du fichier local comparée à l'empreinte du fichier **relu depuis HDFS** (`hdfs dfs -cat | sha256sum`).

En plus, pour `store_sales.dat` : nombre de lignes comparé (667 579 des deux côtés), récupération avec `hdfs dfs -get` puis comparaison octet par octet avec `cmp` (aucune différence).

Remarque : `hdfs dfs -checksum` donne une somme propre à HDFS (`MD5-of-0MD5-of-512CRC32C`), calculée sur les blocs. Elle ne peut pas être comparée directement à une empreinte calculée sur le fichier local, c'est pour ça que j'ai relu le fichier pour calculer sa SHA-256.

### Résultats

| Contrôle | Résultat |
|---|---|
| Répertoires attendus présents | Oui : `raw/tpcxbb/initial` (23 tables), `raw/tpcxbb/refresh` (11 tables), `raw/nifi`, `bronze/tpcxbb`, `silver`, `gold`, `quality`, `logs` |
| Fichiers déposés présents | 34 / 34 |
| Taille identique | 34 / 34 |
| SHA-256 identique | **34 / 34**, 0 écart |
| Permissions | Fichiers `rw-r--r--`, dossiers `rwxr-xr-x`, propriétaire `rymadinari` : seul le propriétaire peut écrire, tout le monde peut lire. Ça convient pour un poste d'apprentissage. En production, il faudrait restreindre la lecture de `raw/` (données clients). |
| Lecture contrôlée | `hdfs dfs -cat` de `store.dat` : contenu lisible, identique au local |
| Source originale conservée | Oui : fichiers du kit inchangés (dates du 15/11/2026) |
| État HDFS (`hdfs fsck /retail-lake`) | HEALTHY, 34 fichiers, 38 blocs, aucun bloc manquant ou corrompu |

### Limites de la méthode (CO-03)

- Relire le fichier pour calculer la SHA-256 prend du temps sur de gros volumes (environ 1 Go ici, ça va). Sur des téraoctets, on utiliserait plutôt le mode de somme de contrôle composite de HDFS (`dfs.checksum.combine.mode=COMPOSITE_CRC`), qui permet de comparer sans relire.
- La vérification prouve que le fichier n'a pas changé pendant le transfert. Elle ne dit rien sur la **qualité** du contenu (lignes en erreur, orphelins) : ce sera le travail du Jour 3.

## 4. Tests de validation UC-03 (§15.1)

| Test | Résultat attendu | Résultat obtenu | Preuve |
|---|---|---|---|
| Accès HDFS | Système accessible | OK : `dfsadmin -report`, interface `localhost:9870` (code 200) | `hadoop/04_verification_environnement.txt` |
| Création de répertoires | Arborescence présente | OK | `hdfs/02_arborescence_finale.txt` |
| Dépôt de fichier | Fichier présent | OK : 34 fichiers | `hdfs/depot_hdfs.log` |
| Lecture ou récupération | Fichier accessible | OK : `-cat`, `-get` + `cmp` | `hdfs/03_controles_stockage.txt` |
| Permissions | Droits cohérents | OK | `hdfs/03_controles_stockage.txt` |
| Intégrité (en plus) | Contenu identique | OK : 34/34 SHA-256 | `hdfs/verif_stockage.csv` |
| Relance sans doublon (en plus) | Rien n'est écrasé | OK : 34 « DEJA PRESENT » | `hdfs/05_relance_depot_sans_doublon.log` |
