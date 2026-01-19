from services.ingredient_service import IngredientService
from models.cocktail import Cocktail
from typing import List, Dict, Any, Optional
from data.ttl_parser import (
    get_all_cocktails as get_local_cocktails,
    get_cocktails_by_ingredients as get_local_cocktails_by_ingredients,
    search_cocktails as search_local_cocktails,
    get_cocktail_details as get_local_cocktail_details
)


class CocktailService:
    def __init__(self):
        self.ingredient_service = IngredientService()
        # No longer maintaining own graph state, relying on centralized parser

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate a slug from cocktail name"""
        # Delegated to the parser via the models usually, but kept for utility if needed
        import re
        slug = name.lower()
        slug = re.sub(r'\([^)]*\)', '', slug)
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def get_all_cocktails(self) -> List[Cocktail]:
        """Get all cocktails from local TTL data using centralized parser"""
        return get_local_cocktails()

    def search_cocktails(self, query: str) -> List[Cocktail]:
        """Search cocktails by name"""
        return search_local_cocktails(query)

    def get_feasible_cocktails(self, user_id: str) -> List[Cocktail]:
        """Get cocktails that can be made with the user's inventory"""
        all_cocktails = self.get_all_cocktails()
        # Ensure we're comparing normalized ingredient names
        inventory = {ing.lower() for ing in self.ingredient_service.get_inventory(user_id)}
        
        feasible = []
        for cocktail in all_cocktails:
            if cocktail.parsed_ingredients:
                # Use the robustly parsed ingredients from ttl_parser
                cocktail_ingredients = {ing.lower() for ing in cocktail.parsed_ingredients}
                
                if cocktail_ingredients.issubset(inventory):
                    feasible.append(cocktail)
        
        return feasible

    def get_almost_feasible_cocktails(self, user_id: str) -> List[Dict[str, Any]]:
        """Get cocktails that are almost feasible (missing 1-2 ingredients)"""
        all_cocktails = self.get_all_cocktails()
        inventory = {ing.lower() for ing in self.ingredient_service.get_inventory(user_id)}
        
        almost_feasible = []
        for cocktail in all_cocktails:
            if cocktail.parsed_ingredients:
                cocktail_ingredients = {ing.lower() for ing in cocktail.parsed_ingredients}
                missing = list(cocktail_ingredients - inventory)
                
                if 1 <= len(missing) <= 2:
                    almost_feasible.append({
                        "cocktail": cocktail,
                        "missing": missing
                    })
        
        return almost_feasible

    def get_cocktails_by_ingredients(self, ingredients: List[str]) -> List[Cocktail]:
        """Get cocktails that contain all specified ingredients"""
        return get_local_cocktails_by_ingredients(ingredients)

    def get_cocktail_details(self, cocktail_uri: str) -> Optional[Dict[str, Any]]:
        """Get full details for a cocktail"""
        return get_local_cocktail_details(cocktail_uri)

    def get_similar_cocktails(self, cocktail_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get cocktails similar to the given cocktail based on ingredient overlap"""
        all_cocktails = self.get_all_cocktails()

        # Find the target cocktail
        target_cocktail = None
        for cocktail in all_cocktails:
            if cocktail.id == cocktail_id:
                target_cocktail = cocktail
                break

        if not target_cocktail or not target_cocktail.parsed_ingredients:
            return []

        target_ingredients = set(ing.lower() for ing in target_cocktail.parsed_ingredients)
        similarities = []

        for cocktail in all_cocktails:
            if cocktail.id == cocktail_id or not cocktail.parsed_ingredients:
                continue

            cocktail_ingredients = set(ing.lower() for ing in cocktail.parsed_ingredients)
            intersection = len(target_ingredients & cocktail_ingredients)
            union = len(target_ingredients | cocktail_ingredients)

            if union > 0:
                similarity_score = intersection / union
                similarities.append({
                    "cocktail": cocktail,
                    "similarity_score": similarity_score
                })

        # Sort by similarity score descending and return top limit
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similarities[:limit]

    def get_same_vibe_cocktails(self, cocktail_id: str, limit: int = 10) -> List[Cocktail]:
        """Get cocktails in the same graph community/cluster as the given cocktail"""
        from .graph_service import GraphService  # Import locally to avoid circular imports

        all_cocktails = self.get_all_cocktails()

        # Find the target cocktail
        target_cocktail = None
        for cocktail in all_cocktails:
            if cocktail.id == cocktail_id:
                target_cocktail = cocktail
                break

        if not target_cocktail:
            return []

        # Get graph analysis with communities
        graph_service = GraphService()
        graph_data = graph_service.build_graph()
        if not graph_data:
            return []
            
        analysis = graph_service.analyze_graph(graph_data)
        if not analysis:
            return []
            
        communities = analysis.get('communities', {})

        # Find the community of the target cocktail (using cocktail id, not name)
        target_community = None
        for node, community_id in communities.items():
            if node == target_cocktail.id:
                target_community = community_id
                break

        if target_community is None:
            return []

        # Find all cocktails in the same community
        same_vibe_cocktails = []
        for cocktail in all_cocktails:
            if cocktail.id != cocktail_id and cocktail.id in communities:
                if communities[cocktail.id] == target_community:
                    same_vibe_cocktails.append(cocktail)

        # Return up to limit cocktails
        return same_vibe_cocktails[:limit]

    def get_bridge_cocktails(self, limit: int = 10) -> List[Cocktail]:
        """Get cocktails that connect different communities (bridge cocktails)"""
        from .graph_service import GraphService  # Import locally to avoid circular imports

        all_cocktails = self.get_all_cocktails()

        # Get graph analysis with communities
        graph_service = GraphService()
        graph_data = graph_service.build_graph()
        if not graph_data:
            return []
            
        analysis = graph_service.analyze_graph(graph_data)
        if not analysis:
            return []
            
        communities = analysis.get('communities', {})

        bridge_cocktails = []

        for cocktail in all_cocktails:
            if not cocktail.parsed_ingredients:
                continue

            # Collect communities of ingredients used in this cocktail
            ingredient_communities = set()
            for ingredient_name in cocktail.parsed_ingredients:
                # Find ingredient ID by name (since graph nodes use ingredient IDs)
                # First, get all ingredients to find matching ID
                from .ingredient_service import IngredientService
                ingredient_service = IngredientService()
                ingredients = ingredient_service.get_all_ingredients()
                
                for ing in ingredients:
                    if ing.name.lower() == ingredient_name.lower():
                        if ing.id in communities:
                            ingredient_communities.add(communities[ing.id])
                        break

            # If ingredients span more than one community, it's a bridge cocktail
            if len(ingredient_communities) > 1:
                bridge_cocktails.append(cocktail)

        # Return up to limit bridge cocktails
        return bridge_cocktails[:limit]
