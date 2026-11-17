# Provenance des données (UC-04, étape 11)

Preuves : captures `preuves/j2/nifi/captures/03_liste_provenance.png`, `04_detail_send.png` et `04b_attributs_send.png`, relevées dans l'interface NiFi (menu ☰ → *Data Provenance*, recherche sur `warehouse.dat`, le fichier du premier test de l'étape 9).

## 1. Événements du FlowFile déposé

| Information | Valeur |
|---|---|
| Identifiant du FlowFile | `2174df4f-0c23-413b-8169-f6e8e6a717bd` |
| Nom | `warehouse.dat` |
| Taille | 584 octets |
| Fichier d'origine | `/home/rymadinari/nifi-data/input/` (copie de `retail_project/data/warehouse/warehouse.dat`) |
| Destination | `/retail-lake/raw/nifi` |
| Date du traitement | 17/11/2026, 16:08:09 |

| Heure | Événement | Processeur | Ce que ça veut dire |
|---|---|---|---|
| 16:08:09.036 | **RECEIVE** | GetFile | NiFi a reçu le fichier depuis `~/nifi-data/input`. |
| 16:08:10.098 | **SEND** | PutHDFS | Le fichier a été envoyé dans HDFS (`/retail-lake/raw/nifi`). L'envoi a duré 1,025 seconde. |
| 16:08:10.100 | ATTRIBUTES_MODIFIED | PutHDFS | PutHDFS a ajouté le chemin HDFS dans les attributs. |
| 16:08:10.100 | **DROP** | PutHDFS | Fin du parcours (relation `success` terminée automatiquement). |

Le fichier a mis environ une seconde entre la lecture et le dépôt dans HDFS.

## 2. Comment ça permet de reconstituer le parcours

- Avec le **nom du fichier** ou son **identifiant**, on retrouve tous ses événements, dans l'ordre.
- **RECEIVE** dit d'où vient le fichier (chemin local exact) et quand il est arrivé.
- **SEND** dit où il a été écrit (chemin HDFS complet) et quand.
- L'**absence** d'un SEND montre qu'un fichier n'est jamais arrivé à destination : il faut alors chercher le message d'erreur (journal ou LogAttribute).
- Les **attributs** (nom, chemin d'origine, chemin HDFS, dates du fichier) relient chaque fichier de HDFS à son origine.
- Avec l'empreinte SHA-256 calculée avant et après (`preuves/j2/nifi/04_verification_depot_hdfs.txt`, pour le deuxième test avec `ship_mode.dat`), on prouve que le contenu n'a pas changé pendant le trajet.

## 3. Provenance du dépôt manuel (UC-03)

Le dépôt avec `hdfs dfs -put` n'a pas d'historique automatique comme NiFi. Sa provenance est gardée par :

- le chemin HDFS (`raw/tpcxbb/<lot>/<table>/<fichier d'origine>`) ;
- le journal du script `preuves/j2/hdfs/depot_hdfs.log` (date, commande pour chaque fichier, utilisateur) ;
- l'empreinte SHA-256 de chaque fichier, local et HDFS (`preuves/j2/hdfs/verif_stockage.csv`) ;
- le propriétaire et la date de chaque fichier dans HDFS (`hdfs dfs -ls`).

## 4. Limites

- La provenance NiFi est gardée sur le disque de NiFi pendant une durée limitée (réglage par défaut : 30 jours ou 10 Go). Pour une conservation longue, il faudrait l'exporter.
- Elle s'arrête à HDFS : ce que deviendra le fichier au Jour 3 (Spark) devra être tracé autrement (colonnes `_batch_id`, `_source_file` prévues au Jour 1).
