from typing import List, Optional
from pydantic import BaseModel, Field


class VibeCluster(BaseModel):
    """
    Represents a cluster of cocktails grouped by similar vibes/characteristics.
    """
    cluster_id: int
    title: Optional[str] = Field(None, description="Descriptive name for the cluster")
    center: Optional[List[float]] = Field(None, description="The centroid of the cluster in embedding space")
    cocktail_ids: List[str] = Field(..., description="All cocktail IDs in this cluster")
    closest_to_center: Optional[List[str]] = Field(None, description="Top 10 cocktail IDs closest to the center")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cluster_id": 1,
                "title": "Tropical Paradise",
                "center": [0.45, -0.23, 0.87, 0.12],
                "cocktail_ids": ["cocktail_1", "cocktail_2", "cocktail_3"],
                "closest_to_center": ["cocktail_1", "cocktail_2"]
            }
        }
