from .cocktail_service import CocktailService
from .ingredient_service import IngredientService
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
        if not cocktail_names:
            return {'selected_ingredients': [], 'covered_cocktails': []}

        # Filter to existing cocktails
        universe = set(c for c in cocktail_names if c in self.cocktail_ingredients)
        if not universe:
            return {'selected_ingredients': [], 'covered_cocktails': []}

        # Get all unique ingredients
        all_ingredients = set()
        for ings in self.cocktail_ingredients.values():
            all_ingredients.update(ings)

        selected = []
        covered = set()

        while covered != universe:
            best_ing = None
            max_cover = 0
            for ing in all_ingredients - set(selected):
                covers = {c for c in universe if ing in self.cocktail_ingredients.get(c, set()) and c not in covered}
                if len(covers) > max_cover:
                    max_cover = len(covers)
                    best_ing = ing
            if best_ing is None:
                # Cannot cover remaining
                break
            selected.append(best_ing)
            covered.update(covers)

        return {
            'selected_ingredients': selected,
            'covered_cocktails': list(covered)
        }