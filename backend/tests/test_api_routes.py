"""
Comprehensive API endpoint tests for MarmiTonic backend.

This module tests all API routes including:
- Cocktails endpoints
- Ingredients endpoints
- Planner endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app
from backend.models.cocktail import Cocktail
from backend.models.ingredient import Ingredient


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_cocktail():
    """Create a mock cocktail for testing"""
    return Cocktail(
        uri="http://example.com/Mojito", id="mojito",
        name="Mojito",
        ingredients="* 45 ml White Rum\n* 20 ml Lime Juice\n* 15 ml Sugar Syrup\n* 90 ml Soda Water\n* 6 leaves Mint",
        parsed_ingredients=["White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"],
        preparation="Muddle mint and lime, add rum and sugar, top with soda",
        served="Highball glass",
        garnish="Mint sprig and lime wedge"
    )


@pytest.fixture
def mock_ingredient():
    """Create a mock ingredient for testing"""
    return Ingredient(
        id="http://example.com/Rum",
        name="Rum",
        category="Base Spirit",
        description="A distilled alcoholic drink"
    )


class TestCocktailsEndpoints:
    """Test cocktails API endpoints"""

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_all_cocktails(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/"""
        mock_get_service.return_value.get_all_cocktails.return_value = [mock_cocktail]

        response = client.get("/cocktails/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Mojito"

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_search_cocktails(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/?q=query"""
        mock_get_service.return_value.search_cocktails.return_value = [mock_cocktail]

        response = client.get("/cocktails/?q=Mojito")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Mojito"

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_cocktails_empty_result(self, mock_get_service, client):
        """Test GET /cocktails/ with no results"""
        mock_get_service.return_value.get_all_cocktails.return_value = []

        response = client.get("/cocktails/")
        
        assert response.status_code == 200
        assert response.json() == []

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_cocktails_service_error(self, mock_get_service, client):
        """Test GET /cocktails/ with service error"""
        mock_get_service.return_value.get_all_cocktails.side_effect = Exception("Service error")

        response = client.get("/cocktails/")
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_feasible_cocktails(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/feasible/{user_id}"""
        mock_get_service.return_value.get_feasible_cocktails.return_value = [mock_cocktail]

        response = client.get("/cocktails/feasible/user123")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Mojito"

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_feasible_cocktails_error(self, mock_get_service, client):
        """Test GET /cocktails/feasible/{user_id} with error"""
        mock_get_service.return_value.get_feasible_cocktails.side_effect = Exception("Inventory error")

        response = client.get("/cocktails/feasible/user123")
        
        assert response.status_code == 400
        assert "Invalid user_id or query failure" in response.json()["detail"]

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_almost_feasible_cocktails(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/almost-feasible/{user_id}"""
        mock_get_service.return_value.get_almost_feasible_cocktails.return_value = [
            {"cocktail": mock_cocktail, "missing": ["Mint"]}
        ]

        response = client.get("/cocktails/almost-feasible/user123")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["missing"] == ["Mint"]

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_cocktails_by_ingredients(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/by-ingredients?ingredients="""
        mock_get_service.return_value.get_cocktails_by_ingredients.return_value = [mock_cocktail]

        response = client.get("/cocktails/by-ingredients?ingredients=Rum&ingredients=Lime")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Mojito"

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_cocktails_by_ingredients_no_params(self, mock_service, client):
        """Test GET /cocktails/by-ingredients without parameters"""
        response = client.get("/cocktails/by-ingredients")
        
        assert response.status_code == 422  # Validation error

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_cocktails_by_uris(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/by-uris?uris="""
        mock_get_service.return_value.get_cocktails_by_uris.return_value = [mock_cocktail]

        response = client.get("/cocktails/by-uris?uris=http://example.com/Rum")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @patch('backend.routes.cocktails.similarity_service')
    def test_get_similar_cocktails(self, mock_service, client, mock_cocktail):
        """Test GET /cocktails/similar/{cocktail_id}"""
        mock_service.find_similar_cocktails.return_value = [
            {"cocktail": mock_cocktail, "similarity_score": 0.75}
        ]

        response = client.get("/cocktails/similar/mojito")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_cocktails"]) == 1
        assert data["similar_cocktails"][0]["similarity_score"] == 0.75

    @patch('backend.routes.cocktails.similarity_service')
    def test_get_similar_cocktails_with_limit(self, mock_service, client, mock_cocktail):
        """Test GET /cocktails/similar/{cocktail_id}?limit=5"""
        mock_service.find_similar_cocktails.return_value = []

        response = client.get("/cocktails/similar/mojito?limit=5")
        
        assert response.status_code == 200
        mock_service.find_similar_cocktails.assert_called_once_with("mojito", top_k=5)

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_same_vibe_cocktails(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/same-vibe/{cocktail_id}"""
        # Create a mock service instance
        mock_service = mock_get_service.return_value
        
        # Set return value for get_same_vibe_cocktails
        mock_service.get_same_vibe_cocktails.return_value = [mock_cocktail]

        # Make the request
        response = client.get("/cocktails/same-vibe/mojito")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Verify the method was called correctly
        mock_service.get_same_vibe_cocktails.assert_called_once_with("mojito", limit=10)

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_bridge_cocktails(self, mock_get_service, client, mock_cocktail):
        """Test GET /cocktails/bridge"""
        # Create a mock service instance
        mock_service = mock_get_service.return_value
        
        mock_service.get_bridge_cocktails.return_value = [mock_cocktail]

        response = client.get("/cocktails/bridge")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @patch('backend.routes.cocktails.get_cocktail_service')
    def test_get_bridge_cocktails_with_limit(self, mock_get_service, client):
        """Test GET /cocktails/bridge?limit=20"""
        # Create a mock service instance
        mock_service = mock_get_service.return_value
        
        mock_service.get_bridge_cocktails.return_value = []

        response = client.get("/cocktails/bridge?limit=20")
        
        assert response.status_code == 200
        mock_service.get_bridge_cocktails.assert_called_once_with(limit=20)


class TestIngredientsEndpoints:
    """Test ingredients API endpoints"""

    @patch('backend.routes.ingredients.service')
    def test_search_ingredients(self, mock_service, client, mock_ingredient):
        """Test GET /ingredients/search?q=query"""
        mock_service.search_ingredients.return_value = [mock_ingredient]

        response = client.get("/ingredients/search?q=Rum")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Rum"

    @patch('backend.routes.ingredients.service')
    def test_search_ingredients_no_query(self, mock_service, client):
        """Test GET /ingredients/search without query parameter"""
        response = client.get("/ingredients/search")
        
        assert response.status_code == 422  # Validation error

    @patch('backend.routes.ingredients.service')
    def test_search_ingredients_empty_result(self, mock_service, client):
        """Test GET /ingredients/search with no results"""
        mock_service.search_ingredients.return_value = []

        response = client.get("/ingredients/search?q=NonExistent")
        
        assert response.status_code == 200
        assert response.json() == []

    @patch('backend.routes.ingredients.service')
    def test_update_inventory(self, mock_service, client):
        """Test POST /ingredients/inventory"""
        mock_service.update_inventory.return_value = None

        payload = {
            "user_id": "user123",
            "ingredients": ["Rum", "Vodka", "Gin"]
        }

        response = client.post("/ingredients/inventory", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"message": "Inventory updated successfully"}
        mock_service.update_inventory.assert_called_once_with("user123", ["Rum", "Vodka", "Gin"])

    @patch('backend.routes.ingredients.service')
    def test_update_inventory_empty_list(self, mock_service, client):
        """Test POST /ingredients/inventory with empty ingredients"""
        mock_service.update_inventory.return_value = None

        payload = {
            "user_id": "user123",
            "ingredients": []
        }

        response = client.post("/ingredients/inventory", json=payload)
        
        assert response.status_code == 200
        mock_service.update_inventory.assert_called_once_with("user123", [])

    @patch('backend.routes.ingredients.service')
    def test_update_inventory_error(self, mock_service, client):
        """Test POST /ingredients/inventory with error"""
        mock_service.update_inventory.side_effect = Exception("Update failed")

        payload = {
            "user_id": "user123",
            "ingredients": ["Rum"]
        }

        response = client.post("/ingredients/inventory", json=payload)
        
        assert response.status_code == 500
        assert "Failed to update inventory" in response.json()["detail"]

    @patch('backend.routes.ingredients.service')
    def test_update_inventory_invalid_payload(self, mock_service, client):
        """Test POST /ingredients/inventory with invalid payload"""
        payload = {
            "user_id": "user123"
            # Missing required 'ingredients' field
        }

        response = client.post("/ingredients/inventory", json=payload)
        
        assert response.status_code == 422  # Validation error

    @patch('backend.routes.ingredients.service')
    def test_get_inventory(self, mock_service, client):
        """Test GET /ingredients/inventory/{user_id}"""
        mock_service.get_inventory.return_value = ["Rum", "Vodka", "Gin"]

        response = client.get("/ingredients/inventory/user123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user123"
        assert len(data["ingredients"]) == 3
        assert "Rum" in data["ingredients"]

    @patch('backend.routes.ingredients.service')
    def test_get_inventory_empty(self, mock_service, client):
        """Test GET /ingredients/inventory/{user_id} with empty inventory"""
        mock_service.get_inventory.return_value = []

        response = client.get("/ingredients/inventory/user123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ingredients"] == []

    @patch('backend.routes.ingredients.service')
    def test_get_inventory_error(self, mock_service, client):
        """Test GET /ingredients/inventory/{user_id} with error"""
        mock_service.get_inventory.side_effect = Exception("Retrieval failed")

        response = client.get("/ingredients/inventory/user123")
        
        assert response.status_code == 500
        assert "Failed to retrieve inventory" in response.json()["detail"]


class TestPlannerEndpoints:
    """Test planner API endpoints"""

    @patch('backend.routes.planner.service')
    def test_playlist_mode(self, mock_service, client):
        """Test POST /planner/playlist-mode"""
        mock_service.optimize_playlist_mode.return_value = {
            "selected_ingredients": ["Rum", "Lime", "Mint"],
            "covered_cocktails": ["Mojito", "Daiquiri"]
        }

        payload = {"cocktail_names": ["Mojito", "Daiquiri"]}
        response = client.post("/planner/playlist-mode", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "Rum" in data["selected_ingredients"]
        assert len(data["covered_cocktails"]) == 2

    @patch('backend.routes.planner.service')
    def test_playlist_mode_error(self, mock_service, client):
        """Test POST /planner/playlist-mode with error"""
        mock_service.optimize_playlist_mode.side_effect = Exception("Optimization failed")

        payload = {"cocktail_names": ["Mojito"]}
        response = client.post("/planner/playlist-mode", json=payload)
        
        assert response.status_code == 500
        assert "Failed to optimize playlist mode" in response.json()["detail"]


class TestRootEndpoint:
    """Test root endpoint"""

    def test_read_root(self, client):
        """Test GET /"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "MarmiTonic" in data["message"]


class TestInvalidRoutes:
    """Test invalid routes and error handling"""

    def test_404_not_found(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/nonexistent/route")
        
        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """Test using wrong HTTP method"""
        response = client.post("/")
        
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
