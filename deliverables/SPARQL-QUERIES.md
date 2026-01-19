# SPARQL Queries Documentation 🔍

This document catalogs the SPARQL queries used within **MarmiTonic** to interact with DBpedia and the local RDF graph.

---

## 1. Data Extraction (ETL)

**Source**: `backend/data/rdfbinder.py`
**Purpose**: To extract IBA Official Cocktails from DBpedia and construct a local Turtle (`.ttl`) knowledge graph.

### Query: Construct Cocktail Graph
Extracts cocktails, ingredients, descriptions, and images.

```sparql
PREFIX dbr:  <http://dbpedia.org/resource/>
PREFIX dbo:  <http://dbpedia.org/ontology/>
PREFIX dbp:  <http://dbpedia.org/property/>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

CONSTRUCT {
  dbr:List_of_IBA_official_cocktails dbo:wikiPageWikiLink ?cocktail .
  ?cocktail rdfs:label ?label ;
            dbo:description ?desc ;
            foaf:depiction ?img ;
            dbp:garnish ?garnish ;
            dbp:ingredients ?ingredients ;
            dbp:prep ?prep .
}
WHERE {
  dbr:List_of_IBA_official_cocktails dbo:wikiPageWikiLink ?cocktail .
  ?cocktail dbp:iba ?iba .
  FILTER(LCASE(STR(?iba)) = "yes" || STR(?iba) = "1")
  
  OPTIONAL { ?cocktail rdfs:label ?label . FILTER(lang(?label) = "en") }
  OPTIONAL { ?cocktail dbo:description ?desc . FILTER(lang(?desc) = "en") }
  OPTIONAL { ?cocktail foaf:depiction ?img . }
  OPTIONAL { ?cocktail dbp:ingredients ?ingredients . }
}
```

---

## 2. Cocktail Service Queries

**Source**: `backend/services/cocktail_service.py`

### Query: Get All Cocktails
Retrieves a list of all available cocktails with their basic metadata.

```sparql
SELECT ?cocktail ?name ?description ?image
WHERE {
    ?cocktail a dbo:Beverage ;
              rdfs:label ?name .
    OPTIONAL { ?cocktail dbo:description ?description }
    OPTIONAL { ?cocktail foaf:depiction ?image }
}
```

### Query: Get Cocktail Details
Retrieves detailed properties for a specific cocktail URI.

```sparql
SELECT ?property ?value
WHERE {
    <TARGET_COCKTAIL_URI> ?property ?value .
}
```

---

## 3. Ingredient Service Queries

**Source**: `backend/services/ingredient_service.py`

### Query: Get All Ingredients
Extracts unique ingredients linked to cocktails.

```sparql
SELECT DISTINCT ?ingredient ?ingredientLabel
WHERE {
    ?cocktail dbp:ingredients ?ingredient .
    ?ingredient rdfs:label ?ingredientLabel .
    FILTER(lang(?ingredientLabel) = "en")
}
ORDER BY ?ingredientLabel
```

---

## 4. Advanced Graph Queries

**Source**: `backend/services/graph_service.py`

### Query: Shared Ingredients (Similarity)
Finds cocktails that share specific ingredients with a target cocktail.

```sparql
SELECT ?otherCocktail (COUNT(?ingredient) as ?sharedCount)
WHERE {
    <TARGET_COCKTAIL> dbp:ingredients ?ingredient .
    ?otherCocktail dbp:ingredients ?ingredient .
    FILTER (?otherCocktail != <TARGET_COCKTAIL>)
}
GROUP BY ?otherCocktail
ORDER BY DESC(?sharedCount)
LIMIT 5
```
