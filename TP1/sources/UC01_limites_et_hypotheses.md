# UC-01 — Limites, hypothèses et questions de recul

Retail Intelligence Platform · Jour 1 · Livrable 6/6 de l'UC-01

## 1. Limites des données et des indicateurs

| # | Limite | Ce que j'ai vu dans le kit | Conséquence et solution proposée |
|---|---|---|---|
| L1 | **Une table présente ne veut pas dire que toutes ses colonnes sont remplies ou utilisables.** | `i_rec_end_date` toujours vide, `d_holiday` = Y partout, `i_container` toujours identique, textes au hasard dans `reason` et `ship_mode`. | Vérifier chaque colonne, pas seulement chaque table. Les colonnes inutilisables sont listées et ne servent à aucun indicateur. |
| L2 | **Les ventes en magasin et sur le web ne sont pas organisées de la même façon.** | `store_sales` : 23 colonnes, un ticket, un magasin, un client. `web_sales` : 34 colonnes, une commande, un client qui paie et un client livré (parfois différents), un site, une page, un entrepôt, des frais de livraison. | Pour additionner les deux canaux, n'utiliser que les colonnes communes (montant payé, quantité). Ajouter une colonne « canal ». Ne pas compter les frais de livraison web dans le CA comparé. |
| L3 | **Vente, commande, ligne de vente et transaction ne veulent pas dire la même chose.** | Une ligne de `store_sales` = un produit dans un ticket. Un ticket contient en moyenne 7,5 lignes. Une transaction = un ticket (magasin) ou une commande (web). | Nombre de transactions = nombre de tickets **différents**, pas nombre de lignes. Le panier moyen se calcule par ticket. Les numéros de ticket et de commande ne doivent jamais être mélangés. |
| L4 | **Un clic sur le site n'est pas forcément un ajout au panier ni un achat.** | `web_clickstreams` n'indique ni le type d'action ni la session. 90 % des clics ne mènent à aucun achat et 42 % sont anonymes. | Le taux de conversion = clics liés à un achat ÷ total des clics, en s'appuyant sur une hypothèse (H1). On ne peut pas suivre le parcours visite → panier → achat. |
| L5 | **Les retours doivent rester séparés des ventes.** | Fichiers séparés. Des retours arrivent jusqu'à 2 ans après la vente (jusqu'en 2008). 112 retours dépassent la quantité achetée. | Ne jamais retirer les retours du CA sans le dire. On présente trois chiffres distincts : CA brut, montant des retours, CA après retours. Le taux de retour est calculé selon la date de **vente**. |
| L6 | **Si deux chiffres évoluent ensemble, cela ne prouve pas que l'un cause l'autre.** | Avis, promotions et ventes peuvent bouger en même temps. 99,98 % des ventes ont une promotion : il n'y a rien à quoi comparer. | Q4 et Q14 décrivent ce qu'on observe, sans conclure sur les causes. Pour prouver un effet, il faudrait un test (par exemple un groupe avec promotion et un groupe sans). |
| L7 | **Les données sont inventées.** | 74 % des lignes ont une marge négative (marge globale en magasin de −48 %), remise moyenne de 50 %, panier moyen d'environ 12 900 par ticket, magasins presque identiques (CA de 94 à 99 millions), presque aucune différence entre les mois. | Les chiffres ne décrivent pas une vraie entreprise. Le kit sert à tester la chaîne de traitement, pas à prendre des décisions. |
| L8 | **La période est incomplète.** | `data/` s'arrête au 13/12/2005 ; `data_refresh/` complète jusqu'au 31/12/2005. Le stock n'est connu qu'une fois par semaine. | Pour comparer 2005 à 2004, il faut inclure le refresh ou comparer le même nombre de jours. |
| L9 | **Les deux lots dépendent l'un de l'autre.** | Le stock du lot principal utilise 180 produits qui n'existent que dans `data_refresh/item`. | Charger les produits et clients des deux lots avant les ventes et le stock, ou mettre de côté les lignes sans produit. |
| L10 | **Les noms de colonnes ne sont pas dans les fichiers.** | Aucun en-tête : les noms viennent du schéma TPCx-BB. | Un décalage de colonnes passerait inaperçu. À chaque chargement, on vérifie le nombre de colonnes et la cohérence des montants (montant = quantité × prix). |
| L11 | **Il y a des données personnelles.** | `customer` contient nom, prénom, email, identifiant, date et pays de naissance (inventés, mais du même type que de vraies données). | Les protéger comme de vraies données : les rendre anonymes lors du nettoyage et limiter les accès (voir la gouvernance, UC-02). |

## 2. Hypothèses de travail

