# Retail Intelligence Platform – Jour 3 : transformation, qualité et Parquet

TP-J3-UC06 · IPSSI Mastère Data & IA · Ryma Dinari · 18/11/2026

À partir des fichiers bruts TPCx-BB des jours 1 et 2, je produis des données nettoyées (Silver) et des indicateurs (Gold) en Parquet avec PySpark, puis je vérifie leur qualité.

Partie réalisée : **UC-06 (obligatoire)**. Les parties UC-05 (HBase) et Lakehouse avancée, facultatives, n'ont pas été faites.

## Prérequis et versions

| Outil | Version |
|---|---|
| Ubuntu | 24.04.4 LTS |
| Python | 3.12.3 |
| PySpark / Spark | 4.3.0 |
| Java | OpenJDK 17.0.21 (`~/opt/jdk-17`, installé au jour 2) |
| JupyterLab | 4.6.6 |

Exécution en **local** (`local[*]`) sur mon PC, pas sur un cluster. Détails dans `docs/fiche-environnement.md`.

## Installation

```bash
cd ~/TP3
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyspark jupyterlab ipykernel
```

## Données

- **Entrée** : `~/TP1/retail_project/data/` (kit TPCx-BB, mêmes fichiers que ceux déposés dans HDFS au jour 2 sous `/retail-lake/raw/tpcxbb/initial/`). Ces fichiers ne sont jamais modifiés.
- **Sources utilisées** : `store_sales`, `item`, `store`, `date_dim` (voir `docs/inventaire-sources.md`).
- Tous les chemins sont dans `config.py`. Pour lire ailleurs (par exemple depuis HDFS), il suffit de changer `SOURCE`.

## Ordre d'exécution

```bash
cd ~/TP3
source .venv/bin/activate
jupyter lab
```
Puis ouvrir et exécuter dans l'ordre (*Run → Run All Cells*) :

| # | Notebook | Étapes du TP | Ce qu'il fait |
|---|---|---|---|
| 1 | `notebooks/01_exploration.ipynb` | 1, 2, 3 | Environnement, inventaire, exploration (nulls, doublons, valeurs atypiques, relations) |
| 2 | `notebooks/02_nettoyage_silver.ipynb` | 4, 5, 6 | Règles de nettoyage, typage, écriture du Silver |
| 3 | `notebooks/03_gold_parquet.ipynb` | 5, 7, 8 | Jointures, agrégations, écriture du Gold, comparaison des formats |
| 4 | `notebooks/04_qualite.ipynb` | 9 | Contrôles qualité et rapport |

Le notebook 02 doit être lancé avant le 03, et le 03 avant le 04 (chacun lit les sorties du précédent). Durée totale : quelques minutes.

## Sorties produites

| Zone | Chemin | Contenu | Lignes |
|---|---|---|---|
| Silver | `data/silver/sales` | ventes magasin nettoyées | 667 579 |
| Silver | `data/silver/products` | produits | 17 820 |
| Silver | `data/silver/stores` | magasins | 12 |
| Silver | `data/silver/dates` | calendrier | 109 573 |
| Gold | `data/gold/ventes_magasin_mois` | CA, quantité, tickets, panier moyen, marge par magasin et par mois (Q1, Q5) | 720 |
| Gold | `data/gold/ventes_categorie_annee` | CA, quantité, part du CA par catégorie et par année (Q3) | 45 |
| Quarantaine | `data/quarantine/<domaine>` | lignes écartées, créé seulement s'il y en a (aucune aujourd'hui) | 0 |

Tout est en Parquet. Chaque table Silver garde sa provenance (`source_fichier`, `date_traitement`). Le dossier `data/` n'est pas versionné dans Git (il se recrée en relançant les notebooks).

## Contrôles disponibles

Le notebook 04 vérifie la complétude, l'unicité, les types, la cohérence des valeurs, les volumes et l'intégrité des relations, sur le Silver et le Gold.
Résultat : **42 OK, 6 ATTENTION, 0 KO**. Rapport : `preuves/controles_qualite.csv`.

## Limites connues

- Données synthétiques TPCx-BB : les résultats montrent que la chaîne marche, pas la réalité d'une enseigne.
- 2005 est incomplète (ventes jusqu'au 13/12) dans le lot principal ; le lot `data_refresh` n'est pas traité.
- 74 % de marges négatives et un panier moyen d'environ 13 000 € : effets du générateur.
- Seules les ventes magasin sont traitées (pas le web ni les retours).
- Parquet seul n'offre pas de transactions ni d'historique de versions.
- Exécution locale sur un seul PC, pas sur un cluster.

## Contenu du dossier

```
TP3/
├── config.py                  chemins, colonnes et types, session Spark
├── notebooks/                 01 à 04 (avec leurs résultats)
├── docs/
│   ├── fiche-environnement.md
│   ├── inventaire-sources.md
│   └── questions-de-recul.md
├── preuves/controles_qualite.csv
├── data/                      silver/, gold/, test/ (non versionné)
└── README.md
```

## Correspondance avec les livrables (§10.2)

| # | Livrable | Où |
|---|---|---|
| 1 | Fiche environnement | `docs/fiche-environnement.md` |
| 2 | Inventaire technique | `docs/inventaire-sources.md` |
| 3 | Notebook d'exploration | `notebooks/01_exploration.ipynb` |
| 4 | Règles de nettoyage | tableau au début de `notebooks/02_nettoyage_silver.ipynb` |
| 5 | Scripts PySpark | `config.py` et les notebooks 02 et 03 |
| 6 | Données Silver | `data/silver/` |
| 7 | Données Gold | `data/gold/` + définitions dans le notebook 03 |
| 8 | Données Parquet | écriture et relecture dans les notebooks 02 et 03 |
| 9 | Rapport qualité | `notebooks/04_qualite.ipynb`, `preuves/controles_qualite.csv` |
| 10 | README | ce fichier |
| 11 | Preuves | sorties des notebooks, `preuves/` |
