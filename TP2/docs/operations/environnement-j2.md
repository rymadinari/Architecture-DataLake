# Fiche d'environnement technique et découverte de Hadoop (Jour 2)

Relevés faits le 17/11/2026 sur mon ordinateur portable. Les sorties complètes des commandes sont dans `preuves/j2/hadoop/` et `preuves/j2/nifi/`.

## 1. Environnement réellement utilisé (§7.3)

| Élément | Valeur relevée | Preuve |
|---|---|---|
| Système | Ubuntu 24.04.4 LTS, 12 cœurs, 15 Go de RAM | `preuves/j2/hadoop/04_verification_environnement.txt` |
| Java pour Hadoop | OpenJDK 17.0.21 (Temurin) | idem |
| Java pour NiFi | OpenJDK 21.0.13 (Temurin) | `preuves/j2/nifi/01_demarrage_nifi.txt` |
| Hadoop | 3.5.0 (version du TP) | `04_verification_environnement.txt` |
| NiFi | 2.12.0 (version du TP) | `preuves/j2/nifi/02_decouverte_nifi.txt` |
| Python | 3.12.3 | — |
| Chemins d'installation | `~/opt/jdk-17`, `~/opt/jdk-21`, `~/opt/hadoop`, `~/opt/nifi` | — |
| Configuration Hadoop | `~/opt/hadoop/etc/hadoop/` (`core-site.xml`, `hdfs-site.xml`, `hadoop-env.sh`) | — |
| Données HDFS sur le disque | `~/hadoop-data/namenode` et `~/hadoop-data/datanode` | — |
| Dossiers NiFi locaux | `~/nifi-data/input`, `~/nifi-data/error`, `~/nifi-data/archive` | — |
| Services actifs | NameNode, DataNode, SecondaryNameNode (vus avec `jps`), NiFi | `03_demarrage_daemons_jps.txt` |
| Ports | HDFS `9000`, interface NameNode `9870`, DataNode `9866`, NiFi `8444` (HTTPS) | — |

### Écarts avec la procédure du TP, et pourquoi

| Procédure du TP | Ce que j'ai fait | Raison |
|---|---|---|
| `sudo apt install openjdk-17-jdk openjdk-21-jdk` | Téléchargement des JDK Temurin 17 et 21 (archives officielles Adoptium) dans `~/opt` | Pas de droits `sudo` sur mon poste. |
| Installation dans `/opt/hadoop` et `/opt/nifi` | Installation dans `~/opt/hadoop` et `~/opt/nifi` | Même raison. Les sommes de contrôle SHA-512 des archives Apache ont été vérifiées. |
| Variables ajoutées dans `~/.bashrc` | Variables dans `ingestion/scripts/env-j2.sh`, à charger avec `source` | Pour ne pas modifier ma configuration personnelle. |
| `start-dfs.sh` | `hdfs --daemon start namenode`, puis `datanode`, puis `secondarynamenode` | `start-dfs.sh` passe par SSH, et il n'y a pas de serveur SSH sur mon poste (erreur dans `02_start-dfs_erreur_ssh.txt`). |
| NiFi sur le port 8443 | NiFi sur le port 8444 | Le port 8443 est déjà utilisé par un autre service de mon poste. |
| Dossiers `/data/nifi/...` | Dossiers `~/nifi-data/...` | Pas de droits pour créer `/data`. |
| PutHDFS directement disponible | Ajout des modules officiels `nifi-hadoop-nar` et `nifi-hadoop-libraries-nar` 2.12.0 (Maven Central, SHA-1 vérifiés) dans `~/opt/nifi/extensions/` | Ils ne sont plus inclus dans le téléchargement standard de NiFi 2.12.0 : sans eux, PutHDFS n'existe pas. |

Contraintes réseau et sécurité : tout est en local (`localhost`). NiFi est en HTTPS avec un certificat auto-signé et un seul utilisateur. Le mot de passe est rangé dans `~/opt/nifi-identifiants.txt` (droits `600`), **en dehors du projet**, et n'est jamais écrit dans Git.

## 2. Hadoop et HDFS (étape 1)

### Ce que j'ai observé

- `hadoop version` → **Hadoop 3.5.0**.
- `jps` → 3 processus Java : **NameNode**, **DataNode**, **SecondaryNameNode**.
- `hdfs dfsadmin -report` → **1 DataNode vivant** (`127.0.0.1:9866`), capacité 136 Go, 37 Go libres pour HDFS, aucun bloc manquant ou corrompu.
- Mode sans écriture (*safe mode*) : désactivé.
- Interface web du NameNode : `http://localhost:9870`, répond (code 200).
- Configuration : `fs.defaultFS = hdfs://localhost:9000`, réplication = 1, taille de bloc = 134 217 728 octets (128 Mo).
- Erreur de démarrage : seulement celle de `start-dfs.sh` (SSH absent), contournée en démarrant chaque service à la main.

