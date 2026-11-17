# UC-02 — Environnement local et cible Azure

Retail Intelligence Platform · Jour 1 · Livrable 6/6 de l'UC-02

La partie Azure est un plan. Rien n'a été créé sur Azure au Jour 1 ; ce sera fait au Jour 4. Les noms proposés ci-dessous sont des exemples.

## 1. La même architecture, en deux versions

<div class="diag">
<div class="col"><div class="t">Local — Linux / Ubuntu</div>
<div class="box">Dépôt : dossier <code>landing/</code></div>
<div class="box">Réception : <b>Apache NiFi</b></div>
<div class="box bronze">HDFS <code>/datalake/bronze</code></div>
<div class="box">Traitement : <b>Spark / PySpark</b></div>
<div class="box silver">HDFS <code>/datalake/silver</code> (Parquet)</div>
<div class="box gold">HDFS <code>/datalake/gold</code> (Parquet)</div>
<div class="box">Droits : utilisateurs et groupes Linux + droits HDFS</div>
<div class="box">Mots de passe : fichier protégé, hors Git</div>
</div>
<div class="arrow">⇄</div>
<div class="col"><div class="t">Cloud — Azure</div>
<div class="box">Dépôt : conteneur <code>landing</code></div>
<div class="box">Réception : <b>Azure Data Factory</b> (étude)</div>
<div class="box bronze">ADLS Gen2, conteneur <code>bronze</code></div>
<div class="box">Traitement : <b>Synapse Spark</b> (étude), même code PySpark</div>
<div class="box silver">ADLS Gen2, conteneur <code>silver</code></div>
<div class="box gold">ADLS Gen2, conteneur <code>gold</code> (+ requêtes SQL Synapse)</div>
<div class="box">Droits : Microsoft Entra ID + RBAC + ACL</div>
<div class="box">Mots de passe : Azure Key Vault + identités managées</div>
</div>
</div>

## 2. Correspondance outil par outil

| Rôle | En local (parcours) | Sur Azure | Remarque |
|---|---|---|---|
| Système | Linux / Ubuntu | Services gérés par Azure | Plus de serveur à entretenir soi-même. |
| Stockage | Hadoop / HDFS | **ADLS Gen2** (un compte de stockage avec de vrais dossiers) | Spark lit ADLS Gen2 comme HDFS : seul le début du chemin change (`hdfs://` devient `abfss://`). |
| Réception et enchaînement | Apache NiFi | Azure Data Factory | Copie des fichiers, déclenchement automatique, suivi des exécutions. |
| Traitement | Spark / PySpark | Synapse Spark (ou Azure Databricks) | On réutilise le même code PySpark ; seuls les chemins changent. |
| Requêtes | Spark SQL | Synapse SQL serverless sur les fichiers Gold | Payé selon la quantité de données lue. |
| Format | Parquet | Parquet (Delta Lake possible, facultatif) | Identique. |
| Identités | Comptes Linux / HDFS | Microsoft Entra ID (utilisateurs, groupes, identités des services) | Connexion centralisée. |
| Droits | Droits HDFS sur les dossiers | RBAC (droits larges, sur tout un espace) + ACL (droits fins, dossier par dossier) | Même logique : des droits différents par zone. |
| Mots de passe et clés | Fichier local protégé | Azure Key Vault (coffre-fort) | Rien dans le code ni dans les traitements. |
| Surveillance | Interface NiFi, journaux Spark | Azure Monitor, Log Analytics, suivi Data Factory | — |

## 3. Détails de la version Azure

### 3.1 Compte de stockage

- Nom proposé : `stretailintel<env>` (par exemple `stretailinteldev`), un compte pour le développement et un pour la production.
- Type : **StorageV2**, avec l'option « espace de noms hiérarchique » activée. C'est cette option qui en fait un ADLS Gen2 : de vrais dossiers, des renommages instantanés et des droits par dossier.
- Copies de sécurité : LRS (copies dans un seul centre de données) en développement ; ZRS ou GRS (copies dans plusieurs zones ou régions) en production, selon le besoin. <span class="s a">À valider</span>
- Région : une région européenne (par exemple France Central), pour la proximité et le respect du RGPD. <span class="s a">À valider</span>
- Réseau : accès public fermé en production, accès uniquement par un lien privé ; données chiffrées sur le disque (par défaut) ; connexions HTTPS obligatoires.

### 3.2 Conteneurs et rangement des données

Un **conteneur** est un grand dossier de premier niveau dans le compte de stockage.

