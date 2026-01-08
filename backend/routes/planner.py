from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..services.planner_service import PlannerService

router = APIRouter()

service = PlannerService()

class PartyModeRequest(BaseModel):
    num_ingredients: int

class PlaylistModeRequest(BaseModel):
    cocktail_names: List[str]

@router.post("/party-mode")
async def party_mode(request: PartyModeRequest):
    try:
        if request.num_ingredients <= 0:
            raise HTTPException(status_code=400, detail="num_ingredients must be a positive integer")
        
        result = service.optimize_party_mode(request.num_ingredients)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to optimize party mode: {str(e)}")

@router.post("/playlist-mode")
async def playlist_mode(request: PlaylistModeRequest):
    try:
        if not request.cocktail_names:
            raise HTTPException(status_code=400, detail="cocktail_names list cannot be empty")
        
        result = service.optimize_playlist_mode(request.cocktail_names)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to optimize playlist mode: {str(e)}")