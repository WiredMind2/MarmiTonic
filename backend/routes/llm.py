from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.llm_service import LLMService

router = APIRouter()

class NL2SparqlRequest(BaseModel):
    prompt: str

class NL2SparqlResponse(BaseModel):
    sparql_query: str

@router.post("/nl2sparql", response_model=NL2SparqlResponse)
async def nl2sparql(request: NL2SparqlRequest):
    """
    Convert Natural Language prompt to SPARQL query using LLM.
    """
    try:
        service = LLMService()
        sparql_query = service.nl2sparql(request.prompt)
        # Clean up the response if it contains markdown code blocks
        clean_query = sparql_query.replace("```sparql", "").replace("```", "").strip()
        return NL2SparqlResponse(sparql_query=clean_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Service Error: {str(e)}")
