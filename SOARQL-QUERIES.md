# Documentation des Requêtes SPARQL - MarmiTonic

Ce document recense toutes les requêtes SPARQL utilisées dans le projet MarmiTonic, classées par fichier et fonction.

---

## Table des Matières

1. [Requête d'Extraction Principale (rdfbinder.py)](#1-requête-dextraction-principale-rdfbinderpy)
2. [Requêtes du Service SPARQL (sparql_service.py)](#2-requêtes-du-service-sparql-sparql_servicepy)
3. [Requêtes du Service d'Ingrédients (ingredient_service.py)](#3-requêtes-du-service-dingrédients-ingredient_servicepy)
4. [Requêtes du Service de Graphe (graph_service.py)](#4-requêtes-du-service-de-graphe-graph_servicepy)
5. [Requêtes du Service LLM (llm_service.py)](#5-requêtes-du-service-llm-llm_servicepy)

---

## 1. Requête d'Extraction Principale (rdfbinder.py)

### Extraction des Cocktails IBA depuis DBpedia

**Fichier:** `backend/data/rdfbinder.py`

**Type:** `CONSTRUCT`

**Description:** Cette requête est la plus importante du projet. Elle interroge le endpoint SPARQL de DBpedia pour extraire toutes les données des cocktails officiels IBA (International Bartenders Association) et les sauvegarder en format Turtle (`.ttl`). Elle constitue la base de données locale du projet.

**Requête:**
```sparql
PREFIX dbr:  <http://dbpedia.org/resource/>
PREFIX dbo:  <http://dbpedia.org/ontology/>
PREFIX dbp:  <http://dbpedia.org/property/>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

CONSTRUCT {
  # Liste IBA -> cocktails
  dbr:List_of_IBA_official_cocktails dbo:wikiPageWikiLink ?cocktail .

  # Propriétés cocktail
  ?cocktail rdfs:label ?label .
  ?cocktail dbo:description ?desc .
  ?cocktail foaf:depiction ?img .
  ?cocktail dbp:garnish ?garnish .
  ?cocktail dbp:ingredients ?ingredients .
  ?cocktail dbp:name ?name .
  ?cocktail dbp:served ?served .
  ?cocktail dbp:sourcelink ?sourcelink .
  ?cocktail dbp:prep ?prep .
  ?cocktail dct:subject ?subject .

  # Liens wiki sortants du cocktail
  ?cocktail dbo:wikiPageWikiLink ?outLink .
}
WHERE {
  # 1) Récupère les cocktails depuis la page-liste
  dbr:List_of_IBA_official_cocktails dbo:wikiPageWikiLink ?cocktail .

  # Évite les liens parasites
  FILTER(STRSTARTS(STR(?cocktail), "http://dbpedia.org/resource/"))
  FILTER(!CONTAINS(STR(?cocktail), "File:"))
  FILTER(!CONTAINS(STR(?cocktail), "Category:"))

  # 1bis) GARDE UNIQUEMENT ceux qui ont dbp:iba = "yes"
  ?cocktail dbp:iba ?iba .
  FILTER(
    LCASE(STR(?iba)) = "yes" ||
    STR(?iba) = "1" || STR(?iba) = "true"
  )

  # 2) rdfs:label (multi-langues: anglais et français)
  OPTIONAL {
    ?cocktail rdfs:label ?label .
    FILTER(lang(?label) = "en" || lang(?label) = "fr")
  }

  # 3) dbo:description (multi-langues: anglais et français)
  OPTIONAL {
    ?cocktail dbo:description ?desc .
    FILTER(lang(?desc) = "en" || lang(?desc) = "fr")
  }

  # 4) Image du cocktail
  OPTIONAL { ?cocktail foaf:depiction ?img . }

  # 5) Propriétés Infobox (dbp:*)
  OPTIONAL { ?cocktail dbp:garnish ?garnish . }
  OPTIONAL { ?cocktail dbp:ingredients ?ingredients . }
  OPTIONAL { ?cocktail dbp:name ?name . }
  OPTIONAL { ?cocktail dbp:served ?served . }
  OPTIONAL { ?cocktail dbp:sourcelink ?sourcelink . }
  OPTIONAL { ?cocktail dbp:prep ?prep . }

  # 6) Catégories
  OPTIONAL { ?cocktail dct:subject ?subject . }

  # 7) Liens wiki sortants (ingrédients potentiels, etc.)
  OPTIONAL {
    ?cocktail dbo:wikiPageWikiLink ?outLink .
    FILTER(!CONTAINS(STR(?outLink), "File:"))
    FILTER(!CONTAINS(STR(?outLink), "Category:"))
  }
}
```

**Données extraites:**
- Labels et descriptions des cocktails (EN/FR)
- Images (`foaf:depiction`)
- Liste d'ingrédients (`dbp:ingredients`)
- Informations de préparation (`dbp:prep`)
- Garniture (`dbp:garnish`)
- Type de service (`dbp:served`)
- Liens sortants vers d'autres ressources DBpedia (ingrédients, techniques, etc.)

---

## 2. Requêtes du Service SPARQL (sparql_service.py)

### 2.1 Récupération de Tous les Cocktails

**Fichier:** `backend/services/sparql_service.py`

**Méthode:** `query_local_data(query_type="cocktails")`

**Type:** `SELECT`

**Description:** Récupère la liste de tous les cocktails dans la base de données locale.

**Requête:**
```sparql
PREFIX : <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?cocktail WHERE {
    ?cocktail a :Cocktail .
}
```

---

### 2.2 Récupération des Détails d'un Cocktail

**Fichier:** `backend/services/sparql_service.py`

**Méthode:** `query_local_data(query_type="cocktail", uri=<cocktail_uri>)`

**Type:** `SELECT`

**Description:** Récupère toutes les propriétés d'un cocktail spécifique à partir de son URI.

**Requête:**
```sparql
PREFIX : <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?property ?value WHERE {
    <{uri}> ?property ?value .
}
```

---

### 2.3 Récupération de Tous les Ingrédients

**Fichier:** `backend/services/sparql_service.py`

**Méthode:** `query_local_data(query_type="ingredients")`

**Type:** `SELECT`

**Description:** Récupère la liste de tous les ingrédients dans la base de données locale.

**Requête:**
```sparql
PREFIX : <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?ingredient WHERE {
    ?ingredient a :Ingredient .
}
```

---

### 2.4 Requête Générique (Tous Triplets)

**Fichier:** `backend/services/sparql_service.py`

**Méthode:** `query_local_data()` (sans paramètres)

**Type:** `SELECT`

**Description:** Requête par défaut qui récupère tous les triplets RDF de la base de données.

**Requête:**
```sparql
PREFIX : <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?s ?p ?o WHERE {
    ?s ?p ?o .
}
```

---

### 2.5 Récupération des Cocktails depuis DBpedia

**Fichier:** `backend/services/sparql_service.py`

**Méthode:** `get_all_cocktails_from_dbpedia()`

**Type:** `SELECT`

**Description:** Interroge directement DBpedia pour récupérer 100 cocktails (utilisé comme fallback ou pour des données supplémentaires).

**Requête:**
```sparql
SELECT ?cocktail WHERE {
    ?cocktail rdf:type dbo:Cocktail .
} LIMIT 100
```

---

### 2.6 Construction de Requêtes Dynamiques

**Fichier:** `backend/services/sparql_service.py`

**Méthode:** `_build_query()`

**Type:** `SELECT` (dynamique)

**Description:** Construit dynamiquement des requêtes SPARQL selon le type demandé.

#### 2.6.1 Requête pour les Détails d'un Cocktail
```sparql
SELECT ?name ?description WHERE {
    <{uri}> rdfs:label ?name .
    OPTIONAL { <{uri}> dbo:abstract ?description . FILTER(LANG(?description) = "en") }
}
```

#### 2.6.2 Requête pour les Ingrédients d'un Cocktail
```sparql
SELECT ?ingredient WHERE {
    <{uri}> dbo:ingredient ?ingredient .
}
```

#### 2.6.3 Requête Générique avec Type RDF
```sparql
SELECT ?type WHERE {
    <{uri}> rdf:type ?type .
}
```

#### 2.6.4 Requête Complète pour une Ressource
```sparql
SELECT ?property ?value WHERE {
    <{uri}> rdf:type ?type .
    <{uri}> ?property ?value .
}
```

---

## 3. Requêtes du Service d'Ingrédients (ingredient_service.py)

### 3.1 Recherche d'Ingrédients depuis DBpedia

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `get_all_ingredients()` (fallback DBpedia)

**Type:** `SELECT`

**Description:** Récupère 50 ingrédients alimentaires depuis DBpedia avec leurs propriétés.

**Requête:**
```sparql
SELECT ?id ?name ?category ?description WHERE {
    ?id rdf:type dbo:Food .
    ?id rdfs:label ?name .
    FILTER(LANG(?name) = "en")
    OPTIONAL { ?id dbo:category ?category }
    OPTIONAL { ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }
} LIMIT 50
```

---

### 3.2 Extraction des URIs d'Ingrédients Locaux

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `_get_local_ingredient_uris()`

**Type:** `SELECT`

**Description:** Extrait les URIs uniques d'ingrédients à partir des liens wiki des cocktails.

**Requête:**
```sparql
SELECT DISTINCT ?ingredient WHERE {
    ?cocktail dbo:wikiPageWikiLink ?ingredient .
    ?cocktail rdfs:label ?cocktailName .
    FILTER(LANG(?cocktailName) = "en")
}
```

---

### 3.3 Requête Détaillée pour un Ingrédient Local

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `_query_local_ingredient(uri)`

**Type:** `SELECT`

**Description:** Récupère le nom et la description d'un ingrédient spécifique dans la base locale.

**Requête:**
```sparql
SELECT ?name ?description WHERE {
    <{uri}> rdfs:label ?name .
    FILTER(LANG(?name) = "en")
    OPTIONAL { <{uri}> dbo:abstract ?description . FILTER(LANG(?description) = "en") }
}
```

---

### 3.4 Recherche d'Ingrédients par Nom (DBpedia)

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `search_ingredients(query)`

**Type:** `SELECT`

**Description:** Recherche des ingrédients sur DBpedia dont le nom contient la chaîne de recherche.

**Requête:**
```sparql
SELECT ?id ?name ?category ?description WHERE {
    ?id rdf:type dbo:Food .
    ?id rdfs:label ?name .
    FILTER(LANG(?name) = "en" && CONTAINS(LCASE(?name), LCASE("{query}")))
    OPTIONAL { ?id dbo:category ?category }
    OPTIONAL { ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }
} LIMIT 20
```

---

### 3.5 Récupération d'Ingrédient par URI

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `get_ingredient_by_uri(uri)`

**Type:** `SELECT`

**Description:** Récupère les détails complets d'un ingrédient à partir de son URI sur DBpedia.

**Requête:**
```sparql
SELECT ?name ?category ?description WHERE {
    <{uri}> rdfs:label ?name .
    FILTER(LANG(?name) = "en")
    OPTIONAL { <{uri}> dbo:category ?category }
    OPTIONAL { <{uri}> dbo:abstract ?description . FILTER(LANG(?description) = "en") }
}
```

---

### 3.6 Ingrédients par Catégorie

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `get_ingredients_by_category(category)`

**Type:** `SELECT`

**Description:** Récupère tous les ingrédients d'une catégorie spécifique.

**Requête:**
```sparql
SELECT ?id ?name ?description WHERE {
    ?id rdf:type dbo:Food .
    ?id rdfs:label ?name .
    ?id dbo:category "{category}" .
    FILTER(LANG(?name) = "en")
    OPTIONAL { ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }
}
```

---

### 3.7 Ingrédients d'un Cocktail Spécifique

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `get_ingredients_for_cocktail(cocktail_id)`

**Type:** `SELECT`

**Description:** Récupère tous les ingrédients utilisés dans un cocktail donné.

**Requête:**
```sparql
SELECT ?ingredient ?name ?description WHERE {
    <{cocktail_id}> dbo:ingredient ?ingredient .
    ?ingredient rdfs:label ?name .
    FILTER(LANG(?name) = "en")
    OPTIONAL { ?ingredient dbo:abstract ?description . FILTER(LANG(?description) = "en") }
}
```

---

### 3.8 Toutes les Catégories d'Ingrédients

**Fichier:** `backend/services/ingredient_service.py`

**Méthode:** `get_all_categories()`

**Type:** `SELECT`

**Description:** Liste toutes les catégories uniques d'ingrédients disponibles.

**Requête:**
```sparql
SELECT DISTINCT ?category WHERE {
    ?ingredient rdf:type dbo:Food .
    ?ingredient dbo:category ?category .
}
```

---

## 4. Requêtes du Service de Graphe (graph_service.py)

### 4.1 Requête par Défaut du Graphe

**Fichier:** `backend/services/graph_service.py`

**Méthode:** `get_graph_data()`

**Type:** `SELECT`

**Description:** Récupère les relations entre cocktails et ingrédients pour construire le graphe de connaissances.

**Requête:**
```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>

SELECT ?cocktail ?ingredient WHERE {
    ?cocktail a dbo:Cocktail .
    ?cocktail dbp:ingredients ?ingredient .
} LIMIT 100
```

**Note:** Cette requête est utilisée pour construire le graphe de relations entre les cocktails et leurs ingrédients, permettant l'analyse de centralité et la détection de communautés.

---

## 5. Requêtes du Service LLM (llm_service.py)

### 5.1 Exemple de Requête pour le LLM

**Fichier:** `backend/services/llm_service.py`

**Type:** `SELECT` (exemple documenté)

**Description:** Exemple fourni au modèle de langage pour générer des requêtes SPARQL à partir de questions en langage naturel.

**Exemple de Requête:**
```sparql
SELECT ?cocktail WHERE { 
    ?cocktail dbp:ingredients ?ingredients. 
}
```

**Contexte:** Cette requête est mentionnée dans le prompt du LLM pour lui montrer comment interroger le graphe. Le LLM peut ensuite générer des requêtes similaires adaptées aux questions des utilisateurs.

---

## 6. Requêtes de Test (test_sparql_service.py)

### 6.1 Requête de Test Simple

**Fichier:** `backend/tests/test_sparql_service.py`

**Type:** `SELECT`

**Description:** Requête simple utilisée dans les tests unitaires pour vérifier le bon fonctionnement du service SPARQL.

**Requête:**
```sparql
SELECT * WHERE { ?s ?p ?o }
```

**Note:** Cette requête basique sélectionne tous les triplets et est utilisée uniquement pour les tests de connectivité et de fonctionnement du service.

---

## Résumé des Préfixes Utilisés

Les préfixes suivants sont utilisés dans l'ensemble du projet :

```sparql
PREFIX dbr:  <http://dbpedia.org/resource/>       # Ressources DBpedia
PREFIX dbo:  <http://dbpedia.org/ontology/>       # Ontologie DBpedia
PREFIX dbp:  <http://dbpedia.org/property/>       # Propriétés DBpedia
PREFIX dct:  <http://purl.org/dc/terms/>          # Dublin Core Terms
PREFIX foaf: <http://xmlns.com/foaf/0.1/>         # Friend of a Friend
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  # RDF Schema
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>  # RDF Syntax
PREFIX :     <http://dbpedia.org/resource/>       # Raccourci pour les ressources
```

---

## Architecture des Données

### Schéma Principal des Cocktails

Chaque cocktail dans le graphe possède la structure suivante :

```
dbr:Cocktail_Name
    ├── rdfs:label          → Nom du cocktail (EN/FR)
    ├── dbo:description     → Description (EN/FR)
    ├── foaf:depiction      → URL de l'image
    ├── dbp:iba             → Statut IBA ("yes")
    ├── dbp:ingredients     → Liste textuelle des ingrédients
    ├── dbp:garnish         → Garniture
    ├── dbp:served          → Type de service
    ├── dbp:prep            → Instructions de préparation
    ├── dct:subject         → Catégories
    └── dbo:wikiPageWikiLink → Liens vers ingrédients et autres ressources
```

---

## Notes Techniques

### Optimisations

1. **Cache Partagé:** Le `SparqlService` utilise un parser partagé (`_shared_parser`) pour éviter de recharger le fichier TTL à chaque requête.

2. **Requêtes Locales vs Distantes:** 
   - Les requêtes locales utilisent `rdflib` sur le fichier `data.ttl`
   - Les requêtes distantes utilisent `SPARQLWrapper` vers DBpedia
   - Un système de fallback bascule sur DBpedia si les données locales sont insuffisantes

3. **Filtres de Langue:** La plupart des requêtes filtrent pour l'anglais (`en`) et le français (`fr`) pour éviter les doublons multilingues.

### Limitations

- Les requêtes DBpedia sont limitées (LIMIT 50-100) pour éviter les timeouts
- Le fichier `data.ttl` local doit être généré avant utilisation via `rdfbinder.py`
- Certaines propriétés sont OPTIONAL car tous les cocktails n'ont pas toutes les informations

---

## Utilisation

### Génération de la Base de Données Locale

```bash
cd backend/data
python rdfbinder.py
```

Cette commande génère le fichier `data.ttl` contenant tous les cocktails IBA avec leurs propriétés.

### Exécution de Requêtes

```python
from backend.services.sparql_service import SparqlService

# Créer une instance du service
sparql = SparqlService()

# Exécuter une requête locale
results = sparql.execute_local_query("""
    SELECT ?cocktail ?name WHERE {
        ?cocktail rdfs:label ?name .
        FILTER(LANG(?name) = "en")
    }
""")

# Exécuter une requête sur DBpedia
results = sparql.execute_query("""
    SELECT ?cocktail WHERE {
        ?cocktail rdf:type dbo:Cocktail .
    } LIMIT 10
""")
```

---

**Dernière mise à jour:** Janvier 2026  
**Projet:** MarmiTonic - Application de Découverte de Cocktails  
**Technologies:** SPARQL, RDFLib, DBpedia, Python, FastAPI
