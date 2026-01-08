from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from ..services.ingredient_service import IngredientService

router = APIRouter()

service = IngredientService()

class InventoryUpdate(BaseModel):
    user_id: str
    ingredients: List[str]

@router.get("/")
async def get_all_ingredients():
    try:
        ingredients = service.get_all_ingredients()
        return ingredients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ingredients: {str(e)}")

@router.get("/search")
async def search_ingredients(q: str = Query(..., description="Search query for ingredients")):
    try:
        ingredients = service.search_ingredients(q)
        return ingredients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search ingredients: {str(e)}")

@router.post("/inventory")
async def update_inventory(update: InventoryUpdate):
    try:
        service.update_inventory(update.user_id, update.ingredients)
        return {"message": "Inventory updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update inventory: {str(e)}")

@router.get("/inventory/{user_id}")
async def get_inventory(user_id: str):
    try:
        inventory = service.get_inventory(user_id)
        return {"user_id": user_id, "ingredients": inventory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve inventory: {str(e)}")