# UC-01 — Fiche de cadrage métier

Retail Intelligence Platform · Jour 1 · Livrable 1/6 de l'UC-01

## 1. Contexte et objectif

Retail Intelligence est une enseigne qui vend en magasin et sur un site web. Ses directions commerciale et financière veulent des indicateurs fiables pour suivre les ventes, comparer les magasins et voir comment l'activité évolue.

Dans cette première étape, je cherche à :

1. savoir qui va utiliser la plateforme et quelles décisions ces personnes doivent prendre ;
2. transformer leurs besoins en questions précises et en indicateurs ;
3. vérifier si les données du dossier `retail_project/` permettent vraiment de répondre ;
4. séparer ce qui est possible, possible en partie, impossible ou encore à vérifier.

Statuts utilisés dans tous les documents : <span class="s v">Vérifié</span> vu dans un fichier · <span class="s d">Déduit</span> trouvé par analyse · <span class="s h">Hypothèse</span> à confirmer · <span class="s n">Non disponible</span> absent des données · <span class="s a">À valider</span> à confirmer par le formateur.

## 2. Informations sur le kit de données (§3.4)

Le « kit », c'est l'ensemble des fichiers de données fournis pour le TP.

| Information | Ce que j'ai constaté | Statut |
|---|---|---|
| Nom du kit | `retail_project`, avec deux sous-dossiers : `data/` et `data_refresh/`. Aucune documentation n'est jointe. | <span class="s v">Vérifié</span> |
| Provenance | Fourni par le formateur. D'après l'énoncé, les données viennent de TPCx-BB, un jeu de test pour la distribution. | <span class="s v">Vérifié</span> |
| Version | Inconnue : aucun numéro de version dans les fichiers, et le formateur ne l'a pas indiqué. | <span class="s n">Non communiqué</span> |
| Date de mise à disposition | 16/11/2026. Les fichiers datent du 15/11/2026 (23 h 34 à 23 h 36), c'est-à-dire du moment où ils ont été préparés. | <span class="s v">Vérifié</span> |
| Moyen de distribution | Lien Microsoft Teams partagé par le formateur. | <span class="s v">Vérifié</span> |
| Format des fichiers | 34 fichiers `.dat` en texte. Les colonnes sont séparées par `|`. Il n'y a **pas de ligne d'en-tête** (pas de nom de colonne). Les fins de ligne sont au format Windows (**CRLF**). Une valeur manquante = un champ vide. Il y a aussi 2 petits fichiers CSV de rapport (`item_marketprices_audit.csv`). | <span class="s v">Vérifié</span> |
| Volume total | 1 033 993 587 octets, soit environ 1 Go : `data/` ≈ 1 024 Mo (978 Mio affichés par `du`), `data_refresh/` ≈ 9,6 Mo. | <span class="s v">Vérifié</span> |
| Nombre de fichiers | 36 : 24 dans `data/` (23 tables + 1 rapport) et 12 dans `data_refresh/` (11 tables + 1 rapport). | <span class="s v">Vérifié</span> |
| Outil de génération | Pas indiqué. Le fichier de rapport montre qu'un générateur a été utilisé, mais son nom n'apparaît nulle part. | <span class="s h">Hypothèse</span> |
| Modifications par le formateur | Pas indiquées. On sait seulement qu'un dossier `data_refresh/` ajoute des données de fin décembre 2005. | <span class="s a">À valider</span> |
| Noms des colonnes | Absents des fichiers. Je les ai repris du schéma officiel TPCx-BB, après avoir vérifié que le nombre de colonnes correspond bien. | <span class="s d">Déduit</span> |

Les données sont inventées (synthétiques). Elles servent à apprendre et ne représentent pas une vraie entreprise. Certains textes, comme les motifs de retour ou les noms de marques, sont même des suites de lettres au hasard.

## 3. Utilisateurs métier

| # | Profil | Son rôle | Ce dont il a besoin | Priorité |
|---|---|---|---|---|
| U1 | Direction générale | Décide de la stratégie et de l'argent investi entre magasins et web. | Une vue globale du chiffre d'affaires (CA), de la marge et de leur évolution. | Indispensable |
| U2 | Direction commerciale | Gère les produits, les promotions et les canaux de vente. | Les ventes par produit, catégorie, canal et promotion. | Indispensable |
| U3 | Responsable de magasin | Gère un magasin : équipe, produits, objectifs. | Suivre son magasin et le comparer aux autres. | Indispensable |
| U4 | Contrôleur de gestion | Vérifie les chiffres, suit les marges, remises et retours. | Des indicateurs financiers fiables, comparables d'une année à l'autre. | Indispensable |
| U5 | Responsable des stocks | Gère les stocks des entrepôts et les réapprovisionnements. | Savoir quels produits sont disponibles et comment le stock évolue. | Utile |
| U6 | Responsable e-commerce / marketing *(profil ajouté)* | Gère le site web et les campagnes. | Comprendre la navigation sur le site, les achats en ligne et les avis clients. | Utile |
| U7 | Équipe Data | Charge, vérifie et met à disposition les données. | Des données documentées, contrôlées et dont on connaît l'origine. | Indispensable (pour tous) |

