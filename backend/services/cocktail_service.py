from .sparql_service import SparqlService
from .ingredient_service import IngredientService
from ..models.cocktail import Cocktail
from typing import List, Dict, Any


class CocktailService:
    def __init__(self):
        self.sparql_service = SparqlService()
        self.ingredient_service = IngredientService()

    def get_all_cocktails(self) -> List[Cocktail]:
        query = """
        SELECT ?id ?name ?instructions ?category ?description ?image WHERE {
            ?id rdf:type dbo:Cocktail .
            ?id rdfs:label ?name .
            FILTER(LANG(?name) = "en")
            OPTIONAL { ?id dbo:instructions ?instructions }
            OPTIONAL { ?id dbo:category ?category }
            OPTIONAL { ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }
            OPTIONAL { ?id dbo:thumbnail ?image }
        } LIMIT 50
        """
        results = self.sparql_service.execute_query(query)
        cocktails = []
        for result in results["results"]["bindings"]:
            cocktail = Cocktail(
                id=result["id"]["value"],
                name=result["name"]["value"],
                ingredients=[],  # To be filled
                instructions=result.get("instructions", {}).get("value"),
                category=result.get("category", {}).get("value"),
                description=result.get("description", {}).get("value"),
                image=result.get("image", {}).get("value")
            )
            cocktails.append(cocktail)
        
        # Fetch ingredients for each cocktail
        for cocktail in cocktails:
            cocktail.ingredients = self._get_cocktail_ingredients(cocktail.id)
        
        return cocktails

    def search_cocktails(self, query: str) -> List[Cocktail]:
        sparql_query = f"""
        SELECT ?id ?name ?instructions ?category ?description ?image WHERE {{
            ?id rdf:type dbo:Cocktail .
            ?id rdfs:label ?name .
            FILTER(LANG(?name) = "en" && CONTAINS(LCASE(?name), LCASE("{query}")))
            OPTIONAL {{ ?id dbo:instructions ?instructions }}
            OPTIONAL {{ ?id dbo:category ?category }}
            OPTIONAL {{ ?id dbo:abstract ?description . FILTER(LANG(?description) = "en") }}
            OPTIONAL {{ ?id dbo:thumbnail ?image }}
        }} LIMIT 50
        """
        results = self.sparql_service.execute_query(sparql_query)
        cocktails = []
        for result in results["results"]["bindings"]:
            cocktail = Cocktail(
                id=result["id"]["value"],
                name=result["name"]["value"],
                ingredients=[],  # To be filled
                instructions=result.get("instructions", {}).get("value"),
                category=result.get("category", {}).get("value"),
                description=result.get("description", {}).get("value"),
                image=result.get("image", {}).get("value")
            )
            cocktails.append(cocktail)
        
        # Fetch ingredients for each cocktail
        for cocktail in cocktails:
            cocktail.ingredients = self._get_cocktail_ingredients(cocktail.id)
        
        return cocktails

    def get_feasible_cocktails(self, user_id: str) -> List[Cocktail]:
        all_cocktails = self.get_all_cocktails()
        inventory = self.ingredient_service.get_inventory(user_id)
        feasible = []
        for cocktail in all_cocktails:
            missing = [ing for ing in cocktail.ingredients if ing not in inventory]
            if len(missing) == 0:
                feasible.append(cocktail)
        return feasible

    def get_almost_feasible_cocktails(self, user_id: str) -> List[Dict[str, Any]]:
        all_cocktails = self.get_all_cocktails()
        inventory = self.ingredient_service.get_inventory(user_id)
        almost_feasible = []
        for cocktail in all_cocktails:
            missing = [ing for ing in cocktail.ingredients if ing not in inventory]
            if 1 <= len(missing) <= 2:
                almost_feasible.append({
                    "cocktail": cocktail,
                    "missing": missing
                })
        return almost_feasible

    def _get_cocktail_ingredients(self, cocktail_id: str) -> List[str]:
        query = f"""
        SELECT ?label WHERE {{
            <{cocktail_id}> dbo:ingredient ?ingredient .
            ?ingredient rdfs:label ?label .
            FILTER(LANG(?label) = "en")
        }}
        """
        results = self.sparql_service.execute_query(query)
        ingredients = [result["label"]["value"] for result in results["results"]["bindings"]]
        return ingredients

    def get_cocktails_by_ingredients(self, ingredients: List[str]) -> List[Cocktail]:
        all_cocktails = self.get_all_cocktails()
        matching_cocktails = []
        for cocktail in all_cocktails:
            # Check if all provided ingredients are in the cocktail's ingredients
            if all(ingredient in cocktail.ingredients for ingredient in ingredients):
                matching_cocktails.append(cocktail)
        return matching_cocktails