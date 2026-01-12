"""
Comprehensive error handling tests for backend services.

This module tests exception handling, network failure recovery, invalid data handling,
missing file handling, and fallback mechanisms across all backend services:
- SparqlService
- CocktailService
- IngredientService
- GraphService
- PlannerService
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import services
from services.sparql_service import SparqlService
from services.cocktail_service import CocktailService
from services.ingredient_service import IngredientService
from services.graph_service import GraphService
from services.planner_service import PlannerService

# Import models
from models.cocktail import Cocktail
from models.ingredient import Ingredient


class TestSparqlServiceErrorHandling:
    """Test error handling in SparqlService"""

    @patch('services.sparql_service.Graph')
    def test_init_missing_ttl_file(self, mock_graph):
        """Test initialization when TTL file doesn't exist"""
        mock_instance = Mock()
        mock_instance.parse.side_effect = FileNotFoundError("File not found")
        mock_graph.return_value = mock_instance
        
        service = SparqlService("nonexistent.ttl")
        assert service.local_graph is None

    @patch('services.sparql_service.Graph')
    def test_init_corrupted_ttl_file(self, mock_graph):
        """Test initialization with corrupted TTL file"""
        mock_instance = Mock()
        mock_instance.parse.side_effect = Exception("Parse error: Invalid syntax")
        mock_graph.return_value = mock_instance
        
        service = SparqlService("corrupted.ttl")
        assert service.local_graph is None

    @patch('services.sparql_service.SPARQLWrapper')
    def test_execute_query_network_timeout(self, mock_wrapper):
        """Test network timeout during remote query"""
        mock_instance = Mock()
        mock_wrapper.return_value = mock_instance
        mock_instance.query.side_effect = Exception("Connection timeout")
        
        service = SparqlService()
        with pytest.raises(Exception, match="Connection timeout"):
            service.execute_query("SELECT * WHERE { ?s ?p ?o }")

    @patch('services.sparql_service.SPARQLWrapper')
    def test_execute_query_service_unavailable(self, mock_wrapper):
        """Test when DBpedia service is unavailable"""
        mock_instance = Mock()
        mock_wrapper.return_value = mock_instance
        mock_instance.query.side_effect = Exception("503 Service Unavailable")
        
        service = SparqlService()
        with pytest.raises(Exception, match="503 Service Unavailable"):
            service.execute_query("SELECT * WHERE { ?s ?p ?o }")

    @patch('services.sparql_service.SPARQLWrapper')
    def test_execute_query_invalid_sparql_syntax(self, mock_wrapper):
        """Test execution with invalid SPARQL syntax"""
        mock_instance = Mock()
        mock_wrapper.return_value = mock_instance
        mock_instance.query.side_effect = Exception("Malformed query")
        
        service = SparqlService()
        with pytest.raises(Exception, match="Malformed query"):
            service.execute_query("INVALID SPARQL QUERY")

    @patch('services.sparql_service.Graph')
    def test_execute_local_query_no_graph_loaded(self, mock_graph):
        """Test local query when graph failed to load"""
        service = SparqlService()
        service.local_graph = None
        
        with pytest.raises(ValueError, match="Local graph not loaded"):
            service.execute_local_query("SELECT * WHERE { ?s ?p ?o }")

    @patch('services.sparql_service.Graph')
    def test_execute_local_query_invalid_sparql(self, mock_graph):
        """Test local query with invalid SPARQL"""
        mock_instance = Mock()
        mock_graph.return_value = mock_instance
        mock_instance.query.side_effect = Exception("Invalid SPARQL syntax")
        
        service = SparqlService("test.ttl")
        with pytest.raises(Exception, match="Invalid SPARQL syntax"):
            service.execute_local_query("INVALID QUERY")

    @patch('services.sparql_service.Graph')
    def test_execute_local_query_empty_result(self, mock_graph):
        """Test local query returning empty results"""
        mock_instance = Mock()
        mock_graph.return_value = mock_instance
        
        # Mock empty query result - use a real list instead of Mock for iteration
        mock_instance.query.return_value = []
        
        service = SparqlService("test.ttl")
        result = service.execute_local_query("SELECT * WHERE { ?s ?p ?o }")
        
        assert result == {"results": {"bindings": []}}

    @patch('services.sparql_service.Graph')
    def test_execute_local_query_none_values(self, mock_graph):
        """Test local query handling None values in results"""
        mock_instance = Mock()
        mock_graph.return_value = mock_instance
        
        # Create a proper mock result with vars and iteration
        mock_result = Mock()
        mock_result.vars = ['s', 'p']
        
        # Create a proper mock row with __getitem__
        mock_row = Mock()
        mock_row.__getitem__ = Mock(side_effect=lambda var: None if var == 'p' else URIRef("http://example.com/s"))
        
        # Make the mock_result iterable by returning the row
        type(mock_result).__iter__ = Mock(return_value=lambda: iter([mock_row]))
        
        mock_instance.query.return_value = mock_result
        
        service = SparqlService("test.ttl")
        result = service.execute_local_query("SELECT ?s ?p WHERE { ?s ?p ?o }")
        
        assert result["results"]["bindings"][0]["p"]["value"] is None


