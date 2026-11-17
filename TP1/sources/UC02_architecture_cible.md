# UC-02 — Architecture logique cible

Retail Intelligence Platform · Jour 1 · Livrable 2/6 de l'UC-02

Il s'agit d'un plan, pas d'une installation. Rien n'est installé au Jour 1 : les outils seront mis en place petit à petit (HDFS et NiFi au Jour 2, Spark au Jour 3, Azure au Jour 4).

## 1. Vue d'ensemble

Architecture choisie : un **Data Lake en trois zones (Bronze, Silver, Gold)** sur HDFS, avec des fichiers Parquet. La zone Gold est organisée en étoile pour les indicateurs. Le choix est expliqué dans `UC02_comparaison_architectures.pdf`.

<div class="diag">
<div class="col"><div class="t">1. Sources</div>
<div class="box ok"><b>TPCx-BB · data/</b>23 tables .dat (≈ 1 024 Mo)</div>
<div class="box ok"><b>TPCx-BB · data_refresh/</b>11 tables .dat (≈ 9,5 Mo), lot d'ajout</div>
<div class="box ok"><b>Rapports du générateur</b>2 CSV</div>
<div class="box wish"><b>Autres sources</b> (optionnel)<br>JSON, météo, logistique : gardées à part</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">2. Ingestion</div>
<div class="box"><b>Apache NiFi</b>Repère les nouveaux fichiers, calcule une empreinte, note le lot, la date et la source, puis copie dans HDFS sans rien modifier</div>
<div class="box"><b>Python</b>Vérifie la forme des fichiers avant (nombre de colonnes, encodage)</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">3. Bronze (brut)</div>
<div class="box bronze"><b>HDFS /datalake/bronze</b>Fichiers d'origine, sans modification<br>Rangés par source / table / lot / date<br>Lecture seule, gardés longtemps</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">4. Nettoyage et contrôle</div>
<div class="box"><b>Spark / PySpark</b>Ajoute les noms de colonnes, corrige les types, nettoie les fins de ligne, gère les vides, contrôle la qualité, retire les doublons, rend les clients anonymes</div>
<div class="box silver"><b>HDFS /datalake/silver</b>Parquet propre, une table par sujet, rangée par date</div>
<div class="box wish"><b>/datalake/quarantine</b>Lignes rejetées + raison</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">5. Données pour l'analyse</div>
<div class="box"><b>Spark SQL</b>Organisation en étoile, calcul des totaux</div>
<div class="box gold"><b>HDFS /datalake/gold</b>Parquet : faits + références + totaux pour les indicateurs</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">6. Utilisation</div>
<div class="box ok"><b>Tableaux de bord</b>K1 à K12 selon le profil (U1 à U6)</div>
<div class="box ok"><b>Requêtes SQL</b>Spark SQL / Jupyter (U4, U7)</div>
<div class="box ok"><b>Exports</b>CSV pour les métiers</div>
</div>
</div>
<div class="band"><b>7. Suivi et gouvernance (pour toutes les étapes)</b> : origine de chaque fichier (NiFi) · catalogue des tables et noms de colonnes gardés dans Git · rapport de qualité pour chaque lot · droits d'accès par zone et par rôle · journaux des traitements Spark · suivi des volumes. Détails dans <code>UC02_gouvernance.pdf</code>.</div>

## 2. Rôle de chaque zone

| Zone | À quoi elle sert | Ce qu'elle contient | Format | Qui écrit / qui lit | Durée de conservation |
|---|---|---|---|---|---|
| **Bronze (brut)** | Garder exactement ce qu'on a reçu, avec son origine, pour pouvoir le prouver et tout refaire si besoin. | Les 36 fichiers tels quels, un dossier par lot (`data`, `data_refresh_2005-12`…), et une fiche par lot (taille, empreinte, nombre de lignes, date de réception). | Fichiers `.dat` d'origine | NiFi est le seul à écrire. Spark et l'équipe Data lisent. | Longue (c'est la référence) |
| **Silver** | Avoir des données propres et cohérentes, sur lesquelles on peut faire des liens entre tables sans erreur. | Une table par sujet, avec les noms de colonnes, des types corrects (montants en `DECIMAL(7,2)`, dates en `DATE`), les fins de ligne nettoyées, les vides en `NULL`, et des colonnes techniques qui indiquent l'origine (`_batch_id`, `_source_file`, `_ingest_ts`). Clients rendus anonymes. Lignes en erreur envoyées en quarantaine. | Parquet, rangé par date | Les traitements Spark écrivent. L'équipe Data et les traitements Gold lisent. | Moyenne (on peut la refaire depuis Bronze) |
| **Gold** | Fournir des données prêtes à l'emploi pour les indicateurs et les analyses. | Modèle en étoile : tables de faits et de référence, plus des totaux déjà calculés (CA par jour, par magasin, par canal, par catégorie…). | Parquet | Les traitements Spark écrivent. Les outils de tableaux de bord et les métiers lisent, selon leurs droits. | On peut la refaire |
| **Quarantaine** | Mettre de côté, sans les perdre, les lignes qui ne passent pas les contrôles. | Par exemple : les 407 retours du refresh sans vente, les 112 retours supérieurs à la quantité achetée. | Parquet + une colonne `_reject_reason` (raison du rejet) | Spark écrit. L'équipe Data lit. | Jusqu'à correction |

## 3. Les tables de la zone Gold

