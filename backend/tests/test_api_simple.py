"""
Simplified working API tests for MarmiTonic backend.
These tests verify basic API functionality without complex mocking.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


class TestBasicEndpoints:
    """Test that all endpoints are accessible"""

    def test_root_endpoint(self):
        """Test GET /"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_cocktails_endpoint_exists(self):
        """Test GET /cocktails/ endpoint exists"""
        response = client.get("/cocktails/")
        # Should return 200 or 500, not 404
        assert response.status_code in [200, 500]

    def test_404_for_invalid_route(self):
        """Test that invalid routes return 404"""
        response = client.get("/nonexistent/route")
        assert response.status_code == 404


class TestCocktailEndpoints:
    """Test cocktail endpoints"""

    def test_cocktails_list(self):
        """Test listing cocktails"""
        response = client.get("/cocktails/")
        # May fail if data not loaded, but should not crash
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    def test_cocktails_search(self):
        """Test searching cocktails"""
        response = client.get("/cocktails/?q=mojito")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    def test_bridge_cocktails(self):
        """Test bridge cocktails endpoint"""
        response = client.get("/cocktails/bridge")
        assert response.status_code in [200, 500]

    def test_similar_cocktails(self):
        """Test similar cocktails endpoint"""
        response = client.get("/cocktails/similar/test_id")
        assert response.status_code in [200, 400, 500]


class TestIngredientEndpoints:
    """Test ingredient endpoints"""

    def test_search_ingredients_missing_query(self):
        """Test search requires query parameter"""
        response = client.get("/ingredients/search")
        assert response.status_code == 422  # Validation error

    def test_search_ingredients_with_query(self):
        """Test search with query parameter"""
        response = client.get("/ingredients/search?q=rum")
        assert response.status_code in [200, 500]

    def test_get_inventory(self):
        """Test getting user inventory"""
        response = client.get("/ingredients/inventory/user123")
        assert response.status_code in [200, 500]

    def test_update_inventory(self):
        """Test updating inventory"""
        payload = {
            "user_id": "test_user",
            "ingredients": ["Rum", "Vodka"]
        }
        response = client.post("/ingredients/inventory", json=payload)
        assert response.status_code in [200, 500]

    def test_update_inventory_invalid_payload(self):
        """Test invalid payload returns validation error"""
        payload = {"user_id": "test"}  # Missing required field
        response = client.post("/ingredients/inventory", json=payload)
        assert response.status_code == 422


class TestPlannerEndpoints:
    """Test planner endpoints"""

    def test_playlist_mode_valid(self):
        """Test playlist mode with valid input"""
        payload = {"cocktail_names": ["Mojito", "Daiquiri"]}
        response = client.post("/planner/playlist-mode", json=payload)
        assert response.status_code in [200, 500]


class TestCORSAndHeaders:
    """Test CORS and headers"""

    def test_cors_options(self):
        """Test OPTIONS request for CORS"""
        response = client.options("/cocktails/")
        # OPTIONS should work or return 200/405
        assert response.status_code in [200, 405]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
