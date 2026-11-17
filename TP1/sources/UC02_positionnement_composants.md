# UC-02 — Positionnement des composants technologiques

Retail Intelligence Platform · Jour 1 · Livrable 4/6 de l'UC-02

## 1. Tableau des composants

Les statuts sont repris **exactement** du référentiel du parcours (énoncé, étape D). Aucun outil facultatif n'est présenté comme obligatoire.

| Outil | Statut (référentiel) | Étape de l'architecture | Rôle dans Retail Intelligence | Quand |
|---|---|---|---|---|
| **Linux / Ubuntu** | Obligatoire | Système de base | Système sur lequel tournent HDFS, NiFi, Spark et Python en local. | Jour 2 |
| **Python** | Obligatoire | Exploration, contrôles, scripts | Analyse du kit (déjà fait au Jour 1 avec `scripts/profilage.py`), vérification des fichiers avant chargement. | Jour 1 (fait), puis tout le parcours |
| **Hadoop / HDFS** | Obligatoire | Stockage des zones Bronze, Silver, Gold et quarantaine | Stocke les données sur plusieurs machines : `/datalake/bronze`, `/silver`, `/gold`, `/quarantine`, avec des droits par dossier. | Jour 2 |
| **Apache NiFi** | Obligatoire | Réception et enchaînement des étapes | Repère les nouveaux fichiers, calcule leur empreinte, note leur origine, les copie dans HDFS et lance les traitements. | Jour 2 |
| **Apache Spark / PySpark** | Obligatoire | Nettoyage (Bronze → Silver) et organisation (Silver → Gold) | Ajoute les noms de colonnes, corrige les types, contrôle la qualité, met de côté les erreurs, rend les clients anonymes, construit l'étoile et les totaux. | Jour 3 |
| **Parquet** | Format de référence | Silver et Gold | Format de fichier qui range les données par colonne, compressé et rangé par date. | Jour 3 |
| **HBase** | Facultatif | Approfondissement NoSQL (hors socle) | Pourrait servir à retrouver très vite un client ou le dernier stock d'un produit. **Pas nécessaire** à l'architecture. | UC-05 facultatif (Jour 3) |
| **PDGF** | Selon le kit | Avant tout (création des données) | Outil qui génère les données TPCx-BB. Le kit est **déjà généré** et l'outil n'est ni fourni ni documenté : il n'est pas utilisé. | Non prévu |
| **Delta Lake** | Facultatif | Évolution Lakehouse de Silver et Gold (hors socle) | Ajouterait les modifications sûres, l'historique des versions, la mise à jour simple des retours tardifs et la suppression de données personnelles. **Pas nécessaire** au socle. | Approfondissement Jour 3 |
| **ADLS Gen2** | Objectif obligatoire | Stockage dans le cloud | Remplace HDFS sur Azure, avec des espaces `bronze`, `silver`, `gold` et `quarantine`. | Jour 4 |
| **Azure Data Factory** | Présentation / étude | Réception et enchaînement dans le cloud | Équivalent de NiFi sur Azure, pour copier les fichiers et enchaîner les étapes. Pas d'installation demandée. | Étude Jour 4 |
| **Azure Synapse** | Présentation / étude | Traitement et requêtes dans le cloud | Permet de lancer le même code PySpark sur Azure et de faire du SQL sur la zone Gold. Pas d'installation demandée. | Étude Jour 4 |
| DuckDB *(outil d'appoint)* | Hors référentiel | Exploration locale (Jour 1 seulement) | Utilisé pour analyser rapidement le kit sur mon ordinateur. Ne fait pas partie de l'architecture. | Jour 1 (fait) |

## 2. Vue par étape

<div class="diag">
<div class="col"><div class="t">Réception</div><div class="box ok"><b>NiFi</b> obligatoire</div><div class="box">Python (contrôles avant)</div><div class="box part">ADF (étude cloud)</div></div>
<div class="col"><div class="t">Stockage</div><div class="box ok"><b>HDFS</b> obligatoire</div><div class="box ok"><b>Parquet</b> référence</div><div class="box ok"><b>ADLS Gen2</b> objectif cloud</div><div class="box wish">HBase (facultatif)</div></div>
<div class="col"><div class="t">Traitement</div><div class="box ok"><b>Spark / PySpark</b> obligatoire</div><div class="box ok"><b>Python</b> obligatoire</div><div class="box part">Synapse (étude cloud)</div><div class="box wish">Delta Lake (facultatif)</div></div>
<div class="col"><div class="t">Base</div><div class="box ok"><b>Linux / Ubuntu</b> obligatoire</div><div class="box wish">PDGF (selon le kit : non utilisé)</div></div>
</div>
<p class="legend">Vert : obligatoire · orange : étudié ou présenté · rouge en pointillé : facultatif ou non utilisé.</p>

## 3. Confusions à éviter

- **Stocker n'est pas traiter** : HDFS et ADLS Gen2 stockent ; Spark et Synapse traitent ; NiFi et ADF déplacent les fichiers et enchaînent les étapes.
- **Un format n'est pas une table** : Parquet est un format de fichier ; Delta Lake ajoute une couche de gestion par-dessus.
- **Étudier n'est pas installer** : ADF et Synapse sont décrits, pas installés. La partie Azure est un plan (voir `UC02_local_vers_azure.pdf`).

## 4. Question de recul

**Quels outils sont indispensables au socle, et lesquels sont des approfondissements ?** Indispensables : Linux/Ubuntu, Python, Hadoop/HDFS, NiFi, Spark/PySpark, le format Parquet et l'objectif ADLS Gen2. Étudiés sans installation : Azure Data Factory et Synapse. Facultatifs : HBase et Delta Lake. PDGF dépend du kit et n'est pas utilisé ici, car les données sont déjà générées.
