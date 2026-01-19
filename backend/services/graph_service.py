import networkx as nx
from typing import Dict, List, Any, Optional
from backend.services.cocktail_service import CocktailService
from backend.services.ingredient_service import IngredientService
from backend.services.sparql_service import SparqlService
import json
import io


class GraphService:
    def __init__(self):
        self.cocktail_service = CocktailService()
        self.ingredient_service = IngredientService()
        self.sparql_service = SparqlService()

    def build_graph(self) -> Optional[Dict[str, Any]]:
        """
        Build a graph from cocktail and ingredient data.
        Returns graph data in a format suitable for analysis and visualization.
        """
        try:
            # Get all cocktails and ingredients
            cocktails = self.cocktail_service.get_all_cocktails()
            ingredients = self.ingredient_service.get_all_ingredients()
            
            # Build graph data structure
            graph_data = {
                'nodes': [],
                'edges': []
            }
            
            # Add cocktail nodes
            cocktail_nodes = {}
            for cocktail in cocktails:
                if cocktail.id and cocktail.name:
                    cocktail_nodes[cocktail.id] = {
                        'id': cocktail.id,
                        'name': cocktail.name,
                        'type': 'cocktail'
                    }
                    graph_data['nodes'].append(cocktail_nodes[cocktail.id])
            
            # Add ingredient nodes
            ingredient_nodes = {}
            for ingredient in ingredients:
                if ingredient.id and ingredient.name:
                    ingredient_nodes[ingredient.id] = {
                        'id': ingredient.id,
                        'name': ingredient.name,
                        'type': 'ingredient'
                    }
                    graph_data['nodes'].append(ingredient_nodes[ingredient.id])
            
            # Add edges between cocktails and their ingredients
            for cocktail in cocktails:
                if cocktail.id and hasattr(cocktail, 'parsed_ingredients') and cocktail.parsed_ingredients:
                    for ingredient_name in cocktail.parsed_ingredients:
                        # Find ingredient by name (simplified for testing)
                        # Use case-insensitive matching and check for partial matches
                        ing_name_lower = ingredient_name.lower().strip()
                        for ingredient in ingredients:
                            if ingredient.id and ingredient.name:
                                target_name_lower = ingredient.name.lower().strip()
                                if ing_name_lower == target_name_lower or \
                                   ing_name_lower in target_name_lower or \
                                   target_name_lower in ing_name_lower:
                                    graph_data['edges'].append({
                                        'source': cocktail.id,
                                        'target': ingredient.id,
                                        'type': 'cocktail_ingredient'
                                    })
                                    break
            
            return graph_data
            
        except Exception as e:
            print(f"Error building graph: {e}")
            raise Exception("Failed to build graph")

    def get_graph_data(self, query: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get graph data from SPARQL service and convert to graph format.
        If query is provided, execute it. Otherwise use default query.
        """
        try:
            # Query data from SPARQL service
            if query:
                final_results = self.sparql_service.execute_local_query(query)
            else:
                # Default behavior: generic query for cocktails and ingredients
                default_query = """
                PREFIX dbo: <http://dbpedia.org/ontology/>
                PREFIX dbp: <http://dbpedia.org/property/>
                
                SELECT ?cocktail ?ingredient WHERE {
                    ?cocktail a dbo:Cocktail .
                    ?cocktail dbp:ingredients ?ingredient .
                } LIMIT 100
                """
                final_results = self.sparql_service.execute_local_query(default_query)
            
            if not final_results or 'results' not in final_results or 'bindings' not in final_results['results']:
                return None
            
            # Build graph from query results (Flexible parsing)
            nodes = {}
            edges = []
            
            bindings = final_results['results']['bindings']
            
            for row in bindings:
                # Extract all URIs/Literals as nodes
                row_values = []
                for var_name, value_obj in row.items():
                    val = value_obj['value']
                    type_ = value_obj['type']
                    
                    if val not in nodes:
                         nodes[val] = {
                             'id': val, 
                             'name': val.split('/')[-1] if type_ == 'uri' else val,
                             'type': 'resource' if type_ == 'uri' else 'literal'
                         }
                    row_values.append(val)
                
                # Create links (Star topology or pairwise)
                if len(row_values) > 1:
                    source = row_values[0]
                    for target in row_values[1:]:
                        if source != target:
                            edges.append({
                                'source': source,
                                'target': target
                            })
                            
            return {
                'nodes': list(nodes.values()),
                'edges': edges
            }
            
        except Exception as e:
            print(f"Error getting graph data: {e}")
            return None

        """
        Convert graph data to NetworkX graph format.
        """
        graph = nx.Graph()
        
        # Add nodes
        for node in graph_data['nodes']:
            node_id = node['id']
            graph.add_node(node_id)
        
        # Add edges
        for edge in graph_data['edges']:
            source = edge['source']
            target = edge['target']
            graph.add_edge(source, target)
        
        return graph