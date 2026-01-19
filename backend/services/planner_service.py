from backend.services.cocktail_service import CocktailService
from backend.services.ingredient_service import IngredientService
from typing import List, Dict, Set


class PlannerService:
    def __init__(self):
        self.cocktail_service = CocktailService()
        self.ingredient_service = IngredientService()
        self.cocktail_ingredients: Dict[str, Set[str]] = {}
        self._build_mapping()

    def _build_mapping(self):
        cocktails = self.cocktail_service.get_all_cocktails()
        for cocktail in cocktails:
            if cocktail.parsed_ingredients:
                self.cocktail_ingredients[cocktail.name] = set(cocktail.parsed_ingredients)
            else:
                self.cocktail_ingredients[cocktail.name] = set()

  

    def optimize_playlist_mode(self, cocktail_names: List[str]) -> Dict[str, List]:
        """
        Get all unique ingredients needed to make all cocktails in the playlist.
        Returns all ingredients required across the cocktail list.
        """
        if not cocktail_names:
            return {'selected_ingredients': [], 'covered_cocktails': []}

        # Filter to existing cocktails
        valid_cocktails = [c for c in cocktail_names if c in self.cocktail_ingredients]
        if not valid_cocktails:
            return {'selected_ingredients': [], 'covered_cocktails': []}

        # Get union of all ingredients needed for these cocktails
        all_ingredients = set()
        for cocktail_name in valid_cocktails:
            all_ingredients.update(self.cocktail_ingredients.get(cocktail_name, set()))

        return {
            'selected_ingredients': sorted(list(all_ingredients)),
            'covered_cocktails': valid_cocktails
        }