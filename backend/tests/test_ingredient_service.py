import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ingredient_service import IngredientService


@pytest.fixture
def ingredient_service():
    with patch('services.ingredient_service.SparqlService'):
        service = IngredientService()
        return service


class TestIngredientService:

    def test_init(self, ingredient_service):
        assert hasattr(ingredient_service, 'sparql_service')

    def test_get_ingredient_by_id_success(self, ingredient_service):
        mock_data = {
            "results": {
                "bindings": [
                    {
                        "id": {"value": "http://example.com/ingredient1"},
                        "name": {"value": "Gin"},
                        "category": {"value": "Base Spirit"},
                        "description": {"value": "A distilled alcoholic drink"}
                    }
                ]
            }
        }

        ingredient_service.sparql_service.query_local_data.return_value = mock_data

        result = ingredient_service.get_ingredient_by_id("http://example.com/ingredient1")

        assert result is not None
        assert result.id == "http://example.com/ingredient1"
        assert result.name == "Gin"

    def test_get_ingredient_by_id_not_found(self, ingredient_service):
        ingredient_service.sparql_service.query_local_data.return_value = {"results": {"bindings": []}}

        result = ingredient_service.get_ingredient_by_id("http://example.com/nonexistent")

        assert result is None

    def test_search_ingredients_by_name_no_match(self, ingredient_service):
        ingredient_service.sparql_service.query_local_data.return_value = {"results": {"bindings": []}}

        result = ingredient_service.search_ingredients_by_name("Vodka")

        assert result == []

    def test_get_ingredients_by_category_empty(self, ingredient_service):
        ingredient_service.sparql_service.query_local_data.return_value = {"results": {"bindings": []}}

        result = ingredient_service.get_ingredients_by_category("Unknown Category")

        assert result == []

    def test_get_ingredients_for_cocktail_empty(self, ingredient_service):
        ingredient_service.sparql_service.query_local_data.return_value = {"results": {"bindings": []}}

        result = ingredient_service.get_ingredients_for_cocktail("http://example.com/cocktail1")

        assert result == []

    def test_get_all_categories_empty(self, ingredient_service):
        ingredient_service.sparql_service.query_local_data.return_value = {"results": {"bindings": []}}

        result = ingredient_service.get_all_categories()

        assert result == []

    def test_get_popular_ingredients(self, ingredient_service):
        mock_data = {
            "results": {
                "bindings": [
                    {
                        "id": {"value": "http://example.com/ingredient1"},
                        "name": {"value": "Gin"},
                        "category": {"value": "Base Spirit"}
                    }
                ]
            }
        }

        ingredient_service.sparql_service.query_local_data.return_value = mock_data

        result = ingredient_service.get_popular_ingredients(5)

        assert result is not None
        assert len(result) <= 5

    def test_get_related_ingredients(self, ingredient_service):
        mock_data = {
            "results": {
                "bindings": [
                    {
                        "id": {"value": "http://example.com/ingredient1"},
                        "name": {"value": "Gin"},
                        "category": {"value": "Base Spirit"}
                    }
                ]
            }
        }

        ingredient_service.sparql_service.query_local_data.return_value = mock_data

        result = ingredient_service.get_related_ingredients("http://example.com/ingredient1")

        assert result is not None
        assert len(result) >= 0

    def test_get_ingredients_by_ids(self, ingredient_service):
        mock_data = {
            "results": {
                "bindings": [
                    {
                        "id": {"value": "http://example.com/ingredient1"},
                        "name": {"value": "Gin"},
                        "category": {"value": "Base Spirit"}
                    }
                ]
            }
        }

        ingredient_service.sparql_service.query_local_data.return_value = mock_data

        result = ingredient_service.get_ingredients_by_ids(["http://example.com/ingredient1"])

        assert result is not None
        assert len(result) == 1

    def test_get_ingredients_by_ids_empty(self, ingredient_service):
        ingredient_service.sparql_service.query_local_data.return_value = {"results": {"bindings": []}}

        result = ingredient_service.get_ingredients_by_ids([])

        assert result == []

    def test_get_random_ingredients(self, ingredient_service):
        mock_data = {
            "results": {
                "bindings": [
                    {
                        "id": {"value": "http://example.com/ingredient1"},
                        "name": {"value": "Gin"},
                        "category": {"value": "Base Spirit"}
                    }
                ]
            }
        }

        ingredient_service.sparql_service.query_local_data.return_value = mock_data

        result = ingredient_service.get_random_ingredients(3)

        assert result is not None
        assert len(result) <= 3
