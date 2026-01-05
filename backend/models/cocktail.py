from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Cocktail(BaseModel):
    id: str = Field(..., description="DBpedia resource URI for the cocktail")
    name: str = Field(..., min_length=1, description="Name of the cocktail")
    alternative_names: Optional[List[str]] = Field(None, description="Alternative names for the cocktail")
    description: Optional[str] = Field(None, description="Description of the cocktail")
    image: Optional[str] = Field(None, description="URL to cocktail image")
    ingredients: Optional[str] = Field(None, description="Ingredients list with measurements")
    parsed_ingredients: Optional[List[str]] = Field(None, description="Extracted ingredient names")
    ingredient_uris: Optional[List[str]] = Field(None, description="Semantic URIs for ingredients")
    preparation: Optional[str] = Field(None, description="Preparation instructions")
    served: Optional[str] = Field(None, description="How the cocktail is served")
    garnish: Optional[str] = Field(None, description="Garnish for the cocktail")
    source_link: Optional[str] = Field(None, description="Source link for the recipe")
    categories: Optional[List[str]] = Field(None, description="Categories the cocktail belongs to")
    related_ingredients: Optional[List[str]] = Field(None, description="Related ingredients and concepts")
    labels: Optional[Dict[str, str]] = Field(None, description="Multilingual labels")
    descriptions: Optional[Dict[str, str]] = Field(None, description="Multilingual descriptions")

    class Config:
        json_encoders = {
            # Custom encoders if needed
        }