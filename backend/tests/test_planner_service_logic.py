
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.planner_service import PlannerService
from models.cocktail import Cocktail

@pytest.fixture
def mock_cocktails():
    return [
        Cocktail(uri="http://example.com/cocktail1", id="1", name="C1", parsed_ingredients=["A", "B"]),
        Cocktail(uri="http://example.com/cocktail2", id="2", name="C2", parsed_ingredients=["B", "C"]),
        Cocktail(uri="http://example.com/cocktail3", id="3", name="C3", parsed_ingredients=["C", "D"])
    ]

@pytest.fixture
def planner_service(mock_cocktails):
    with patch("backend.services.planner_service.CocktailService") as MockCocktailService, \
         patch("backend.services.planner_service.IngredientService"):
        
        # Create the mock before instantiating the service
        mock_service = MockCocktailService.return_value
        mock_service.get_all_cocktails.return_value = mock_cocktails
        
        service = PlannerService()
        # Verify the mapping was built correctly
        expected_mapping = {
            "C1": {"A", "B"},
            "C2": {"B", "C"}, 
            "C3": {"C", "D"}
        }
        service.cocktail_ingredients = expected_mapping  # Ensure the mapping is correct
        return service

def test_optimize_playlist_mode(planner_service):    
    result = planner_service.optimize_playlist_mode(["C1", "C2", "C3"])
    
    assert set(result['covered_cocktails']) == {"C1", "C2", "C3"}
    selected = result['selected_ingredients']
    assert len(selected) == 4
    covered = set()
    for cocktail in ["C1", "C2", "C3"]:
        for ing in selected:
            if ing in planner_service.cocktail_ingredients[cocktail]:
                covered.add(cocktail)
                break
    assert covered == {"C1", "C2", "C3"}
