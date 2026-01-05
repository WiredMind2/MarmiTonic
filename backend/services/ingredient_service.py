from .sparql_service import SparqlService
from ..models.ingredient import Ingredient
from typing import List, Dict

class IngredientService:
    def __init__(self):
        self.sparql_service = SparqlService()
        self.inventories: Dict[str, List[str]] = {}  # user_id -> list of ingredient names

    def get_all_ingredients(self) -> List[Ingredient]:
        query = """
        SELECT ?id ?name ?category ?description WHERE {
            ?id rdf:type dbo:Food .
            ?id rdfs:label ?name .
            FILTER(LANG(?name) = "en")
            OPTIONAL { ?id dbo:category ?category }
            OPTIONAL { ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }
        } LIMIT 50
        """
        results = self.sparql_service.execute_query(query)
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