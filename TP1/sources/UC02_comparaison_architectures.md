# UC-02 — Comparaison Data Warehouse / Data Lake / Lakehouse

Retail Intelligence Platform · Jour 1 · Livrable 1/6 de l'UC-02

## 1. Contraintes du projet (tirées de l'UC-01)

| Contrainte | Ce que j'ai constaté | Ce que l'architecture doit permettre |
|---|---|---|
| Formats | 34 fichiers texte séparés par `|`, sans en-tête, au format Windows ; 2 petits rapports CSV ; du texte libre dans les avis | Recevoir des fichiers bruts ; garder les noms de colonnes dans un fichier à part ; gérer du texte libre. |
| Volumes | Environ 1 Go au total ; 23,3 millions de lignes pour le stock, 6,8 millions pour les clics, environ 0,67 million par table de ventes | Le volume reste modeste, mais il justifie un format de stockage efficace et des traitements répartis sur plusieurs machines, comme prévu dans le parcours. |
| Diversité | 23 tables, 11 domaines. Tous les fichiers sont des tableaux, donc des données **structurées** (même les clics). Seul le texte des avis (`pr_review_content`) est libre, donc **non structuré**. Des fichiers JSON (**semi-structurés**) pourraient être ajoutés plus tard. | Stocker des données de natures différentes sans tout forcer dans un seul modèle dès le départ. |
| Historique | 5 ans de ventes ; un lot de mise à jour (`data_refresh/`) ; des retours jusqu'à 2 ans après la vente | Garder chaque lot reçu ; pouvoir ajouter des données au fil de l'eau ; pouvoir recalculer les périodes passées. |
| Qualité | 14 anomalies trouvées (A1 à A14), des orphelins, des colonnes inutilisables | Une étape de contrôle avec des règles claires, un endroit où mettre de côté les lignes en erreur, et une trace de ce qui a été rejeté. |
| Usages | Tableaux de bord avec les indicateurs K1 à K12, analyses à la demande, analyse des avis et des clics | Des données organisées pour les tableaux de bord, plus un accès aux données détaillées pour explorer. |
| Sécurité | Données personnelles dans `customer` | Des accès différents selon le rôle ; données personnelles rendues anonymes avant d'être partagées. |
| Évolution | Autres sources prévues (météo, événements, logistique) ; passage sur le cloud Azure au Jour 4 | Une architecture facile à faire grandir et à transposer sur Azure (ADLS Gen2). |

## 2. Les trois approches

| Critère | Data Warehouse (entrepôt de données) | Data Lake (lac de données) organisé en zones | Data Lakehouse |
|---|---|---|---|
| **Principe** | Une base de données faite pour l'analyse. Les données sont nettoyées et transformées **avant** d'être chargées, dans un modèle défini à l'avance. | Un grand espace de stockage de fichiers, peu coûteux. Les données y sont déposées telles quelles, puis améliorées étape par étape (zones). | Un lac de données auquel on ajoute une couche qui le fait fonctionner comme une vraie base : modifications sûres, structure imposée, historique des versions (outils : Delta Lake, Iceberg, Hudi). |
| **Données adaptées** | Données structurées, propres et stables. | Tout type de données : structurées, semi-structurées (JSON, journaux), non structurées (texte, images). | Tout type, avec une gestion de tables pour les données structurées et semi-structurées. |
| **Avantages** | Requêtes rapides pour les tableaux de bord, chiffres cohérents, SQL classique, outils de reporting connus, gouvernance éprouvée. | Stockage peu cher, grande souplesse, conservation des données brutes (on peut tout refaire), passe facilement à grande échelle, adapté à Spark. | Réunit la souplesse du lac et la fiabilité de l'entrepôt ; une seule copie des données ; on peut revenir à une version passée ; on peut modifier ou supprimer des lignes (utile pour le RGPD). |
| **Limites** | Plus cher ; peu souple quand une nouvelle source arrive ; les données brutes sont perdues si on ne les garde pas ailleurs ; mal adapté au texte et aux journaux. | Sans règles, il devient vite un fouillis (« marécage de données ») ; pas de modification sûre des données ; structure non vérifiée ; moins rapide pour les tableaux de bord s'il n'est pas organisé. | Technologie plus récente et plus difficile à maîtriser ; dépend d'un format de table ; demande des compétences Spark. |
| **Usages** | Reporting, tableaux de bord, analyses financières. | Exploration, data science, archivage, alimentation d'un entrepôt. | Tableaux de bord et data science sur les mêmes données, ajouts réguliers de données, historique détaillé. |
| **Gouvernance** | Tout est centralisé et contrôlé à l'entrée : plus simple à gouverner, mais lent à faire évoluer. | Il faut tout mettre en place soi-même : catalogue, règles de nommage, contrôles par zone, droits d'accès. Sinon les données deviennent introuvables ou peu fiables. | Mêmes besoins que le lac, mais le format de table impose la structure et garde la trace des versions. |
| **Intérêt pour Retail Intelligence** | Bien pour les indicateurs (K1 à K9 utilisent des données structurées). Insuffisant seul : il gère mal le texte des avis, les futurs fichiers JSON, la conservation des lots bruts, la mise de côté des anomalies et les 30 millions de lignes de stock et de clics. | Bien : il garde les lots reçus, accueille les clics et les avis, et utilise HDFS, NiFi et Spark, qui sont obligatoires dans le parcours. Il faut le compléter par une zone organisée pour les tableaux de bord. | Très bien sur le principe, mais Delta Lake est **facultatif** dans le parcours : on ne peut pas en faire une obligation. Je le garde comme évolution possible. |

