from pydantic import BaseModel, Field
from typing import List, Optional


class Cocktail(BaseModel):
    id: str = Field(..., description="Unique identifier for the cocktail")
    name: str = Field(..., min_length=1, description="Name of the cocktail")
    ingredients: List[str] = Field(..., description="List of ingredient names or IDs")
    instructions: Optional[str] = Field(None, description="Preparation instructions")
    category: Optional[str] = Field(None, description="Category or style of the cocktail")
    description: Optional[str] = Field(None, description="Description of the cocktail")
    image: Optional[str] = Field(None, description="URL to cocktail image")

    class Config:
        json_encoders = {
            # Custom encoders if needed
        }