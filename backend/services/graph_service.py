import networkx as nx
from typing import Dict, List, Any
from .cocktail_service import CocktailService
from .ingredient_service import IngredientService
import json


class GraphService:
    def __init__(self):
        self.cocktail_service = CocktailService()
        self.ingredient_service = IngredientService()

    def build_graph(self) -> nx.Graph:
        """
        Build a NetworkX graph from cocktail and ingredient data.
        Nodes represent cocktails and ingredients, edges represent ingredient usage.
        """
        try:
            # Create a new graph
            graph = nx.Graph()
            
            # Get all cocktails
            cocktails = self.cocktail_service.get_all_cocktails()
            
            # Add cocktail nodes with type attribute
            for cocktail in cocktails:
                graph.add_node(cocktail.name, type='cocktail', id=cocktail.id)
            
            # Get all ingredients
            ingredients = self.ingredient_service.get_all_ingredients()
            
            # Add ingredient nodes with type attribute
            for ingredient in ingredients:
                graph.add_node(ingredient.name, type='ingredient', id=ingredient.id)
            
            # Add edges between cocktails and their ingredients
            for cocktail in cocktails:
                for ingredient_name in cocktail.parsed_ingredients or []:
                    if graph.has_node(ingredient_name):
                        graph.add_edge(cocktail.name, ingredient_name)
            
            return graph
            
        except Exception as e:
            raise Exception(f"Failed to build graph: {str(e)}")

    def analyze_graph(self) -> Dict[str, Any]:
        """
        Calculate centrality metrics and perform community detection.
        Returns a dict with 'metrics' and 'communities'.
        """
        try:
            # Build the graph
            graph = self.build_graph()
            
            # Calculate centrality metrics
            degree_centrality = nx.degree_centrality(graph)
            betweenness_centrality = nx.betweenness_centrality(graph)
            closeness_centrality = nx.closeness_centrality(graph)
            
            # Perform community detection using Louvain method
            communities = nx.algorithms.community.louvain_communities(graph)
            
            # Convert communities to a more usable format
            community_dict = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_dict[node] = i
            
            return {
                'metrics': {
                    'degree_centrality': degree_centrality,
                    'betweenness_centrality': betweenness_centrality,
                    'closeness_centrality': closeness_centrality
                },
                'communities': community_dict
            }
            
        except Exception as e:
            raise Exception(f"Failed to analyze graph: {str(e)}")

    def visualize_graph(self) -> Dict[str, Any]:
        """
        Generate a JSON representation suitable for D3.js visualization.
        Returns a dict with nodes and links with relevant properties.
        """
        try:
            # Build the graph
            graph = self.build_graph()
            
            # Prepare nodes with properties
            nodes = []
            for node, attributes in graph.nodes(data=True):
                node_type = attributes.get('type', 'unknown')
                node_id = attributes.get('id', node)
                
                # Calculate degree for each node
                degree = graph.degree(node)
                
                nodes.append({
                    'id': node,
                    'name': node,
                    'type': node_type,
                    'node_id': node_id,
                    'degree': degree
                })
            
            # Prepare links (edges)
            links = []
            for source, target in graph.edges():
                links.append({
                    'source': source,
                    'target': target,
                    'value': 1  # Weight of the edge
                })
            
            return {
                'nodes': nodes,
                'links': links
            }
            
        except Exception as e:
            raise Exception(f"Failed to visualize graph: {str(e)}")

    def analyze_disjoint_components(self) -> Dict[str, Any]:
        """
        Analyze disjoint components in the graph.
        Returns information about connected components including size and composition.
        """
        try:
            # Build the graph
            graph = self.build_graph()
            
            # Find connected components
            components = list(nx.connected_components(graph))
            
            # Analyze each component
            component_analysis = []
            
            for i, component in enumerate(components):
                component_nodes = list(component)
                
                # Count types in this component
                type_counts = {'cocktail': 0, 'ingredient': 0, 'unknown': 0}
                
                for node in component_nodes:
                    node_type = graph.nodes[node].get('type', 'unknown')
                    if node_type in type_counts:
                        type_counts[node_type] += 1
                    else:
                        type_counts['unknown'] += 1
                
                component_analysis.append({
                    'component_id': i,
                    'size': len(component_nodes),
                    'type_counts': type_counts,
                    'cocktail_ratio': type_counts['cocktail'] / len(component_nodes) if len(component_nodes) > 0 else 0,
                    'nodes': component_nodes
                })
            
            return {
                'num_components': len(components),
                'components': component_analysis,
                'largest_component_size': max([len(c) for c in components]) if components else 0,
                'smallest_component_size': min([len(c) for c in components]) if components else 0
            }
        
        except Exception as e:
            raise Exception(f"Failed to analyze disjoint components: {str(e)}")

    def export_graph(self) -> str:
        """
        Export graph data in Gephi-compatible format (GEXF).
        Returns the GEXF XML string.
        """
        try:
            # Build the graph
            graph = self.build_graph()
            
            # Export to GEXF format
            gexf_data = nx.write_gexf(graph, encoding='utf-8')
            
            # Convert bytes to string if needed
            if isinstance(gexf_data, bytes):
                gexf_data = gexf_data.decode('utf-8')
            
            return gexf_data
            
        except Exception as e:
            raise Exception(f"Failed to export graph: {str(e)}")