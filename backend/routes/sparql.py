from fastapi import APIRouter, HTTPException
from ..services.sparql_service import SparqlService
from ..models.sparql_query import SparqlQuery

router = APIRouter()

@router.post("/")
async def execute_sparql_query(query: SparqlQuery):
    service = SparqlService()
    try:
        results = service.execute_query(query.query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SPARQL query execution failed: {str(e)}")

@router.get("/example")
async def get_example_query():
    return {
        "query": """
        SELECT ?cocktail ?name WHERE {
            ?cocktail rdf:type dbo:Cocktail .
            ?cocktail rdfs:label ?name .
            FILTER(LANG(?name) = "en")
        } LIMIT 10
        """,
        "description": "Get 10 cocktails from DBpedia"
    }
