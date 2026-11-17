# Procédure de reprise après échec d'ingestion et supervision (CO-04, CO-05)

## 1. Comment voir qu'un traitement a échoué

| Où regarder | Ce qui indique un échec |
|---|---|
| Canvas NiFi | Un processeur avec une icône rouge (invalide) ou un carré rouge avec un bulletin (avertissement ou erreur en haut à droite). |
| File `failure` (PutHDFS → LogAttribute) | Un FlowFile en attente ou déjà passé dans cette file. En temps normal, elle est toujours à 0. |
| Journal `~/opt/nifi/logs/nifi-app.log` | Lignes `WARN` ou `ERROR` de PutHDFS ; bloc écrit par LogAttribute avec les attributs du fichier en échec. |
| Provenance | Un FlowFile qui a un RECEIVE mais **pas de SEND** n'est jamais arrivé dans HDFS. |
| HDFS | `hdfs dfs -ls /retail-lake/raw/nifi` : le fichier attendu est absent, ou sa taille ne correspond pas. |

## 2. Retrouver le fichier source

- Le nom et le chemin d'origine sont dans les attributs du FlowFile en échec : `filename`, `absolute.path` (visibles dans la provenance ou dans le bloc LogAttribute du journal).
- La copie de travail a été retirée du dossier d'entrée par GetFile (`Keep Source File=false`), mais **l'original est toujours dans le kit** : `~/TP1/retail_project/<lot>/<table>/<fichier>`. On ne met jamais l'unique exemplaire d'un fichier dans le dossier d'entrée NiFi.

## 3. Éviter les doublons

- PutHDFS est réglé avec `Conflict Resolution Strategy = fail` : il **refuse d'écraser** un fichier existant : le FlowFile part dans la file `failure`, puis LogAttribute note l'échec dans le journal.
- Le script de dépôt manuel vérifie avec `hdfs dfs -test -e` si le fichier existe avant de l'envoyer. Testé en le relançant : 34 fichiers « DEJA PRESENT », 0 envoi (`preuves/j2/hdfs/05_relance_depot_sans_doublon.log`).
- Avant de relancer, comparer l'empreinte : si le fichier HDFS a la même SHA-256 que l'original, il n'y a **rien à refaire**.
- Ne pas relancer le flux plusieurs fois sans avoir compris le premier résultat.

## 4. Relancer le traitement

Cas 1 : **le fichier n'est pas dans HDFS** (erreur de configuration, HDFS arrêté…)
1. Lire le message d'erreur (bulletin ou journal) et corriger la cause : HDFS démarré (`jps`), bon chemin, processeur valide.
2. Si le FlowFile est encore dans la file `failure` : le renvoyer vers PutHDFS (dans l'interface, déplacer la connexion ou relier temporairement `failure` à PutHDFS).
3. Sinon : remettre une **copie** de l'original dans `~/nifi-data/input`.

Cas 2 : **un fichier du même nom existe déjà dans HDFS**
1. Comparer les empreintes (`bash tests/ingestion/verif_depot_nifi.sh <original>`).
2. Si elles sont identiques : c'est un doublon, ne rien faire. Vider la file `failure` après avoir noté le cas.
3. Si elles sont différentes (nouvelle version du fichier) : ne pas écraser. Déposer la nouvelle version sous un autre nom ou dans un dossier daté (voir la convention de nommage, `docs/architecture/convention-nommage.md`), et noter le changement.

Cas 3 : **dépôt manuel interrompu**
- Relancer `bash ingestion/scripts/depot_hdfs.sh` : les fichiers déjà présents sont sautés.
- Attention : un fichier coupé en cours d'envoi peut exister avec une taille fausse. C'est pour ça qu'on lance ensuite `tests/hdfs/verif_stockage.sh`. Pour un fichier en « ECART », on supprime seulement ce fichier (`hdfs dfs -rm <chemin>`), puis on relance le dépôt.

## 5. Vérifier le résultat

```bash
hdfs dfs -ls -h /retail-lake/raw/nifi
bash tests/ingestion/verif_depot_nifi.sh ~/TP1/retail_project/data/ship_mode/ship_mode.dat
bash tests/hdfs/verif_stockage.sh          # pour le dépôt manuel complet
```
Puis, dans NiFi : menu ☰ → *Data Provenance*, recherche sur le nom du fichier.
Le traitement est réussi quand : le fichier est présent, la taille et la SHA-256 sont identiques à l'original, la provenance montre un SEND, et la file `failure` est vide.

## 6. Tableau de suivi du flux (CO-04)

À remplir à chaque exécution. Exemple avec les valeurs réelles du 17/11/2026 :

| Date / heure | Flux | Fichier | Lu par GetFile | Déposé (SEND) | En échec | File en attente | Vérif. SHA-256 | Remarque |
|---|---|---|---|---|---|---|---|---|
| 17/11 16:08 | UC04 - Flux(étape 8) | `warehouse.dat` (584 o) | oui | oui | 0 | 0 | identique | Premier test réussi (fichier retiré ensuite pour refaire le test) |
| 17/11 16:11 | UC04 - Flux(étape 8) | — | non | non | 0 | 0 | — | Erreur volontaire : GetFile invalide (dossier inexistant), corrigé tout de suite |
| 17/11 16:30 | UC04 - Flux(étape 8) | `ship_mode.dat` (1 220 o) | oui | oui | 0 | 0 | identique | Test refait sur une destination vide, `raw/nifi/ship_mode.dat` |

Indicateurs à suivre et où les trouver :

| Indicateur | Où |
|---|---|
| Nombre de FlowFiles entrés / sortis par processeur | Compteurs sur chaque processeur (5 dernières minutes) |
| Taille des files d'attente | Sur chaque connexion |
| État des processeurs (Running, Stopped, Invalid) | Canvas, barre d'état en haut |
| Avertissements et erreurs | Bulletins (carré rouge), menu ☰ → *Bulletin Board* |
| Parcours d'un fichier | Menu ☰ → *Data Provenance* |
| Journaux techniques | `~/opt/nifi/logs/nifi-app.log` |
