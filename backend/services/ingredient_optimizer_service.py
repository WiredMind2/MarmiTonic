from typing import List, Dict, Set
from services.cocktail_service import CocktailService
from services.ingredient_service import IngredientService

class IngredientOptimizerService:
    def __init__(self):
        self.cocktail_service = CocktailService()
        self.ingredient_service = IngredientService()

    def find_optimal_ingredients(self, N: int) -> Dict[str, any]:
        """
        Find the optimal set of N ingredients that can produce the largest number of cocktails.
        Uses a heuristic algorithm to select ingredients that complete the most cocktail recipes.
        
        Args:
            N (int): Number of ingredients to select
            
        Returns:
            Dict[str, any]: Dictionary containing selected ingredients and cocktail count
        """
        # Step 1: Get all cocktails and filter those that require too many ingredients
        all_cocktails = self.cocktail_service.get_all_cocktails()
        
        # Pre-process cocktails to sets for faster lookup
        # Only consider cocktails that have ingredients and can possibly be made with N ingredients
        valid_cocktails = []
        possible_ingredients = set()
        
        for c in all_cocktails:
            if c.parsed_ingredients and len(c.parsed_ingredients) <= N:
                ing_set = set(c.parsed_ingredients)
                valid_cocktails.append({
                    'cocktail': c,
                    'ingredients': ing_set
                })
                possible_ingredients.update(ing_set)
        
        selected_ingredients = set()
        
        # Step 2: Iteratively select N ingredients
        for _ in range(N):
            best_ingredient = None
            best_score = -1.0
            
            # Identify candidates (ingredients not yet selected)
            candidates = possible_ingredients - selected_ingredients
            
            if not candidates:
                break
                
            for ingredient in candidates:
                score = 0.0
                
                # Calculate score based on how much this ingredient helps complete cocktails
                for vc in valid_cocktails:
                    required = vc['ingredients']
                    if ingredient not in required:
                        continue
                        
                    # Calculate missing ingredients if we were to add this one
                    missing_count = sum(1 for i in required if i not in selected_ingredients)
                    
                    # If this ingredient is one of the missing ones, it reduces the count by 1
                    # We want to know the *current* missing count (including this ingredient)
                    # The loop above calculates missing count *before* adding this ingredient.
                    # Wait, careful. "if i not in selected_ingredients".
                    # Since 'ingredient' is from 'candidates' (not selected), it IS in the missing count.
                    
                    # We want to incentivize completing cocktails.
                    # If missing_count == 1: picking this ingredient -> Complete! Score High.
                    
                    if missing_count == 1:
                        score += 100.0
                    else:
                        # missing_count > 1. 
                        # We reward progress. smaller missing_count is better.
                        score += 1.0 / missing_count
                
                if score > best_score:
                    best_score = score
                    best_ingredient = ingredient
            
            if best_ingredient:
                selected_ingredients.add(best_ingredient)
        
        # Step 3: Calculate final results
        completed_count = 0
        possible_cocktails = []
        for vc in valid_cocktails:
            if vc['ingredients'].issubset(selected_ingredients):
                completed_count += 1
                possible_cocktails.append(vc['cocktail'])
        
        return {
            "ingredients": list(selected_ingredients),
            "cocktail_count": completed_count,
            "cocktails": possible_cocktails
        }