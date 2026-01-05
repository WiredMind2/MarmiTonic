from pydantic import BaseModel, Field
from typing import Optional


class Ingredient(BaseModel):
    id: str = Field(..., description="Unique identifier for the ingredient")
    name: str = Field(..., min_length=1, description="Name of the ingredient")
    category: str = Field(..., description="Category of the ingredient (e.g., spirit, mixer, garnish)")
    description: Optional[str] = Field(None, description="Description of the ingredient")

    class Config:
        json_encoders = {
            # Custom encoders if needed
        }