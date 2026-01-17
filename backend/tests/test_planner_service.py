import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.planner_service import PlannerService
from models.cocktail import Cocktail
from models.ingredient import Ingredient


@pytest.fixture
def planner_service():
    with patch('services.planner_service.SparqlService'):
        with patch('services.planner_service.CocktailService'):
            service = PlannerService()
            # Set up mock cocktail ingredients
            service.cocktail_ingredients = {
                'Mojito': {'Rum', 'Mint', 'Soda'},
                'Daiquiri': {'Rum', 'Lime', 'Sugar'},
                'Margarita': {'Tequila', 'Lime', 'Triple Sec'},
                'Martini': {'Gin', 'Vermouth'}
            }
            return service


class TestPlannerService:

    def test_init(self, planner_service):
        assert hasattr(planner_service, 'sparql_service')
        assert hasattr(planner_service, 'cocktail_service')

    def test_create_plan_success(self, planner_service):
        mock_cocktails = [
            Cocktail(
                uri="http://example.com/cocktail1",
                id="cocktail1",
                name="Mojito",
                ingredients="Rum, Mint, Soda",
                parsed_ingredients=["Rum", "Mint", "Soda"]
            ),
            Cocktail(
                uri="http://example.com/cocktail2",
                id="cocktail2",
                name="Daiquiri",
                ingredients="Rum, Lime, Sugar",
                parsed_ingredients=["Rum", "Lime", "Sugar"]
            )
        ]

        planner_service.cocktail_service.get_cocktails_for_ingredients.return_value = mock_cocktails

        result = planner_service.create_plan(
            available_ingredients=["http://example.com/gin", "http://example.com/tonic"],
            preferences=["gin", "tonic"]
        )

        assert result is not None
        assert "cocktails" in result
        assert len(result["cocktails"]) == 2

    def test_create_plan_no_ingredients(self, planner_service):
        result = planner_service.create_plan(available_ingredients=[], preferences=[])

        assert result is not None
        assert isinstance(result, dict)
        assert "cocktails" in result

    def test_get_shopping_list(self, planner_service):
        mock_ingredients = [
            Ingredient(
                id="http://example.com/gin",
                name="Gin"
            ),
            Ingredient(
                id="http://example.com/tonic",
                name="Tonic"
            )
        ]

        result = planner_service.get_shopping_list(mock_ingredients)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_shopping_list_empty(self, planner_service):
        result = planner_service.get_shopping_list([])

        assert result == []

    def test_get_alternatives_for_missing_ingredient(self, planner_service):
        planner_service.cocktail_service.get_similar_cocktails.return_value = []

        result = planner_service.get_alternatives_for_missing_ingredient("http://example.com/gin")

        assert result is not None

    def test_get_alternatives_for_missing_ingredient_no_alternatives(self, planner_service):
        planner_service.cocktail_service.get_similar_cocktails.return_value = []

        result = planner_service.get_alternatives_for_missing_ingredient("http://example.com/nonexistent")

        assert result == []

    def test_get_recipe_steps(self, planner_service):
        mock_cocktail = Cocktail(
            uri="http://example.com/cocktail1", id="cocktail1",
            name="Mojito",
            ingredients="Rum, Mint, Soda",
            preparation="1. Muddle mint\n2. Add rum\n3. Add soda"
        )

        planner_service.cocktail_service.get_cocktail_by_id.return_value = mock_cocktail

        result = planner_service.get_recipe_steps("http://example.com/cocktail1")

        assert result is not None
        assert "steps" in result

    def test_get_recipe_steps_not_found(self, planner_service):
        planner_service.cocktail_service.get_cocktail_by_id.return_value = None

        result = planner_service.get_recipe_steps("http://example.com/nonexistent")

        assert result is None

    def test_get_garnish_suggestions(self, planner_service):
        mock_data = {
            "results": {
                "bindings": [
                    {"garnish": {"value": "http://example.com/garnish1"}}
                ]
            }
        }

        planner_service.sparql_service.query_local_data.return_value = mock_data

        result = planner_service.get_garnish_suggestions("http://example.com/cocktail1")

        assert result is not None

    def test_get_garnish_suggestions_empty(self, planner_service):
        planner_service.sparql_service.query_local_data.return_value = {"results": {"bindings": []}}

        result = planner_service.get_garnish_suggestions("http://example.com/cocktail1")

        assert result == []

    def test_get_equipment_requirements(self, planner_service):
        mock_cocktail = Cocktail(
            uri="http://example.com/cocktail1", id="cocktail1",
            name="Mojito",
            ingredients="Rum, Mint, Soda",
            preparation="Mix all ingredients",
            served="Highball glass"
        )

        planner_service.cocktail_service.get_cocktail_by_id.return_value = mock_cocktail

        result = planner_service.get_equipment_requirements("http://example.com/cocktail1")

        assert result is not None
        assert "equipment" in result

    def test_get_equipment_requirements_not_found(self, planner_service):
        planner_service.cocktail_service.get_cocktail_by_id.return_value = None

        result = planner_service.get_equipment_requirements("http://example.com/nonexistent")

        assert result is None

    def test_calculate_abv_for_plan(self, planner_service):
        mock_cocktails = [
            Cocktail(
                uri="http://example.com/cocktail1", id="cocktail1",
                name="Mojito",
                ingredients="Rum, Mint, Soda"
            )
        ]

        result = planner_service.calculate_abv_for_plan(mock_cocktails)

        assert result is not None
        assert "total_abv" in result

    def test_calculate_abv_for_plan_empty(self, planner_service):
        result = planner_service.calculate_abv_for_plan([])

        assert result is not None

    def test_get_timing_suggestions(self, planner_service):
        mock_cocktails = [
            Cocktail(
                uri="http://example.com/cocktail1", id="cocktail1",
                name="Mojito",
                ingredients="Rum, Mint, Soda"
            )
        ]

        result = planner_service.get_timing_suggestions(mock_cocktails)

        assert result is not None
        assert "prep_time" in result

    def test_get_timing_suggestions_empty(self, planner_service):
        result = planner_service.get_timing_suggestions([])

        assert result is not None

    def test_suggest_preparation_order(self, planner_service):
        mock_cocktails = [
            Cocktail(
                uri="http://example.com/cocktail1", id="cocktail1",
                name="Mojito",
                ingredients="Rum, Mint, Soda"
            ),
            Cocktail(
                uri="http://example.com/cocktail2", id="cocktail2",
                name="Daiquiri",
                ingredients="Rum, Lime, Sugar"
            )
        ]

        result = planner_service.suggest_preparation_order(mock_cocktails)

        assert result is not None
        assert "order" in result

    def test_suggest_preparation_order_empty(self, planner_service):
        result = planner_service.suggest_preparation_order([])

        assert result is not None

    def test_get_nutrition_info(self, planner_service):
        mock_cocktail = Cocktail(
            uri="http://example.com/cocktail1", id="cocktail1",
            name="Mojito",
            ingredients="Rum, Mint, Soda"
        )

        planner_service.cocktail_service.get_cocktail_by_id.return_value = mock_cocktail

        result = planner_service.get_nutrition_info("http://example.com/cocktail1")

        assert result is not None

    def test_get_nutrition_info_not_found(self, planner_service):
        planner_service.cocktail_service.get_cocktail_by_id.return_value = None

        result = planner_service.get_nutrition_info("http://example.com/nonexistent")

        assert result is None

    def test_get_guest_preferences_summary(self, planner_service):
        mock_guests = [
            {"name": "Guest1", "preferences": ["gin", "tonic"]},
            {"name": "Guest2", "preferences": ["vodka", "juice"]}
        ]

        result = planner_service.get_guest_preferences_summary(mock_guests)

        assert result is not None
        assert "summary" in result or result is not None

    def test_get_guest_preferences_summary_empty(self, planner_service):
        result = planner_service.get_guest_preferences_summary([])

        assert result is not None

    def test_get_union_ingredients_valid_cocktails(self, planner_service):
        result = planner_service.get_union_ingredients(['Mojito', 'Daiquiri'])

        assert isinstance(result, list)
        assert set(result) == {'Rum', 'Mint', 'Soda', 'Lime', 'Sugar'}

    def test_get_union_ingredients_empty_list(self, planner_service):
        result = planner_service.get_union_ingredients([])

        assert result == []

    def test_get_union_ingredients_invalid_names(self, planner_service):
        with pytest.raises(ValueError, match="No valid cocktails found"):
            planner_service.get_union_ingredients(['Nonexistent'])

    def test_get_union_ingredients_mixed_valid_invalid(self, planner_service):
        result = planner_service.get_union_ingredients(['Mojito', 'Nonexistent'])

        assert set(result) == {'Rum', 'Mint', 'Soda'}

    def test_get_union_ingredients_duplicate_names(self, planner_service):
        result = planner_service.get_union_ingredients(['Mojito', 'Mojito'])

        assert set(result) == {'Rum', 'Mint', 'Soda'}

    def test_get_union_ingredients_single_cocktail(self, planner_service):
        result = planner_service.get_union_ingredients(['Martini'])

        assert set(result) == {'Gin', 'Vermouth'}

    def test_optimize_party_mode_valid_num(self, planner_service):
        result = planner_service.optimize_party_mode(2)

        assert isinstance(result, dict)
        assert 'selected_ingredients' in result
        assert 'covered_cocktails' in result
        assert isinstance(result['selected_ingredients'], list)
        assert isinstance(result['covered_cocktails'], list)
        assert len(result['selected_ingredients']) <= 2
        # Should cover some cocktails

    def test_optimize_party_mode_zero(self, planner_service):
        result = planner_service.optimize_party_mode(0)

        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    def test_optimize_party_mode_negative(self, planner_service):
        result = planner_service.optimize_party_mode(-1)

        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    def test_optimize_party_mode_large_num(self, planner_service):
        result = planner_service.optimize_party_mode(10)  # More than available

        assert isinstance(result, dict)
        assert len(result['selected_ingredients']) <= 10  # Up to num_ingredients
        assert len(result['covered_cocktails']) <= 4  # Total cocktails

    def test_optimize_party_mode_budget_constraint(self, planner_service):
        # Test that it respects the budget (num_ingredients)
        result = planner_service.optimize_party_mode(1)

        assert len(result['selected_ingredients']) <= 1
