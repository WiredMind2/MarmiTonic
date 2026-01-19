from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from backend.services.graph_service import GraphService

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