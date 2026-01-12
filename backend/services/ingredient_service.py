from .sparql_service import SparqlService
from ..models.ingredient import Ingredient
from typing import List, Dict
from ..data.ttl_parser import get_all_ingredients as get_local_ingredients

class IngredientService:
    def __init__(self):
        self.sparql_service = SparqlService(local_graph_path="backend/data/data.ttl")
        self.inventories: Dict[str, List[str]] = {}  # user_id -> list of ingredient names

    def get_all_ingredients(self) -> List[Ingredient]:
        # First, load parsed ingredients from the local TTL parser
        # These are the "canonical" ingredients used in our cocktail database
        ingredients = []
        try:
            local_ings = get_local_ingredients()
            if local_ings:
                ingredients.extend(local_ings)
        except Exception:
            # Fall back to empty list if parser fails
            local_ings = []

        # If we have very few ingredients, supplement with DBpedia
        # This handles the case where local data might be missing or empty
        if len(ingredients) < 10:
            dbpedia_query = """
            SELECT ?id ?name ?category ?description WHERE {
                ?id rdf:type dbo:Food .
                ?id rdfs:label ?name .
                FILTER(LANG(?name) = "en")
                OPTIONAL { ?id dbo:category ?category }
                OPTIONAL { ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }
            } LIMIT 50
            """
            results = self.sparql_service.execute_query(dbpedia_query)
            
            existing_ids = {ing.id for ing in ingredients}
            existing_names = {ing.name.lower() for ing in ingredients}
            
            for result in results["results"]["bindings"]:
                uri = result["id"]["value"]
                name = result["name"]["value"]
                
                if uri not in existing_ids and name.lower() not in existing_names:
                    category_val = result.get("category", {}).get("value", "Unknown")
                    ingredient = Ingredient(
                        id=uri,
                        name=name,
                        categories=[category_val], # Normalized to list
                        description=result.get("description", {}).get("value")
                    )
                    ingredients.append(ingredient)

        return ingredients

    def search_ingredients(self, query: str) -> List[Ingredient]:
        # 1. Search locally first (fast and relevant)
        local_matches = []
        query_lower = query.lower()
        
        try:
            all_local = get_local_ingredients()
            for ing in all_local:
                if query_lower in ing.name.lower():
                    local_matches.append(ing)
        except Exception:
            pass
            
        # 2. Setup DBpedia search for broader results
        sparql_query = f"""
        SELECT ?id ?name ?category ?description WHERE {{
            ?id rdf:type dbo:Food .
            ?id rdfs:label ?name .
            FILTER(LANG(?name) = "en" && CONTAINS(LCASE(?name), LCASE("{query}")))
            OPTIONAL {{ ?id dbo:category ?category }}
            OPTIONAL {{ ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }}
        }} LIMIT 20
        """
        
        dbpedia_matches = []
        try:
            results = self.sparql_service.execute_query(sparql_query)
            
            local_names = {ing.name.lower() for ing in local_matches}
            
            for result in results["results"]["bindings"]:
                name = result["name"]["value"]
                if name.lower() in local_names:
                    continue # Skip if already found locally
                    
                category_val = result.get("category", {}).get("value", "Unknown")
                ingredient = Ingredient(
                    id=result["id"]["value"],
                    name=name,
                    categories=[category_val], # Normalized to list
                    description=result.get("description", {}).get("value")
                )
                dbpedia_matches.append(ingredient)
        except Exception:
            pass # DBpedia might be down
            
        return local_matches + dbpedia_matches

    def update_inventory(self, user_id: str, ingredients: List[str]):
        self.inventories[user_id] = ingredients

    def get_inventory(self, user_id: str) -> List[str]:
        return self.inventories.get(user_id, [])