| Conteneur | Contenu | Rangement |
|---|---|---|
| `landing` | Dépôt temporaire des lots reçus | `tpcxbb/<lot>/…` |
| `bronze` | Fichiers d'origine + fiches de lot | `tpcxbb/<table>/batch_id=<lot>/<fichier>.dat` ; `complementaire/<source>/…` |
| `silver` | Parquet propre et contrôlé | `tpcxbb/<table>/<date>=AAAA-MM-JJ/part-*.parquet` |
| `quarantine` | Lignes rejetées | `tpcxbb/<table>/batch_id=<lot>/` + raison |
| `gold` | Étoile + totaux | `fact_sales/sold_date=…/`, `dim_item/`, `agg_sales_daily/`… |

### 3.3 Identités et accès

| Groupe Entra ID | Rôle RBAC (sur quoi) | ACL en plus |
|---|---|---|
| Identité de Data Factory | *Storage Blob Data Contributor* (lecture + écriture) sur `landing` et `bronze` | — |
| Identité de Synapse | *Storage Blob Data Reader* (lecture) sur `bronze` ; *Contributor* sur `silver`, `quarantine`, `gold` | — |
| `grp-data-engineers` (U7) | *Storage Blob Data Reader* sur tout le compte | Écriture sur `silver/sandbox` |
| `grp-finance` (U4) | Aucun rôle large | ACL lecture sur `gold/` |
| `grp-business` (U1, U2, U3, U5, U6) | Aucun rôle large | ACL lecture sur `gold/agg_*` ; filtre par magasin dans l'outil de tableaux de bord |

- **RBAC** donne des droits larges (tout un compte ou tout un conteneur) ; les **ACL** donnent des droits précis, dossier par dossier. Attention : si une personne a un rôle RBAC sur un conteneur, Azure ne regarde même pas les ACL. C'est pourquoi les profils métier n'ont **pas** de rôle RBAC, seulement des ACL.
- Pas de clé de compte ni de lien d'accès longue durée dans les traitements : les services se connectent avec leur propre identité (« identité managée »).

### 3.4 Protection des mots de passe et des clés

- Azure Key Vault garde les informations de connexion et les éventuelles clés de sources externes ; les services y accèdent avec leur identité.
- Les secrets sont changés régulièrement, et chaque accès au coffre est enregistré.
- La valeur secrète qui sert à rendre les clients anonymes est gardée dans Key Vault, jamais dans le code.

### 3.5 Coûts et limites

| Poste | Ce qui fait varier le coût | Comment le maîtriser |
|---|---|---|
| Stockage ADLS | Quantité stockée × niveau de stockage + nombre d'opérations | Environ 1 Go aujourd'hui (coût très faible) ; Bronze passe automatiquement en stockage moins cher (*cool* puis *archive*) après quelques mois. |
| Data Factory | Nombre d'exécutions et durée des copies | Lancement seulement quand un lot arrive, pas de vérification en permanence. |
| Synapse Spark | Taille des machines × durée | Petites machines, mise en pause automatique après quelques minutes sans activité. |
| Synapse SQL serverless | Quantité de données lue | Parquet + rangement par date = moins de données lues ; requêtes sur les totaux Gold. |
| Suivi financier | — | Budget et alertes dans Azure Cost Management, étiquettes (`projet=retail-intel`, `env=dev`). |
| Limites (quotas) | Nombre de processeurs autorisés par région et par abonnement, limites d'un compte étudiant | À vérifier avant le Jour 4. <span class="s a">À valider</span> |

## 4. Comparaison rapide

| Critère | Local Linux | Azure |
|---|---|---|
| Coût | Matériel déjà disponible, rien à payer | Payé à l'usage ; faible pour ce volume, mais à surveiller (Spark) |
| Mise en place | Installation et réglages à la main (HDFS, NiFi, Spark) | Services prêts à l'emploi, plus rapides à configurer |
| Montée en charge | Limitée par l'ordinateur (16 Go de RAM conseillés) | On ajoute de la puissance quand on veut |
| Sécurité | Comptes locaux, peu centralisés | Entra ID, RBAC/ACL, Key Vault, chiffrement automatique |
| Disponibilité | Une seule machine | Copies de sécurité LRS/ZRS/GRS |
| Intérêt pédagogique | Comprendre chaque outil | Comprendre le fonctionnement du cloud |
| Passage de l'un à l'autre | Mêmes zones, même code PySpark, même format Parquet : seuls les chemins (`hdfs://` → `abfss://`), l'outil d'enchaînement et la gestion des identités changent. | |

## 5. Limites

- Ce plan n'a pas été testé : les rôles RBAC, les quotas et les coûts devront être vérifiés sur le vrai abonnement au Jour 4.
- Le choix entre Synapse et Databricks pour le traitement reste ouvert ; le parcours cite Synapse.
- Si Azure n'est pas accessible, ce plan reste une simulation, à distinguer d'une vraie installation (§5.2.19).