| Table Gold | Une ligne = | Construite à partir de | Indicateurs |
|---|---|---|---|
| `fact_sales` | Un produit vendu, en magasin ou sur le web | `store_sales` + `web_sales` (colonnes communes : date, heure, produit, client, promotion, quantité, montants) ; une colonne `channel` (canal) et un numéro de transaction qui indique le canal (`S-<ticket>`, `W-<commande>`) | K1 à K7 |
| `fact_returns` | Un produit retourné, rattaché à la date de vente | `store_returns` + `web_returns` | K8 |
| `fact_inventory` | Une semaine × un produit × un entrepôt | `inventory` | K9 |
| `fact_web_clicks` | Un clic | `web_clickstreams` (avec une indication « mène à un achat ») | K10 |
| `fact_reviews` | Un avis | `product_reviews` (la note ; le texte reste en Silver) | K12 |
| `dim_date`, `dim_time` | Un jour, une seconde | `date_dim`, `time_dim` (sans `d_holiday`, inutilisable) | tous |
| `dim_item` | Un produit | `item` des deux lots | tous |
| `dim_customer` | Un client (anonyme) | `customer` + adresse + profil + foyer + tranche de revenu | analyse des clients |
| `dim_store`, `dim_warehouse`, `dim_web_page`, `dim_web_site`, `dim_promotion` | Un magasin, un entrepôt, une page… | tables de référence correspondantes | découpages |
| `agg_sales_daily` | Un jour × un canal × un magasin × une catégorie | `fact_sales` | tableaux de bord rapides |

Règles tirées de l'UC-01 :

- le nombre de transactions se compte toujours en numéros de transaction **différents** ;
- les retours ne sont jamais retirés du CA dans `fact_sales` ;
- les frais de livraison web sont rangés dans une colonne à part ;
- les colonnes inutilisables (`d_holiday`, `s_closed_date_sk`, `r_reason_desc`…) ne sont pas mises en Gold.

## 4. Pourquoi ces choix

| Choix | Raison (besoin ou constat de l'UC-01) |
|---|---|
| Garder les fichiers bruts en Bronze | Les fichiers n'ont pas de noms de colonnes et certains liens sont encore des hypothèses (H1, H2). Si on change d'avis, il faut pouvoir tout refaire à partir des fichiers d'origine. |
| Zone Silver avec quarantaine | 14 anomalies trouvées, dont des orphelins (A12, A13). On ne peut ni les ignorer ni les utiliser telles quelles dans les indicateurs. |
| Parquet | Format qui range les données par colonne et les compresse. Les indicateurs n'utilisent que quelques colonnes sur 23 à 34, donc on lit moins de données. Le rangement par date accélère les recherches par période. C'est le format de référence du parcours. |
| Spark | 23 millions de lignes de stock et 6,8 millions de clics : un traitement réparti est demandé par le parcours, et le même code fonctionne en local et sur Azure. |
| NiFi pour recevoir les fichiers | Les lots arrivent à des moments différents (lot principal, puis refresh). NiFi repère les nouveaux fichiers, garde la trace de leur origine et permet de relancer. |
| Gold en étoile | Les questions métier (Q1 à Q16) ont toutes la forme « une mesure selon des axes » : produit, magasin, canal, date, client. |
| Autres sources rangées à part (`bronze/complementaire/…`) | L'énoncé (§3.6) interdit de les mélanger sans le dire aux données TPCx-BB. Leur origine doit rester connue. |
| Traitement par lots | Les données arrivent par lots, et aucun besoin de temps réel n'a été identifié. Un traitement en continu des clics reste possible plus tard (voir `UC02_schema_flux.pdf`). |

## 5. Limites de ma proposition

- Sans Delta Lake (facultatif), les fichiers Parquet ne garantissent ni des modifications sûres, ni le contrôle de la structure, ni l'historique des versions, ni la suppression simple d'une ligne. Un traitement interrompu peut laisser des fichiers à moitié écrits. Pour éviter ça, on écrit d'abord dans un dossier temporaire, puis on le renomme à la fin.
- Il n'y a pas d'outil de requêtes interactives dédié dans le socle : les tableaux de bord lisent les totaux de Gold ou passent par Spark SQL.
- Le volume actuel (environ 1 Go) est petit : le cluster HDFS se justifie surtout par l'objectif du cours et par une croissance future, qui reste à confirmer.
- L'outil de tableaux de bord n'est pas choisi dans le parcours. <span class="s a">À valider</span>

## 6. Questions de recul

**Pourquoi garder les données brutes ?** Pour prouver ce qu'on a reçu, pour pouvoir tout refaire si on corrige une règle ou une hypothèse (par exemple H1 sur les clics), et parce qu'une donnée inutile aujourd'hui peut servir demain.

**Pourquoi ranger les données en zones ?** Pour séparer les niveaux de confiance (reçu, contrôlé, prêt à l'emploi), donner des droits différents selon la zone, savoir où trouver une donnée et ce qu'on peut en attendre, et éviter que le lac devienne un fouillis.

**Qu'est-ce que le simple stockage en Parquet ne garantit pas ?** Il ne garantit ni des modifications sûres, ni plusieurs écritures en même temps sans risque, ni une structure identique entre fichiers, ni l'historique des versions, ni la modification ou la suppression d'une ligne, ni la qualité des données, ni un catalogue, ni la gestion des droits. Ces garanties viennent d'un format de table (Delta Lake), d'un catalogue et des règles de gouvernance.
