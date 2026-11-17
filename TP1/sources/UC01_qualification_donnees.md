# UC-01 — Qualification des données et des relations

Retail Intelligence Platform · Jour 1 · Livrable 5/6 de l'UC-01

## 1. Méthode

Pour pouvoir refaire l'analyse à l'identique, je l'ai faite avec des scripts :

- `scripts/schema_tpcxbb.py` donne les noms des colonnes de chaque fichier. Ils viennent du schéma officiel TPCx-BB, puisque les fichiers n'ont pas d'en-tête (statut <span class="s d">Déduit</span>).
- `scripts/profilage.py` lit les 34 fichiers `.dat` en entier avec DuckDB (un outil qui permet de faire du SQL sur des fichiers). Il compte les lignes, analyse chaque colonne, vérifie les clés et les liens entre tables, et fait des contrôles de cohérence.

Les résultats bruts sont dans le dossier `preuves/` : `controles_resultats.txt`, `profil_colonnes.csv`, `relations_controles.csv`, `inventaire_fichiers.csv`. Le détail colonne par colonne (type, minimum, maximum, nombre de valeurs différentes, % de vides) est dans `UC01_inventaire_sources.xlsx`, onglet *Colonnes*.

J'ai aussi compté le nombre de champs sur chaque ligne avec la commande `awk -F'|'`. Résultat : **dans chaque fichier, toutes les lignes ont le même nombre de colonnes**, et ce nombre correspond au schéma TPCx-BB. Il n'y a donc pas de ligne coupée ou mal formée.

## 2. Format des fichiers

| Point observé | Ce que j'ai vu | Conséquence pour le chargement | Statut |
|---|---|---|---|
| Séparateur | `|` (barre verticale) | Il faut l'indiquer à l'outil de lecture. | <span class="s v">Vérifié</span> |
| En-tête | Aucun dans les 34 fichiers `.dat` | Les noms de colonnes doivent être fournis à part et gardés dans un fichier versionné. | <span class="s v">Vérifié</span> |
| Fin de ligne | Format Windows (CRLF) dans les 36 fichiers | Il faut enlever le caractère `\r` en fin de ligne, sinon la dernière colonne est abîmée. | <span class="s v">Vérifié</span> |
| Encodage | ASCII ; UTF-8 pour `customer` | Lire les fichiers en UTF-8. | <span class="s v">Vérifié</span> |
| Valeur manquante | Champ vide entre deux `|` | La transformer en `NULL` (vide), pas en texte vide ni en 0. | <span class="s v">Vérifié</span> |
| Guillemets | Pas utilisés comme délimiteurs, mais présents dans le texte des avis | Ne pas les interpréter à la lecture. | <span class="s v">Vérifié</span> |
| Dates | Au format `AAAA-MM-JJ` dans certaines colonnes ; ailleurs, un numéro qui renvoie à la table `date_dim` (colonnes `*_date_sk`) | Faire le lien avec `date_dim` pour retrouver la vraie date. | <span class="s v">Vérifié</span> |
| Montants | Nombres à 2 décimales avec un point | Les stocker en nombre décimal exact (`DECIMAL(7,2)`). | <span class="s v">Vérifié</span> |
| Fichiers de rapport | `item_marketprices_audit.csv` : petit rapport texte, pas un vrai tableau | Ne pas le charger comme une table ; le garder comme information sur la génération. | <span class="s v">Vérifié</span> |

Types de données trouvés sur les 344 colonnes du lot principal : 166 nombres entiers (`BIGINT`), 120 textes (`VARCHAR`), 51 nombres décimaux (`DOUBLE`), 6 dates (`DATE`), 1 heure (`TIME`).

## 3. Résumé par table (lot principal `data/`)

Une **clé** est la colonne qui identifie chaque ligne de façon unique (comme un numéro de client).

