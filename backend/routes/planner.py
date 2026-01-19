from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.planner_service import PlannerService

router = APIRouter()

service = PlannerService()

class PlaylistModeRequest(BaseModel):
    cocktail_names: List[str]

@router.post("/playlist-mode")
async def playlist_mode(request: PlaylistModeRequest):
    try:
        if not request.cocktail_names:
            raise HTTPException(status_code=400, detail="cocktail_names list cannot be empty")

        result = service.optimize_playlist_mode(request.cocktail_names)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to optimize playlist mode: {str(e)}")
