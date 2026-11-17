# Questions de recul (§19)

**1. Quel est le rôle du NameNode dans HDFS ?**
C'est le sommaire de HDFS. Il connaît l'arborescence (dossiers, fichiers, droits) et sait sur quels DataNodes se trouve chaque bloc. Quand on lit un fichier, on lui demande d'abord où sont les blocs, puis on va les chercher directement sur les DataNodes.

**2. Quelle différence entre un NameNode et un DataNode ?**
Le NameNode garde les informations *sur* les fichiers (les métadonnées) ; les DataNodes gardent les données elles-mêmes, découpées en blocs. Il y a un seul NameNode actif, et plusieurs DataNodes (un seul sur mon poste).

**3. Pourquoi HDFS découpe-t-il les fichiers en blocs ?**
Pour pouvoir stocker un fichier plus gros qu'un seul disque, le répartir sur plusieurs machines et le lire en parallèle. Mon `inventory.dat` de 425 Mo est découpé en 4 blocs de 128 Mo maximum. Des gros blocs limitent aussi le nombre d'informations que le NameNode doit retenir.

**4. Quel est l'intérêt de la réplication ?**
Avoir plusieurs copies de chaque bloc sur des machines différentes. Si une machine tombe, les données restent lisibles et HDFS recrée la copie perdue. Ici la réplication est à 1 (une seule machine), donc aucune protection.

**5. Pourquoi organiser un Data Lake en plusieurs zones ?**
Pour séparer les niveaux de confiance (brut, nettoyé, prêt à l'emploi), donner des droits différents selon la zone, savoir où trouver une donnée et ce qu'on peut en attendre, et éviter que le lac devienne un fouillis.

**6. Pourquoi conserver les données sources dans Raw ?**
Pour prouver ce qu'on a reçu et pour pouvoir tout refaire si on change une règle de nettoyage. Au Jour 1, les noms de colonnes ont été déduits : si l'un d'eux est faux, on recommence depuis Raw sans redemander les fichiers.

**7. Quel est le rôle d'un FlowFile dans NiFi ?**
C'est le « colis » qui circule dans le flux : le contenu du fichier + des attributs (nom, chemin, taille, date, et ceux qu'on peut ajouter soi-même avec UpdateAttribute, comme un numéro de lot). Les processeurs lisent et modifient les FlowFiles, et la provenance garde leur historique.

**8. Quelle différence entre un Processor et une Connection ?**
Le Processor fait une action (lire un fichier, écrire dans HDFS). La Connection est le tuyau qui relie deux processeurs pour une relation donnée (`success`, `failure`) ; elle contient la file d'attente.

**9. Pourquoi la provenance est-elle importante ?**
Elle permet de savoir d'où vient chaque fichier, quand il est arrivé, ce qui lui est arrivé et où il a été déposé. En cas de chiffre bizarre ou d'erreur, on remonte jusqu'à la source. Dans mon test, elle montre que `warehouse.dat` a été lu à 16:08:09 dans `~/nifi-data/input` et envoyé dans `/retail-lake/raw/nifi` une seconde plus tard (événement SEND). Si un fichier n'a pas d'événement SEND, on sait tout de suite qu'il n'est jamais arrivé dans HDFS.

**10. Comment distinguer un échec technique d'un rejet métier ?**
- Échec technique : l'outil n'arrive pas à faire son travail (HDFS arrêté, dossier inexistant, droits refusés, fichier déjà présent). Le fichier est peut-être bon ; on corrige la cause et on relance. Exemple : la relation `failure` de PutHDFS.
- Rejet métier : le traitement marche, mais le contenu ne respecte pas une règle (fichier qui n'est pas une table attendue, mauvais nombre de colonnes, retour sans vente). Relancer ne sert à rien : il faut corriger ou écarter la donnée. Exemple : un fichier `.csv` qui arrive alors qu'on attend des tables `.dat`.
On les sépare en les envoyant vers des chemins différents : la relation `failure` vers le journal (LogAttribute) pour les échecs techniques, et un dossier de rejet pour les rejets métier (avec RouteOnAttribute, par exemple).

**11. Quels risques si un flux est relancé sans contrôle des doublons ?**
Des fichiers en double ou écrasés, donc des ventes comptées deux fois et un chiffre d'affaires faux. On peut aussi perdre une version correcte si elle est remplacée par une mauvaise. C'est pour ça que PutHDFS est réglé sur `fail` et que mon script vérifie l'existence avant d'envoyer (testé : 34 fichiers « DEJA PRESENT », rien d'écrasé).

**12. Quelles limites présente un environnement mono-nœud ?**
Pas de tolérance aux pannes (une seule copie de chaque bloc), pas de vrai calcul en parallèle, NameNode seul sans secours, capacité limitée à mon disque (37 Go libres pour HDFS), et Hadoop + NiFi qui partagent la mémoire de l'ordinateur. Il sert à apprendre, pas à la production.

**13. Pourquoi une copie locale ne constitue-t-elle pas une preuve de dépôt HDFS ?**
Une copie dans un dossier local ne passe ni par le NameNode ni par les DataNodes : elle ne montre pas que le fichier est dans HDFS, découpé en blocs, avec ses droits HDFS. La preuve, c'est une commande HDFS (`hdfs dfs -ls`, `-stat`, `fsck`) ou un événement SEND vers `hdfs://...`, plus une comparaison de contenu avec l'original.

**14. Quelles informations conserver pour reproduire une ingestion ?**
Les versions des outils (Java, Hadoop, NiFi) ; la configuration (`core-site.xml`, `hdfs-site.xml`, propriétés des processeurs ou export du flux) ; les chemins source et destination ; l'identité du fichier (nom, taille, SHA-256, lot) ; la date et l'utilisateur ; les commandes ou scripts lancés ; les erreurs rencontrées et leur correction. Tout ça est dans ce dossier (README, `docs/`, `ingestion/`, `preuves/`).
