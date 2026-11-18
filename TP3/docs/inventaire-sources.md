# Inventaire des sources utilisées (étape 2)

J'ai repris l'inventaire des jours 1 et 2 et j'ai gardé 4 fichiers, ceux qu'il faut pour mes questions Q1, Q3 et Q5. Les chiffres viennent du notebook `01_exploration.ipynb`.

Points communs aux 4 fichiers : texte délimité par `|`, sans ligne d'en-tête, fins de ligne Windows, champ vide = valeur manquante. C'est des données **structurées** (tableau avec un nombre fixe de colonnes). Les noms de colonnes viennent du schéma TPCx-BB repris au jour 1.

## Ventes et produits

| Information | Source 1 : ventes magasin | Source 2 : produits |
|---|---|---|
| Nom réel du fichier | `store_sales.dat` | `item.dat` |
| Emplacement | `~/TP1/retail_project/data/store_sales/` (et `/retail-lake/raw/tpcxbb/initial/store_sales/` dans HDFS) | `~/TP1/retail_project/data/item/` (et HDFS) |
| Format | texte délimité `|` | texte délimité `|` |
| Taille | 88,5 Mo | 6,5 Mo |
| Nombre de lignes | 667 579 | 17 820 |
| Nombre de colonnes | 23 | 22 |
| Colonnes principales | `ss_sold_date_sk`, `ss_item_sk`, `ss_store_sk`, `ss_ticket_number`, `ss_quantity`, `ss_sales_price`, `ss_net_paid`, `ss_net_profit` | `i_item_sk`, `i_item_id`, `i_category`, `i_class`, `i_brand`, `i_current_price` |
| Types observés | tout en texte dans le fichier ; après contrôle : entiers (clés, quantité), décimaux (montants) | entiers (clés, identifiants), décimaux (prix), dates, texte |
| Clé candidate | (ticket, produit) attendue, mais **pas unique** (4 136 doublons, vraies ventes) | `i_item_sk` (unique) |
| Granularité | une ligne de ticket de caisse | un produit |
| Anomalies identifiées | 74 % de marges négatives, 3 324 ventes à 0 €, quelques clés facultatives vides, 2005 incomplète (jusqu'au 13/12) | quelques descriptions et marques vides, textes aléatoires |

## Magasins et calendrier

| Information | Source 3 : magasins | Source 4 : calendrier |
|---|---|---|
| Nom réel du fichier | `store.dat` | `date_dim.dat` |
| Emplacement | `~/TP1/retail_project/data/store/` (et HDFS) | `~/TP1/retail_project/data/date_dim/` (et HDFS) |
| Format | texte délimité `|` | texte délimité `|` |
| Taille | 3,3 Ko | 14,7 Mo |
| Nombre de lignes | 12 | 109 573 |
| Nombre de colonnes | 29 | 28 |
| Colonnes principales | `s_store_sk`, `s_store_name`, `s_number_employees`, `s_floor_space`, `s_state` | `d_date_sk`, `d_date`, `d_year`, `d_moy` |
| Types observés | entiers, décimaux, dates, texte | entiers, dates, texte |
| Clé candidate | `s_store_sk` (unique) | `d_date_sk` (unique) |
| Granularité | un magasin | un jour |
| Anomalies identifiées | dates de fermeture entre 1917 et 2141 (impossibles), surfaces irréalistes (plusieurs millions) | `d_holiday` = Y partout |

## Réponses aux questions techniques (§4.5.2)

1. **Structurés ?** Oui, les 4 fichiers sont structurés (colonnes fixes, séparateur).
2. **Bien typés ?** Non, tout est du texte dans le fichier. J'ai défini les types moi-même dans `config.py` et vérifié qu'aucune valeur ne bloque la conversion.
3. **Valeurs nulles ?** Oui, mais seulement sur des colonnes facultatives (promotion, adresse, client, marque, description).
4. **Identifiants uniques ?** Oui pour les produits, magasins et dates. Non pour (ticket, produit) dans les ventes, mais c'est expliqué.
5. **Granularité connue ?** Oui, voir les tableaux.
6. **Adaptées aux questions du jour 1 ?** Oui pour Q1 (CA par période), Q3 (catégories) et Q5 (magasins), avec les limites : données synthétiques, 2005 incomplète, marge peu réaliste.
