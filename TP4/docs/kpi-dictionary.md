# Dictionnaire des indicateurs (KPI) mis à jour (J4-02, étape 2)

Un **KPI** est un indicateur chiffré qui aide à prendre une décision (par exemple le chiffre d'affaires).

Je pars de la liste faite au TP1 (UC-01, K1 à K13). Au TP1, j'additionnais les ventes en magasin et sur le web. Au TP4, je n'ai que les **ventes en magasin** (les seules nettoyées au TP3). Tous les calculs ci-dessous portent donc sur les ventes en magasin.

Les valeurs viennent du notebook (fichier `resultats/kpi.csv`). Ce sont **exactement les mêmes** que celles calculées au TP1 avec un autre outil (DuckDB), directement sur les fichiers bruts. Ça prouve que mes traitements du TP1, du TP3 et du TP4 sont cohérents.

## Les 6 indicateurs retenus

Période pour tous : du 1er janvier 2001 au 13 décembre 2005. Devise : non indiquée dans les données.

### K1 – Chiffre d'affaires (CA)
- **C'est quoi** : l'argent encaissé, après les remises et les bons de réduction, sans les taxes.
- **Calcul** : somme de la colonne `ss_net_paid` (`F.sum("ss_net_paid")`).
- **Résultat** : 1 150 529 586,37.
- **Limites** : les retours ne sont pas enlevés ; données inventées ; 2005 incomplète.

### K2 – Nombre de transactions
- **C'est quoi** : le nombre de tickets de caisse différents.
- **Calcul** : nombre de numéros de ticket différents (`F.countDistinct("ss_ticket_number")`).
- **Résultat** : 89 100 tickets.
- **Attention** : un ticket n'est **pas** une ligne. Il y a 667 579 lignes, car un ticket contient plusieurs produits.

### K3 – Panier moyen
- **C'est quoi** : ce que dépense un client en moyenne par ticket.
- **Calcul** : K1 ÷ K2.
- **Résultat** : 12 912,79.
- **Limite** : quelques très gros tickets font monter la moyenne. La moitié des tickets est en dessous de 11 641 (c'est la **médiane**).

### K4 – Quantité vendue
- **C'est quoi** : le nombre d'articles vendus.
- **Calcul** : somme de `ss_quantity`.
- **Résultat** : 33 755 474 articles.
- **Limite** : on additionne des produits très différents (un livre et une télé comptent pareil).

### K7 – Évolution du chiffre d'affaires
- **C'est quoi** : de combien le CA a monté ou baissé par rapport à l'année d'avant.
- **Calcul** : (CA de l'année − CA de l'année d'avant) ÷ CA de l'année d'avant. Je compare toujours **la même période** (du 1er janvier au 13 décembre), car 2005 s'arrête le 13 décembre.
- **Résultat** : 2002 : −0,75 % ; 2003 : +1,11 % ; 2004 : +0,18 % ; 2005 : −1,53 %.
- **Pourquoi la même période** : si on comparait 2005 entière à 2004 entière, on trouverait −6,48 %. C'est faux : il manque juste 18 jours en 2005.

### K11 – Chiffre d'affaires par employé
- **C'est quoi** : combien rapporte un employé, en moyenne, dans chaque magasin.
- **Calcul** : CA du magasin ÷ nombre d'employés du magasin.
- **Résultat** : de 324 089 à 454 218 selon le magasin (moyenne : 407 392).
- **Limite** : on n'a qu'un seul nombre d'employés par magasin, comme s'il n'avait pas changé en 5 ans.

## Les indicateurs que je n'ai pas calculés

| Code | Indicateur | Pourquoi je ne l'ai pas calculé |
|---|---|---|
| K5 | Taux de remise | Possible, mais la remise est de 50 % en moyenne partout : ce n'est pas réaliste. Et la table des promotions n'a pas été nettoyée. Il ne sert pas pour mes questions. |
| K6 | Marge | **Possible mais pas fiable** : 74 % des ventes sont à perte. Le TP dit de ne pas présenter une marge si les coûts ne sont pas fiables. |
| K8 | Taux de retour | La table des retours n'a pas été nettoyée au TP3. |
| K9 | Stock | La table des stocks n'a pas été nettoyée. |
| K10 | Conversion web | Les clics du site web n'ont pas été nettoyés. |
| K11 bis | CA par m² | Les surfaces des magasins sont fausses (plusieurs millions de m²). |
| K12 | Note des avis clients | La table des avis n'a pas été nettoyée. |
| K13 | Rentabilité d'un magasin | Il n'y a aucune donnée sur les coûts (loyer, salaires) dans le kit. |

## Règles que j'ai respectées

- Je ne calcule pas le panier moyen avec le nombre de lignes : je compte les vrais tickets.
- Je ne mélange pas les lignes (667 579), les articles (33 755 474) et les tickets (89 100).
- Je ne présente pas la marge comme un chiffre fiable.
