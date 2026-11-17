# Tableau des erreurs et des corrections (Jour 2)

Toutes ces erreurs ont été rencontrées pour de vrai. La dernière a été provoquée volontairement pour l'étape 10.

| # | Étape | Erreur constatée | Cause | Correction | Preuve |
|---|---|---|---|---|---|
| 1 | Installation | `sudo` demande un mot de passe : impossible d'installer avec `apt` ni d'écrire dans `/opt` ou `/data` | Pas de droits administrateur sur le poste | Installation dans mon dossier personnel (`~/opt`), avec les archives officielles (JDK Temurin, Apache Hadoop, Apache NiFi), sommes de contrôle vérifiées | `docs/operations/environnement-j2.md` |
| 2 | Démarrage HDFS | `start-dfs.sh` → `ssh: connect to host localhost port 22: Connection refused` | `start-dfs.sh` lance les services par SSH, et il n'y a pas de serveur SSH sur le poste | Démarrage de chaque service sans SSH : `hdfs --daemon start namenode / datanode / secondarynamenode` | `preuves/j2/hadoop/02_start-dfs_erreur_ssh.txt`, `03_demarrage_daemons_jps.txt` |
| 3 | Découverte HDFS | `ls: '/retail-lake': No such file or directory` | Le dossier n'existait pas encore | `hdfs dfs -mkdir -p /retail-lake` | `preuves/j2/hdfs/01_decouverte_commandes.txt` |
| 4 | Contrôle stockage | Accents remplacés par `??` dans la sortie de `hdfs dfs -stat` | Le format de `-stat` n'accepte pas bien les accents | Format réécrit sans accents | `preuves/j2/hdfs/03_controles_stockage.txt` |
| 5 | Installation NiFi | Port 8443 déjà utilisé | Un autre service du poste écoute déjà sur 8443 | `nifi.web.https.port=8444` dans `nifi.properties` | `preuves/j2/nifi/01_demarrage_nifi.txt` |
| 6 | Découverte NiFi | Processeur **PutHDFS absent** de NiFi 2.12.0 | Les modules Hadoop ne sont plus inclus dans le téléchargement standard de NiFi 2 | Ajout des modules officiels `nifi-hadoop-nar` et `nifi-hadoop-libraries-nar` 2.12.0 (Maven Central, SHA-1 vérifiés) dans `~/opt/nifi/extensions/` | `preuves/j2/nifi/02_decouverte_nifi.txt` |
| 7 | Démarrage NiFi | La commande `nifi.sh start | tail` ne rendait pas la main | La sortie reste ouverte par le processus NiFi | Vérification à part avec `nifi.sh status` et le journal (`Started Server`) | `preuves/j2/nifi/01_demarrage_nifi.txt` |
| 8 | Construction du flux | Processeurs avec un ⚠️ juste après leur ajout | Relations `success` / `failure` pas encore reliées | Création des flèches à la souris, puis les trois processeurs deviennent valides | `docs/ingestion/flux-nifi.md` §3 |
| 9 | Étape 10 (volontaire) | GetFile invalide : *Directory does not exist* | Dossier d'entrée inexistant | Remise du bon dossier `/home/rymadinari/nifi-data/input` | capture `preuves/j2/nifi/captures/05_erreur_dossier_inexistant.png` |
