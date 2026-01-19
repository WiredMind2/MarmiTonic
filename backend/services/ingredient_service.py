
from backend.services.sparql_service import SparqlService
from backend.models.ingredient import Ingredient
from typing import List, Dict
from pathlib import Path
from backend.utils.graph_loader import get_shared_graph
from backend.data.ttl_parser import get_all_ingredients as get_local_ingredients

class IngredientService:
    def __init__(self, local_ingredient_loader=None):
        # SparqlService now defaults to using the shared graph
        self.sparql_service = SparqlService()
        self.inventories: Dict[str, List[str]] = {}  # user_id -> list of ingredient names
        if local_ingredient_loader:
            self._local_ingredient_loader = local_ingredient_loader
        else:
            self._local_ingredient_loader = get_local_ingredients

    def get_all_ingredients(self) -> List[Ingredient]:
        # First, load parsed ingredients from the local TTL parser
        # These are the "canonical" ingredients used in our cocktail database
        ingredients = []
        try:
            local_ings = self._local_ingredient_loader()
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
            try:
                results = self.sparql_service.execute_query(dbpedia_query)
                
                existing_ids = {ing.id for ing in ingredients}
                existing_names = {ing.name.lower() for ing in ingredients}
                
                for result in results:
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
                        if len(ingredients) >= 50:
                            break
            except Exception as e:
                print(f"Error querying DBpedia for ingredients: {e}")

        return ingredients

    def _get_local_ingredient_uris(self) -> List[str]:
        """Extract unique ingredient URIs from cocktail wikiPageWikiLink"""
        query = """
        SELECT DISTINCT ?ingredient WHERE {
            ?cocktail dbo:wikiPageWikiLink ?ingredient .
            ?cocktail rdfs:label ?cocktailName .
            FILTER(LANG(?cocktailName) = "en")
        }
        """
        try:
            results = self.sparql_service.execute_local_query(query)
            return [result["ingredient"]["value"] for result in results]
        except:
            return []

    def _query_local_ingredient(self, uri: str) -> Ingredient:
        """Query local graph for ingredient details"""
        query = f"""
        SELECT ?name ?description WHERE {{
            <{uri}> rdfs:label ?name .
            FILTER(LANG(?name) = "en")
            OPTIONAL {{ <{uri}> dbo:abstract ?description . FILTER(LANG(?description) = "en") }}
        }}
        """
        try:
            results = self.sparql_service.execute_local_query(query)
            if results and len(results) > 0:
                result = results[0]
                return Ingredient(
                    id=uri,
                    name=result.get("name", {}).get("value", "Unknown"),
                    description=result.get("description", {}).get("value")
                )
        except Exception as e:
            print(f"Error querying local ingredient {uri}: {e}")

        return None
    def search_ingredients(self, query: str) -> List[Ingredient]:
        # 1. Search locally first (fast and relevant)
        local_matches = []
        query_lower = query.lower()
        
        try:
            all_local = self._local_ingredient_loader()
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
            
            for result in results:
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
        except Exception as e:
            print(f"Error searching ingredients: {e}")
            
        return local_matches + dbpedia_matches

    def update_inventory(self, user_id: str, ingredients: List[str]):
        self.inventories[user_id] = ingredients

    def get_inventory(self, user_id: str) -> List[str]:
        return self.inventories.get(user_id, [])

    def get_ingredient_by_uri(self, uri: str) -> Ingredient:
        # Try local first
        local_ing = self._query_local_ingredient(uri)
        if local_ing:
            return local_ing
        # Then DBpedia
        query = f"""
        SELECT ?name ?category ?description WHERE {{
            <{uri}> rdfs:label ?name .
            FILTER(LANG(?name) = "en")
            OPTIONAL {{ <{uri}> dbo:category ?category }}
            OPTIONAL {{ <{uri}> dbo:abstract ?description . FILTER(LANG(?description) = "en") }}
        }}
        """
        try:
            results = self.sparql_service.execute_query(query)
            if results and len(results) > 0:
                result = results[0]
                return Ingredient(
                    id=uri,
                    name=result["name"]["value"],
                    categories=[result.get("category", {}).get("value", "Unknown")],
                    description=result.get("description", {}).get("value")
                )
        except Exception as e:
            print(f"Error getting ingredient by URI {uri}: {e}")
        return None

    def get_ingredient_by_id(self, ingredient_id: str) -> Ingredient:
        """Alias for get_ingredient_by_uri for compatibility"""
        return self.get_ingredient_by_uri(ingredient_id)

    def search_ingredients_by_name(self, name: str) -> List[Ingredient]:
        """Search ingredients by name"""
        return self.search_ingredients(name)

    def get_ingredients_for_cocktail(self, cocktail_id: str) -> List[Ingredient]:
        """Get ingredients for a specific cocktail"""
        query = f"""
        SELECT ?ingredient ?name ?description WHERE {{
            <{cocktail_id}> dbo:ingredient ?ingredient .
            ?ingredient rdfs:label ?name .
            FILTER(LANG(?name) = "en")
            OPTIONAL {{ ?ingredient dbo:abstract ?description . FILTER(LANG(?description) = "en") }}
        }}
        """
        try:
            results = self.sparql_service.execute_query(query)
            ingredients = []
            for result in results:
                ingredient = Ingredient(
                    id=result["ingredient"]["value"],
                    name=result["name"]["value"],
                    description=result.get("description", {}).get("value")
                )
                ingredients.append(ingredient)
            return ingredients
        except Exception as e:
            print(f"Error getting ingredients for cocktail {cocktail_id}: {e}")
            return []

    def get_all_categories(self) -> List[str]:
        """Get all unique ingredient categories"""
        query = """
        SELECT DISTINCT ?category WHERE {
            ?ingredient rdf:type dbo:Food .
            ?ingredient dbo:category ?category .
        }
        """
        try:
            results = self.sparql_service.execute_query(query)
            return [result["category"]["value"] for result in results]
        except Exception as e:
            print(f"Error getting all categories: {e}")
            return []
