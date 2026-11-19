# Ce que j'en conclus : constats, limites et conseils (J4-06, étape 6)

**Attention** : les données TPCx-BB sont **inventées par un programme**. Mes résultats montrent que ma méthode fonctionne. Ils ne parlent pas d'un vrai magasin.

Autre règle importante : quand deux choses vont ensemble, ça ne veut pas dire que l'une cause l'autre.

## Constat 1 – Le chiffre d'affaires ne bouge presque pas

- **Ce que je vois** : 19,36 millions par mois en moyenne, avec très peu de variation (3,2 %). D'une année à l'autre, sur la même période, on reste entre −1,53 % et +1,11 %. Il n'y a pas de pic à Noël. Février est toujours le mois le plus faible.
- **Ce que ça peut vouloir dire** : les ventes n'augmentent pas et ne dépendent pas de la saison. Les petites différences viennent surtout du nombre de jours dans le mois (février en a 28).
- **Limites** : le programme qui a inventé les données répartit les ventes de façon égale dans le temps ; décembre 2005 est incomplet ; le web et les retours ne sont pas inclus.
- **Mon conseil** : fixer les objectifs à partir de la moyenne des 12 derniers mois, ou du chiffre d'affaires par jour, et pas à partir d'un seul mois. Toujours comparer les années sur la même période. Traiter le deuxième lot de données pour compléter 2005.

## Constat 2 – Les magasins vendent presque autant, mais pas par employé

- **Ce que je vois** : les 12 magasins font entre 94,0 et 99,0 millions (5,2 % d'écart), et leur panier moyen est presque le même. Mais par employé, l'écart monte à 40 % (de 324 000 à 454 000) et le classement change. Williamstown (298 employés) passe de 5ᵉ à dernier. Germantown (213 employés) passe premier.
- **Ce que ça peut vouloir dire** : le chiffre d'affaires seul ne suffit pas pour dire quel magasin est le meilleur. En le divisant par le nombre d'employés, on voit des différences.
- **Limites** : on ne connaît qu'un seul nombre d'employés par magasin pour 5 ans ; les surfaces sont fausses ; on n'a pas les coûts ; on ne connaît ni la taille de la ville ni les clients.
- **Mon conseil** : comparer les magasins avec des chiffres « ramenés » (par employé, par ticket) plutôt qu'avec le total. Demander le nombre d'employés année par année et les coûts (loyer, salaires) avant de décider quoi que ce soit.

## Constat 3 – Deux catégories font 72 % des ventes

- **Ce que je vois** : Music (45,2 %) et Books (26,7 %). Ces parts ne changent presque pas d'une année à l'autre.
- **Ce que ça peut vouloir dire** : le magasin dépend beaucoup de ces deux catégories.
- **Limites** : sans marge fiable, on ne sait pas si elles rapportent vraiment de l'argent ; ça vient peut-être juste du nombre de produits dans chaque catégorie.
- **Mon conseil** : compter le nombre de produits par catégorie avant de changer quoi que ce soit dans les rayons.

## Constat 4 – Le panier moyen donne une image trop haute

- **Ce que je vois** : le panier moyen est de 12 913, mais la moitié des tickets est sous 11 641. Quelques très gros tickets (jusqu'à 64 786) font monter la moyenne.
- **Mon conseil** : montrer aussi la médiane à côté du panier moyen dans les tableaux de bord.

## Limites générales

1. Données inventées : 74 % des ventes sont à perte, les montants ne sont pas réalistes, les ventes sont réparties presque au hasard.
2. Ventes en magasin seulement : je ne peux pas comparer avec le site web (Q7).
3. Les retours ne sont pas enlevés du chiffre d'affaires.
4. 2005 est incomplète.
5. Tout tourne sur mon PC, pas sur plusieurs machines.
