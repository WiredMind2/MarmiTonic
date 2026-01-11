from fastapi import APIRouter, HTTPException, Query, Response
from typing import List
from ..services.cocktail_service import CocktailService
from ..services.similarity_service import SimilarityService

router = APIRouter()
similarity_service = SimilarityService()

@router.get("/cocktails")
async def get_cocktails(q: str = None):
    service = CocktailService()
    try:
        if q:
            return service.search_cocktails(q)
        else:
            return service.get_all_cocktails()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cocktails/feasible/{user_id}")
async def get_feasible_cocktails(user_id: str):
    service = CocktailService()
    try:
        return service.get_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/cocktails/almost-feasible/{user_id}")
async def get_almost_feasible_cocktails(user_id: str):
    service = CocktailService()
    try:
        return service.get_almost_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/cocktails/by-ingredients")
async def get_cocktails_by_ingredients(ingredients: List[str] = Query(..., description="List of ingredients to search for")):
    service = CocktailService()
    try:
        return service.get_cocktails_by_ingredients(ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cocktails/similar/{cocktail_id}")
async def get_similar_cocktails(cocktail_id: str, top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_cocktails(cocktail_id, top_k=top_k)
        return {"cocktail_id": cocktail_id, "similar_cocktails": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cocktails: {str(e)}")

@router.get("/cocktails/search-semantic")
async def search_cocktails_semantic(query: str = Query(...), top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_by_text(query, top_k=top_k)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in semantic search: {str(e)}")

@router.get("/cocktails/similar-by-ingredients")
async def get_similar_by_ingredients(ingredients: List[str] = Query(...), top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_by_ingredients(ingredients, top_k=top_k)
        return {"ingredients": ingredients, "similar_cocktails": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cocktails: {str(e)}")

@router.post("/cocktails/build-index")
async def build_similarity_index(force_rebuild: bool = False, response: Response = None):
    try:
        similarity_service.build_index(force_rebuild=force_rebuild)
        if response:
            response.headers["Access-Control-Allow-Origin"] = "*"
        return {"status": "success", "message": f"Index built with {len(similarity_service.cocktails)} cocktails"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building index: {str(e)}")