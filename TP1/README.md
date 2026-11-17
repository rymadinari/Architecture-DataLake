# J1 — Retail Intelligence Platform

TP Jour 1 · IPSSI · Mastère Développement, Data & IA — socle obligatoire **UC-01** et **UC-02**.

Données analysées : kit `retail_project` (TPCx-BB) fourni par le formateur via Teams le 16/11/2026 (`data/` + `data_refresh/`, 36 fichiers, ≈ 1,03 Go ; version non communiquée).

## Contenu

```
J1_Retail_Intelligence/
├── README.md
├── 01_UC01_besoin_exploration/
│   ├── UC01_cadrage_metier.pdf             fiche de cadrage, kit, utilisateurs, schéma fonctionnel
│   ├── UC01_questions_decisionnelles.pdf   matrice profils × questions × décisions × KPI
│   ├── UC01_dictionnaire_KPI.xlsx          13 KPI (9 attributs + statut + valeur de contrôle sur le kit)
│   ├── UC01_inventaire_sources.xlsx        onglets Kit / Fichiers / Colonnes / Relations / Domaines
│   ├── UC01_qualification_donnees.pdf      formats, nulls, 14 anomalies, clés, relations
│   ├── UC01_limites_et_hypotheses.pdf      11 limites, 8 hypothèses, questions de recul
│   └── preuves/                            arborescence, extraits, résultats des contrôles, CSV de profilage, schéma,
│                                           captures terminal (arborescence, aperçu store_sales, volumes,
│                                           contrôle du nombre de colonnes)
├── 02_UC02_architecture/
│   ├── UC02_comparaison_architectures.pdf  contraintes + DW / Data Lake / Lakehouse
│   ├── UC02_architecture_cible.pdf         schéma logique, zones Bronze/Silver/Gold, modèle Gold
│   ├── UC02_schema_flux.pdf                10 flux décrits (source → consommateur), batch / continu
│   ├── UC02_positionnement_composants.pdf  matrice des composants selon leur statut
│   ├── UC02_gouvernance.pdf                provenance, qualité, accès, protection, suivi, coûts
│   ├── UC02_local_vers_azure.pdf           local Ubuntu vs cible ADLS Gen2 (conception logique)
│   └── preuves/                            captures des schémas
├── 05_contribution_individuelle/
│   └── contribution_ryma_dinari.pdf
└── scripts/                                profilage et génération des livrables (reproductibles)
```

Les parties complémentaire (UC-C1, UC-C2) et avancée (UC-A1) ne sont pas réalisées : les dossiers `03_complementaire/` et `04_avance/` sont donc absents. Projet réalisé seule : la contribution individuelle est dans `05_contribution_individuelle/contribution_ryma_dinari.pdf`.

## Principaux constats

- Fichiers texte `|`, **sans en-tête**, fins de ligne **CRLF** ; noms de colonnes repris du schéma TPCx-BB (statut *Déduit*), nombre de colonnes vérifié sur 100 % des lignes.
- Ventes du 01/01/2001 au 13/12/2005 (lot initial), complétées jusqu'au 31/12/2005 par `data_refresh/` (lot d'ajout, clés disjointes).
- Toutes les relations faits → référentiels sont vérifiées sans orphelin, **sauf** `inventory` → `item` (180 produits définis uniquement dans le refresh) et 407 retours du refresh sans vente d'origine.
- Données synthétiques : marge négative sur 74 % des lignes magasin, remise moyenne de 50 %, libellés aléatoires (motifs de retour, transporteurs), dates de référentiels irréalistes.
- Architecture retenue : Data Lake Bronze / Silver / Gold sur HDFS en Parquet, zone Gold en étoile, ingestion NiFi, traitements Spark ; déclinaison sur ADLS Gen2 ; Delta Lake et HBase restent facultatifs.

## Reproduire

```bash
cd TP1
python3 -m venv .venv && .venv/bin/pip install duckdb pandas openpyxl markdown
.venv/bin/python J1_Retail_Intelligence/scripts/profilage.py    # ~3 min, écrit les preuves UC-01
.venv/bin/python J1_Retail_Intelligence/scripts/build_xlsx.py   # dictionnaire KPI + inventaire
```
