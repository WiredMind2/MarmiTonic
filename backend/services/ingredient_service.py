from .sparql_service import SparqlService
from ..models.ingredient import Ingredient
from typing import List, Dict

class IngredientService:
    def __init__(self):
        self.sparql_service = SparqlService(local_graph_path="backend/data/data.ttl")
        self.inventories: Dict[str, List[str]] = {}  # user_id -> list of ingredient names

    def get_all_ingredients(self) -> List[Ingredient]:
        # First, get unique ingredient URIs from local cocktails
        local_uris = self._get_local_ingredient_uris()
        ingredients = []

        # Query local graph for ingredients mentioned in cocktails
        for uri in local_uris:
            local_ing = self._query_local_ingredient(uri)
            if local_ing:
                ingredients.append(local_ing)

        # If we have less than 50, supplement with DBpedia
        if len(ingredients) < 50:
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
            for result in results["results"]["bindings"]:
                uri = result["id"]["value"]
                if uri not in [ing.id for ing in ingredients]:  # Avoid duplicates
                    ingredient = Ingredient(
                        id=uri,
                        name=result["name"]["value"],
                        category=result.get("category", {}).get("value", "Unknown"),
                        description=result.get("description", {}).get("value")
                    )
                    ingredients.append(ingredient)
                    if len(ingredients) >= 50:
                        break

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
            return [result["ingredient"]["value"] for result in results["results"]["bindings"]]
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
            if results["results"]["bindings"]:
                result = results["results"]["bindings"][0]
                return Ingredient(
                    id=uri,
                    name=result.get("name", {}).get("value", "Unknown"),
                    description=result.get("description", {}).get("value")
                )
        except:
            pass
        return None

    def search_ingredients(self, query: str) -> List[Ingredient]:
        sparql_query = f"""
        SELECT ?id ?name ?category ?description WHERE {{
            ?id rdf:type dbo:Food .
            ?id rdfs:label ?name .
            FILTER(LANG(?name) = "en" && CONTAINS(LCASE(?name), LCASE("{query}")))
            OPTIONAL {{ ?id dbo:category ?category }}
            OPTIONAL {{ ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }}
        }} LIMIT 50
        """
        results = self.sparql_service.execute_query(sparql_query)
        ingredients = []
        for result in results["results"]["bindings"]:
            ingredient = Ingredient(
                id=result["id"]["value"],
                name=result["name"]["value"],
                category=result.get("category", {}).get("value", "Unknown"),
                description=result.get("description", {}).get("value")
            )
            ingredients.append(ingredient)
        return ingredients

    def update_inventory(self, user_id: str, ingredients: List[str]):
        self.inventories[user_id] = ingredients

    def get_inventory(self, user_id: str) -> List[str]:
        return self.inventories.get(user_id, [])