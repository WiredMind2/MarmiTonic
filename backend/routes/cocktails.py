from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..services.cocktail_service import CocktailService

router = APIRouter()

@router.get("/")
async def get_cocktails(q: str = None):
    service = CocktailService()
    try:
        if q:
            return service.search_cocktails(q)
        else:
            return service.get_all_cocktails()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feasible/{user_id}")
async def get_feasible_cocktails(user_id: str):
    service = CocktailService()
    try:
        return service.get_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/almost-feasible/{user_id}")
async def get_almost_feasible_cocktails(user_id: str):
    service = CocktailService()
    try:
        return service.get_almost_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/by-ingredients")
async def get_cocktails_by_ingredients(ingredients: List[str] = Query(..., description="List of ingredients to search for")):
    service = CocktailService()
    try:
        return service.get_cocktails_by_ingredients(ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-uris")
async def get_cocktails_by_uris(uris: List[str] = Query(..., description="List of ingredient URIs to search for")):
    service = CocktailService()
    try:
        return service.get_cocktails_by_uris(uris)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{cocktail_id}")
async def get_similar_cocktails(cocktail_id: str, limit: int = 10):
    service = CocktailService()
    try:
        return service.get_similar_cocktails(cocktail_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/same-vibe/{cocktail_id}")
async def get_same_vibe_cocktails(cocktail_id: str, limit: int = 10):
    service = CocktailService()
    try:
        return service.get_same_vibe_cocktails(cocktail_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bridge")
async def get_bridge_cocktails(limit: int = 10):
    service = CocktailService()
    try:
        return service.get_bridge_cocktails(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))