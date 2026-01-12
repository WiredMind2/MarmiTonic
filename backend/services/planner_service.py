from .cocktail_service import CocktailService
from .ingredient_service import IngredientService
from .sparql_service import SparqlService
from typing import List, Dict, Set, Optional, Any


class PlannerService:
    def __init__(self):
        self.cocktail_service = CocktailService()
        self.ingredient_service = IngredientService()
        self.sparql_service = SparqlService()
        self.cocktail_ingredients: Dict[str, Set[str]] = {}
        self._build_mapping()

    def _build_mapping(self):
        cocktails = self.cocktail_service.get_all_cocktails()
        for cocktail in cocktails:
            if cocktail.parsed_ingredients:
                self.cocktail_ingredients[cocktail.name] = set(cocktail.parsed_ingredients)
            else:
                self.cocktail_ingredients[cocktail.name] = set()

    def create_plan(self, available_ingredients: List[str], preferences: List[str]) -> Dict[str, Any]:
        """Create a plan based on available ingredients and preferences"""
        cocktails = self.cocktail_service.get_cocktails_for_ingredients(available_ingredients)
        
        return {
            "cocktails": cocktails,
            "available_ingredients": available_ingredients,
            "preferences": preferences
        }

    def get_shopping_list(self, ingredients: List[Any]) -> List[str]:
        """Generate a shopping list from ingredients"""
        if not ingredients:
            return []
        
        return [ing.name for ing in ingredients]

    def get_alternatives_for_missing_ingredient(self, ingredient_id: str) -> List[Any]:
        """Get alternative ingredients for a missing ingredient"""
        similar_cocktails = self.cocktail_service.get_similar_cocktails([])
        if not similar_cocktails:
            return []
        
        # This is a simplified implementation
        # In a real scenario, you'd analyze similar cocktails to find alternatives
        return []

    def get_recipe_steps(self, cocktail_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed recipe steps for a cocktail"""
        cocktail = self.cocktail_service.get_cocktail_by_id(cocktail_id)
        if not cocktail:
            return None
        
        steps = cocktail.preparation.split('\n') if cocktail.preparation else []
        
        return {
            "steps": steps,
            "cocktail": cocktail.name
        }

    def get_garnish_suggestions(self, cocktail_id: str) -> List[str]:
        """Get garnish suggestions for a cocktail"""
        query = f"""
        SELECT ?garnish WHERE {{
            <{cocktail_id}> <http://example.com/hasGarnish> ?garnish .
        }}
        """
        
        try:
            result = self.sparql_service.query_local_data(query)
            garnishes = []
            for binding in result.get("results", {}).get("bindings", []):
                if "garnish" in binding:
                    garnishes.append(binding["garnish"]["value"])
            return garnishes
        except Exception:
            return []

    def get_equipment_requirements(self, cocktail_id: str) -> Optional[Dict[str, Any]]:
        """Get equipment requirements for a cocktail"""
        cocktail = self.cocktail_service.get_cocktail_by_id(cocktail_id)
        if not cocktail:
            return None
        
        # Simple heuristic based on preparation
        equipment = []
        if cocktail.preparation and ("shake" in cocktail.preparation.lower()):
            equipment.append("Cocktail shaker")
        if cocktail.served:
            equipment.append(cocktail.served)
        
        return {
            "equipment": equipment,
            "cocktail": cocktail.name
        }

    def calculate_abv_for_plan(self, cocktails: List[Any]) -> Dict[str, float]:
        """Calculate total ABV for a plan"""
        total_abv = 0.0
        
        for cocktail in cocktails:
            # This is a placeholder - in reality you'd calculate based on ingredients
            total_abv += 0.1  # Assume 0.1 ABV per cocktail as placeholder
        
        return {
            "total_abv": total_abv,
            "cocktail_count": len(cocktails)
        }

    def get_timing_suggestions(self, cocktails: List[Any]) -> Dict[str, Any]:
        """Get timing suggestions for preparing multiple cocktails"""
        if not cocktails:
            return {"prep_time": 0, "total_time": 0}
        
        # Simple heuristic: 5 minutes per cocktail
        prep_time = len(cocktails) * 5
        total_time = prep_time + 10  # Add 10 minutes for setup
        
        return {
            "prep_time": prep_time,
            "total_time": total_time,
            "cocktail_count": len(cocktails)
        }

    def suggest_preparation_order(self, cocktails: List[Any]) -> Dict[str, Any]:
        """Suggest optimal preparation order for cocktails"""
        if not cocktails:
            return {"order": []}
        
        # Simple approach: sort by name for now
        order = sorted(cocktails, key=lambda x: x.name)
        
        return {
            "order": order,
            "strategy": "alphabetical"
        }

    def get_nutrition_info(self, cocktail_id: str) -> Optional[Dict[str, Any]]:
        """Get nutrition information for a cocktail"""
        cocktail = self.cocktail_service.get_cocktail_by_id(cocktail_id)
        if not cocktail:
            return None
        
        # Placeholder nutrition info
        return {
            "calories": 150,
            "carbs": "10g",
            "sugar": "8g",
            "cocktail": cocktail.name
        }

    def get_guest_preferences_summary(self, guests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of guest preferences"""
        if not guests:
            return {"summary": "No guests"}
        
        all_preferences = []
        for guest in guests:
            all_preferences.extend(guest.get("preferences", []))
        
        return {
            "summary": f"{len(guests)} guests with {len(set(all_preferences))} unique preferences",
            "guest_count": len(guests),
            "unique_preferences": len(set(all_preferences))
        }

    def optimize_party_mode(self, num_ingredients: int) -> Dict[str, List]:
        if num_ingredients <= 0:
            return {'selected_ingredients': [], 'covered_cocktails': []}

        # Get all unique ingredients
        all_ingredients = set()
        for ings in self.cocktail_ingredients.values():
            all_ingredients.update(ings)

        selected = []
        covered_cocktails = set()

        for _ in range(min(num_ingredients, len(all_ingredients))):
            best_ing = None
            max_new = 0
            for ing in all_ingredients - set(selected):
                new_covered = {c for c in self.cocktail_ingredients if ing in self.cocktail_ingredients[c] and c not in covered_cocktails}
                if len(new_covered) > max_new:
                    max_new = len(new_covered)
                    best_ing = ing
            if best_ing is None:
                break
            selected.append(best_ing)
            covered_cocktails.update(new_covered)

        return {
            'selected_ingredients': selected,
            'covered_cocktails': list(covered_cocktails)
        }

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
            best_covers = set()
            for ing in all_ingredients - set(selected):
                covers = {c for c in universe if ing in self.cocktail_ingredients.get(c, set()) and c not in covered}
                if len(covers) > max_cover:
                    max_cover = len(covers)
                    best_ing = ing
                    best_covers = covers
            if best_ing is None:
                # Cannot cover remaining
                break
            selected.append(best_ing)
            covered.update(best_covers)

        return {
            'selected_ingredients': selected,
            'covered_cocktails': list(covered)
        }

    def get_union_ingredients(self, cocktail_names: List[str]) -> List[str]:
        """Get the union of ingredients for a list of cocktails"""
        union_ingredients = set()
        found_any = False

        for name in cocktail_names:
            if name in self.cocktail_ingredients:
                union_ingredients.update(self.cocktail_ingredients[name])
                found_any = True

        if not found_any and cocktail_names:
            raise ValueError("No valid cocktails found in the provided list")

        return list(union_ingredients)