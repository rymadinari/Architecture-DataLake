# UC-02 — Proposition de gouvernance

Retail Intelligence Platform · Jour 1 · Livrable 5/6 de l'UC-02

La **gouvernance**, ce sont les règles qui permettent de savoir d'où viennent les données, si on peut leur faire confiance, qui a le droit d'y accéder et combien elles coûtent.

## 1. Savoir d'où vient chaque donnée

| Moyen | Comment | Exemple |
|---|---|---|
| Numéro de lot | NiFi donne un numéro à chaque dépôt, gardé jusqu'en Gold (colonne `_batch_id`). | `tpcxbb_initial`, `tpcxbb_refresh_2005-12` |
| Colonnes techniques sur chaque ligne Silver | `_source_file` (fichier d'origine), `_batch_id` (lot), `_ingest_ts` (date de réception), `_source_system` (`TPCx-BB` ou `COMPLEMENTAIRE`) | Une vente en Gold renvoie à son fichier `.dat` d'origine. |
| Fiche de lot (Bronze) | Pour chaque fichier : chemin, taille, empreinte SHA-256 (sorte de signature qui prouve que le fichier n'a pas changé), nombre de lignes et de colonnes, date de réception. | Faite à partir de l'inventaire de l'UC-01 (`preuves/inventaire_fichiers.csv`). |
| Historique NiFi | NiFi garde automatiquement l'historique de chaque fichier (reçu, modifié, envoyé). | Qui a déposé quoi, et quand. |
| Sources séparées | Les données supplémentaires ont leurs propres dossiers et `_source_system = COMPLEMENTAIRE`. | Jamais mélangées aux données TPCx-BB sans le dire (§3.6). |

## 2. Documenter les fichiers et les tables

- **Dictionnaire de données** : les noms de colonnes TPCx-BB (`scripts/schema_tpcxbb.py`), gardés dans Git. Toute modification est relue avant d'être acceptée.
- **Catalogue** : pour chaque table Silver et Gold, une description, un responsable, ce que représente une ligne, la clé, la fréquence de mise à jour, le niveau de qualité, les colonnes sensibles. Base de départ : `UC01_inventaire_sources.xlsx`.
- **Dictionnaire des indicateurs** : `UC01_dictionnaire_KPI.xlsx` est la seule référence pour les formules. Un tableau de bord ne doit jamais calculer un indicateur autrement.
- **Liste des hypothèses** : H1 à H8 (`UC01_limites_et_hypotheses.pdf`), avec leur statut mis à jour quand elles sont confirmées ou non.

## 3. Contrôles de qualité

| Niveau | Contrôle | Exemple tiré de l'UC-01 | Si le contrôle échoue |
|---|---|---|---|
| Fichier (réception) | Fichier non vide, empreinte, extension, lot pas déjà chargé | — | Lot bloqué, alerte |
| Forme (Bronze → Silver) | Nombre de colonnes par ligne = nombre attendu | 23 colonnes pour `store_sales` | Lot bloqué |
| Type | Les dates et montants se convertissent correctement | `DECIMAL(7,2)`, `DATE` | Ligne en quarantaine |
| Champs obligatoires | Les colonnes principales sont remplies | date, produit, ticket, magasin | Ligne en quarantaine |
| Unicité | Clé unique dans les tables de référence ; pas de numéro en double entre lots | `i_item_sk`, `c_customer_sk` | Lot bloqué |
| Liens entre tables | Le produit, le client… existent bien | 232 380 lignes de stock (A12) si les produits du refresh manquent | Ligne en quarantaine, retraitée au lot suivant |
| Cohérence métier | Montant = quantité × prix ; retour ≤ achat ; retour après la vente | 112 retours en trop (A4) | Ligne en quarantaine |
| Valeurs possibles | Quantité de 1 à 100 ; stock de 0 à 1 000 ; note de 1 à 5 | — | Ligne en quarantaine |
| Volume | Nombre de lignes très différent du lot précédent | Le refresh fait environ 1 % du lot principal | Alerte |
| Colonnes utilisables | Les colonnes connues comme inutilisables ne vont pas en Gold | `d_holiday`, `s_closed_date_sk`, `r_reason_desc` | — |

Chaque traitement produit un **rapport de qualité** (lignes lues, chargées, mises de côté, et pourquoi), gardé avec le lot.

## 4. Qui a accès à quoi

| Rôle | Bronze | Silver | Quarantaine | Gold | Données personnelles visibles |
|---|---|---|---|---|---|
| Compte technique NiFi | Écriture | — | — | — | — |
| Compte technique Spark | Lecture | Écriture | Écriture | Écriture | Lecture (pour les rendre anonymes) |
| Équipe Data (U7) | Lecture | Lecture | Lecture | Lecture | Sur demande justifiée |
| Contrôleur de gestion (U4) | — | — | — | Lecture | Non |
| Directions et responsables (U1, U2, U3, U5, U6) | — | — | — | Lecture (totaux, limités à leur périmètre si besoin, par exemple un seul magasin pour U3) | Non |
| Administrateur de la plateforme | Gestion | Gestion | Gestion | Gestion | Non (rôles séparés) |

Principe : chacun n'a que les droits **strictement nécessaires**. Les droits sont donnés à des groupes, pas à des personnes, et revus régulièrement.

## 5. Protection des données

- `customer` contient des données personnelles : nom, prénom, email, identifiant, date et pays de naissance. Elles sont inventées, mais je les traite **comme si elles étaient vraies**.
- En Silver : le prénom, le nom, l'email et l'identifiant sont remplacés par un code (on dit qu'on les « pseudonymise »). La table qui permet de retrouver les vraies valeurs, si elle existe, est gardée à part avec un accès très limité.
- En Gold : seulement des informations utiles à l'analyse (tranche d'âge, pays, genre, tranche de revenu), et rien qui permette de reconnaître une personne.
- On ne garde que le nécessaire : `c_last_review_date` (texte au hasard) et `c_login` ne sont pas partagés.
- Bronze contient les données d'origine en clair : seuls les comptes techniques et l'équipe Data y ont accès.
- Les mots de passe et les clés ne sont jamais écrits dans le code : fichier protégé en local, Azure Key Vault dans le cloud.

## 6. Suivi des traitements

- Chaque traitement Spark enregistre un journal : numéro d'exécution, lot, durée, lignes lues, écrites et rejetées, résultat.
- Surveillance des flux NiFi (files d'attente, erreurs, blocages).
- Les fichiers Gold sont d'abord écrits dans un dossier temporaire, puis renommés à la fin, pour qu'on ne lise jamais un fichier à moitié écrit (Parquet seul ne protège pas de ce problème).
- Alerte en cas d'échec ou de volume anormal.

## 7. Maîtriser les coûts et les volumes

| Moyen | Application |
|---|---|
| Format compressé par colonne | Parquet en Silver et Gold : on s'attend à des fichiers bien plus petits qu'en texte <span class="s h">Hypothèse</span>, à mesurer au Jour 3. |
| Rangement par date | Une recherche sur une période ne lit que les dates utiles. |
| Totaux en Gold | Les tableaux de bord lisent des totaux, pas les 23 millions de lignes de stock. |
| Durées de conservation différentes | Bronze est gardé ; Silver et Gold peuvent être refaits ; la quarantaine est vidée après correction. |
| Suivi des volumes | Volume par zone et par lot (environ 1 Go brut aujourd'hui ; le refresh ajoute environ 9,5 Mo pour 19 jours). |
| Cloud | Niveaux de stockage plus ou moins chers selon l'usage, suppression ou archivage automatique, budgets et alertes (voir `UC02_local_vers_azure.pdf`). |

## 8. Question de recul

**Quels risques si la gouvernance est insuffisante ?** Le lac devient un fouillis où personne ne retrouve rien ni ne fait confiance aux données. Chaque service calcule les indicateurs à sa façon (par exemple les « transactions » comptées en lignes ici, en tickets là). On prend des décisions sur des données fausses (orphelins, retours en trop). Des données personnelles fuient, avec un risque RGPD. On ne sait plus expliquer d'où vient un chiffre. Les coûts de stockage augmentent sans contrôle. Et des données supplémentaires inventées se mélangent aux données TPCx-BB sans que personne le sache.