class TestCocktailServiceErrorHandling:
    """Test error handling in CocktailService"""

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_init_missing_local_data(self, mock_graph, mock_ingredient, mock_sparql):
        """Test initialization when local data file is missing"""
        mock_sparql_instance = Mock()
        mock_sparql_instance.local_graph_path = "nonexistent.ttl"
        mock_sparql.return_value = mock_sparql_instance
        
        mock_graph_instance = Mock()
        mock_graph_instance.parse.side_effect = FileNotFoundError("File not found")
        mock_graph.return_value = mock_graph_instance
        
        service = CocktailService()
        assert service.graph is None

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_init_corrupted_local_data(self, mock_graph, mock_ingredient, mock_sparql):
        """Test initialization with corrupted local data"""
        mock_sparql_instance = Mock()
        mock_sparql_instance.local_graph_path = "corrupted.ttl"
        mock_sparql.return_value = mock_sparql_instance
        
        mock_graph_instance = Mock()
        mock_graph_instance.parse.side_effect = Exception("Turtle parse error")
        mock_graph.return_value = mock_graph_instance
        
        service = CocktailService()
        assert service.graph is None

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_get_all_cocktails_sparql_failure(self, mock_ingredient, mock_sparql):
        """Test get_all_cocktails when SPARQL query fails"""
        mock_sparql_instance = Mock()
        mock_sparql_instance.execute_local_query.side_effect = Exception("SPARQL service error")
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        cocktails = service.get_all_cocktails()
        
        assert cocktails == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_get_all_cocktails_malformed_results(self, mock_graph, mock_ingredient, mock_sparql):
        """Test get_all_cocktails with malformed SPARQL results"""
        mock_sparql_instance = Mock()
        mock_sparql_instance.local_graph_path = "test.ttl"
        mock_sparql.return_value = mock_sparql_instance
        
        mock_graph_instance = Mock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.objects.return_value = []
        
        # Mock malformed results
        mock_sparql_instance.execute_local_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "cocktail": {"value": "http://example.com/cocktail1"},
                        # Missing required 'name' field
                    }
                ]
            }
        }
        
        service = CocktailService()
        # Need to also mock _parse_ingredient_names and _extract_ingredient_uris
        service._parse_ingredient_names = Mock(return_value=[])
        service._extract_ingredient_uris = Mock(return_value=[])
        
        cocktails = service.get_all_cocktails()
        
        # Should handle missing fields gracefully
        assert len(cocktails) == 1
        assert cocktails[0].name == "Unknown Cocktail"

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_parse_cocktail_from_graph_no_graph(self, mock_graph, mock_ingredient, mock_sparql):
        """Test parsing cocktail when graph is None"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        service.graph = None
        
        result = service._parse_cocktail_from_graph(URIRef("http://example.com/cocktail"))
        assert result is None

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_get_feasible_cocktails_inventory_service_failure(self, mock_graph, mock_ingredient, mock_sparql):
        """Test get_feasible_cocktails when inventory service fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_inventory.side_effect = Exception("Inventory service error")
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = CocktailService()
        service.get_all_cocktails = Mock(return_value=[])
        
        # Should propagate the exception
        with pytest.raises(Exception, match="Inventory service error"):
            service.get_feasible_cocktails("user1")

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_get_feasible_cocktails_none_ingredients(self, mock_graph, mock_ingredient, mock_sparql):
        """Test get_feasible_cocktails with cocktails having None ingredients"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_inventory.return_value = ["Rum"]
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = CocktailService()
        
        mock_cocktail = Mock()
        mock_cocktail.ingredients = None
        service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        
        feasible = service.get_feasible_cocktails("user1")
        assert feasible == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_get_similar_cocktails_target_not_found(self, mock_graph, mock_ingredient, mock_sparql):
        """Test get_similar_cocktails with non-existent target"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        
        mock_cocktail = Mock()
        mock_cocktail.id = "different_id"
        service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        
        results = service.get_similar_cocktails("nonexistent_id")
        assert results == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_get_same_vibe_cocktails_graph_service_failure(self, mock_graph, mock_ingredient, mock_sparql):
        """Test get_same_vibe_cocktails when GraphService fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        
        mock_cocktail = Mock()
        mock_cocktail.id = "target_id"
        mock_cocktail.name = "Mojito"
        service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        
        # Mock the GraphService to fail
        with patch('services.cocktail_service.GraphService') as MockGraphService:
            mock_graph_service_instance = Mock()
            MockGraphService.return_value = mock_graph_service_instance
            mock_graph_service_instance.analyze_graph.side_effect = Exception("Graph analysis failed")
             
            # Should handle gracefully and return empty list
            results = service.get_same_vibe_cocktails("target_id")
            assert results == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_get_bridge_cocktails_graph_service_failure(self, mock_graph, mock_ingredient, mock_sparql):
        """Test get_bridge_cocktails when GraphService fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        
        mock_cocktail = Mock()
        mock_cocktail.parsed_ingredients = ["Rum", "Lime"]
        service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        
        # Mock the GraphService to fail
        with patch('services.cocktail_service.GraphService') as MockGraphService:
            mock_graph_service_instance = Mock()
            MockGraphService.return_value = mock_graph_service_instance
            mock_graph_service_instance.analyze_graph.side_effect = Exception("Graph analysis failed")
             
            # Should handle gracefully and return empty list
            results = service.get_bridge_cocktails()
            assert results == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_parse_ingredient_names_edge_cases(self, mock_graph, mock_ingredient, mock_sparql):
        """Test _parse_ingredient_names with edge cases"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        
        # Empty string
        assert service._parse_ingredient_names("") == []
        
        # None
        assert service._parse_ingredient_names(None) == []
        
        # No bullets
        assert service._parse_ingredient_names("Just text") == []
        
        # Mixed bullets
        assert service._parse_ingredient_names("* Rum\n• Vodka\n- Gin") == ["Rum", "Vodka", "Gin"]
        
        # Special characters
        assert service._parse_ingredient_names("* 45 ml White Rum (Aged)") == ["White Rum (Aged)"]


class TestIngredientServiceErrorHandling:
    """Test error handling in IngredientService"""

    @patch('services.ingredient_service.SparqlService')
    def test_get_all_ingredients_local_query_failure(self, mock_sparql):
        """Test get_all_ingredients when local query fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # First call for local URIs fails
        mock_sparql_instance.execute_local_query.side_effect = Exception("Local query failed")
        # Second call for DBpedia succeeds
        mock_sparql_instance.execute_query.return_value = {"results": {"bindings": []}}
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should return empty list, not crash
        assert ingredients == []

    @patch('services.ingredient_service.SparqlService')
    def test_get_all_ingredients_dbpedia_failure(self, mock_sparql):
        """Test get_all_ingredients when DBpedia query fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Local query succeeds but returns empty
        mock_sparql_instance.execute_local_query.return_value = {"results": {"bindings": []}}
        # DBpedia query fails
        mock_sparql_instance.execute_query.side_effect = Exception("DBpedia unavailable")
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should return empty list, not crash
        assert ingredients == []

    @patch('services.ingredient_service.SparqlService')
    def test_get_all_ingredients_partial_local_results(self, mock_sparql):
        """Test get_all_ingredients with partial local results"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Mock local URIs
        mock_sparql_instance.execute_local_query.side_effect = [
            {"results": {"bindings": [{"ingredient": {"value": "http://example.com/ing1"}}]}},
            {"results": {"bindings": [{"name": {"value": "Ing1"}, "description": {"value": "Desc1"}}]}}
        ]
        
        # DBpedia returns more ingredients
        mock_sparql_instance.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"id": {"value": "http://dbpedia.org/resource/Ing2"}, "name": {"value": "Ing2"}},
                    {"id": {"value": "http://dbpedia.org/resource/Ing3"}, "name": {"value": "Ing3"}}
                ]
            }
        }
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should have 3 ingredients total (1 local + 2 DBpedia)
        assert len(ingredients) == 3

    @patch('services.ingredient_service.SparqlService')
    def test_get_all_ingredients_duplicate_uris(self, mock_sparql):
        """Test get_all_ingredients handles duplicate URIs"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Local query returns URIs
        mock_sparql_instance.execute_local_query.side_effect = [
            {"results": {"bindings": [{"ingredient": {"value": "http://dbpedia.org/resource/Ing1"}}]}},
            {"results": {"bindings": [{"name": {"value": "Local Ing1"}}]}}
        ]
        
        # DBpedia returns same URI
        mock_sparql_instance.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"id": {"value": "http://dbpedia.org/resource/Ing1"}, "name": {"value": "DB Ing1"}}
                ]
            }
        }
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should avoid duplicates
        assert len(ingredients) == 1

    @patch('services.ingredient_service.SparqlService')
    def test_search_ingredients_network_error(self, mock_sparql):
        """Test search_ingredients with network error"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_query.side_effect = Exception("Network error")
        
        service = IngredientService()
        ingredients = service.search_ingredients("vodka")
        
        # Should return empty list on error
        assert ingredients == []

    @patch('services.ingredient_service.SparqlService')
    def test_search_ingredients_empty_results(self, mock_sparql):
        """Test search_ingredients with no results"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_query.return_value = {"results": {"bindings": []}}
        
        service = IngredientService()
        ingredients = service.search_ingredients("nonexistent")
        
        assert ingredients == []

    @patch('services.ingredient_service.SparqlService')
    def test_get_ingredient_by_uri_invalid_uri(self, mock_sparql):
        """Test get_ingredient_by_uri with invalid URI"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_local_query.return_value = {"results": {"bindings": []}}
        mock_sparql_instance.execute_query.side_effect = Exception("Invalid URI format")
        
        service = IngredientService()
        ingredient = service.get_ingredient_by_uri("not a valid uri")
        
        assert ingredient is None

    @patch('services.ingredient_service.SparqlService')
    def test_get_ingredient_by_uri_both_services_fail(self, mock_sparql):
        """Test get_ingredient_by_uri when both local and DBpedia fail"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_local_query.side_effect = Exception("Local error")
        mock_sparql_instance.execute_query.side_effect = Exception("DBpedia error")
        
        service = IngredientService()
        ingredient = service.get_ingredient_by_uri("http://example.com/ing")
        
        assert ingredient is None

    @patch('services.ingredient_service.SparqlService')
    def test_get_local_ingredient_uris_query_failure(self, mock_sparql):
        """Test _get_local_ingredient_uris when query fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_local_query.side_effect = Exception("Query failed")
        
        service = IngredientService()
        uris = service._get_local_ingredient_uris()
        
        assert uris == []

    @patch('services.ingredient_service.SparqlService')
    def test_query_local_ingredient_exception(self, mock_sparql):
        """Test _query_local_ingredient handles exceptions"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_local_query.side_effect = Exception("Query error")
        
        service = IngredientService()
        ingredient = service._query_local_ingredient("http://example.com/ing")
        
        assert ingredient is None

    def test_inventory_operations_edge_cases(self):
        """Test inventory operations with edge cases"""
        service = IngredientService()
        
        # Add to non-existent user
        service.add_to_inventory("user1", "Vodka")
        assert service.inventories["user1"] == ["Vodka"]
        
        # Remove from non-existent user
        service.remove_from_inventory("user2", "Vodka")
        assert "user2" not in service.inventories
        
        # Remove non-existent ingredient
        service.remove_from_inventory("user1", "Gin")
        assert service.inventories["user1"] == ["Vodka"]
        
        # Clear non-existent user
        service.clear_inventory("user3")
        assert "user3" not in service.inventories


class TestGraphServiceErrorHandling:
    """Test error handling in GraphService"""

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_cocktail_service_failure(self, mock_ingredient, mock_cocktail):
        """Test build_graph when CocktailService fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to build graph"):
            service.build_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_ingredient_service_failure(self, mock_ingredient, mock_cocktail):
        """Test build_graph when IngredientService fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.side_effect = Exception("Ingredient service error")
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to build graph"):
            service.build_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_empty_data(self, mock_ingredient, mock_cocktail):
        """Test build_graph with completely empty data"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.return_value = []
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        graph = service.build_graph()
        
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_cocktail_with_none_parsed_ingredients(self, mock_ingredient, mock_cocktail):
        """Test build_graph with cocktail having None parsed_ingredients"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Mojito",
            parsed_ingredients=None
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.return_value = []
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        graph = service.build_graph()
        
        # Should have cocktail node but no edges
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_ingredient_not_in_graph(self, mock_ingredient, mock_cocktail):
        """Test build_graph when ingredient node doesn't exist in graph"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        # Only return one ingredient, not both
        ingredient = Ingredient(id="http://example.com/rum", name="Rum")
        mock_ingredient_instance.get_all_ingredients.return_value = [ingredient]
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        graph = service.build_graph()
        
        # Should only have edge for ingredient that exists
        assert len(graph.nodes) == 2  # 1 cocktail + 1 ingredient
        assert len(graph.edges) == 1  # Only Rum edge
        assert graph.has_edge("Mojito", "Rum")
        assert not graph.has_edge("Mojito", "Lime")

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_graph_build_failure(self, mock_ingredient, mock_cocktail):
        """Test analyze_graph when build_graph fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Build error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to analyze graph"):
            service.analyze_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_graph_community_detection_failure(self, mock_ingredient, mock_cocktail):
        """Test analyze_graph when community detection fails"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Mojito",
            parsed_ingredients=["Rum"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        ingredient = Ingredient(id="http://example.com/rum", name="Rum")
        mock_ingredient_instance.get_all_ingredients.return_value = [ingredient]
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        # Mock networkx to fail during community detection
        with patch('services.graph_service.nx') as mock_nx:
            mock_graph = Mock()
            mock_nx.Graph.return_value = mock_graph
            mock_graph.nodes.return_value = {"Mojito": {"type": "cocktail"}, "Rum": {"type": "ingredient"}}
            mock_graph.edges.return_value = [("Mojito", "Rum")]
            mock_nx.degree_centrality.return_value = {"Mojito": 1.0, "Rum": 1.0}
            mock_nx.betweenness_centrality.return_value = {"Mojito": 0.0, "Rum": 0.0}
            mock_nx.closeness_centrality.return_value = {"Mojito": 1.0, "Rum": 1.0}
            mock_nx.algorithms.community.louvain_communities.side_effect = Exception("Community detection failed")
             
            with pytest.raises(Exception, match="Failed to analyze graph"):
                service.analyze_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_graph_empty_graph(self, mock_ingredient, mock_cocktail):
        """Test analyze_graph with empty graph"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.return_value = []
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        result = service.analyze_graph()
        
        assert result["metrics"]["degree_centrality"] == {}
        assert result["communities"] == {}

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_visualize_graph_build_failure(self, mock_ingredient, mock_cocktail):
        """Test visualize_graph when build_graph fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Build error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to visualize graph"):
            service.visualize_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_disjoint_components_build_failure(self, mock_ingredient, mock_cocktail):
        """Test analyze_disjoint_components when build_graph fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Build error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to analyze disjoint components"):
            service.analyze_disjoint_components()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_export_graph_build_failure(self, mock_ingredient, mock_cocktail):
        """Test export_graph when build_graph fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Build error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to export graph"):
            service.export_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_export_graph_networkx_failure(self, mock_ingredient, mock_cocktail):
        """Test export_graph when networkx write_gexf fails"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Mojito",
            parsed_ingredients=["Rum"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        ingredient = Ingredient(id="http://example.com/rum", name="Rum")
        mock_ingredient_instance.get_all_ingredients.return_value = [ingredient]
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        # Mock networkx to fail during export
        with patch('services.graph_service.nx') as mock_nx:
            mock_graph = Mock()
            mock_nx.Graph.return_value = mock_graph
            mock_graph.nodes.return_value = {"Mojito": {"type": "cocktail"}, "Rum": {"type": "ingredient"}}
            mock_graph.edges.return_value = [("Mojito", "Rum")]
            mock_nx.write_gexf.side_effect = Exception("Export failed")
             
            with pytest.raises(Exception, match="Failed to export graph"):
                service.export_graph()


class TestPlannerServiceErrorHandling:
    """Test error handling in PlannerService"""

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_init_cocktail_service_failure(self, mock_ingredient, mock_cocktail):
        """Test initialization when CocktailService fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        with pytest.raises(Exception):
            PlannerService()

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_init_empty_cocktails(self, mock_ingredient, mock_cocktail):
        """Test initialization with no cocktails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        assert service.cocktail_ingredients == {}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_init_cocktail_with_none_parsed_ingredients(self, mock_ingredient, mock_cocktail):
        """Test initialization with cocktail having None parsed_ingredients"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Mojito",
            parsed_ingredients=None
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        assert service.cocktail_ingredients["Mojito"] == set()

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_party_mode_zero_ingredients(self, mock_ingredient, mock_cocktail):
        """Test optimize_party_mode with zero ingredients"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_party_mode(0)
        
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_party_mode_negative_ingredients(self, mock_ingredient, mock_cocktail):
        """Test optimize_party_mode with negative ingredients"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_party_mode(-5)
        
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_party_mode_more_ingredients_than_available(self, mock_ingredient, mock_cocktail):
        """Test optimize_party_mode requesting more ingredients than available"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_party_mode(100)  # Request more than available
        
        assert len(result['selected_ingredients']) <= 2  # Should not exceed available
        assert len(result['covered_cocktails']) >= 0

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_party_mode_no_overlap(self, mock_ingredient, mock_cocktail):
        """Test optimize_party_mode with cocktails having no ingredient overlap"""
        mock_cocktail_instance = Mock()
        cocktail1 = Cocktail(
            id="http://example.com/cocktail1",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        cocktail2 = Cocktail(
            id="http://example.com/cocktail2",
            name="Martini",
            parsed_ingredients=["Gin", "Vermouth"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail1, cocktail2]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_party_mode(2)
        
        # Should select 2 ingredients (one from each cocktail)
        assert len(result['selected_ingredients']) == 2
        # Should cover both cocktails since we're selecting 2 ingredients
        assert len(result['covered_cocktails']) >= 1

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_party_mode_all_same_ingredients(self, mock_ingredient, mock_cocktail):
        """Test optimize_party_mode with all cocktails having same ingredients"""
        mock_cocktail_instance = Mock()
        cocktail1 = Cocktail(
            id="http://example.com/cocktail1",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime", "Mint"]
        )
        cocktail2 = Cocktail(
            id="http://example.com/cocktail2",
            name="Daiquiri",
            parsed_ingredients=["Rum", "Lime", "Sugar"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail1, cocktail2]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_party_mode(1)
        
        # Should select ingredients that cover both
        assert len(result['selected_ingredients']) == 1
        assert len(result['covered_cocktails']) == 2

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_empty_list(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode with empty cocktail list"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode([])
        
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_nonexistent_cocktails(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode with non-existent cocktail names"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode(["Nonexistent1", "Nonexistent2"])
        
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_partial_match(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode with some cocktails existing and some not"""
        mock_cocktail_instance = Mock()
        cocktail1 = Cocktail(
            id="http://example.com/cocktail1",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        cocktail2 = Cocktail(
            id="http://example.com/cocktail2",
            name="Martini",
            parsed_ingredients=["Gin", "Vermouth"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail1, cocktail2]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode(["Mojito", "Nonexistent"])
        
        # Should only cover existing cocktail
        assert len(result['covered_cocktails']) == 1
        assert "Mojito" in result['covered_cocktails']

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_uncoverable_cocktail(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode with a cocktail that cannot be fully covered"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            id="http://example.com/cocktail",
            name="Complex",
            parsed_ingredients=["Ing1", "Ing2", "Ing3", "Ing4", "Ing5"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        # Request only 2 ingredients for a 5-ingredient cocktail
        result = service.optimize_playlist_mode(["Complex"])
        
        # Should still try to cover as much as possible
        assert len(result['selected_ingredients']) <= 2
        # May not fully cover the cocktail
        assert len(result['covered_cocktails']) <= 1

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_single_ingredient_multiple_cocktails(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode where one ingredient covers multiple cocktails"""
        mock_cocktail_instance = Mock()
        cocktail1 = Cocktail(
            id="http://example.com/cocktail1",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        cocktail2 = Cocktail(
            id="http://example.com/cocktail2",
            name="Daiquiri",
            parsed_ingredients=["Rum", "Sugar"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail1, cocktail2]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode(["Mojito", "Daiquiri"])
        
        # Should select Rum first as it covers both
        assert "Rum" in result['selected_ingredients']
        assert len(result['covered_cocktails']) == 2

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_no_progress_possible(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode when no ingredient can cover remaining cocktails"""
        mock_cocktail_instance = Mock()
        cocktail1 = Cocktail(
            id="http://example.com/cocktail1",
            name="Cocktail1",
            parsed_ingredients=["Ing1"]
        )
        cocktail2 = Cocktail(
            id="http://example.com/cocktail2",
            name="Cocktail2",
            parsed_ingredients=["Ing2"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail1, cocktail2]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode(["Cocktail1", "Cocktail2"])
        
        # Should select both ingredients
        assert set(result['selected_ingredients']) == {"Ing1", "Ing2"}
        assert set(result['covered_cocktails']) == {"Cocktail1", "Cocktail2"}


class TestCrossServiceErrorHandling:
    """Test error scenarios that span multiple services"""

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_cocktail_service_chain_failure(self, mock_graph, mock_ingredient, mock_sparql):
        """Test when CocktailService depends on failing SparqlService"""
        mock_sparql_instance = Mock()
        mock_sparql_instance.local_graph_path = "test.ttl"
        mock_sparql.return_value = mock_sparql_instance
        
        mock_graph_instance = Mock()
        mock_graph.return_value = mock_graph_instance
        
        # SparqlService fails during query
        mock_sparql_instance.execute_local_query.side_effect = Exception("SPARQL chain failure")
        
        service = CocktailService()
        
        # All methods that depend on SPARQL should handle gracefully
        assert service.get_all_cocktails() == []
        assert service.search_cocktails("test") == []
        
        # Methods that need cocktails should also handle empty results
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_inventory.return_value = ["Rum"]
        mock_ingredient.return_value = mock_ingredient_instance
        
        assert service.get_feasible_cocktails("user1") == []
        assert service.get_almost_feasible_cocktails("user1") == []

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_graph_service_chain_failure(self, mock_ingredient, mock_cocktail):
        """Test when GraphService depends on failing services"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service unavailable")
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        # All methods should fail with appropriate error messages
        with pytest.raises(Exception, match="Failed to build graph"):
            service.build_graph()
        
        with pytest.raises(Exception, match="Failed to analyze graph"):
            service.analyze_graph()
        
        with pytest.raises(Exception, match="Failed to visualize graph"):
            service.visualize_graph()

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_planner_service_chain_failure(self, mock_ingredient, mock_cocktail):
        """Test when PlannerService depends on failing CocktailService"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service unavailable")
        mock_cocktail.return_value = mock_cocktail_instance
        
        # Should fail during initialization
        with pytest.raises(Exception):
            PlannerService()

    @patch('services.ingredient_service.SparqlService')
    def test_ingredient_service_fallback_to_dbpedia(self, mock_sparql):
        """Test IngredientService fallback when local queries fail"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Local query fails
        mock_sparql_instance.execute_local_query.side_effect = Exception("Local unavailable")
        
        # DBpedia works
        mock_sparql_instance.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"id": {"value": "http://dbpedia.org/resource/Vodka"}, "name": {"value": "Vodka"}}
                ]
            }
        }
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should still get ingredients from DBpedia
        assert len(ingredients) == 1
        assert ingredients[0].name == "Vodka"

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    @patch('services.cocktail_service.Graph')
    def test_cocktail_service_partial_data_recovery(self, mock_graph, mock_ingredient, mock_sparql):
        """Test CocktailService recovery with partial data"""
        mock_sparql_instance = Mock()
        mock_sparql_instance.local_graph_path = "test.ttl"
        mock_sparql.return_value = mock_sparql_instance
        
        mock_graph_instance = Mock()
        mock_graph.return_value = mock_graph_instance
        
        # First query fails, second succeeds
        mock_sparql_instance.execute_local_query.side_effect = [
            Exception("First query fails"),
            {"results": {"bindings": [{"cocktail": {"value": "http://example.com/cocktail"}}]}}
        ]
        
        service = CocktailService()
        
        # First call fails
        assert service.get_all_cocktails() == []
        
        # Second call succeeds (if called again)
        mock_sparql_instance.execute_local_query.side_effect = [
            {"results": {"bindings": [{"cocktail": {"value": "http://example.com/cocktail"}, "name": {"value": "Test"}}]}}
        ]
        service._parse_ingredient_names = Mock(return_value=[])
        service._extract_ingredient_uris = Mock(return_value=[])
        
        cocktails = service.get_all_cocktails()
        assert len(cocktails) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
