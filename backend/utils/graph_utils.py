import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import numpy as np
from collections import defaultdict

# Import force-directed layout components
from utils.force_directed_graphs.layout import compute_layout
from utils.force_directed_graphs.config import REPULSIVE_MULTIPLIER, ATTRACTIVE_MULTIPLIER

def create_graph(data):
    """
    Create a NetworkX graph from data.
    Data should be a dict with 'nodes' and 'edges' keys.
    nodes: list of dicts with 'id' and 'label'
    edges: list of dicts with 'source' and 'target'
    """
    G = nx.Graph()
    if 'nodes' in data:
        for node in data['nodes']:
            G.add_node(node['id'], label=node.get('label', str(node['id'])))
    if 'edges' in data:
        for edge in data['edges']:
            G.add_edge(edge['source'], edge['target'])
    return G

def calculate_metrics(graph):
    """
    Calculate various graph metrics.
    """
    metrics = {}
    if len(graph) > 0:
        metrics['num_nodes'] = len(graph)
        metrics['num_edges'] = graph.number_of_edges()
        metrics['density'] = nx.density(graph)
        if nx.is_connected(graph):
            metrics['diameter'] = nx.diameter(graph)
            metrics['average_clustering'] = nx.average_clustering(graph)
        else:
            metrics['diameter'] = 'Graph is not connected'
            metrics['average_clustering'] = nx.average_clustering(graph)
        # Degree statistics
        degrees = [d for n, d in graph.degree()]
        if degrees:
            metrics['avg_degree'] = sum(degrees) / len(degrees)
            metrics['max_degree'] = max(degrees)
            metrics['min_degree'] = min(degrees)
    return metrics

def compute_force_directed_layout(graph, iterations=50):
    """
    Compute force-directed layout positions for the graph.
    Adapted from force_directed_graphs.layout.compute_layout
    """
    # Initialize positions randomly
    pos = {node: [random.uniform(-10, 10), random.uniform(-10, 10)] for node in graph.nodes()}
    
    # Create adjacency list
    adj = defaultdict(list)
    for u, v in graph.edges():
        adj[u].append(v)
        adj[v].append(u)
    
    # Convert to arrays for computation
    node_ids = list(pos.keys())
    pos_array = np.array([pos[node] for node in node_ids], dtype=np.float32)
    
    # Get edge indices
    edges_list = list(graph.edges())
    if edges_list:
        edge_indices = np.array([(node_ids.index(u), node_ids.index(v)) for u, v in edges_list])
    else:
        edge_indices = np.array([]).reshape(0, 2)
    
    n = len(pos)
    AREA = 4 * n * n
    k = math.sqrt(AREA / n) if n > 0 else 1.0
    initial_temp = math.sqrt(AREA) * 0.1
    
    for iteration in range(iterations):
        temp = initial_temp * (1 - iteration / iterations)
        
        # Repulsive forces
        forces_array = np.zeros((n, 2), dtype=np.float32)
        
        # Compute repulsive forces (simplified, non-parallel version)
        for i in range(n):
            for j in range(n):
                if i != j:
                    diff = pos_array[i] - pos_array[j]
                    dist_sq = np.sum(diff**2)
                    if dist_sq > 1e-9:
                        dist = math.sqrt(dist_sq)
                        f = (k**2 / dist) * REPULSIVE_MULTIPLIER
                        force_vec = diff * (f / dist)
                        forces_array[i] += force_vec
        
        # Attractive forces
        if len(edge_indices) > 0:
            edge_diffs = pos_array[edge_indices[:, 0]] - pos_array[edge_indices[:, 1]]
            dist = np.maximum(np.sqrt(np.sum(edge_diffs**2, axis=1)), 0.01)
            f_attr = (dist**2 / k) * ATTRACTIVE_MULTIPLIER
            directions = edge_diffs / dist[:, np.newaxis]
            forces_attr = directions * f_attr[:, np.newaxis]
            np.add.at(forces_array, edge_indices[:, 0], -forces_attr)
            np.add.at(forces_array, edge_indices[:, 1], forces_attr)
        
        # Update positions
        disp = np.sqrt(np.sum(forces_array**2, axis=1))
        scale = np.where(disp > 0, np.minimum(disp, temp) / disp, 0)
        pos_array += forces_array * scale[:, np.newaxis]
        
        # Early stopping
        total_disp = np.sum(disp)
        if total_disp < 0.01 * n:
            break
    
    # Update pos dict
    for idx, node in enumerate(node_ids):
        pos[node] = pos_array[idx].tolist()
    
    return pos

def visualize_graph(graph):
    """
    Visualize the graph using force-directed layout.
    """
    if len(graph) == 0:
        print("Graph is empty")
        return
    
    # Compute positions using force-directed layout
    pos = compute_force_directed_layout(graph)
    
    # Draw the graph
    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos=pos, with_labels=True, node_color='lightblue',
            node_size=500, font_size=10, font_weight='bold',
            edge_color='gray', width=1)
    plt.title("Force-Directed Graph Visualization")
    plt.axis('off')
    plt.show()