# Retail Intelligence Platform – Jour 2 : Hadoop, HDFS et ingestion avec NiFi

TP-J2-UC03-UC04 · IPSSI Mastère Data & IA · Ryma Dinari · réalisé le 17/11/2026

- **UC-03** : HDFS installé en mode pseudo-distribué, arborescence du Data Lake créée, les 34 fichiers TPCx-BB du kit déposés dans `raw/`, et 34/34 fichiers vérifiés identiques (SHA-256).
- **UC-04** : flux NiFi GetFile → PutHDFS construit à la main dans l'interface, exécuté (fichiers `warehouse.dat` puis `ship_mode.dat` déposés et vérifiés), erreur volontaire testée, provenance relevée.
- Tout a été exécuté pour de vrai. Aucune solution de repli n'a été nécessaire.

## Versions

| Composant | Version | Emplacement |
|---|---|---|
| Ubuntu | 24.04.4 LTS | — |
| Java (Hadoop) | OpenJDK Temurin 17.0.21 | `~/opt/jdk-17` |
| Java (NiFi) | OpenJDK Temurin 21.0.13 | `~/opt/jdk-21` |
| Hadoop | 3.5.0 | `~/opt/hadoop` |
| NiFi | 2.12.0 + modules `nifi-hadoop-nar` 2.12.0 | `~/opt/nifi` |
| Python | 3.12.3 | système |

Pourquoi `~/opt` et pas `/opt` : pas de droits `sudo` sur mon poste. Le détail des écarts avec la procédure du TP est dans `docs/operations/environnement-j2.md`.

## Démarrage

```bash
cd ~/TP2/J2_Retail_Intelligence
source ingestion/scripts/env-j2.sh                 # variables + Java 17

# HDFS (sans start-dfs.sh : pas de serveur SSH sur le poste)
hdfs --daemon start namenode
hdfs --daemon start datanode
hdfs --daemon start secondarynamenode
jps                                                # NameNode, DataNode, SecondaryNameNode
hdfs dfsadmin -report

# NiFi (Java 21)
JAVA_HOME=$HOME/opt/jdk-21 ~/opt/nifi/bin/nifi.sh start
JAVA_HOME=$HOME/opt/jdk-21 ~/opt/nifi/bin/nifi.sh status
```
- Interface du NameNode : http://localhost:9870
- Interface NiFi : https://localhost:8444/nifi (certificat auto-signé à accepter). Les identifiants sont dans `~/opt/nifi-identifiants.txt`, **hors du projet**.

La toute première fois seulement (déjà fait, à ne **jamais** refaire) : `hdfs namenode -format`.

## Reproduire le TP

```bash
# UC-03 : arborescence + dépôt des 34 fichiers, puis vérification
bash ingestion/scripts/depot_hdfs.sh
bash tests/hdfs/verif_stockage.sh

# UC-04 : préparer le dossier d'entrée et une COPIE du fichier de test
mkdir -p ~/nifi-data/input ~/nifi-data/error ~/nifi-data/archive
cp ~/TP1/retail_project/data/ship_mode/ship_mode.dat ~/nifi-data/input/
```
Puis, dans l'interface NiFi (détail dans `docs/ingestion/flux-nifi.md` §3 à §5) :
1. créer un Process Group et y ajouter GetFile, PutHDFS et LogAttribute (*Add Processor*) ;
2. les régler avec les valeurs du tableau « Paramètres NiFi » ci-dessous ;
3. tirer les flèches : `success` de GetFile vers PutHDFS, `failure` de PutHDFS vers LogAttribute ;
4. démarrer PutHDFS, puis LogAttribute, puis GetFile ;
5. vérifier le dépôt :
```bash
bash tests/ingestion/verif_depot_nifi.sh ~/TP1/retail_project/data/ship_mode/ship_mode.dat
```
6. regarder la provenance : menu ☰ → *Data Provenance*, recherche sur le nom du fichier.

## Chemins HDFS

| Chemin | Contenu |
|---|---|
| `/retail-lake/raw/tpcxbb/initial/<table>/` | 23 fichiers du lot principal (dépôt manuel) |
| `/retail-lake/raw/tpcxbb/refresh/<table>/` | 11 fichiers du lot d'ajout (dépôt manuel) |
| `/retail-lake/raw/nifi/` | `ship_mode.dat` déposé par le flux NiFi |
| `/retail-lake/bronze/tpcxbb`, `silver`, `gold`, `quality`, `logs` | Vides, prévus pour le Jour 3 |

## Paramètres NiFi (non sensibles)