## 3. Comparaison et choix

| Critère important pour le projet | Data Warehouse | Data Lake en zones | Lakehouse |
|---|:---:|:---:|:---:|
| Accepte tous les types de données du kit | ◐ | ● | ● |
| Garde les données brutes et permet de tout refaire | ○ | ● | ● |
| Rapide et simple pour les indicateurs | ● | ◐ | ● |
| Utilise les outils **obligatoires** du parcours (HDFS, NiFi, Spark, Parquet) | ○ | ● | ◐ (Delta facultatif) |
| Simple à mettre en place aux Jours 2 à 4 | ● | ● | ◐ |
| Facile à transposer sur Azure (ADLS Gen2) | ◐ | ● | ● |

<p class="legend">● adapté · ◐ en partie adapté · ○ peu adapté</p>

**Mon choix : un Data Lake organisé en trois zones (Bronze, Silver, Gold) sur HDFS, avec des fichiers Parquet, dont la dernière zone (Gold) est organisée comme un entrepôt de données.** Autrement dit, c'est un mélange des deux :

- le **Data Lake** gère la variété des données, garde les lots bruts et permet les traitements avec Spark ;
- la **zone Gold**, organisée en étoile, apporte ce qu'offrirait un Data Warehouse pour les indicateurs : des tables de ventes, de retours et de stock, reliées à des tables de référence communes ;
- passer en **Lakehouse**, en ajoutant Delta Lake sur les zones Silver et Gold, reste une évolution **facultative**. Cela ajouterait des modifications sûres, l'historique des versions et la suppression de données personnelles, sans changer l'organisation en zones.

## 4. Questions de recul

**Pourquoi un Data Lake peut-il compléter un Data Warehouse ?** Le Data Warehouse ne garde que des données déjà transformées selon un modèle fixe. Le lac, lui, garde les données brutes : on peut tout refaire si une règle change, et prouver ce qu'on a reçu. Il accueille aussi ce que l'entrepôt gère mal (texte des avis, fichiers JSON, détail des clics très volumineux), et coûte moins cher pour de gros volumes. L'entrepôt, ou une zone Gold bien organisée, reste l'endroit d'où partent les indicateurs.

**Dans quels cas un Lakehouse est-il intéressant ?** Quand les mêmes données servent à la fois aux tableaux de bord et à la data science. Quand on ajoute et corrige souvent des données (par exemple des retours qui arrivent tard). Quand on doit pouvoir supprimer des données personnelles (RGPD). Ou quand on ne veut pas garder deux copies des données, une dans le lac et une dans l'entrepôt. Pour Retail Intelligence, ces besoins existent mais restent limités au Jour 1 : le Lakehouse est une évolution, pas une obligation.
