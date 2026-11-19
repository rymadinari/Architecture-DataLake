# Retail Intelligence Platform – Jour 4 : analyser les données et préparer le passage au cloud

TP-J4 UC-08 et UC-07 · IPSSI Mastère Data & IA · Ryma Dinari · 19/11/2026 · projet fait seule

## En deux mots

- **UC-08 (analyse)** : je reprends les données propres du TP3. Je calcule des indicateurs (chiffre d'affaires, nombre de tickets, panier moyen…), je fais des graphiques et j'explique ce qu'ils montrent.
- **UC-07 (architecture)** : j'explique comment on rangerait ces données dans Azure (le cloud de Microsoft), et comment on fait la même chose sans Azure, avec des outils gratuits sur mon PC.

**Je n'ai pas d'accès Azure.** J'ai donc choisi le **parcours B** (sur mon PC, avec des outils gratuits). Pour Azure, j'ai seulement préparé les plans et les commandes : **rien n'a été créé dans Azure**.

Les parties facultatives (complémentaire et avancée) ne sont pas faites.

## Outils utilisés

| Outil | Version | À quoi il sert |
|---|---|---|
| Ubuntu | 24.04.4 | système de mon PC (12 cœurs, 15 Go de mémoire) |
| Python | 3.12.3 | langage utilisé ; je reprends l'environnement du TP3 (`~/TP3/.venv`) |
| Spark / PySpark | 4.3.0 | faire les gros calculs ; il tourne sur mon PC (`local[*]`) |
| Java | 17.0.21 | nécessaire pour faire tourner Spark |
| JupyterLab | 4.6.6 | écrire et lancer le notebook |
| Pandas | 3.1.1 | manipuler les petits tableaux de résultats |
| Matplotlib | 3.11.2 | dessiner les graphiques |

Spark affiche un message qui dit qu'il n'est « pas encore totalement compatible » avec Pandas 3. Ce n'est pas grave ici : je ne passe à Pandas que de tout petits tableaux. Le message est caché dans le notebook.

## Installation

Je reprends l'environnement du TP3. J'ai juste ajouté les outils pour les graphiques :

```bash
source ~/TP3/.venv/bin/activate
python -m pip install matplotlib pandas jupyterlab ipykernel
```

## Données utilisées

Ce sont les fichiers produits au TP3. Je les lis, je ne les modifie jamais. Les chemins sont dans `config.py` :

- `~/TP3/data/silver/` : données nettoyées (ventes, magasins, dates) ;
- `~/TP3/data/gold/` : données déjà regroupées (ventes par magasin et par mois, ventes par catégorie et par année).

Si ces dossiers n'existent plus, il faut relancer les notebooks 02 et 03 du TP3. Plus de détails : `docs/business-analysis.md` (partie 0).

## Lancer le projet

```bash
cd ~/TP4
source ~/TP3/.venv/bin/activate
jupyter lab
```

Puis ouvrir `TP4_Retail_Intelligence.ipynb` et faire **Run → Restart Kernel and Run All Cells**. Ça prend environ 1 minute.

Sans ouvrir JupyterLab, on peut aussi lancer :

```bash
jupyter nbconvert --to notebook --execute --inplace TP4_Retail_Intelligence.ipynb
```

À chaque lancement, le notebook recrée tous les tableaux (`resultats/`) et tous les graphiques (`graphiques/`).

## Résultats principaux

Ventes en magasin du 1er janvier 2001 au 13 décembre 2005 :

| Indicateur | Résultat |
|---|---|
| K1 – Chiffre d'affaires | 1 150 529 586,37 |
| K2 – Nombre de tickets | 89 100 (pour 667 579 lignes de vente) |
| K3 – Panier moyen (montant moyen d'un ticket) | 12 912,79 (la moitié des tickets est sous 11 641) |
| K4 – Quantité vendue | 33 755 474 articles |
| K7 – Évolution d'une année sur l'autre (même période) | entre −1,53 % et +1,11 % |
| K11 – Chiffre d'affaires par employé | de 324 089 à 454 218 selon le magasin |

Ce que j'en retiens :
- le chiffre d'affaires ne bouge presque pas, et il n'y a pas de pic à Noël ;
- les 12 magasins vendent presque autant (5 % d'écart), mais si on divise par le nombre d'employés, l'écart monte à 40 % ;
- deux catégories (Music et Books) font 72 % des ventes.

**Attention : ce sont des données inventées par un programme (TPCx-BB).** La méthode est bonne, mais les chiffres ne parlent pas d'un vrai magasin. Plus de détails : `docs/interpretation.md`.

## Contenu du dossier

```
TP4/
├── README.md                        ce fichier (J4-11)
├── TP4_Retail_Intelligence.ipynb    le notebook de l'analyse (avec ses résultats)
├── config.py                        chemins des fichiers et démarrage de Spark
├── resultats/                       les tableaux de résultats (CSV), recréés par le notebook
├── graphiques/                      les 4 graphiques (PNG), recréés par le notebook
├── preuves/                         2 captures d'écran : le notebook a bien tourné sur mon PC
└── docs/
    ├── business-analysis.md         J4-01, J4-03 à J4-05 : données, statistiques, analyses
    ├── kpi-dictionary.md            J4-02 : les indicateurs
    ├── interpretation.md            J4-06 : conclusions, limites, conseils
    ├── azure-architecture.md        J4-07 : architecture Azure et version sans Azure
    ├── architecture_azure_cible.png         schéma Azure (prévu, pas créé)
    ├── architecture_locale_open_source.png  schéma sur mon PC (utilisé)
    ├── adls-organization.md         J4-08 : rangement des données dans Azure
    ├── security-matrix.md           J4-09 : qui a le droit de faire quoi
    ├── simulation-azure.md          J4-10 : ce qu'on aurait fait dans Azure
    └── questions-de-recul.md
```

## Où trouver chaque livrable (§13.1)

| Code | Livrable | Fichier | État |
|---|---|---|---|
| J4-01 | Liste des données utilisées | `docs/business-analysis.md` (partie 0) + partie 2 du notebook | Fait |
| J4-02 | Dictionnaire des indicateurs | `docs/kpi-dictionary.md`, `resultats/kpi.csv` | Fait (6 indicateurs) |
| J4-03 | Statistiques | partie 4 du notebook, `resultats/statistiques.csv` | Fait |
| J4-04 | Analyses métier | parties 5 à 7 du notebook, `docs/business-analysis.md` | Fait (2 + 1 en bonus) |
| J4-05 | Graphiques | `graphiques/*.png` | Fait (4) |
| J4-06 | Conclusions | `docs/interpretation.md` | Fait |
| J4-07 | Architecture Azure | `docs/azure-architecture.md` + les 2 schémas PNG | Fait (sur papier) |
| J4-08 | Rangement dans ADLS Gen2 | `docs/adls-organization.md` | Fait (sur papier) |
| J4-09 | Sécurité | `docs/security-matrix.md` | Fait (sur papier) |
| J4-10 | Preuves Azure | `docs/simulation-azure.md` | **Simulation** : rien n'a été créé |
| J4-11 | README | ce fichier | Fait |

## Vérifications (§12)

### UC-08 – Analyse

| Vérification | État | Preuve |
|---|---|---|
| Les données utilisées sont identifiées | ☑ | `docs/business-analysis.md` (partie 0) |
| Ce que représente une ligne (granularité) a été vérifié | ☑ | notebook partie 2 (0 doublon, 1 ticket = 1 magasin) |
| Les indicateurs ont une définition claire | ☑ | `docs/kpi-dictionary.md` |
| Les calculs peuvent être refaits | ☑ | notebook (Run All recrée tout), `preuves/capture_notebook_controles.png` |
| Les statistiques sont cohérentes avec les données | ☑ | même total Silver / Gold / par ticket (1 150 529 586,37) |
| Les graphiques sont lisibles et ont une légende | ☑ | `graphiques/` (titre, axes, unité, source), `preuves/capture_notebook_graphique.png` |
| Les interprétations sont justifiées | ☑ | `docs/interpretation.md` |
| Les limites des données sont écrites | ☑ | `docs/interpretation.md`, partie « Limites » de ce README |

### UC-07 – Architecture

| Vérification | État | Preuve |
|---|---|---|
| Le rôle d'ADLS Gen2 est expliqué | ☑ | `docs/azure-architecture.md` |
| Le rôle du HNS est expliqué | ☑ | `docs/adls-organization.md` (partie 3) |
| Les zones Bronze, Silver et Gold sont organisées | ☑ | `docs/adls-organization.md` + les 2 schémas |
| Les chemins et les règles de nom sont écrits | ☑ | `docs/adls-organization.md` (parties 1 et 2) |
| La sécurité et les accès sont étudiés | ☑ | `docs/security-matrix.md` |
| Les rôles d'ADF et de Synapse sont expliqués | ☑ | `docs/azure-architecture.md` (partie 2) |
| On voit clairement ce qui est simulé et ce qui est utilisé | ☑ | `docs/simulation-azure.md`, schémas (couleurs différentes) |
| Les coûts et les limites d'accès sont pris en compte | ☑ | `docs/azure-architecture.md` (partie 6) |

## Limites

- Données inventées (TPCx-BB). Seules les ventes en magasin sont analysées : pas le site web, pas les retours.
- Décembre 2005 n'a que 13 jours (le deuxième lot de données n'a pas été traité au TP3).
- Je n'utilise pas la marge (74 % des ventes sont à perte, ce n'est pas réaliste) ni le chiffre d'affaires par m² (les surfaces des magasins sont fausses).
- Rien n'a été créé dans Azure : tout ce qui concerne Azure est expliqué, mais pas testé.
- Tout tourne sur mon PC, pas sur plusieurs machines.
