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
        Requires a query - no default fallback.
        Uses parsed ingredients from cocktails to create individual ingredient nodes.
        """
        try:
            # Query data from SPARQL service
            if not query:
                raise ValueError("No SPARQL query provided")
            
            final_results = self.sparql_service.execute_local_query(query)
            
            if not final_results or 'results' not in final_results or 'bindings' not in final_results['results']:
                return None
            
            # Build graph from query results
            nodes = {}
            edges = []
            
            bindings = final_results['results']['bindings']
            
            # Get all cocktails with parsed ingredients for enrichment
            cocktails = self.cocktail_service.get_all_cocktails()
            cocktails_by_uri = {c.uri: c for c in cocktails if hasattr(c, 'uri')}
            
            for row in bindings:
                row_values = []
                cocktail_uri = None
                cocktail_name_from_query = None
                
                for var_name, value_obj in row.items():
                    val = value_obj['value']
                    type_ = value_obj['type']
                    
                    # Track cocktail URI and name
                    if var_name == 'cocktail':
                        cocktail_uri = val
                    elif var_name == 'name':
                        cocktail_name_from_query = val
                    
                    if val not in nodes:
                        # Use the name from query if available for better display
                        node_name = val.split('/')[-1].replace('_', ' ') if type_ == 'uri' else val
                        if var_name == 'cocktail' and cocktail_name_from_query:
                            node_name = cocktail_name_from_query
                        
                        # For cocktails, get the slug ID from cocktail_service
                        cocktail_id = val  # Default to URI
                        if var_name == 'cocktail' and cocktail_uri in cocktails_by_uri:
                            cocktail_id = cocktails_by_uri[cocktail_uri].id  # Use slug ID
                        
                        nodes[val] = {
                            'id': cocktail_id if var_name == 'cocktail' else val,
                            'uri': val if var_name == 'cocktail' else None,  # Keep URI for reference
                            'name': node_name,
                            'type': 'cocktail' if var_name == 'cocktail' else ('ingredient' if type_ == 'uri' else 'literal')
                        }
                    row_values.append(val)
                
                # Update cocktail node with proper name and ID if we got it from query
                if cocktail_uri and cocktail_uri in nodes and cocktail_uri in cocktails_by_uri:
                    nodes[cocktail_uri]['name'] = cocktail_name_from_query or nodes[cocktail_uri]['name']
                    nodes[cocktail_uri]['id'] = cocktails_by_uri[cocktail_uri].id  # Ensure slug ID
                
                # Create edges between cocktail and ingredients (use URI as key)
                if len(row_values) > 1:
                    source = row_values[0]
                    for target in row_values[1:]:
                        if source != target:
                            edges.append({
                                'source': cocktails_by_uri[source].id if source in cocktails_by_uri else source,
                                'target': target
                            })
                
                # Add parsed ingredients as individual nodes
                if cocktail_uri and cocktail_uri in cocktails_by_uri:
                    cocktail = cocktails_by_uri[cocktail_uri]
                    if hasattr(cocktail, 'parsed_ingredients') and cocktail.parsed_ingredients:
                        for ingredient_name in cocktail.parsed_ingredients:
                            # Create unique ID for ingredient
                            ingredient_id = f"ingredient:{ingredient_name.lower().replace(' ', '_')}"
                            
                            if ingredient_id not in nodes:
                                nodes[ingredient_id] = {
                                    'id': ingredient_id,
                                    'name': ingredient_name,
                                    'type': 'ingredient'
                                }
                            
                            # Add edge from cocktail (using slug ID) to ingredient
                            if not any(e['source'] == cocktail.id and e['target'] == ingredient_id for e in edges):
                                edges.append({
                                    'source': cocktail.id,  # Use slug ID
                                    'target': ingredient_id
                                })
            
            # Filter out literal nodes (text fields like dbp:ingredients raw text)
            # Keep only cocktail and ingredient nodes
            filtered_nodes = [node for node in nodes.values() if node['type'] in ['cocktail', 'ingredient']]
            
            # Filter edges to only those connecting filtered nodes
            filtered_node_ids = {node['id'] for node in filtered_nodes}
            filtered_edges = [
                edge for edge in edges 
                if edge['source'] in filtered_node_ids and edge['target'] in filtered_node_ids
            ]
            
            return {
                'nodes': filtered_nodes,
                'edges': filtered_edges
            }
            
        except Exception as e:
            print(f"Error getting graph data: {e}")
            import traceback
            traceback.print_exc()
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