from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class Ingredient(BaseModel):
    id: str = Field(..., description="DBpedia resource URI for the ingredient")
    name: str = Field(..., min_length=1, description="Name of the ingredient")
    alternative_names: Optional[List[str]] = Field(None, description="Alternative names for the ingredient")
    description: Optional[str] = Field(None, description="Description of the ingredient")
    image: Optional[str] = Field(None, description="URL to ingredient image")
    categories: Optional[List[str]] = Field(None, description="Categories the ingredient belongs to")
    related_concepts: Optional[List[str]] = Field(None, description="Related concepts and ingredients")
    labels: Optional[Dict[str, str]] = Field(None, description="Multilingual labels")
    descriptions: Optional[Dict[str, str]] = Field(None, description="Multilingual descriptions")

    class Config:
        json_encoders = {
            # Custom encoders if needed
        }