| Table | Domaine | Lignes | Col. | Clé possible | Unique ? | Qualité constatée |
|---|---|---:|---:|---|---|---|
| `store_sales` | Ventes magasin | 667 579 | 23 | `ss_ticket_number` + `ss_item_sk` | Non (4 136 lignes en trop) | Montants cohérents ; moins de 0,1 % de vides |
| `web_sales` | Ventes web | 668 052 | 34 | `ws_order_number` + `ws_item_sk` | Non (4 076 lignes en trop) | Montants cohérents ; moins de 0,1 % de vides |
| `store_returns` | Retours | 37 902 | 20 | `sr_ticket_number` + `sr_item_sk` | Non | 112 retours dépassent la quantité vendue |
| `web_returns` | Retours | 38 487 | 24 | `wr_order_number` + `wr_item_sk` | Non | Retours jusqu'en mars 2008 |
| `item` | Produits | 17 820 | 22 | `i_item_sk` | Oui | `i_rec_end_date` toujours vide ; `i_container` toujours identique |
| `item_marketprices` | Prix concurrents | 89 100 | 6 | `imp_sk` | Oui | Concurrents désignés par un code, sans nom |
| `promotion` | Promotions | 300 | 19 | `p_promo_sk` | Oui | Dates de 1901 à 2199 |
| `product_reviews` | Avis | 89 991 | 8 | `pr_review_sk` | Oui | Vrai texte d'avis (en anglais) |
| `customer` | Clients | 99 000 | 18 | `c_customer_sk` | Oui | Données personnelles (nom, email, date de naissance) |
| `customer_address` | Clients | 49 500 | 13 | `ca_address_sk` | Oui | Rues et numéros en partie inventés |
| `customer_demographics` | Clients | 1 920 800 | 9 | `cd_demo_sk` | Oui | Liste de profils types, pas de vraies personnes |
| `household_demographics` | Clients | 7 200 | 5 | `hd_demo_sk` | Oui | — |
| `income_band` | Clients | 20 | 3 | `ib_income_band_sk` | Oui | — |
| `store` | Magasins | 12 | 29 | `s_store_sk` | Oui | Dates de fermeture impossibles |
| `warehouse` | Entrepôts | 5 | 14 | `w_warehouse_sk` | Oui | — |
| `inventory` | Stocks | 23 255 100 | 4 | date + produit + entrepôt | Oui | 232 380 lignes sur des produits absents de `data/item` |
| `web_clickstreams` | Navigation | 6 770 550 | 6 | aucune | — | `wcs_sales_sk` vide à 90 %, `wcs_user_sk` vide à 42 % |
| `web_page` | Navigation | 60 | 14 | `wp_web_page_sk` | Oui | 8 types de pages |
| `web_site` | Navigation | 30 | 26 | `web_site_sk` | Oui | 5 noms de site, 6 versions chacun |
| `date_dim` | Dates | 109 573 | 28 | `d_date_sk` | Oui | De 1900 à 2199 ; `d_holiday` = Y pour toutes les dates |
| `time_dim` | Heures | 86 400 | 10 | `t_time_sk` | Oui | Une ligne par seconde de la journée |
| `reason` | Motifs de retour | 35 | 3 | `r_reason_sk` | Oui | Textes au hasard |
| `ship_mode` | Livraison | 20 | 6 | `sm_ship_mode_sk` | Oui | Textes au hasard |

## 4. Valeurs vides (nulls)

