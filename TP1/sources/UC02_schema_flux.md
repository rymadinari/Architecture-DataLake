# UC-02 — Schéma des flux de données

Retail Intelligence Platform · Jour 1 · Livrable 3/6 de l'UC-02

Un **flux**, c'est le chemin que suit une donnée : d'où elle vient, par où elle passe, ce qu'on lui fait, et qui l'utilise à la fin.

## 1. Schéma général

<div class="diag">
<div class="col"><div class="t">Dépôt des fichiers</div>
<div class="box ok"><b>landing/</b>retail_project/data<br>retail_project/data_refresh</div>
<div class="box wish"><b>landing/complementaire/</b>(si fourni)</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">NiFi</div>
<div class="box">Repère et récupère les fichiers</div>
<div class="box">Vérifie : fichier non vide, extension, empreinte</div>
<div class="box">Ajoute : n° de lot, source, date de réception</div>
<div class="box">Copie dans Bronze + fiche du lot</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Bronze</div>
<div class="box bronze">/bronze/tpcxbb/&lt;table&gt;/batch_id=…/</div>
<div class="box bronze">/bronze/complementaire/&lt;source&gt;/…</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Spark : Bronze → Silver</div>
<div class="box">1. Tables de référence (des deux lots)</div>
<div class="box">2. Faits (ventes, retours, stock, clics, avis)</div>
<div class="box">Contrôles → quarantaine</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Spark : Silver → Gold</div>
<div class="box gold">tables de référence communes</div>
<div class="box gold">fact_sales, fact_returns, fact_inventory, fact_web_clicks, fact_reviews</div>
<div class="box gold">totaux pour les indicateurs</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Utilisateurs</div>
<div class="box ok">Tableaux de bord (U1 à U6)</div>
<div class="box ok">Requêtes SQL (U4, U7)</div>
</div>
</div>

**Ordre obligatoire, tiré de l'UC-01** : on charge d'abord les tables de référence des deux lots (`item`, `customer`, `customer_address`), **puis** les faits. Sinon, le stock du lot principal se retrouve avec 232 380 lignes sans produit (A12).

## 2. Les flux principaux

| Flux | Source | Format d'entrée | Réception | Destination | Contrôles | Transformations | Résultat | Utilisateurs |
|---|---|---|---|---|---|---|---|---|
| **F1 Ventes magasin** | `store_sales.dat` (data + refresh) | Texte `|`, 23 colonnes, format Windows | NiFi, par lot | Bronze → Silver `store_sales` → Gold `fact_sales` | 23 colonnes par ligne ; colonnes obligatoires remplies ; produit, magasin, client et date existent ; montant = quantité × prix ; quantité entre 1 et 100 ; tickets du refresh absents du lot principal | Bons types, montants en décimal exact, canal = `STORE`, n° de transaction = `S-` + ticket, ajout de la date, rangement par date de vente | Ventes en magasin propres | U1, U2, U3, U4 |
| **F2 Ventes web** | `web_sales.dat` (data + refresh) | Texte `|`, 34 colonnes | NiFi, par lot | Silver `web_sales` → Gold `fact_sales` | Comme F1 + date d'expédition après la vente ; site, page et entrepôt existent | Mise au même format que F1 sur les colonnes communes ; frais de livraison à part ; canal = `WEB` | Ventes web propres | U1, U2, U4, U6 |
| **F3 Retours** | `store_returns.dat`, `web_returns.dat` (+ `reason`) | Texte `|`, 20 et 24 colonnes | NiFi, par lot | Silver → Gold `fact_returns` | Le retour retrouve sa vente (ticket ou commande + produit) ; quantité retournée ≤ quantité achetée ; date de retour après la vente | Rattachement à la date de vente ; suppression des doublons créés par le lien (A3) | Retours rattachés ; 407 retours sans vente et 112 retours en trop mis en quarantaine | U2, U4 |
| **F4 Tables de référence** | `item`, `customer*`, `household_demographics`, `income_band`, `store`, `warehouse`, `web_page`, `web_site`, `promotion`, `date_dim`, `time_dim`, `reason`, `ship_mode` | Texte `|` | NiFi, à chaque lot | Silver → Gold `dim_*` | Clé unique ; pas de numéro en double entre les lots ; nombre de colonnes | Clients anonymes (nom, email, identifiant remplacés par un code) ; colonnes inutilisables retirées | Tables de référence communes | Tous |
| **F5 Stock** | `inventory.dat` (23,3 millions de lignes + 0,23 million dans le refresh) | Texte `|`, 4 colonnes | NiFi, par lot | Silver → Gold `fact_inventory` | Une seule ligne par (date, produit, entrepôt) ; quantité entre 0 et 1 000 ; produit existe (après chargement des produits du refresh) | Rangement par date ; un stock vide reste vide (pas 0) | Photo du stock chaque semaine | U5 |
| **F6 Navigation** | `web_clickstreams.dat` (6,8 millions de lignes + 69 000 dans le refresh) | Texte `|`, 6 colonnes | NiFi, par lot (en continu possible plus tard) | Silver → Gold `fact_web_clicks` | Produit, page et date existent ; suivi de la part de clics anonymes | Indication « clic menant à un achat » (hypothèse H1) ; rangement par date | Clics prêts à l'analyse | U6 |
| **F7 Avis produits** | `product_reviews.dat` | Texte `|`, texte libre en dernière colonne | NiFi, par lot | Silver (texte) → Gold `fact_reviews` (note) | Note entre 1 et 5 ; produit et client existent | Texte gardé en Silver pour une éventuelle analyse | Notes par produit | U6, U2 |
| **F8 Prix concurrents** | `item_marketprices.dat` | Texte `|` | NiFi, par lot | Silver → Gold | Produit existe ; prix supérieur à 0 | — | Prix des concurrents par produit | U2 |
| **F9 Rapports du générateur** | `item_marketprices_audit.csv` | Rapport texte | NiFi | Bronze uniquement | Fichier présent | Aucune | Archivé pour garder la trace | U7 |
| **F10 Autres sources** *(si fournies)* | JSON, météo, logistique | Variable | NiFi, flux séparé | `bronze/complementaire/…` → Silver séparé | Structure propre à chaque source ; origine obligatoire | Mélange avec TPCx-BB uniquement en Gold, de façon visible et documentée | Données en plus, clairement identifiées comme non TPCx-BB | selon le besoin |

## 3. Par lots ou en continu ?

| Flux | Mode choisi | Pourquoi |
|---|---|---|
| F1 à F5, F7 à F9 | **Par lots** | Les données arrivent par lots (lot principal, puis refresh). Les indicateurs sont consultés par jour ou par mois. Personne n'a besoin de temps réel. |
| F6 Navigation | **Par lots** au début, **en continu** possible plus tard | Les clics arrivent naturellement au fil de l'eau. Suivre le site presque en temps réel (par exemple pour repérer un problème de page) justifierait NiFi en continu avec Spark Structured Streaming. Ce n'est pas demandé par les questions actuelles. |

## 4. Gestion des nouveaux lots

1. Chaque dépôt reçoit un numéro de lot (par exemple `2005-12-refresh`), gardé jusqu'en Gold (colonne `_batch_id`).
2. Le lot refresh **ajoute** des données (numéros différents, hypothèse H4). On recalcule en Silver les dates concernées, puis les totaux Gold de ces dates.
3. Les retours qui arrivent tard sont rattachés à la date de **vente** : le taux de retour des mois passés est donc recalculé à chaque nouveau lot.
4. Un lot qui échoue à un contrôle bloquant (mauvais nombre de colonnes, fichier vide, lot déjà chargé) ne passe pas en Silver.
