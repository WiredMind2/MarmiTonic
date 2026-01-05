
1) Mon Bar (inventaire)

L’utilisateur coche/cherche les ingrédients qu’il a (gin, citron, sucre, vermouth…).
L’app renvoie :

Cocktails faisables maintenant (0 ingrédient manquant)

Presque faisables (il manque 1 ingrédient, puis 2)

Bouton “ajouter au panier” pour les manquants

Pourquoi c’est utile : c’est concret, c’est un vrai besoin.

Ce que ça exploite :

Graphe cocktail–ingrédient + requêtes SPARQL pour extraire les données.

2) Bar Minimum (optimisation)

Deux modes pratiques :

Mode “Party” : “j’ai N ingrédients → maximise le nombre de cocktails”

Mode “Playlist” : “je veux ces cocktails → donne la liste minimale d’ingrédients”

Sortie :

la liste optimisée + combien de cocktails couverts

et surtout “presque couverts” (manque 1 ingrédient) → effet démo garanti

Pourquoi c’est utile : ça te dit quoi acheter sans te ruiner.

3) Découverte type Spotify

Sur la fiche d’un cocktail :

“Similaires” (même style / mêmes ingrédients) avec score

“Dans la même vibe” (cluster)

“Pont vers d’autres styles” (cocktails qui connectent des familles)

Pourquoi c’est utile : tu trouves quoi boire ensuite, pas juste une recette.

Bonus utiles (si vous avez du temps)
4) Substitutions intelligentes

Ex : il te manque “triple sec” → l’app suggère alternatives plausibles (curaçao, Cointreau, etc.)
Méthode : similarité d’ingrédients par co-occurrence + éventuellement catégories.

Utile : ça sauve les soirées.

5) Filtres “réels”

sans œuf

sans lait/crème

sans sucre ajouté

“citrus / mint / coffee / bitter”
Ça se fait en tags dérivés (mapping simple), pas besoin d’inventer une ontologie parfaite.

6) Shopping list consolidée

Tu sélectionnes 10 cocktails → ça te sort :

liste des ingrédients uniques

et les plus “rentables” (ceux qui débloquent le plus de cocktails)

À quoi ressemble l’appli (IHM simple, efficace)
Onglet 1 — Discover

recherche cocktail / ingrédient

tendances : “cocktails centraux”, “familles”, “random”

Onglet 2 — My Bar

liste d’ingrédients (avec search)

résultats faisables / presque faisables

Onglet 3 — Planner

Bar minimum (slider N)

playlist → ingrédients minimaux

export shopping list

Onglet 4 — Insights

stats graphe (top ingrédients, communautés)

export Gephi

Pourquoi ça colle au sujet, point par point
3.1 SPARQL & Linked Data

Vous interrogez DBpedia en SPARQL pour extraire cocktails/ingrédients.

Vous construisez un graphe à partir de ces données (pas une liste statique).

3.2 Analyse de données

Similarité cocktail–cocktail (projection) + communautés + centralités

Bar minimum = optimisation (set cover greedy) → c’est une vraie “analyse/valorisation”.

3.3 LLM (optionnel)

Si vous le faites : NL→SPARQL (“cocktail au gin sans sucre”), ou résumé des clusters.

Le point que tu dois comprendre (sinon tu te plantes)

Ton dataset actuel avec ingredientsRaw n’est pas exploitable tel quel. L’appli devient utile quand vous transformez ça en vraies arêtes :

Cocktail --usesIngredient--> Ingredient

Dès que tu as ça, tout le reste (My Bar, Bar minimum, reco) devient mécanique.

Si tu veux, je te donne une spec ultra courte “user stories + écrans + endpoints API” pour que votre groupe parte direct en dev.
