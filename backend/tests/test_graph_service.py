import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.graph_service import GraphService


@pytest.fixture
def graph_service():
    patcher = patch('services.graph_service.SparqlService')
    mock_sparql = patcher.start()
    service = GraphService()
    yield service
    patcher.stop()


class TestGraphService:

    def test_init(self, graph_service):
        assert hasattr(graph_service, 'sparql_service')

    def test_get_graph_data_success(self, graph_service):
        mock_data = {
            "results": {
                "bindings": [
                    {
                        "cocktail": {"value": "http://example.com/cocktail1", "type": "uri"},
                        "ingredient": {"value": "http://example.com/ingredient1", "type": "uri"}
                    },
                    {
                        "cocktail": {"value": "http://example.com/cocktail2", "type": "uri"},
                        "ingredient": {"value": "http://example.com/ingredient2", "type": "uri"}
                    }
                ]
            }
        }

        # Mock the execute_local_query method to return our test data
        graph_service.sparql_service.execute_local_query = lambda query: mock_data

        result = graph_service.get_graph_data()

        assert result is not None
        assert len(result["nodes"]) == 4  # 2 cocktails + 2 ingredients
        assert "edges" in result
        assert len(result["edges"]) == 2

    def test_get_graph_data_empty(self, graph_service):
        # Mock the execute_local_query method to return empty data
        graph_service.sparql_service.execute_local_query = lambda query: {"results": {"bindings": []}}

        result = graph_service.get_graph_data()

        assert result is not None
        assert len(result["nodes"]) == 0
        assert "edges" in result
        assert len(result["edges"]) == 0

    def test_get_graph_data_error(self, graph_service):
        # Mock the query_local_data method to return None
        graph_service.sparql_service.query_local_data = lambda query: None

        result = graph_service.get_graph_data()

        assert result is None