| # | Hypothèse | Pourquoi je la fais | Comment la vérifier | Statut |
|---|---|---|---|---|
| H1 | `wcs_sales_sk` (dans les clics) contient le numéro de commande web (`ws_order_number`). | Toutes les valeurs existent comme numéro de commande, et il y a autant de clics avec achat que de lignes de vente web. | Documentation TPCx-BB ; vérifier que le produit cliqué fait bien partie de la commande. | <span class="s h">Hypothèse</span> |
| H2 | `pr_order_sk` (dans les avis) désigne une commande web. | Toutes les valeurs existent, mais dans la même plage de nombres. | Vérifier que le produit et le client de l'avis correspondent à la commande. | <span class="s h">Hypothèse</span> |
| H3 | `wcs_user_sk` et `pr_user_sk` désignent des clients. | Aucun orphelin. | Documentation. | <span class="s d">Déduit</span> |
| H4 | `data_refresh/` est un lot à ajouter après `data/`. | Numéros et dates différents, période qui suit. | Confirmation du formateur. | <span class="s a">À valider</span> |
| H5 | Le montant payé (`net_paid` : hors taxes, après remise et coupon) est la bonne base pour le CA. | La relation marge = montant payé − coût d'achat est vraie sur toutes les lignes. | Validation par le contrôle de gestion. | <span class="s a">À valider</span> |
| H6 | Le stock est une photo prise une fois par semaine (pas un mouvement de stock). | 259 dates différentes, espacées d'exactement 7 jours. | Documentation. | <span class="s d">Déduit</span> |
| H7 | Les quelques vides (0,01 à 0,05 %) ont été ajoutés exprès par le générateur. | Taux très faible et identique sur presque toutes les colonnes. | Documentation du générateur. | <span class="s h">Hypothèse</span> |
| H8 | Tous les montants sont dans la même monnaie. | Aucune colonne ne donne la monnaie. | Impossible à vérifier avec le kit. | <span class="s a">À valider</span> |

## 3. Données supplémentaires utiles à l'entreprise

| Besoin non couvert | Donnée à récupérer | Où la trouver |
|---|---|---|
| Vraie rentabilité des magasins | Loyers, salaires, charges | Comptabilité |
| Atteinte des objectifs | Budgets et objectifs par magasin et par mois | Contrôle de gestion |
| Taux d'achat en magasin | Nombre de personnes qui entrent | Compteurs à l'entrée |
| Parcours d'achat sur le web | Type d'action (vue, panier, paiement), session | Outil de mesure d'audience du site |
| Motifs de retour | Liste de motifs compréhensibles | Service client |
| Stock en magasin et mouvements | Entrées, sorties, transferts par magasin | Logiciel de gestion de stock ou de caisse |
| Effet de facteurs extérieurs | Météo, vrais jours fériés | Données publiques (à garder séparées du kit TPCx-BB) |

## 4. Réponses aux questions de recul (§5.1.20)

**1. Quels besoins sont vraiment couverts par les données ?** Le suivi des ventes (CA, transactions, panier, quantités) par produit, catégorie, magasin, canal et période ; les remises ; les retours en quantité et en montant ; la description des clients ; le stock des entrepôts chaque semaine. La navigation web et les avis ne sont couverts qu'en partie.

**2. Quels indicateurs ne peuvent pas être calculés de façon fiable ?** La marge (K6), qu'on peut calculer mais qui n'a pas de sens ici (L7). Le taux de conversion web (K10), qui repose sur l'hypothèse H1 et ne permet pas de suivre un parcours d'achat. L'effet des promotions (A7, A8), l'ancienneté des clients (A9), et tout ce qui utilise les motifs de retour, les jours fériés ou la rentabilité complète des magasins.

**3. Quelle différence entre une donnée disponible et une donnée exploitable ?** Une donnée est *disponible* si elle se trouve dans un fichier. Elle est *exploitable* si elle est remplie, cohérente, compréhensible, reliée aux autres données et utile pour le métier. Par exemple, `reason.r_reason_desc` est disponible mais pas exploitable (texte au hasard). `ss_promo_sk` est disponible mais ne permet pas de comparer les ventes avec et sans promotion.

**4. Quels liens entre les données restent à vérifier ?** Le lien entre les clics et les commandes (H1), entre les avis et les commandes (H2), le sens des colonnes « utilisateur » (H3), et l'origine des 407 retours du refresh sans vente.

**5. Quelles limites des données inventées faut-il garder en tête ?** Les valeurs sont trop régulières (magasins presque identiques, pas d'effet de saison), les marges sont négatives, les remises sont de 50 %, certains textes sont au hasard et certaines dates vont de 1900 à 2199. Le jeu convient pour tester des volumes et des traitements, pas pour en tirer des conclusions métier.

**6. Quelles données supplémentaires seraient utiles ?** Voir la partie 3 : coûts et objectifs, fréquentation des magasins, actions détaillées sur le site, motifs de retour lisibles, stock des magasins.

## 5. Solutions de repli appliquées (§5.1.19)

- Les indicateurs impossibles à calculer (rentabilité complète, parcours d'achat) restent dans le dictionnaire avec la mention « besoin non couvert ».
- Je n'ai inventé aucune valeur : les vides restent vides, et les orphelins sont comptés et mis de côté.
- Les informations inconnues sur le kit (version, outil de génération) sont marquées « non communiqué » ou « à valider ».
