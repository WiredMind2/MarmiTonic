
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ingredient_service import IngredientService
from models.ingredient import Ingredient

@pytest.fixture
def ingredient_service():
    # Patch get_local_ingredients first
    with patch("backend.services.ingredient_service.get_local_ingredients") as mock_get_local,\
         patch("backend.services.ingredient_service.SparqlService") as mock_sparql,\
         patch("backend.services.ingredient_service.get_shared_graph"):
        
        # Set default return value for get_local_ingredients
        mock_get_local.return_value = []
        
        service = IngredientService()
        
        # Replace sparql service with a mock
        service.sparql_service = MagicMock()
        service.sparql_service.execute_query = MagicMock()
        # Also ensure that _local_ingredient_loader is properly mocked
        service._local_ingredient_loader = MagicMock(return_value=[])
        return service

def test_get_all_ingredients():
    # Create a test ingredient service with a custom local ingredient loader
    mock_local = [
        Ingredient(id="1", name="Rum"),
        Ingredient(id="2", name="Gin")
    ]
    
    test_service = IngredientService(lambda: mock_local)
    test_service.sparql_service = MagicMock()
    test_service.sparql_service.execute_query.return_value = {"results": {"bindings": []}}
    
    ingredients = test_service.get_all_ingredients()
    assert len(ingredients) == 2
    names = [i.name for i in ingredients]
    assert "Rum" in names
    assert "Gin" in names

def test_get_ingredient_by_id_local(ingredient_service):
    # Mock _query_local_ingredient
    mock_ing = Ingredient(id="http://test/rum", name="Rum")
    ingredient_service._query_local_ingredient = MagicMock(return_value=mock_ing)
    
    result = ingredient_service.get_ingredient_by_id("http://test/rum")
    assert result.name == "Rum"

def test_search_ingredients(ingredient_service):
    # Mock sparql_service.execute_query
    mock_results = {
        "results": {
            "bindings": [
                {
                    "id": {"value": "http://test/vodka"},
                    "name": {"value": "Vodka"},
                    "category": {"value": "Spirit"}
                }
            ]
        }
    }
    ingredient_service.sparql_service.execute_query.return_value = mock_results
    
    results = ingredient_service.search_ingredients("vodka")
    assert len(results) == 1
    assert results[0].name == "Vodka"
