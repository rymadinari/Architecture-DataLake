# UC-01 — Matrice utilisateurs et questions décisionnelles

Retail Intelligence Platform · Jour 1 · Livrable 2/6 de l'UC-01

## 1. Principe

Pour chaque question, j'indique qui la pose (profils U1 à U7, voir `UC01_cadrage_metier.pdf`), quelle **décision** elle aide à prendre, sa priorité, les indicateurs utiles (K1 à K12, voir le dictionnaire KPI) et les fichiers nécessaires. La dernière colonne dit si les données permettent vraiment d'y répondre.

Priorités : **I** = indispensable · **U** = utile · **C** = complémentaire.

## 2. Matrice

| # | Profil | Question | Décision possible | Prio. | KPI | Fichiers nécessaires | Réponse possible ? |
|---|---|---|---|---|---|---|---|
| Q1 | U1 Dir. générale | Comment évolue le chiffre d'affaires, au total et par canal, d'une année et d'un mois à l'autre ? | Répartir les investissements entre magasins et web, fixer les objectifs de l'année. | I | K1, K7 | `store_sales`, `web_sales`, `date_dim` | <span class="s v">Oui</span> 2005 incomplète dans `data/` (s'arrête au 13/12) |
| Q2 | U1 Dir. générale | Quelle marge fait-on, et comment évolue-t-elle ? | Revoir les prix et les remises. | I | K6 | `store_sales`, `web_sales` | <span class="s v">Oui</span> mais la marge est surtout négative (effet des données inventées) |
| Q3 | U2 Dir. commerciale | Quels produits et quelles catégories vendent le plus (en CA et en quantité) ? | Mettre en avant, réapprovisionner ou retirer des produits. | I | K1, K4 | `store_sales`, `web_sales`, `item` | <span class="s v">Oui</span> |
| Q4 | U2 Dir. commerciale | Les ventes en promotion sont-elles différentes des autres ? | Garder ou arrêter une promotion. | U | K1, K5 | `store_sales`, `web_sales`, `promotion` | <span class="s d">En partie</span> : on peut comparer, mais pas prouver que la promotion est la cause |
| Q5 | U3 Resp. magasin | Quels magasins marchent le mieux (CA, tickets, panier, CA par m², CA par employé) ? | Fixer des objectifs par magasin, partager ce qui marche. | I | K1, K2, K3, K11 | `store_sales`, `store` | <span class="s v">Oui</span> (12 magasins) |
| Q6 | U3 Resp. magasin | Quels produits se vendent le mieux dans mon magasin, et à quelle heure ? | Adapter les produits du magasin et les horaires du personnel. | U | K1, K4 | `store_sales`, `item`, `time_dim` | <span class="s v">Oui</span> |
| Q7 | U2 Dir. commerciale | Combien vend-on par canal (magasin / web) ? | Ajuster la stratégie entre les canaux et la logistique. | I | K2, K4, K1 | `store_sales`, `web_sales` | <span class="s v">Oui</span> seulement 2 canaux dans le kit |
| Q8 | U4 Contrôleur | Combien accorde-t-on en remises et en coupons, par canal, magasin et catégorie ? | Limiter les remises, repérer les abus. | I | K5 | `store_sales`, `web_sales` | <span class="s v">Oui</span> |
| Q9 | U4 / U2 | Quels produits sont retournés, et dans quelle proportion ? | Retirer ou corriger un produit, changer de fournisseur. | I | K8 | `store_returns`, `web_returns`, `item`, ventes | <span class="s v">Oui</span> sauf les motifs (illisibles) |
| Q10 | U4 Contrôleur | Combien coûtent les retours (remboursements, pertes) ? | Changer la politique de retour. | U | K8, K6 | `store_returns`, `web_returns` | <span class="s v">Oui</span> |
| Q11 | U5 Resp. stocks | Peut-on suivre le stock par produit, entrepôt et semaine ? | Commander à nouveau, déplacer du stock entre entrepôts. | U | K9 | `inventory`, `item`, `warehouse` | <span class="s v">Oui</span> une photo par semaine, entrepôts seulement |
| Q12 | U5 Resp. stocks | Quels produits sont en rupture ou en surstock par rapport aux ventes ? | Ajuster les commandes aux fournisseurs. | U | K9, K4 | `inventory`, `web_sales` | <span class="s d">En partie</span> : seules les ventes web sont liées à un entrepôt ; pas de stock en magasin |
| Q13 | U6 E-commerce | Les visites sur le site mènent-elles à des achats ? | Améliorer les pages et le parcours d'achat. | U | K10 | `web_clickstreams`, `web_sales`, `web_page` | <span class="s d">En partie</span> : pas de type d'action ni de session ; 42 % des clics sont anonymes |
| Q14 | U6 E-commerce | Quels produits sont les mieux notés ? Se vendent-ils mieux ? | Mettre en avant les produits bien notés, traiter les mal notés. | C | K12, K4 | `product_reviews`, `item`, ventes | <span class="s d">En partie</span> : on voit un lien, pas une cause |
| Q15 | U2 / U6 | Comment décrire les clients (âge, revenu, famille, lieu) ? | Créer des groupes de clients et cibler les campagnes. | U | K1, K3 par groupe | `customer`, `customer_demographics`, `household_demographics`, `income_band`, `customer_address` | <span class="s v">Oui</span> |
| Q16 | U2 Dir. commerciale | Nos prix sont-ils plus hauts ou plus bas que ceux des concurrents ? | Revoir le prix de certains produits. | C | — | `item_marketprices`, `item` | <span class="s d">En partie</span> : les concurrents n'ont qu'un code, pas de nom |
| Q17 | U7 Équipe Data | Chaque lot de données reçu est-il complet et cohérent ? | Accepter, refuser ou mettre de côté un lot. | I | contrôles qualité | tous | <span class="s v">Oui</span> (voir les contrôles de l'UC-01) |
| Q18 | U1 / U4 | Quels sont les coûts fixes, objectifs et budgets des magasins ? | Calculer la vraie rentabilité d'un magasin. | U | — | aucun | <span class="s n">Non disponible</span> |

## 3. Lien avec les questions de départ de l'énoncé (§2.2)

| Question de l'énoncé | Mes questions | Possible avec le kit ? |
|---|---|---|
| Quels produits génèrent le plus de ventes ? | Q3, Q6 | <span class="s v">Oui</span> |
| Comment évoluent les ventes dans le temps ? | Q1 | <span class="s v">Oui</span> (sur 5 ans, 2001-2005) |
| Quels magasins présentent les meilleures performances ? | Q5 | <span class="s v">Oui</span> (12 magasins, avec peu d'écart entre eux) |
| Quels sont les volumes de ventes par canal ? | Q7 | <span class="s v">Oui</span> (magasin et web) |
| Quels produits font l'objet de retours ? | Q9, Q10 | <span class="s v">Oui</span>, sans motif lisible |
| Quelles informations permettent de caractériser les clients ? | Q15 | <span class="s v">Oui</span> |
| Peut-on analyser les niveaux de stock ? | Q11, Q12 | <span class="s d">En partie</span> (entrepôts, une fois par semaine) |
| Les données de navigation permettent-elles d'étudier les comportements ? | Q13 | <span class="s d">En partie</span> (clics sans type d'action) |

## 4. Vérifications (§5.1.15)

- Chaque profil de U1 à U6 a au moins deux questions ; U7 en a une qui concerne tout le monde.
- Chaque question est liée à une décision.
- Chaque question à laquelle on peut répondre renvoie à un indicateur défini dans `UC01_dictionnaire_KPI.xlsx`.
- Chaque fichier cité a bien été trouvé dans le kit (voir `UC01_inventaire_sources.xlsx`).
