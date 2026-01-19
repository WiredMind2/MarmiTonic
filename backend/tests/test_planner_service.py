import pytest
from unittest.mock import patch, MagicMock
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
        
        mock_service = MockCocktailService.return_value
        mock_service.get_all_cocktails.return_value = mock_cocktails
        
        service = PlannerService()
        expected_mapping = {
            "C1": {"A", "B"},
            "C2": {"B", "C"},
            "C3": {"C", "D"}
        }
        service.cocktail_ingredients = expected_mapping
        return service

class TestPlannerService:
    def test_init(self, planner_service):
        assert hasattr(planner_service, 'cocktail_service')
        assert hasattr(planner_service, 'ingredient_service')
        assert hasattr(planner_service, 'cocktail_ingredients')
        assert isinstance(planner_service.cocktail_ingredients, dict)

    def test_optimize_playlist_mode_empty_input(self, planner_service):
        result = planner_service.optimize_playlist_mode([])
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    def test_optimize_playlist_mode_nonexistent_cocktails(self, planner_service):
        result = planner_service.optimize_playlist_mode(['Nonexistent'])
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    def test_optimize_playlist_mode_single_cocktail(self, planner_service):
        result = planner_service.optimize_playlist_mode(['C1'])
        assert set(result['covered_cocktails']) == {'C1'}
        # Should select at least one ingredient from C1
        assert len(result['selected_ingredients']) >= 1
        assert all(ing in {'A', 'B'} for ing in result['selected_ingredients'])

    def test_optimize_playlist_mode_multiple_cocktails(self, planner_service):
        result = planner_service.optimize_playlist_mode(['C1', 'C2', 'C3'])
        assert set(result['covered_cocktails']) == {'C1', 'C2', 'C3'}
        # Should select ingredients that cover all cocktails
        assert len(result['selected_ingredients']) <= 4  # Optimal is 2 (B and D or B and C)

    def test_optimize_playlist_mode_all_cocktails(self, planner_service):
        result = planner_service.optimize_playlist_mode(['C1', 'C2', 'C3'])
        assert set(result['covered_cocktails']) == {'C1', 'C2', 'C3'}
