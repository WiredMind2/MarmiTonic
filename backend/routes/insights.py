from fastapi import APIRouter, HTTPException
from ..services.graph_service import GraphService

router = APIRouter()

@router.get("/graph")
async def get_graph_analysis():
    """
    Return graph analysis results including metrics and communities.
    """
    service = GraphService()
    try:
        return service.analyze_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze graph: {str(e)}")

@router.get("/visualization")
async def get_graph_visualization():
    """
    Return graph data in D3.js compatible format.
    """
    service = GraphService()
    try:
        return service.visualize_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate visualization: {str(e)}")

@router.get("/export")
async def export_graph():
    """
    Return graph data in Gephi-compatible format.
    """
    service = GraphService()
    try:
        gexf_data = service.export_graph()
        return {"gexf_data": gexf_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export graph: {str(e)}")

@router.get("/components")
async def get_disjoint_components():
    """
    Analyze and return information about disjoint components in the graph.
    """
    service = GraphService()
    try:
        return service.analyze_disjoint_components()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze components: {str(e)}")