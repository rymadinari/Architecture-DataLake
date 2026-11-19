# Qui a le droit de faire quoi : la sécurité (J4-09, UC-07 étape 5)

État : **prévu** pour Azure (pas créé). La dernière partie décrit ce qui est **vraiment appliqué** sur mon PC.

## 1. Les groupes d'utilisateurs (dans Entra ID)

| Groupe | Qui | Services liés |
|---|---|---|
| `grp-retail-ingestion` | L'équipe qui reçoit les fichiers | Data Factory (le service qui copie les fichiers) |
| `grp-retail-dataeng` | L'équipe data qui nettoie et calcule (moi, ici) | Synapse (Spark) |
| `grp-retail-analystes` | Les analystes métier, le contrôleur de gestion | Power BI (lecture seulement) |
| `grp-retail-admins` | L'administrateur (2 personnes maximum) | — |

On donne les droits aux **groupes**, jamais directement aux personnes. Quand quelqu'un change d'équipe, on le change juste de groupe.

## 2. Les droits sur chaque dossier (ACL)

Rappel : **r** = lire, **w** = écrire, **x** = ouvrir le dossier pour passer dedans.

| Groupe | raw/ | bronze/ | silver/ | gold/ | quality/ | documentation/ |
|---|---|---|---|---|---|---|
| Ingestion | **Ajouter** de nouveaux fichiers, sans modifier les anciens | Rien | Rien | Rien | Écrire (rapports d'arrivée) | Lire |
| Équipe data | Lire | Lire et écrire | Lire et écrire | Écrire, seulement avec les notebooks validés | Lire et écrire | Lire et écrire |
| Analystes | **Rien** | Rien | Lire certaines tables si besoin (ex. `silver/produits`) | **Lire** | Lire les rapports | Lire |
| Admin | Gère les droits, mais n'utilise pas les données tous les jours | idem | idem | idem | idem | idem |

Pour lire un fichier, il faut le droit **r** sur le fichier, **et** le droit **x** sur tous les dossiers au-dessus.

On met aussi des **droits par défaut** sur chaque zone : comme ça, les nouveaux fichiers écrits par Spark reçoivent tout de suite les bons droits.

## 3. Les rôles (RBAC)

| Qui | Rôle | Sur quoi |
|---|---|---|
| Admins | *Owner* (propriétaire, peut tout gérer) | Le groupe de ressources du projet |
| Équipe data | *Contributor* (peut créer et gérer Synapse, Data Factory) | Le groupe de ressources |
| Tout le monde | *Reader* (voit les ressources, mais pas les données) | Le groupe de ressources |
| Accès aux données | **Pas de grand rôle sur les données** : on passe par les ACL | — |

Pourquoi ce dernier point ? Azure vérifie d'abord le RBAC. Si le RBAC dit « oui », il ne regarde même pas les ACL. Si on donnait à l'équipe data le rôle « *Storage Blob Data Contributor* » sur tout le compte, mes droits par dossier ne serviraient plus à rien pour elle. Donc je ne le fais pas.

## 4. Les différences à bien comprendre

| Notion | C'est quoi | La question | Exemple |
|---|---|---|---|
| **Identité** (Entra ID) | Prouver qui on est : mot de passe + code sur le téléphone pour une personne, ou « identité managée » pour un service Azure (sans mot de passe) | « Qui es-tu ? » | Data Factory se connecte au stockage sans mot de passe |
| **RBAC** | Un rôle sur une ressource **entière** (abonnement, groupe de ressources, compte, conteneur) | « Que peux-tu faire sur cette ressource ? » (large) | L'équipe data peut créer des machines Spark |
| **ACL** | Des droits lire / écrire / ouvrir sur **un dossier ou un fichier** | « Que peux-tu faire dans ce dossier ? » (précis) | Les analystes lisent `gold/`, mais pas `raw/` |
| **Secrets** | Tout ce qui donne un accès : clés du compte, mots de passe, liens d'accès temporaires | « Comment protéger ces clés ? » | Rangés dans **Key Vault** (un coffre-fort Azure), jamais dans Git ni dans un notebook. Mieux encore : on désactive les clés et on utilise Entra ID. |

## 5. Les règles que je suis

1. **Le moins de droits possible** : chacun n'a que ce qu'il lui faut. Personne d'autre que le service de copie ne peut écrire dans `raw/`.
2. **Séparer les rôles** : celui qui reçoit les fichiers ne publie pas les résultats Gold. L'admin gère les droits, mais ne travaille pas sur les données.
3. **Rien de public** : pas d'accès public aux fichiers, connexions chiffrées obligatoires.
4. **Pas de mot de passe en clair** : Key Vault et identités managées ; fichier `.gitignore` dans Git.
5. **Garder une trace** : on enregistre qui a lu ou écrit quoi (journaux du compte de stockage).
6. **Séparer les environnements** : un groupe de ressources pour les tests (`-dev`), un autre plus tard pour la vraie utilisation (`-prod`).
7. **Protéger les données sensibles** : les données clients (noms, adresses, e-mails) iraient dans un dossier `silver/clients/` très protégé, et seraient rendues anonymes si possible. Mon TP4 n'utilise aucune donnée client.

## 6. Ce qui est vraiment appliqué sur mon PC (parcours B)

| Règle | Comment je l'applique |
|---|---|
| Qui je suis | Mon compte Linux personnel, sans droits administrateur |
| Droits | Les droits sur les fichiers de `~/TP*` (moi seule) ; HDFS avec les droits de mon utilisateur (TP2) |
| Ne pas toucher aux fichiers bruts | Les fichiers du kit sont seulement lus, jamais modifiés (empreintes vérifiées au TP2) |
| Mots de passe | Aucun n'est nécessaire ; rien de sensible dans Git (`.gitignore` exclut les données et l'environnement Python) |
| Limite | Je suis la seule utilisatrice : la séparation des rôles n'est pas vraiment testée |
