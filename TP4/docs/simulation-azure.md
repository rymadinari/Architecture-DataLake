# Ce qu'on aurait fait dans Azure : simulation (J4-10, UC-07 étape 4)

> **C'EST UNE SIMULATION.** Je n'ai rien créé dans Azure. Il n'y a donc aucune capture d'écran d'Azure. Les seules preuves du TP4 concernent ce qui a tourné sur mon PC (le notebook, les graphiques, les tableaux).

## 1. Pourquoi une simulation

- Je n'ai pas d'abonnement Azure autorisé pour ce TP
- L'outil Azure CLI n'est pas installé sur mon PC 

## 2. Le rangement prévu

Voir `docs/adls-organization.md` (les dossiers raw, bronze, silver, gold, quality, complementaire, documentation) et le schéma `architecture_azure_cible.png` (dans ce dossier).

## 3. Ce qu'il aurait fallu créer dans Azure

| Élément | Nom prévu | Réglages | Obligatoire ? |
|---|---|---|---|
| Abonnement | celui de l'école | budget surveillé | Oui |
| Groupe de ressources | `rg-retail-intelligence-dev` | en France (France Central) | Oui |
| Budget avec alertes | `budget-retail-tp4` | 10 par mois, alerte à 50 % et 80 % | Oui (pour éviter les mauvaises surprises) |
| Compte de stockage | `stretailintelfrc01` | option la moins chère (LRS), **HNS activé**, connexions chiffrées, pas d'accès public, pas de clé partagée | Oui |
| Conteneur | `retail-intelligence` | privé | Oui |
| Groupes d'utilisateurs | ingestion, data, analystes, admins | voir `security-matrix.md` | Oui (au moins sur le papier) |
| Coffre-fort à secrets (Key Vault) | `kv-retail-dev` | pour les mots de passe | Non (aucun mot de passe au TP4) |
| Data Factory | `adf-retail-dev` | — | Non (seulement étudié) |
| Synapse (Spark + SQL) | `syn-retail-dev` | petite taille, arrêt automatique après 15 min | Non (seulement étudié) |

## 4. Les étapes

Les commandes complètes sont à la fin de ce fichier (partie 7). **Je ne les ai jamais lancées.**

