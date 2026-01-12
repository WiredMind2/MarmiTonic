from fastapi import APIRouter, HTTPException, Query, Response
from typing import List
from ..services.cocktail_service import CocktailService
from ..services.similarity_service import SimilarityService

router = APIRouter()
similarity_service = SimilarityService()
cocktail_service = CocktailService()

@router.get("/")
async def get_cocktails(q: str = None):
    try:
        if q:
            return cocktail_service.search_cocktails(q)
        else:
            return cocktail_service.get_all_cocktails()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feasible/{user_id}")
async def get_feasible_cocktails(user_id: str):
    try:
        return cocktail_service.get_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/almost-feasible/{user_id}")
async def get_almost_feasible_cocktails(user_id: str):
    try:
        return cocktail_service.get_almost_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/by-uris")
async def get_cocktails_by_uris(uris: List[str] = Query(..., description="List of ingredient URIs to search for")):
    try:
        return cocktail_service.get_cocktails_by_ingredient_uris(uris)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# similarity endpoints
@router.get("/similar/{cocktail_id}")
async def get_similar_cocktails(cocktail_id: str, top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_cocktails(cocktail_id, top_k=top_k)
        return {"cocktail_id": cocktail_id, "similar_cocktails": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cocktails: {str(e)}")

@router.get("/search-semantic")
async def search_cocktails_semantic(query: str = Query(...), top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_by_text(query, top_k=top_k)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in semantic search: {str(e)}")

@router.get("/similar-by-ingredients")
async def get_similar_by_ingredients(ingredients: List[str] = Query(...), top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_by_ingredients(ingredients, top_k=top_k)
        return {"ingredients": ingredients, "similar_cocktails": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cocktails: {str(e)}")

@router.post("/build-index")
async def build_similarity_index(force_rebuild: bool = False, response: Response = None):
    try:
        similarity_service.build_index(force_rebuild=force_rebuild)
        return {"status": "success", "message": f"Index built with {len(similarity_service.cocktails)} cocktails"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building index: {str(e)}")
    
@router.post("/create-clusters")
async def create_cocktail_clusters(n_clusters: int = Query(6, ge=2, le=20)):
    try:
        clusters = similarity_service.create_cocktails_clusters(n_clusters=n_clusters)
        # Convert dict to list for easier serialization
        clusters_list = [cluster.dict() for cluster in clusters.values()]
        return {"status": "success", "n_clusters": n_clusters, "clusters": clusters_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating clusters: {str(e)}")
