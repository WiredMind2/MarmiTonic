from .sparql_service import SparqlService
from .ingredient_service import IngredientService
from ..models.cocktail import Cocktail
from typing import List, Dict, Any
import rdflib
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from collections import defaultdict
import re

from pathlib import Path
from ..utils.graph_loader import get_shared_graph

# Define namespaces
DBO = rdflib.Namespace("http://dbpedia.org/ontology/")
DBP = rdflib.Namespace("http://dbpedia.org/property/")
DCT = rdflib.Namespace("http://purl.org/dc/terms/")

class CocktailService:
    def __init__(self):
        # SparqlService now defaults to using the shared graph
        self.sparql_service = SparqlService()
        self.ingredient_service = IngredientService()
        self.graph = get_shared_graph()

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate a slug from cocktail name"""
        # Convert to lowercase
        slug = name.lower()
        # Remove parentheses and their content
        slug = re.sub(r'\([^)]*\)', '', slug)
        # Replace non-alphanumeric characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def _load_local_data(self):
        pass

    def _parse_cocktail_from_graph(self, cocktail_uri: URIRef) -> Cocktail:
        """Parse a cocktail from the RDF graph"""
        if not self.graph:
            return None

        # Get basic properties
        name = self._get_property(cocktail_uri, RDFS.label, "en")
        if not name:
            name = self._get_property(cocktail_uri, DBO.name, "en")

        # Get multilingual labels
        labels = {}
        for lang in self.graph.objects(cocktail_uri, RDFS.label):
            if isinstance(lang, Literal):
                labels[lang.language] = str(lang)

        # Get multilingual descriptions
        descriptions = {}
        for desc in self.graph.objects(cocktail_uri, DBO.description):
            if isinstance(desc, Literal):
                descriptions[desc.language] = str(desc)

        # Get other properties
        image = self._get_property(cocktail_uri, DBO.depiction)
        ingredients = self._get_property(cocktail_uri, DBP.ingredients, "en")
        preparation = self._get_property(cocktail_uri, DBP.prep, "en")
        served = self._get_property(cocktail_uri, DBP.served, "en")
        garnish = self._get_property(cocktail_uri, DBP.garnish, "en")
        source_link = self._get_property(cocktail_uri, DBP.sourcelink, "en")

        # Get categories
        categories = []
        for category in self.graph.objects(cocktail_uri, DCT.subject):
            categories.append(str(category))

        # Get related ingredients/concepts
        related = []
        for related_uri in self.graph.objects(cocktail_uri, DBO.wikiPageWikiLink):
            related.append(str(related_uri))

        # Get alternative names
        alt_names = []
        for alt_name in self.graph.objects(cocktail_uri, DBO.name):
            if isinstance(alt_name, Literal) and alt_name != name:
                alt_names.append(str(alt_name))

        cocktail_name = name or "Unknown Cocktail"
        return Cocktail(
            uri=str(cocktail_uri),
            id=self.generate_slug(cocktail_name),
            name=cocktail_name,
            alternative_names=alt_names if alt_names else None,
            description=descriptions.get("en") or None,
            image=image,
            ingredients=ingredients,
            preparation=preparation,
            served=served,
            garnish=garnish,
            source_link=source_link,
            categories=categories if categories else None,
            related_ingredients=related if related else None,
            labels=labels if labels else None,
            descriptions=descriptions if descriptions else None
            
        )

    def _get_property(self, subject: URIRef, predicate: URIRef, lang: str = None) -> str:
        """Get a property value from the graph"""
        if not self.graph:
            return None

        values = []
        for obj in self.graph.objects(subject, predicate):
            if isinstance(obj, Literal):
                if lang and obj.language != lang:
                    continue
                values.append(str(obj))
            else:
                values.append(str(obj))

        return ", ".join(values) if values else None

    def get_all_cocktails(self) -> List[Cocktail]:
        """Get all cocktails from local TTL data using SPARQL"""
        query = """
        SELECT ?cocktail ?name ?desc ?image ?ingredients ?prep ?served ?garnish ?source WHERE {
            ?cocktail rdfs:label ?name .
            FILTER(LANG(?name) = "en")
            OPTIONAL { ?cocktail dbo:description ?desc . FILTER(LANG(?desc) = "en") }
            OPTIONAL { ?cocktail foaf:depiction ?image }
            OPTIONAL { ?cocktail dbp:ingredients ?ingredients . FILTER(LANG(?ingredients) = "en") }
            OPTIONAL { ?cocktail dbp:prep ?prep . FILTER(LANG(?prep) = "en") }
            OPTIONAL { ?cocktail dbp:served ?served . FILTER(LANG(?served) = "en") }
            OPTIONAL { ?cocktail dbp:garnish ?garnish . FILTER(LANG(?garnish) = "en") }
            OPTIONAL { ?cocktail dbp:sourcelink ?source . FILTER(LANG(?source) = "en") }
        }
        """
        try:
            results = self.sparql_service.execute_local_query(query)
        except Exception as e:
            print(f"SPARQL query failed: {e}")
            return []

        cocktails_dict = {}
        for result in results["results"]["bindings"]:
            cocktail_uri = result["cocktail"]["value"]

            # If we've already seen this cocktail URI, skip (keep first occurrence)
            if cocktail_uri in cocktails_dict:
                continue

            name = result.get("name", {}).get("value", "Unknown Cocktail")
            description = result.get("desc", {}).get("value")
            image = result.get("image", {}).get("value")
            ingredients = result.get("ingredients", {}).get("value")
            preparation = result.get("prep", {}).get("value")
            served = result.get("served", {}).get("value")
            garnish = result.get("garnish", {}).get("value")
            source_link = result.get("source", {}).get("value")

            # Parse ingredients and get URIs
            parsed_ingredients = self._parse_ingredient_names(ingredients) if ingredients else None
            ingredient_uris = self._extract_ingredient_uris(cocktail_uri) if self.graph else None

            cocktail = Cocktail(
                uri=cocktail_uri,
                id=self.generate_slug(name),
                name=name,
                description=description,
                image=image,
                ingredients=ingredients,
                parsed_ingredients=parsed_ingredients,
                ingredient_uris=ingredient_uris,
                preparation=preparation,
                served=served,
                garnish=garnish,
                source_link=source_link
            )
            cocktails_dict[cocktail_uri] = cocktail

        # Return list of unique cocktails preserving first-seen order
        return list(cocktails_dict.values())

    def search_cocktails(self, query: str) -> List[Cocktail]:
        """Search cocktails by name"""
        all_cocktails = self.get_all_cocktails()
        if not query:
            return all_cocktails

        query_lower = query.lower()
        return [
            cocktail for cocktail in all_cocktails 
            if query_lower in cocktail.name.lower() 
            or any(query_lower in alt_name.lower() for alt_name in cocktail.alternative_names or [])
        ]

    def get_feasible_cocktails(self, user_id: str) -> List[Cocktail]:
        """Get cocktails that can be made with the user's inventory"""
        all_cocktails = self.get_all_cocktails()
        inventory = self.ingredient_service.get_inventory(user_id)
        
        feasible = []
        for cocktail in all_cocktails:
            if cocktail.ingredients:
                # Parse ingredients from text format
                ingredient_names = self._parse_ingredient_names(cocktail.ingredients)
                missing = [ing for ing in ingredient_names if ing not in inventory]
                if len(missing) == 0:
                    feasible.append(cocktail)
        
        return feasible

    def get_almost_feasible_cocktails(self, user_id: str) -> List[Dict[str, Any]]:
        """Get cocktails that are almost feasible (missing 1-2 ingredients)"""
        all_cocktails = self.get_all_cocktails()
        inventory = self.ingredient_service.get_inventory(user_id)
        
        almost_feasible = []
        for cocktail in all_cocktails:
            if cocktail.ingredients:
                ingredient_names = self._parse_ingredient_names(cocktail.ingredients)
                missing = [ing for ing in ingredient_names if ing not in inventory]
                if 1 <= len(missing) <= 2:
                    almost_feasible.append({
                        "cocktail": cocktail,
                        "missing": missing
                    })
        
        return almost_feasible

    def _parse_ingredient_names(self, ingredients_text: str) -> List[str]:
        """Parse ingredient names from the text format"""
        if not ingredients_text:
            return []

        # Simple parsing - extract ingredient names after * or numbers
        lines = ingredients_text.split("\n")
        ingredient_names = []

        for line in lines:
            line = line.strip()
            if line.startswith("*") or line.startswith("•"):
                # Remove the bullet and any quantities
                clean_line = line[1:].strip()
                # Remove quantities like "45 ml", "15 ml", etc.
                clean_line = re.sub(r'^\d+\s*(ml|cl|oz|dash|barspoon|tsp|teaspoon|tablespoon)\s*', '', clean_line, flags=re.IGNORECASE)
                clean_line = clean_line.strip()
                if clean_line:
                    ingredient_names.append(clean_line)

        return ingredient_names

    def _extract_ingredient_uris(self, cocktail_uri: str) -> List[str]:
        """Extract ingredient URIs from cocktail's wikiPageWikiLink"""
        if not self.graph:
            return []

        uris = []
        for obj in self.graph.objects(URIRef(cocktail_uri), DBO.wikiPageWikiLink):
            uris.append(str(obj))
        return uris

    def get_cocktails_by_ingredients(self, ingredients: List[str]) -> List[Cocktail]:
        """Get cocktails that contain all specified ingredients"""
        all_cocktails = self.get_all_cocktails()
        matching_cocktails = []

        for cocktail in all_cocktails:
            if cocktail.ingredients:
                ingredient_names = self._parse_ingredient_names(cocktail.ingredients)
                # Check if all provided ingredients are in the cocktail's ingredients
                if all(ingredient.lower() in [ing.lower() for ing in ingredient_names]
                       for ingredient in ingredients):
                    matching_cocktails.append(cocktail)

        return matching_cocktails

    def get_cocktails_by_uris(self, uris: List[str]) -> List[Cocktail]:
        """Get cocktails that contain ingredients with the specified URIs"""
        all_cocktails = self.get_all_cocktails()
        matching_cocktails = []

        for cocktail in all_cocktails:
            if cocktail.ingredient_uris:
                # Check if any of the provided URIs match the cocktail's ingredient URIs
                if any(uri in cocktail.ingredient_uris for uri in uris):
                    matching_cocktails.append(cocktail)

        return matching_cocktails

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
        analysis = graph_service.analyze_graph()
        communities = analysis.get('communities', {})

        # Find the community of the target cocktail
        target_community = None
        for node, community_id in communities.items():
            if node == target_cocktail.name:
                target_community = community_id
                break

        if target_community is None:
            return []

        # Find all cocktails in the same community
        same_vibe_cocktails = []
        for cocktail in all_cocktails:
            if cocktail.id != cocktail_id and cocktail.name in communities:
                if communities[cocktail.name] == target_community:
                    same_vibe_cocktails.append(cocktail)

        # Return up to limit cocktails
        return same_vibe_cocktails[:limit]

    def get_bridge_cocktails(self, limit: int = 10) -> List[Cocktail]:
        """Get cocktails that connect different communities (bridge cocktails)"""
        from .graph_service import GraphService  # Import locally to avoid circular imports

        all_cocktails = self.get_all_cocktails()

        # Get graph analysis with communities
        graph_service = GraphService()
        analysis = graph_service.analyze_graph()
        communities = analysis.get('communities', {})

        bridge_cocktails = []

        for cocktail in all_cocktails:
            if not cocktail.parsed_ingredients:
                continue

            # Collect communities of ingredients used in this cocktail
            ingredient_communities = set()
            for ingredient_name in cocktail.parsed_ingredients:
                if ingredient_name in communities:
                    ingredient_communities.add(communities[ingredient_name])

            # If ingredients span more than one community, it's a bridge cocktail
            if len(ingredient_communities) > 1:
                bridge_cocktails.append(cocktail)

        # Return up to limit bridge cocktails
        return bridge_cocktails[:limit]