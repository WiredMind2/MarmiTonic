"""
Integration tests for MarmiTonic - testing complete workflows.

These tests verify that all components work together correctly
for key user scenarios.
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
def sample_cocktails():
    """Sample cocktails for testing"""
    return [
        Cocktail(
            uri="http://example.com/Mojito", id="mojito",
            name="Mojito",
            ingredients="* White Rum\n* Lime Juice\n* Sugar Syrup\n* Soda Water\n* Mint",
            parsed_ingredients=["White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"],
            preparation="Muddle mint and lime, add rum and sugar, top with soda",
            served="Highball glass"
        ),
        Cocktail(
            uri="http://example.com/Daiquiri", id="daiquiri",
            name="Daiquiri",
            ingredients="* White Rum\n* Lime Juice\n* Sugar Syrup",
            parsed_ingredients=["White Rum", "Lime Juice", "Sugar Syrup"],
            preparation="Shake all ingredients with ice",
            served="Cocktail glass"
        ),
        Cocktail(
            uri="http://example.com/Margarita", id="margarita",
            name="Margarita",
            ingredients="* Tequila\n* Lime Juice\n* Triple Sec",
            parsed_ingredients=["Tequila", "Lime Juice", "Triple Sec"],
            preparation="Shake all ingredients with ice",
            served="Cocktail glass"
        )
    ]


@pytest.fixture
def sample_ingredients():
    """Sample ingredients for testing"""
    return [
        Ingredient(id="http://example.com/Rum", name="White Rum", category="Spirit"),
        Ingredient(id="http://example.com/Lime", name="Lime Juice", category="Juice"),
        Ingredient(id="http://example.com/Sugar", name="Sugar Syrup", category="Sweetener"),
        Ingredient(id="http://example.com/Soda", name="Soda Water", category="Mixer"),
        Ingredient(id="http://example.com/Mint", name="Mint", category="Herb"),
        Ingredient(id="http://example.com/Tequila", name="Tequila", category="Spirit"),
        Ingredient(id="http://example.com/TripleSec", name="Triple Sec", category="Liqueur")
    ]


class TestBarOptimizationWorkflow:
    """Test the complete 'Bar Optimization' feature workflow"""

    @patch('backend.routes.planner.service')
    def test_playlist_mode_workflow(self, mock_planner_service, client):
        """
        Test Playlist Mode optimization:
        1. Select desired cocktails
        2. Get minimum ingredients needed
        3. Get shopping list
        """
        # Mock playlist mode optimization
        mock_planner_service.optimize_playlist_mode.return_value = {
            "selected_ingredients": ["White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"],
            "covered_cocktails": ["Mojito", "Daiquiri"]
        }

        payload = {"cocktail_names": ["Mojito", "Daiquiri"]}
        response = client.post("/planner/playlist-mode", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["selected_ingredients"]) == 5
        assert set(result["covered_cocktails"]) == {"Mojito", "Daiquiri"}


class TestDiscoveryWorkflow:
    """Test the complete 'Discovery' feature workflow"""

    @patch('backend.routes.cocktails.get_cocktail_service')
    @patch('backend.routes.cocktails.similarity_service')
    def test_discovery_workflow(self, mock_similarity_service, mock_get_cocktail_service, client, sample_cocktails):
        """
        Test Discovery features:
        1. Search for a cocktail
        2. Find similar cocktails
        3. Find same-vibe cocktails
        4. Find bridge cocktails
        """
        mock_cocktail_svc = Mock()
        mock_get_cocktail_service.return_value = mock_cocktail_svc

        # Step 1: Search for cocktail
        mock_cocktail_svc.search_cocktails.return_value = [sample_cocktails[0]]
        response = client.get("/cocktails/?q=Mojito")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["name"] == "Mojito"

        # Step 2: Find similar cocktails (by ingredient overlap)
        mock_similarity_service.find_similar_cocktails.return_value = [
            {"cocktail": sample_cocktails[1], "similarity_score": 0.75}
        ]
        response = client.get("/cocktails/similar/Mojito")
        assert response.status_code == 200
        similar = response.json()
        assert similar["cocktail_id"] == "Mojito"
        assert len(similar["similar_cocktails"]) == 1
        assert similar["similar_cocktails"][0]["similarity_score"] == 0.75

        # Step 3: Find same-vibe cocktails (same community)
        mock_cocktail_svc.get_same_vibe_cocktails.return_value = [sample_cocktails[1]]
        response = client.get("/cocktails/same-vibe/Mojito")
        assert response.status_code == 200
        same_vibe = response.json()
        assert len(same_vibe) == 1

        # Step 4: Find bridge cocktails
        mock_cocktail_svc.get_bridge_cocktails.return_value = [sample_cocktails[2]]
        response = client.get("/cocktails/bridge")
        assert response.status_code == 200
        bridges = response.json()
        assert len(bridges) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
