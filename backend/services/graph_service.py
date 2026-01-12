import networkx as nx
from typing import Dict, List, Any, Optional
from .cocktail_service import CocktailService
from .ingredient_service import IngredientService
from .sparql_service import SparqlService
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
                        for ingredient in ingredients:
                            if ingredient.name == ingredient_name and ingredient.id:
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

    def analyze_graph(self, graph_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculate centrality metrics and perform community detection.
        Returns a dict with 'metrics' and 'communities'.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
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
                'node_count': len(graph.nodes()),
                'edge_count': len(graph.edges()),
                'metrics': {
                    'degree_centrality': degree_centrality,
                    'betweenness_centrality': betweenness_centrality,
                    'closeness_centrality': closeness_centrality
                },
                'communities': community_dict
            }
            
        except Exception as e:
            print(f"Error analyzing graph: {e}")
            return None

    def visualize_graph(self, graph_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a visualization representation for the graph.
        Returns a dict with html representation for testing compatibility.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            # Generate a simple HTML representation for testing
            html_content = f"""
            <html>
                <body>
                    <h1>Graph Visualization</h1>
                    <p>Nodes: {len(graph.nodes())}</p>
                    <p>Edges: {len(graph.edges())}</p>
                </body>
            </html>
            """
            
            return {
                'html': html_content,
                'nodes': list(graph.nodes()),
                'edges': list(graph.edges())
            }
            
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            return None

    def analyze_disjoint_components(self, graph_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze disjoint components in the graph.
        Returns information about connected components including size and composition.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            # Find connected components
            components = list(nx.connected_components(graph))
            
            # Analyze each component
            component_analysis = []
            
            for i, component in enumerate(components):
                component_nodes = list(component)
                
                component_analysis.append({
                    'component_id': i,
                    'size': len(component_nodes),
                    'nodes': component_nodes
                })
            
            return {
                'num_components': len(components),
                'components': component_analysis,
                'largest_component_size': max([len(c) for c in components]) if components else 0,
                'smallest_component_size': min([len(c) for c in components]) if components else 0,
                'isolated_nodes': sum(1 for c in components if len(c) == 1)
            }
         
        except Exception as e:
            print(f"Error analyzing disjoint components: {e}")
            return None

    def export_graph(self, graph_data: Dict[str, Any], format: str = "gexf") -> Optional[str]:
        """
        Export graph data in the specified format.
        Returns the formatted string.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            if format == "gexf":
                # Export to GEXF format
                buffer = io.BytesIO()
                nx.write_gexf(graph, buffer, encoding='utf-8')
                return buffer.getvalue().decode('utf-8')
            elif format == "json":
                # Export to JSON format
                return json.dumps(graph_data)
            elif format == "xml":
                # Export to GraphML format
                buffer = io.BytesIO()
                nx.write_graphml(graph, buffer, encoding='utf-8')
                return buffer.getvalue().decode('utf-8')
            elif format == "dot":
                # Export to DOT format
                try:
                    return nx.nx_pydot.to_pydot(graph).to_string()
                except ImportError:
                    # Fallback if pydot is not available
                    dot_content = "digraph G {\n"
                    for node in graph.nodes():
                        dot_content += f"    {node};\n"
                    for source, target in graph.edges():
                        dot_content += f"    {source} -> {target};\n"
                    dot_content += "}\n"
                    return dot_content
            else:
                return None
            
        except Exception as e:
            print(f"Error exporting graph: {e}")
            return None

    def get_centrality_scores(self, graph_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate degree centrality scores for all nodes in the graph.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            # Calculate degree centrality
            return nx.degree_centrality(graph)
            
        except Exception as e:
            print(f"Error getting centrality scores: {e}")
            return {}

    def get_community_detection(self, graph_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform community detection on the graph.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            # Perform community detection using Louvain method
            communities = nx.algorithms.community.louvain_communities(graph)
            
            # Convert communities to a more usable format
            community_dict = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_dict[node] = i
            
            return {
                'communities': community_dict,
                'num_communities': len(communities)
            }
            
        except Exception as e:
            print(f"Error detecting communities: {e}")
            return None

    def get_shortest_path(self, graph_data: Dict[str, Any], source: str, target: str) -> Optional[Dict[str, Any]]:
        """
        Find the shortest path between two nodes in the graph.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            if source not in graph or target not in graph:
                return {"path": None, "length": 0}
            
            if source == target:
                return {"path": [source], "length": 0}
            
            try:
                path = nx.shortest_path(graph, source=source, target=target)
                return {
                    "path": path,
                    "length": len(path) - 1
                }
            except nx.NetworkXNoPath:
                return {"path": None, "length": 0}
            
        except Exception as e:
            print(f"Error finding shortest path: {e}")
            return None

    def get_node_degree(self, graph_data: Dict[str, Any], node: str) -> int:
        """
        Get the degree of a specific node in the graph.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            if node in graph:
                return graph.degree(node)
            else:
                return 0
            
        except Exception as e:
            print(f"Error getting node degree: {e}")
            return 0

    def generate_force_directed_data(self, graph_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate data suitable for force-directed graph visualization.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            # Prepare nodes with properties
            nodes = []
            for node in graph.nodes():
                nodes.append({
                    'id': node,
                    'name': node
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
            print(f"Error generating force-directed data: {e}")
            return None

    def get_graph_statistics(self, graph_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculate various statistics about the graph.
        """
        try:
            # Convert graph data to NetworkX graph
            graph = self._convert_to_networkx(graph_data)
            
            node_count = len(graph.nodes())
            edge_count = len(graph.edges())
            
            # Calculate density
            density = nx.density(graph) if node_count > 1 else 0.0
            
            # Calculate average degree
            avg_degree = sum(dict(graph.degree()).values()) / node_count if node_count > 0 else 0.0
            
            return {
                'node_count': node_count,
                'edge_count': edge_count,
                'density': density,
                'avg_degree': avg_degree
            }
            
        except Exception as e:
            print(f"Error getting graph statistics: {e}")
            return None

    def _convert_to_networkx(self, graph_data: Dict[str, Any]) -> nx.Graph:
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