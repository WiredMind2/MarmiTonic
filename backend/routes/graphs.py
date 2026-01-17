from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from ..services.graph_service import GraphService

router = APIRouter()

class SparqlGraphRequest(BaseModel):
    query: str

@router.post("/sparql", response_model=Dict[str, Any])
async def get_sparql_graph_post(request: SparqlGraphRequest):
    """
    Return graph data directly from SPARQL query results.
    Accepts a custom SPARQL query in the body.
    """
    service = GraphService()
    try:
        # Pass the query to GraphService which now supports flexible parsing
        graph_data = service.get_graph_data(request.query)
        if not graph_data:
            return {"nodes": [], "links": []}
        
        # Convert to D3.js compatible format
        d3_format = {
            'nodes': [],
            'links': []
        }
        
        # Process nodes
        for node in graph_data['nodes']:
            d3_format['nodes'].append({
                'id': node['id'],
                'name': node['name'],
                'type': node['type']
            })
        
        # Process edges as links
        # Note: edges in service were dicts with source, target
        for edge in graph_data['edges']:
            d3_format['links'].append({
                'source': edge['source'],
                'target': edge['target'],
                'value': 1  # Default weight
            })
        
        return d3_format
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SPARQL graph: {str(e)}")

@router.get("/basic")
async def get_basic_graph():
    """
    Return basic graph data in D3.js compatible format.
    Includes cocktails and ingredients with their relationships.
    """
    service = GraphService()
    try:
        graph_data = service.build_graph()
        if not graph_data:
            raise HTTPException(status_code=404, detail="No graph data available")
        
        # Convert to D3.js compatible format
        d3_format = {
            'nodes': [],
            'links': []
        }
        
        # Process nodes
        for node in graph_data['nodes']:
            d3_format['nodes'].append({
                'id': node['id'],
                'name': node['name'],
                'type': node['type']
            })
        
        # Process edges as links
        for edge in graph_data['edges']:
            d3_format['links'].append({
                'source': edge['source'],
                'target': edge['target'],
                'value': 1  # Default weight
            })
        
        return d3_format
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get basic graph: {str(e)}")

@router.get("/force-directed")
async def get_force_directed_graph():
    """
    Return graph data optimized for force-directed visualization.
    Includes additional properties for better visualization.
    """
    service = GraphService()
    try:
        graph_data = service.build_graph()
        if not graph_data:
            raise HTTPException(status_code=404, detail="No graph data available")
        
        # Use the service's force-directed data generator
        force_directed_data = service.generate_force_directed_data(graph_data)
        if not force_directed_data:
            raise HTTPException(status_code=500, detail="Failed to generate force-directed data")
        
        return force_directed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get force-directed graph: {str(e)}")

# Removed duplicate GET /sparql as we now support POST /sparql above
# If backward compatibility is needed, we could keep it calling service.get_graph_data(None)

@router.get("/centrality")
async def get_centrality_graph():
    """
    Return graph data with centrality metrics for node sizing.
    """
    service = GraphService()
    try:
        graph_data = service.build_graph()
        if not graph_data:
            raise HTTPException(status_code=404, detail="No graph data available")
        
        # Get centrality scores
        centrality_scores = service.get_centrality_scores(graph_data)
        
        # Convert to D3.js compatible format with centrality
        d3_format = {
            'nodes': [],
            'links': []
        }
        
        # Process nodes with centrality
        for node in graph_data['nodes']:
            node_id = node['id']
            centrality = centrality_scores.get(node_id, 0)
            
            d3_format['nodes'].append({
                'id': node_id,
                'name': node['name'],
                'type': node['type'],
                'centrality': centrality,
                'size': centrality * 20 + 5  # Scale for visualization
            })
        
        # Process edges as links
        for edge in graph_data['edges']:
            d3_format['links'].append({
                'source': edge['source'],
                'target': edge['target'],
                'value': 1  # Default weight
            })
        
        return d3_format
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get centrality graph: {str(e)}")

@router.get("/communities")
async def get_community_graph():
    """
    Return graph data with community detection results.
    """
    service = GraphService()
    try:
        graph_data = service.build_graph()
        if not graph_data:
            raise HTTPException(status_code=404, detail="No graph data available")
        
        # Get community detection results
        community_results = service.get_community_detection(graph_data)
        
        if not community_results:
            raise HTTPException(status_code=500, detail="Failed to detect communities")
        
        community_dict = community_results['communities']
        
        # Convert to D3.js compatible format with communities
        d3_format = {
            'nodes': [],
            'links': []
        }
        
        # Process nodes with community info
        for node in graph_data['nodes']:
            node_id = node['id']
            community_id = community_dict.get(node_id, 0)
            
            d3_format['nodes'].append({
                'id': node_id,
                'name': node['name'],
                'type': node['type'],
                'community': community_id
            })
        
        # Process edges as links
        for edge in graph_data['edges']:
            d3_format['links'].append({
                'source': edge['source'],
                'target': edge['target'],
                'value': 1  # Default weight
            })
        
        return d3_format
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get community graph: {str(e)}")

@router.get("/statistics")
async def get_graph_statistics():
    """
    Return statistics about the graph structure.
    """
    service = GraphService()
    try:
        graph_data = service.build_graph()
        if not graph_data:
            raise HTTPException(status_code=404, detail="No graph data available")
        
        statistics = service.get_graph_statistics(graph_data)
        if not statistics:
            raise HTTPException(status_code=500, detail="Failed to calculate statistics")
        
        return {
            'statistics': statistics,
            'message': 'Graph statistics calculated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph statistics: {str(e)}")

@router.get("/components")
async def get_graph_components():
    """
    Return analysis of disjoint components in the graph.
    """
    service = GraphService()
    try:
        graph_data = service.build_graph()
        if not graph_data:
            raise HTTPException(status_code=404, detail="No graph data available")
        
        components = service.analyze_disjoint_components(graph_data)
        if not components:
            raise HTTPException(status_code=500, detail="Failed to analyze components")
        
        return {
            'components': components,
            'message': 'Disjoint components analyzed successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph components: {str(e)}")