J'ai ajouté le profil U6 parce que le kit contient des données de navigation web (`web_clickstreams`, `web_page`) et des avis produits (`product_reviews`). Aucun des profils de départ ne les aurait vraiment utilisées.

## 4. Schéma : des utilisateurs jusqu'aux fichiers

<div class="diag">
<div class="col"><div class="t">Utilisateurs</div>
<div class="box">U1 Direction générale</div>
<div class="box">U2 Direction commerciale</div>
<div class="box">U3 Resp. magasin</div>
<div class="box">U4 Contrôleur de gestion</div>
<div class="box">U5 Resp. stocks</div>
<div class="box">U6 E-commerce / marketing</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Questions (extrait)</div>
<div class="box">Q1 Comment évolue le CA ?</div>
<div class="box">Q3 Quels produits vendent le plus ?</div>
<div class="box">Q5 Quels magasins marchent le mieux ?</div>
<div class="box">Q7 Combien vend-on par canal ?</div>
<div class="box">Q9 Quels produits sont retournés ?</div>
<div class="box">Q11 Peut-on suivre les stocks ?</div>
<div class="box">Q13 Les visites mènent-elles à l'achat ?</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Indicateurs</div>
<div class="box">K1 CA net · K7 Évolution du CA</div>
<div class="box">K2 Nb de transactions · K3 Panier moyen</div>
<div class="box">K4 Quantités vendues</div>
<div class="box">K5 Taux de remise · K6 Marge</div>
<div class="box">K8 Taux de retour</div>
<div class="box">K9 Stock disponible</div>
<div class="box part">K10 Taux de conversion web</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Domaines</div>
<div class="box ok">Ventes magasin / web</div>
<div class="box ok">Produits · Promotions</div>
<div class="box ok">Magasins · Entrepôts</div>
<div class="box ok">Retours</div>
<div class="box ok">Stocks</div>
<div class="box part">Navigation</div>
<div class="box ok">Clients · Dates</div>
<div class="box wish">Coûts, objectifs, météo…</div>
</div>
<div class="arrow">→</div>
<div class="col"><div class="t">Fichiers trouvés</div>
<div class="box ok"><code>store_sales</code> <code>web_sales</code></div>
<div class="box ok"><code>item</code> <code>promotion</code> <code>item_marketprices</code></div>
<div class="box ok"><code>store</code> <code>warehouse</code> <code>web_site</code></div>
<div class="box ok"><code>store_returns</code> <code>web_returns</code> <code>reason</code></div>
<div class="box ok"><code>inventory</code></div>
<div class="box part"><code>web_clickstreams</code> <code>web_page</code></div>
<div class="box ok"><code>customer*</code> <code>date_dim</code> <code>time_dim</code></div>
<div class="box wish">aucun fichier</div>
</div>
</div>

<p class="legend">Légende : <b>vert</b> = fichier présent et utilisable · <b>orange</b> = fichier présent mais utilisable en partie (les clics n'indiquent pas s'il s'agit d'une visite, d'un ajout au panier ou d'un achat) · <b>rouge en pointillé</b> = donnée souhaitée mais absente du kit.</p>

Le détail de chaque question (décision, priorité, indicateurs, fichiers) est dans `UC01_questions_decisionnelles.pdf`.

## 5. Ce que les données permettent de faire

| Besoin | Ce que permet le kit | Statut |
|---|---|---|
| CA, nombre de transactions, panier moyen, quantités par canal, produit, magasin et période | Oui : montants, quantités, numéros de ticket et dates sont présents dans `store_sales` et `web_sales`, et les liens avec les autres tables fonctionnent. | <span class="s v">Vérifié</span> |
| Remises et marge | Oui : prix catalogue, prix de vente, coût d'achat et marge sont donnés pour chaque ligne. Mais 74 % des lignes magasin ont une marge négative, ce qui vient du fait que les données sont inventées. | <span class="s v">Vérifié</span> |
| Retours par produit | Oui en quantité et en montant. Les motifs de retour existent (`reason`) mais sont illisibles (lettres au hasard). | <span class="s v">Vérifié</span> |
| Description des clients | Oui : âge, pays de naissance, genre, situation familiale, niveau d'études, tranche de revenu, adresse. | <span class="s v">Vérifié</span> |
| Niveaux de stock | Oui, une photo par semaine, par produit et par entrepôt (5 entrepôts). Pas d'entrées/sorties de stock, pas de stock en magasin. | <span class="s v">Vérifié</span> |
| Comportement sur le site | En partie : on a les clics par produit, page et date, mais pas le type d'action ni la session. On ne peut mesurer les achats qu'en reliant un clic à une vente. | <span class="s d">Déduit</span> |
| Objectifs commerciaux, budgets, coûts des magasins, fréquentation des magasins | Non, absents du kit. | <span class="s n">Non disponible</span> |
| Période couverte | Ventes du 01/01/2001 au 13/12/2005 dans `data/`, puis du 13/12 au 31/12/2005 dans `data_refresh/`. | <span class="s v">Vérifié</span> |
