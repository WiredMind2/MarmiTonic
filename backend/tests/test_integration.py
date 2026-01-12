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

from main import app
from models.cocktail import Cocktail
from models.ingredient import Ingredient


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_cocktails():
    """Sample cocktails for testing"""
    return [
        Cocktail(
            id="http://example.com/Mojito",
            name="Mojito",
            ingredients="* White Rum\n* Lime Juice\n* Sugar Syrup\n* Soda Water\n* Mint",
            parsed_ingredients=["White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"],
            preparation="Muddle mint and lime, add rum and sugar, top with soda",
            served="Highball glass"
        ),
        Cocktail(
            id="http://example.com/Daiquiri",
            name="Daiquiri",
            ingredients="* White Rum\n* Lime Juice\n* Sugar Syrup",
            parsed_ingredients=["White Rum", "Lime Juice", "Sugar Syrup"],
            preparation="Shake all ingredients with ice",
            served="Cocktail glass"
        ),
        Cocktail(
            id="http://example.com/Margarita",
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


class TestMyBarWorkflow:
    """Test the complete 'My Bar' feature workflow"""

    @patch('backend.routes.ingredients.service')
    @patch('backend.routes.cocktails.CocktailService')
    def test_my_bar_complete_workflow(self, mock_cocktail_service, mock_ingredient_service, 
                                      client, sample_cocktails, sample_ingredients):
        """
        Test complete My Bar workflow:
        1. Get all ingredients
        2. Update user inventory
        3. Get feasible cocktails
        4. Get almost-feasible cocktails
        5. Add missing ingredient
        6. Get updated feasible cocktails
        """
        # Step 1: Get all ingredients
        mock_ingredient_service.get_all_ingredients.return_value = sample_ingredients
        response = client.get("/ingredients/ingredients")
        assert response.status_code == 200
        ingredients = response.json()
        assert len(ingredients) == 7

        # Step 2: Update user inventory with partial ingredients
        mock_ingredient_service.update_inventory.return_value = None
        mock_ingredient_service.get_inventory.return_value = ["White Rum", "Lime Juice", "Sugar Syrup"]
        
        payload = {
            "user_id": "user123",
            "ingredients": ["White Rum", "Lime Juice", "Sugar Syrup"]
        }
        response = client.post("/ingredients/ingredients/inventory", json=payload)
        assert response.status_code == 200

        # Step 3: Get feasible cocktails (should only get Daiquiri)
        mock_service = Mock()
        mock_cocktail_service.return_value = mock_service
        mock_service.get_feasible_cocktails.return_value = [sample_cocktails[1]]  # Daiquiri
        
        response = client.get("/cocktails/feasible/user123")
        assert response.status_code == 200
        feasible = response.json()
        assert len(feasible) == 1
        assert feasible[0]["name"] == "Daiquiri"

        # Step 4: Get almost-feasible cocktails (Mojito missing 2 ingredients)
        mock_service.get_almost_feasible_cocktails.return_value = [
            {"cocktail": sample_cocktails[0], "missing": ["Soda Water", "Mint"]}
        ]
        
        response = client.get("/cocktails/almost-feasible/user123")
        assert response.status_code == 200
        almost_feasible = response.json()
        assert len(almost_feasible) == 1
        assert almost_feasible[0]["cocktail"]["name"] == "Mojito"
        assert len(almost_feasible[0]["missing"]) == 2

        # Step 5: Add missing ingredients
        mock_ingredient_service.get_inventory.return_value = [
            "White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"
        ]
        
        payload = {
            "user_id": "user123",
            "ingredients": ["White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"]
        }
        response = client.post("/ingredients/ingredients/inventory", json=payload)
        assert response.status_code == 200

        # Step 6: Get updated feasible cocktails (should now include Mojito)
        mock_service.get_feasible_cocktails.return_value = [
            sample_cocktails[0],  # Mojito
            sample_cocktails[1]   # Daiquiri
        ]
        
        response = client.get("/cocktails/feasible/user123")
        assert response.status_code == 200
        feasible = response.json()
        assert len(feasible) == 2
        cocktail_names = [c["name"] for c in feasible]
        assert "Mojito" in cocktail_names
        assert "Daiquiri" in cocktail_names


class TestBarOptimizationWorkflow:
    """Test the complete 'Bar Optimization' feature workflow"""

    @patch('backend.routes.planner.service')
    def test_party_mode_workflow(self, mock_planner_service, client):
        """
        Test Party Mode optimization:
        1. Request optimization with budget of 3 ingredients
        2. Get recommended ingredients
        3. Get number of cocktails covered
        """
        # Mock party mode optimization
        mock_planner_service.optimize_party_mode.return_value = {
            "selected_ingredients": ["White Rum", "Lime Juice", "Sugar Syrup"],
            "covered_cocktails": ["Mojito", "Daiquiri"]
        }

        payload = {"num_ingredients": 3}
        response = client.post("/planner/planner/party-mode", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["selected_ingredients"]) == 3
        assert len(result["covered_cocktails"]) == 2
        assert "White Rum" in result["selected_ingredients"]

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
        response = client.post("/planner/planner/playlist-mode", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["selected_ingredients"]) == 5
        assert set(result["covered_cocktails"]) == {"Mojito", "Daiquiri"}

    @patch('backend.routes.planner.service')
    def test_union_ingredients_workflow(self, mock_planner_service, client):
        """
        Test getting union of ingredients for multiple cocktails
        """
        mock_planner_service.get_union_ingredients.return_value = [
            "White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"
        ]

        payload = {"cocktail_names": ["Mojito", "Daiquiri"]}
        response = client.post("/planner/planner/union-ingredients", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["ingredients"]) == 5


class TestDiscoveryWorkflow:
    """Test the complete 'Discovery' feature workflow"""

    @patch('backend.routes.cocktails.CocktailService')
    def test_discovery_workflow(self, mock_cocktail_service, client, sample_cocktails):
        """
        Test Discovery features:
        1. Search for a cocktail
        2. Find similar cocktails
        3. Find same-vibe cocktails
        4. Find bridge cocktails
        """
        mock_service = Mock()
        mock_cocktail_service.return_value = mock_service

        # Step 1: Search for cocktail
        mock_service.search_cocktails.return_value = [sample_cocktails[0]]
        response = client.get("/cocktails/?q=Mojito")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["name"] == "Mojito"

        # Step 2: Find similar cocktails (by ingredient overlap)
        mock_service.get_similar_cocktails.return_value = [
            {"cocktail": sample_cocktails[1], "similarity_score": 0.75}
        ]
        response = client.get("/cocktails/similar/Mojito")
        assert response.status_code == 200
        similar = response.json()
        assert len(similar) == 1
        assert similar[0]["similarity_score"] == 0.75

        # Step 3: Find same-vibe cocktails (same community)
        mock_service.get_same_vibe_cocktails.return_value = [sample_cocktails[1]]
        response = client.get("/cocktails/same-vibe/Mojito")
        assert response.status_code == 200
        same_vibe = response.json()
        assert len(same_vibe) == 1

        # Step 4: Find bridge cocktails
        mock_service.get_bridge_cocktails.return_value = [sample_cocktails[2]]
        response = client.get("/cocktails/bridge")
        assert response.status_code == 200
        bridges = response.json()
        assert len(bridges) == 1


class TestInsightsWorkflow:
    """Test the complete 'Insights' feature workflow"""

    @patch('backend.routes.insights.GraphService')
    def test_insights_workflow(self, mock_graph_service, client):
        """
        Test Insights features:
        1. Get graph analysis
        2. Get visualization data
        3. Analyze components
        4. Export graph
        """
        mock_service = Mock()
        mock_graph_service.return_value = mock_service

        # Step 1: Get graph analysis
        mock_service.analyze_graph.return_value = {
            "metrics": {
                "degree_centrality": {"Rum": 0.8, "Vodka": 0.6},
                "betweenness_centrality": {"Rum": 0.5},
                "closeness_centrality": {"Rum": 0.7}
            },
            "communities": {"Rum": 1, "Vodka": 2}
        }
        
        response = client.get("/insights/insights/graph")
        assert response.status_code == 200
        analysis = response.json()
        assert "metrics" in analysis
        assert "communities" in analysis

        # Step 2: Get visualization data
        mock_service.visualize_graph.return_value = {
            "nodes": [
                {"id": "Mojito", "type": "cocktail"},
                {"id": "Rum", "type": "ingredient"}
            ],
            "links": [{"source": "Mojito", "target": "Rum"}]
        }
        
        response = client.get("/insights/insights/visualization")
        assert response.status_code == 200
        viz_data = response.json()
        assert "nodes" in viz_data
        assert "links" in viz_data

        # Step 3: Analyze components
        mock_service.analyze_disjoint_components.return_value = {
            "num_components": 2,
            "largest_component_size": 50,
            "isolated_nodes": 3
        }
        
        response = client.get("/insights/insights/components")
        assert response.status_code == 200
        components = response.json()
        assert components["num_components"] == 2

        # Step 4: Export graph
        mock_service.export_graph.return_value = "<gexf>...</gexf>"
        
        response = client.get("/insights/insights/export")
        assert response.status_code == 200
        export_data = response.json()
        assert "gexf_data" in export_data


class TestEndToEndScenarios:
    """Test realistic end-to-end user scenarios"""

    @patch('backend.routes.ingredients.service')
    @patch('backend.routes.cocktails.CocktailService')
    @patch('backend.routes.planner.service')
    def test_party_planning_scenario(self, mock_planner, mock_cocktail_service, 
                                     mock_ingredient_service, client, sample_cocktails):
        """
        Scenario: User wants to plan a party
        1. Check what cocktails they can make
        2. Use party mode to optimize bar
        3. Get shopping list
        4. Update inventory
        5. Verify they can now make the cocktails
        """
        user_id = "party_host"
        
        # Initial inventory: only basic items
        mock_ingredient_service.get_inventory.return_value = ["Lime Juice", "Sugar Syrup"]
        
        # Check feasible cocktails (none with current inventory)
        mock_service = Mock()
        mock_cocktail_service.return_value = mock_service
        mock_service.get_feasible_cocktails.return_value = []
        
        response = client.get(f"/cocktails/feasible/{user_id}")
        assert len(response.json()) == 0

        # Use party mode to optimize for 5 ingredients
        mock_planner.optimize_party_mode.return_value = {
            "selected_ingredients": ["White Rum", "Lime Juice", "Sugar Syrup", "Soda Water", "Mint"],
            "covered_cocktails": ["Mojito", "Daiquiri"]
        }
        
        response = client.post("/planner/planner/party-mode", json={"num_ingredients": 5})
        optimization = response.json()
        
        # Update inventory with optimized ingredients
        mock_ingredient_service.get_inventory.return_value = optimization["selected_ingredients"]
        payload = {
            "user_id": user_id,
            "ingredients": optimization["selected_ingredients"]
        }
        response = client.post("/ingredients/ingredients/inventory", json=payload)
        assert response.status_code == 200

        # Verify can now make cocktails
        mock_service.get_feasible_cocktails.return_value = [
            sample_cocktails[0],  # Mojito
            sample_cocktails[1]   # Daiquiri
        ]
        
        response = client.get(f"/cocktails/feasible/{user_id}")
        feasible = response.json()
        assert len(feasible) == 2

    @patch('backend.routes.cocktails.CocktailService')
    @patch('backend.routes.insights.GraphService')
    def test_cocktail_exploration_scenario(self, mock_graph_service, mock_cocktail_service, 
                                          client, sample_cocktails):
        """
        Scenario: User discovers new cocktails
        1. Search for a favorite cocktail
        2. Find similar cocktails
        3. Explore community/vibe
        4. View graph insights
        """
        mock_cocktail_svc = Mock()
        mock_cocktail_service.return_value = mock_cocktail_svc
        
        # Find favorite cocktail
        mock_cocktail_svc.search_cocktails.return_value = [sample_cocktails[0]]
        response = client.get("/cocktails/?q=Mojito")
        favorite = response.json()[0]
        
        # Find similar cocktails
        mock_cocktail_svc.get_similar_cocktails.return_value = [
            {"cocktail": sample_cocktails[1], "similarity_score": 0.75}
        ]
        response = client.get(f"/cocktails/similar/{favorite['id']}")
        similar = response.json()
        assert len(similar) >= 1
        
        # Explore same vibe
        mock_cocktail_svc.get_same_vibe_cocktails.return_value = [sample_cocktails[1]]
        response = client.get(f"/cocktails/same-vibe/{favorite['id']}")
        same_vibe = response.json()
        assert len(same_vibe) >= 1
        
        # View graph insights
        mock_graph_svc = Mock()
        mock_graph_service.return_value = mock_graph_svc
        mock_graph_svc.visualize_graph.return_value = {
            "nodes": [],
            "links": []
        }
        
        response = client.get("/insights/insights/visualization")
        assert response.status_code == 200


class TestErrorRecoveryWorkflows:
    """Test error handling and recovery in workflows"""

    @patch('backend.routes.cocktails.CocktailService')
    def test_service_failure_recovery(self, mock_cocktail_service, client):
        """
        Test that API gracefully handles service failures
        """
        mock_service = Mock()
        mock_cocktail_service.return_value = mock_service
        mock_service.get_all_cocktails.side_effect = Exception("Service unavailable")
        
        response = client.get("/cocktails/")
        assert response.status_code == 500
        assert "Service unavailable" in response.json()["detail"]

    @patch('backend.routes.ingredients.service')
    def test_empty_inventory_workflow(self, mock_ingredient_service, client):
        """
        Test workflow with empty inventory
        """
        mock_ingredient_service.get_inventory.return_value = []
        
        response = client.get("/ingredients/ingredients/inventory/user123")
        assert response.status_code == 200
        assert response.json()["ingredients"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