| Processeur | Propriété | Valeur |
|---|---|---|
| GetFile | Input Directory | `~/nifi-data/input` |
| GetFile | Keep Source File / Recurse Subdirectories | `false` / `false` |
| PutHDFS | Hadoop Configuration Resources | `~/opt/hadoop/etc/hadoop/core-site.xml,~/opt/hadoop/etc/hadoop/hdfs-site.xml` |
| PutHDFS | Directory | `/retail-lake/raw/nifi` |
| PutHDFS | Conflict Resolution Strategy | `fail` (pas d'écrasement) |
| PutHDFS | Relations | `success` terminée automatiquement, `failure` → LogAttribute |
| LogAttribute | Log Level / Relations | `warn` / `success` terminée automatiquement |
| NiFi | Port HTTPS | `8444` |

## Arrêt

Ordre : flux NiFi, puis NiFi, puis HDFS.
Dans l'interface NiFi : clic droit sur le groupe « UC04 - Flux(étape 8) » → *Stop*. Puis :
```bash
JAVA_HOME=$HOME/opt/jdk-21 ~/opt/nifi/bin/nifi.sh stop
hdfs --daemon stop secondarynamenode
hdfs --daemon stop datanode
hdfs --daemon stop namenode
```

## Contenu du dossier et livrables (§12.6)

| # | Livrable | Fichier |
|---|---|---|
| 1 | Fiche d'environnement technique | `docs/operations/environnement-j2.md` §1 |
| 2 | Fiche de découverte Hadoop et HDFS | `docs/operations/environnement-j2.md` §2 et §3 |
| 3 | Inventaire des fichiers TPCx-BB utilisés | `docs/ingestion/inventaire-sources.md` |
| 4 | Arborescence du Data Lake + schéma | `docs/architecture/architecture-data-lake.md`, `preuves/j2/hdfs/02_arborescence_finale.txt` |
| 5 | Commandes et résultats HDFS | `preuves/j2/hdfs/01_decouverte_commandes.txt`, `depot_hdfs.log`, `03_controles_stockage.txt` |
| 6 | Preuves du dépôt et des contrôles | `docs/ingestion/verification-stockage-hdfs.md`, `preuves/j2/hdfs/verif_stockage.csv` |
| 7 | Schéma du flux NiFi | `docs/ingestion/flux-nifi.md` §3 |
| 8 | Captures de la configuration NiFi | captures `preuves/j2/nifi/captures/01_flux_getfile_puthdfs.png` (flux) et `02_config_puthdfs.png` (réglages de PutHDFS), expliquées dans `flux-nifi.md` §4 et §5 |
| 9 | Preuves d'exécution et de dépôt | `preuves/j2/nifi/03_preparation_fichier_test.txt`, `04_verification_depot_hdfs.txt`, capture `01_flux_getfile_puthdfs.png` (`flux-nifi.md` §5) |
| 10 | Tableau des erreurs et corrections | `docs/operations/erreurs-et-corrections.md`, capture `05_erreur_dossier_inexistant.png` (`flux-nifi.md` §6) |
| 11 | Documentation de la provenance | `docs/ingestion/provenance.md`, captures `03_liste_provenance.png`, `04_detail_send.png`, `04b_attributs_send.png` (`flux-nifi.md` §7) |
| 12 | Script de repli | Non nécessaire : NiFi a fonctionné |
| 13 | README de reproduction | ce fichier |

Parties facultatives réalisées : CO-01 blocs et réplication (`environnement-j2.md` §3), CO-02 convention de nommage (`docs/architecture/convention-nommage.md`), CO-03 contrôle d'intégrité (`verification-stockage-hdfs.md`), CO-04 tableau de suivi et CO-05 procédure de reprise (`docs/operations/procedures-reprise.md`).

Questions de recul : `docs/questions-de-recul.md`.

Contribution individuelle : `docs/contribution-individuelle.md`.

```
J2_Retail_Intelligence/
├── docs/
│   ├── ingestion/        inventaire-sources.md, flux-nifi.md, provenance.md, verification-stockage-hdfs.md
│   ├── architecture/     architecture-data-lake.md, convention-nommage.md
│   ├── operations/       environnement-j2.md, procedures-reprise.md, erreurs-et-corrections.md
│   ├── questions-de-recul.md
│   └── contribution-individuelle.md
├── ingestion/
│   └── scripts/          env-j2.sh, depot_hdfs.sh
├── tests/
│   ├── hdfs/             verif_stockage.sh
│   └── ingestion/        verif_depot_nifi.sh
├── preuves/j2/
│   ├── hadoop/           installation, démarrage, état du cluster
│   ├── hdfs/             commandes, dépôt, vérifications, blocs
│   └── nifi/             démarrage, découverte, test de dépôt (+ captures/ de l'interface)
└── README.md
```

Les données elles-mêmes (environ 1 Go) ne sont pas dans Git : elles restent dans le kit `~/TP1/retail_project` et dans HDFS.
