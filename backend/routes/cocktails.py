from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..services.cocktail_service import CocktailService

router = APIRouter()

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