1. Se connecter à Azure et vérifier l'abonnement et ses droits.
2. Créer le groupe de ressources et un **budget**.
3. Créer le compte de stockage avec le **HNS activé** (c'est ce qui en fait un ADLS Gen2).
4. Me donner le droit d'écrire, **seulement sur le conteneur**.
5. Créer le conteneur et les dossiers des zones.
6. Déposer un petit fichier de test autorisé : `resultats/kpi.csv` (1 Ko, juste des totaux, aucune donnée personnelle) dans `gold/analyses/kpi/`.
7. Le retélécharger et vérifier qu'il est identique (même empreinte).
8. Donner aux analystes le droit de lire `gold/`.
9. Tout supprimer à la fin.

## 5. Les vérifications qu'on aurait faites

| Ce qu'on vérifie | Comment | Résultat attendu |
|---|---|---|
| Le compte est bien un ADLS Gen2 | regarder l'option `isHnsEnabled` | `true` |
| Le compte est protégé | regarder l'accès public et le chiffrement | pas d'accès public, chiffrement TLS 1.2 |
| Les dossiers existent | lister le contenu du conteneur | les 12 dossiers des zones |
| Le fichier est arrivé intact | le retélécharger et comparer les empreintes | empreintes identiques |
| Les droits sont posés | afficher les droits de `gold/` | les analystes peuvent lire |
| Les analystes n'ont pas trop de droits | se connecter comme analyste et essayer d'écrire dans `gold/` ou de lire `raw/` | refusé (erreur 403) |
| Spark arrive à lire le fichier | `spark.read.csv("abfss://retail-intelligence@stretailintelfrc01.dfs.core.windows.net/gold/analyses/kpi/")` | 9 lignes |
| Ce que ça coûte | regarder les coûts après 24 h | quelques centimes, budget pas dépassé |
| Tout est bien supprimé | lister les groupes de ressources | le groupe n'existe plus |

## 6. Ce qui a été fait ou non

| Action | État |
|---|---|
| Plan du rangement dans ADLS Gen2 | **Fait** (document) |
| Schéma de l'architecture Azure | **Fait** (document et image) |
| Tableau des droits d'accès | **Fait** (document) |
| Écriture des commandes | **Fait** (script jamais lancé) |
| Création du groupe de ressources, du compte, du conteneur | **Pas fait** |
| Dépôt et relecture d'un fichier dans Azure | **Pas fait** |
| Pose des droits et test de refus | **Pas fait** |
| Data Factory, Synapse | **Pas fait** (pas demandé au socle) |
| Préparation du fichier de test (`resultats/kpi.csv`) | **Fait** (sur mon PC) |
| Rangement en zones vraiment utilisé (HDFS au TP2, `~/TP3/data`) | **Fait** |

## 7. Les commandes Azure (jamais lancées)

Voici les commandes qu'on aurait tapées dans un terminal avec l'outil Azure CLI. Elles sont là pour montrer la démarche : **je ne les ai pas lancées**, il ne faut pas les lancer sans l'accord du formateur (ça crée des choses payantes).

```bash
# --- Les noms utilisés (aucun mot de passe ici) -------------------------------------------
RG="rg-retail-intelligence-dev"
LOC="francecentral"
SA="stretailintelfrc01"            # 3 à 24 lettres minuscules ou chiffres, unique dans tout Azure
FS="retail-intelligence"          # le conteneur (le dossier principal)

# --- 0. Se connecter et vérifier l'abonnement --------------
az login
az account show --output table                  # quel abonnement ? est-il actif ?
az provider show -n Microsoft.Storage --query registrationState

# --- 1. Créer le groupe de ressources et un budget ----------------------------
az group create --name "$RG" --location "$LOC" --tags projet=retail-intelligence env=dev
az consumption budget create --budget-name budget-retail-tp4 --amount 10 \
  --category cost --time-grain monthly \
  --start-date 2026-11-01 --end-date 2027-01-31 --resource-group "$RG"
# (les alertes par e-mail à 50 % et 80 % du budget se règlent sur le site Azure, dans Cost Management)

# --- 2. Créer le compte de stockage avec le HNS (= ADLS Gen2) --------------
az storage account create \
  --name "$SA" --resource-group "$RG" --location "$LOC" \
  --sku Standard_LRS --kind StorageV2 \
  --hns true \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false \
  --allow-shared-key-access false              # pas de clé partagée : on se connecte avec Entra ID

# Vérifier que le compte est bien un ADLS Gen2 et qu'il est protégé
az storage account show -n "$SA" -g "$RG" \
  --query "{kind:kind, hns:isHnsEnabled, sku:sku.name, tls:minimumTlsVersion, public:allowBlobPublicAccess}"
# attendu : kind=StorageV2, hns=true, sku=Standard_LRS, tls=TLS1_2, public=false

# --- 3. Me donner le droit d'écrire, seulement dans le conteneur -------
MOI=$(az ad signed-in-user show --query id -o tsv)
SCOPE=$(az storage account show -n "$SA" -g "$RG" --query id -o tsv)
az role assignment create --assignee "$MOI" --role "Storage Blob Data Contributor" \
  --scope "$SCOPE/blobServices/default/containers/$FS"

# --- 4. Créer le conteneur et les dossiers des zones ----------------------------------
az storage fs create -n "$FS" --account-name "$SA" --auth-mode login
for d in raw/tpcxbb bronze/tpcxbb \
         silver/ventes silver/produits silver/magasins silver/referentiel \
         gold/indicateurs gold/analyses \
         quality/rapports quality/quarantine complementaire documentation; do
  az storage fs directory create -n "$d" -f "$FS" --account-name "$SA" --auth-mode login
done

# --- 5. Déposer un petit fichier de test -------------------------
# Fichier sans données personnelles : les indicateurs calculés au TP4 (1 Ko)
az storage fs file upload -s resultats/kpi.csv \
  -p gold/analyses/kpi/kpi.csv -f "$FS" --account-name "$SA" --auth-mode login

# --- 6. Vérifier que le fichier est bien là et intact -------------------------------
az storage fs file list -f "$FS" --path gold/analyses --recursive \
  --account-name "$SA" --auth-mode login --output table
az storage fs file download -p gold/analyses/kpi/kpi.csv -d /tmp/kpi_relu.csv \
  -f "$FS" --account-name "$SA" --auth-mode login
sha256sum resultats/kpi.csv /tmp/kpi_relu.csv   # les deux codes doivent être identiques

# --- 7. Droits par dossier : les analystes peuvent seulement lire gold/ ----------------------
GRP_ANALYSTES=$(az ad group show -g grp-retail-analystes --query id -o tsv)
# x sur la racine (pour passer), lecture sur gold/, et les mêmes droits pour les futurs fichiers
az storage fs access set --acl "user::rwx,group::r-x,other::---,group:$GRP_ANALYSTES:--x" \
  -p / -f "$FS" --account-name "$SA" --auth-mode login
az storage fs access set-recursive \
  --acl "group:$GRP_ANALYSTES:r-x,default:group:$GRP_ANALYSTES:r-x" \
  -p gold -f "$FS" --account-name "$SA" --auth-mode login
az storage fs access show -p gold -f "$FS" --account-name "$SA" --auth-mode login

# --- 8. À la fin : tout supprimer d'un coup (le groupe de ressources entier) ------
az group delete --name "$RG" --yes --no-wait
```