### Rôle des composants

| Composant | Rôle, en simple |
|---|---|
| **NameNode** | Le « sommaire » de HDFS. Il sait quels fichiers existent, dans quels dossiers, avec quels droits, et où sont rangés leurs morceaux (blocs). Il ne stocke pas les données elles-mêmes. S'il est arrêté, plus rien n'est accessible. |
| **DataNode** | Le « disque » de HDFS. Il stocke les blocs de données et les envoie quand on les lit. Il prévient régulièrement le NameNode qu'il est vivant et lui donne la liste de ses blocs. |
| **SecondaryNameNode** | Aide le NameNode en fusionnant régulièrement son journal de modifications avec sa sauvegarde. Ce n'est **pas** un NameNode de secours. |

### Type d'environnement

C'est un **déploiement local mono-nœud** (pseudo-distribué) : les trois services tournent sur la même machine, avec un seul DataNode et une réplication à 1. C'est un environnement pour apprendre. Ce n'est pas un cluster de production : si le disque ou la machine tombe, les données sont perdues, car il n'y a qu'une copie de chaque bloc.

Le formatage du NameNode (`hdfs namenode -format`) n'a été fait **qu'une seule fois**, à l'installation, sur un dossier vide (`preuves/j2/hadoop/01_format_namenode.txt`). Il ne doit jamais être relancé : il effacerait tout le contenu de HDFS.

## 3. Blocs et réplication (activité complémentaire CO-01)

Preuve : `preuves/j2/hdfs/04_blocs_fsck.txt` (`hdfs fsck ... -files -blocks -locations`).

- Le plus gros fichier, `inventory.dat` (424 943 678 octets), est découpé en **4 blocs** : 3 blocs pleins de 128 Mo, plus un dernier bloc de 22 290 494 octets. Le dernier bloc ne prend que la place réellement utilisée.
- Chaque bloc a **1 copie** (`Live_repl=1`), sur le seul DataNode (`127.0.0.1:9866`).
- Sur tout `/retail-lake` : 34 fichiers, 38 blocs, état **HEALTHY** (aucun bloc manquant, corrompu ou sous-répliqué).

| Question | Réponse |
|---|---|
| Rôle des blocs | Découper un gros fichier en morceaux de taille fixe, pour le répartir sur plusieurs machines et le lire en parallèle (plusieurs machines lisent chacune un morceau). |
| Principe de la réplication | Chaque bloc est copié sur plusieurs DataNodes (3 par défaut en production). Si une machine tombe, une autre copie existe. |
| Lien blocs / DataNodes | Le NameNode garde la liste « bloc → DataNodes qui l'ont ». Les DataNodes stockent physiquement les blocs. |
| Si un nœud tombe | En production : le NameNode voit qu'il ne répond plus et recopie ses blocs ailleurs à partir des autres copies. Ici : avec un seul nœud et une seule copie, les fichiers deviennent illisibles. |
| Limites du mono-nœud | Pas de tolérance aux pannes, pas de vrai calcul en parallèle, NameNode seul (pas de haute disponibilité), capacité limitée au disque de l'ordinateur. |

Je n'ai pas modifié les paramètres de réplication ni de stockage.

## 4. Ordre de démarrage et d'arrêt utilisé

Démarrage :
```bash
source ingestion/scripts/env-j2.sh            # Java 17 pour Hadoop
hdfs --daemon start namenode
hdfs --daemon start datanode
hdfs --daemon start secondarynamenode
jps && hdfs dfsadmin -report

export JAVA_HOME=$HOME/opt/jdk-21             # Java 21 pour NiFi
~/opt/nifi/bin/nifi.sh start
~/opt/nifi/bin/nifi.sh status
```

Arrêt (flux NiFi, puis NiFi, puis HDFS) :
D'abord, dans l'interface NiFi : clic droit sur le groupe « UC04 - Flux(étape 8) » → *Stop*.
```bash
JAVA_HOME=$HOME/opt/jdk-21 ~/opt/nifi/bin/nifi.sh stop
hdfs --daemon stop secondarynamenode
hdfs --daemon stop datanode
hdfs --daemon stop namenode
```
