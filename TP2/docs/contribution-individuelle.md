# Contribution individuelle — Ryma Dinari

Retail Intelligence Platform · TP Jour 2 · IPSSI · Mastère Développement, Data & IA

Mode de travail : comme au Jour 1, j'ai réalisé le projet seule. J'ai donc pris en charge toutes les parties : l'installation, HDFS, NiFi et la documentation.

## 1. Ma mise en place de l'environnement

Je n'ai pas les droits administrateur (`sudo`) sur mon poste. Je ne pouvais donc pas suivre la procédure du TP telle quelle, qui installe tout dans `/opt`. J'ai installé Java 17, Java 21, Hadoop 3.5.0 et NiFi 2.12.0 dans mon dossier personnel (`~/opt`), à partir des archives officielles, en vérifiant leurs empreintes.

J'ai dû contourner trois problèmes :
- **pas de serveur SSH** sur le poste, donc `start-dfs.sh` ne marchait pas : j'ai démarré chaque service HDFS un par un avec `hdfs --daemon start` ;
- **le port 8443 était déjà pris** : j'ai mis NiFi sur le port 8444 ;
- **PutHDFS n'existe pas** dans le téléchargement standard de NiFi 2 : j'ai ajouté les deux modules Hadoop officiels d'Apache.

## 2. Ce que j'ai fait sur HDFS (UC-03)

J'ai créé l'arborescence du Data Lake (`raw`, `bronze`, `silver`, `gold`, `quality`, `logs`) en suivant celle proposée par l'énoncé. J'ai expliqué le lien avec l'architecture du Jour 1 : la zone que j'appelais Bronze au Jour 1 correspond maintenant à Raw.

J'ai déposé dans `raw/` les 34 fichiers TPCx-BB du kit (23 du lot principal, 11 du lot refresh), avec les commandes `hdfs dfs -put` regroupées dans un petit script. Ensuite, j'ai vérifié chaque fichier : présence, taille, droits, et surtout l'empreinte SHA-256, qui est identique entre le fichier local et le fichier dans HDFS pour les 34 fichiers. J'ai aussi relancé le dépôt pour vérifier que rien n'était écrasé.

## 3. Ce que j'ai fait sur NiFi (UC-04)

J'ai construit le flux à la main dans l'interface de NiFi : ajout de GetFile, PutHDFS et LogAttribute, réglage de chaque processeur, puis flèches `success` et `failure` tirées à la souris. J'ai choisi la stratégie `fail` sur PutHDFS pour qu'un fichier existant ne soit jamais écrasé sans que je le sache.

J'ai testé le flux deux fois : avec `warehouse.dat`, puis avec `ship_mode.dat` sur une destination vide. Les deux fois, le fichier est arrivé dans HDFS identique à l'original. J'ai ensuite provoqué une erreur volontaire (dossier d'entrée qui n'existe pas), je l'ai observée, puis corrigée. Enfin, j'ai relevé la provenance du fichier dans NiFi pour montrer qu'on peut retrouver tout son parcours.

## 4. Les parties facultatives

J'ai aussi fait les cinq activités complémentaires : l'étude des blocs et de la réplication (CO-01), une convention de nommage des dossiers (CO-02), le contrôle d'intégrité par empreintes (CO-03), un tableau de suivi du flux (CO-04) et une procédure de reprise après échec (CO-05).

## 5. Les outils qui m'ont aidée

Pour les commandes répétitives (déposer et vérifier 34 fichiers), j'ai utilisé de petits scripts shell, qui sont dans le dossier `ingestion/scripts` et `tests/`. Je me suis aussi aidée d'un assistant IA pour préparer certaines commandes et pour la mise en forme de la documentation. J'ai vérifié moi-même chaque résultat dans le terminal et dans NiFi.

## 6. Ce que je retiens / difficultés rencontrées

Ce que je retiens surtout, c'est qu'un dépôt n'est pas prouvé tant qu'on ne l'a pas vérifié : voir le fichier dans HDFS ne suffit pas, il faut comparer son contenu avec l'original. J'ai aussi compris l'intérêt de NiFi par rapport à une commande à la main : le fichier part tout seul, et chaque étape est gardée dans l'historique.

La principale difficulté a été l'environnement : sans droits administrateur, j'ai dû adapter presque chaque étape de l'installation, et bien noter chaque écart pour que le TP reste reproductible.