- **Ventes et retours** : les colonnes secondaires (profil du client, adresse, promotion, page, site, entrepôt, mode de livraison, motif) sont vides dans 0,02 % à 0,16 % des lignes. Les colonnes principales (date, produit, client, magasin, numéro de ticket ou de commande) ne sont **jamais** vides.
- **Tables de référence** : on trouve 0,01 % à 0,05 % de vides un peu partout (`customer`, `customer_address`, `customer_demographics`, `item`). Ce taux très faible et régulier fait penser à des vides ajoutés exprès par le générateur. <span class="s h">Hypothèse</span>
- **Vides normaux** (pas des erreurs) : les dates de fin de validité (`i_rec_end_date`, `s_rec_end_date`, `wp_rec_end_date`, `web_rec_end_date`) sont toujours vides car il s'agit des versions actuelles ; `t_meal_time` est vide à 58 % car beaucoup d'heures ne sont pas des heures de repas.
- **Navigation** : `wcs_sales_sk` est vide à 90,13 % (le clic n'a pas mené à un achat) et `wcs_user_sk` à 42,15 % (visiteur non connecté).
- `inventory.inv_quantity_on_hand` a 5 999 valeurs vides (0,03 %). Un stock vide n'est pas un stock à zéro : il ne faut pas les confondre.

## 5. Anomalies repérées

| # | Anomalie | Mesure | Conséquence | Statut |
|---|---|---|---|---|
| A1 | Marge négative sur la plupart des ventes en magasin | 495 971 lignes, soit 74,3 % | La marge (K6) ne peut pas être lue comme une vraie marge. | <span class="s v">Vérifié</span> |
| A2 | Remise moyenne très forte et identique partout | 50 % du prix catalogue en moyenne | Les prix ont été tirés au hasard. | <span class="s v">Vérifié</span> |
| A3 | Même couple (ticket, produit) présent plusieurs fois, sans ligne identique | 4 136 lignes en trop en magasin, 4 076 sur le web | Relier ventes et retours sur (ticket, produit) crée des doublons : 37 902 retours donnent 38 391 lignes. | <span class="s v">Vérifié</span> |
| A4 | Plus d'articles retournés qu'achetés | 112 retours en magasin | À mettre de côté lors du nettoyage. | <span class="s v">Vérifié</span> |
| A5 | Retours enregistrés longtemps après la dernière vente | Jusqu'au 14/11/2007 (magasin) et au 18/03/2008 (web) | Le taux de retour d'une période doit être calculé selon la date de vente, pas la date de retour. | <span class="s v">Vérifié</span> |
| A6 | Dates de fermeture des magasins impossibles | Entre 1917 et 2141, alors que les 12 magasins vendent de 2001 à 2005 | Colonne inutilisable. | <span class="s v">Vérifié</span> |
| A7 | Dates de promotion impossibles | De 1901 à 2199 ; 462 806 ventes magasin (69 % de celles avec promotion) ont lieu en dehors de la période de leur promotion | On ne peut pas savoir si une promotion était vraiment active le jour de la vente. | <span class="s v">Vérifié</span> |
| A8 | Presque toutes les ventes ont une promotion | 99,98 % des lignes | On ne peut pas comparer « avec » et « sans » promotion. | <span class="s v">Vérifié</span> |
| A9 | Date de premier achat des clients en dehors de la période de vente | 97 333 clients sur 98 982 (98 %) | Impossible de calculer l'ancienneté d'un client. | <span class="s v">Vérifié</span> |
| A10 | `d_holiday` = « Y » (jour férié) pour toutes les dates | 100 % | Impossible de repérer les jours fériés. | <span class="s v">Vérifié</span> |
| A11 | Textes au hasard | `reason`, `ship_mode`, `i_brand`, `i_product_name`, `c_last_review_date` | Motifs de retour et transporteurs illisibles. | <span class="s v">Vérifié</span> |
| A12 | Le stock du lot principal utilise des produits du lot refresh | 180 produits (n° 17 820 à 17 999), 232 380 lignes, présents seulement dans `data_refresh/item` | Si on charge `data/` seul, ces lignes n'ont pas de produit : l'ordre de chargement compte. | <span class="s v">Vérifié</span> |
| A13 | Retours du refresh sans vente d'origine | Sur 426 retours, 19 retrouvent leur vente dans le lot principal, 0 dans le refresh | 407 retours à mettre de côté. | <span class="s v">Vérifié</span> |
| A14 | Année 2005 incomplète dans `data/` | Les ventes s'arrêtent au 13/12/2005 (la suite est dans `data_refresh/`) | Le CA 2005 est trop bas si on oublie le refresh. | <span class="s v">Vérifié</span> |

Contrôles **sans problème** : montant = quantité × prix unitaire (0 écart, sur les deux canaux) ; marge = montant payé − coût d'achat (0 écart) ; prix de vente jamais supérieur au prix catalogue ; date d'expédition web jamais avant la vente ; date de retour jamais avant la vente ; quantités entre 1 et 100 ; stock entre 0 et 1 000 ; un ticket = un seul client, un seul magasin et une seule date ; aucune ligne de vente en double à l'identique.

## 6. Liens entre les tables

### 6.1 Liens vérifiés

Une table de **faits** contient les événements (ventes, retours…) ; une table de **référence** décrit les éléments (produits, clients, magasins…). Pour chaque lien, j'ai vérifié que la colonne existe des deux côtés, qu'elle a le même type, que la clé de la table de référence est unique, et qu'il n'y a **aucun orphelin**. Un orphelin est une ligne qui renvoie à un élément inexistant, par exemple une vente d'un produit absent de la liste des produits. Chaque fois, plusieurs lignes de faits renvoient à une seule ligne de référence.

| Faits → Référence | Colonnes de lien | % vides | Orphelins |
|---|---|---:|---:|
| `store_sales` → `item` / `store` / `customer` / `date_dim` / `time_dim` | `ss_item_sk`, `ss_store_sk`, `ss_customer_sk`, `ss_sold_date_sk`, `ss_sold_time_sk` | 0 % | 0 |
| `store_sales` → `promotion` / `customer_demographics` / `household_demographics` / `customer_address` | `ss_promo_sk`, `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk` | 0,02 – 0,07 % | 0 |
| `web_sales` → `item` / `customer` / `date_dim` | `ws_item_sk`, `ws_bill_customer_sk`, `ws_sold_date_sk` | 0 % | 0 |
| `web_sales` → `web_site` / `web_page` / `warehouse` / `ship_mode` / `promotion` | colonnes `ws_*_sk` | 0,02 – 0,03 % | 0 |
| `store_returns` → `item` / `store` / `reason` | `sr_item_sk`, `sr_store_sk`, `sr_reason_sk` | 0 – 0,03 % | 0 |
| `web_returns` → `item` / `reason` | `wr_item_sk`, `wr_reason_sk` | 0 – 0,02 % | 0 |
| `inventory` → `warehouse` / `date_dim` | `inv_warehouse_sk`, `inv_date_sk` | 0 % | 0 |
| `inventory` → `item` | `inv_item_sk` | 0 % | **232 380** (réglé si on charge aussi `data_refresh/item`) |
| `web_clickstreams` → `item` / `web_page` / `date_dim` / `customer` | `wcs_item_sk`, `wcs_web_page_sk`, `wcs_click_date_sk`, `wcs_user_sk` | 0 – 42 % | 0 |
| `product_reviews` → `item` / `customer` | `pr_item_sk`, `pr_user_sk` | 0 % | 0 |
| `customer` → `customer_address` / `customer_demographics` / `household_demographics` | `c_current_*_sk` | 0,02 – 0,03 % | 0 |
| `household_demographics` → `income_band` | `hd_income_band_sk` | 0,03 % | 0 |
| `store_returns` → `store_sales` | (`sr_ticket_number`, `sr_item_sk`) | 0 % | 0, mais le couple n'est pas unique côté ventes (A3) |
| `web_returns` → `web_sales` | (`wr_order_number`, `wr_item_sk`) | 0 % | 0, mais le couple n'est pas unique côté ventes (A3) |

### 6.2 Liens à confirmer

| Lien envisagé | Ce que j'ai observé | Statut |
|---|---|---|
| `web_clickstreams.wcs_sales_sk` → `web_sales.ws_order_number` | Les 89 100 valeurs de `wcs_sales_sk` existent toutes comme numéro de commande, et le nombre de clics avec achat (668 052) est exactement le nombre de lignes de `web_sales`. Mais le nom de la colonne fait plutôt penser à un numéro de vente. | <span class="s h">Hypothèse</span> forte, à confirmer par la documentation |
| `product_reviews.pr_order_sk` → `web_sales.ws_order_number` | Toutes les valeurs existent comme numéro de commande, mais les deux colonnes vont de 0 à environ 89 000 : ça peut être un hasard. Il faudrait vérifier que le produit et le client de l'avis correspondent à la commande. | <span class="s h">Hypothèse</span> |
| `pr_user_sk` et `wcs_user_sk` → `customer.c_customer_sk` | Aucun orphelin, mais rien n'indique officiellement que « utilisateur du site » = « client ». | <span class="s d">Déduit</span> |
| `ss_ticket_number` (magasin) et `ws_order_number` (web) | Les deux numérotations vont de 0 à 89 099 : ce sont deux numérotations différentes. Il ne faut jamais les relier entre elles. | <span class="s d">Déduit</span> |
| `inventory` ↔ ventes en magasin | Aucune colonne commune (entrepôt ou magasin) : on ne peut pas relier le stock d'un entrepôt à une vente en magasin. | <span class="s n">Non disponible</span> |
| Promotion active le jour de la vente | Dates de promotion impossibles (A7). | <span class="s n">Non vérifiable</span> |

### 6.3 Organisation des données (schéma en étoile)

Les tables forment un **schéma en étoile** : au centre, les tables de faits ; autour, les tables de référence qui les décrivent.

<div class="diag">
<div class="col"><div class="t">Références communes</div>
<div class="box ok"><b>date_dim / time_dim</b>dates et heures</div>
<div class="box ok"><b>item</b>produits (+ ceux du refresh)</div>
<div class="box ok"><b>customer</b>→ adresse, profil, foyer → tranche de revenu</div>
<div class="box ok"><b>promotion</b></div>
</div>
<div class="arrow">↔</div>
<div class="col"><div class="t">Faits</div>
<div class="box ok"><b>store_sales</b>1 ligne = 1 produit d'un ticket</div>
<div class="box ok"><b>web_sales</b>1 ligne = 1 produit d'une commande</div>
<div class="box ok"><b>store_returns / web_returns</b>liés à la ligne de vente</div>
<div class="box ok"><b>inventory</b>1 ligne = semaine × produit × entrepôt</div>
<div class="box part"><b>web_clickstreams</b>1 ligne = 1 clic (pas de clé)</div>
<div class="box ok"><b>product_reviews</b>1 ligne = 1 avis</div>
</div>
<div class="arrow">↔</div>
<div class="col"><div class="t">Références spécifiques</div>
<div class="box ok"><b>store</b> (ventes et retours en magasin)</div>
<div class="box ok"><b>web_site, web_page, ship_mode</b> (web)</div>
<div class="box ok"><b>warehouse</b> (web, stock)</div>
<div class="box ok"><b>reason</b> (retours)</div>
<div class="box ok"><b>item_marketprices</b> (prix concurrents)</div>
</div>
</div>

## 7. Le lot `data_refresh/`

| Constat | Mesure | Statut |
|---|---|---|
| Contient 11 tables (ventes, retours, clics, stock, produits, clients, adresses, avis, prix concurrents), mais pas de magasins ni de dates | 11 fichiers `.dat` + 1 rapport, 9,5 Mo | <span class="s v">Vérifié</span> |
| Couvre la période juste après le lot principal | Ventes et clics du 13/12 au 31/12/2005 ; stock sur 3 semaines (du 12/12 au 26/12/2005) | <span class="s v">Vérifié</span> |
| Utilise de nouveaux numéros, jamais déjà utilisés dans le lot principal | Clients 99 000 à 99 999, produits 17 820 à 17 999, adresses 49 500 à 49 999, tickets 89 100 à 89 999 | <span class="s v">Vérifié</span> |
| C'est donc un lot qui **ajoute** des données, sans modifier les anciennes | Aucun numéro en commun avec `data/` | <span class="s d">Déduit</span> |
| Retours sans vente d'origine | 407 sur 426 (A13) | <span class="s v">Vérifié</span> |
| Le 13/12/2005 est présent dans les deux lots | Ventes du lot principal jusqu'au 13/12, refresh à partir du 13/12 ; aucun ticket en double | <span class="s v">Vérifié</span> |
