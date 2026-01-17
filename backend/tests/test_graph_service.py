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

    def test_analyze_graph_success(self, graph_service):
        mock_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}],
            "edges": [{"source": "n1", "target": "n2"}]
        }

        result = graph_service.analyze_graph(mock_data)

        assert result is not None
        assert "node_count" in result
        assert "edge_count" in result

    def test_analyze_graph_empty(self, graph_service):
        result = graph_service.analyze_graph({"nodes": [], "edges": []})

        assert result is not None
        assert result["node_count"] == 0
        assert result["edge_count"] == 0

    def test_analyze_disjoint_components(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}],
            "edges": [{"source": "n1", "target": "n2"}]
        }

        result = graph_service.analyze_disjoint_components(graph_data)

        assert result is not None
        assert "components" in result
        assert "isolated_nodes" in result

    def test_analyze_disjoint_components_fully_connected(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"}
            ]
        }

        result = graph_service.analyze_disjoint_components(graph_data)

        assert result is not None
        assert result["isolated_nodes"] == 0

    def test_analyze_disjoint_components_all_isolated(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}],
            "edges": []
        }

        result = graph_service.analyze_disjoint_components(graph_data)

        assert result is not None
        assert result["isolated_nodes"] == 2

    def test_visualize_graph(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.visualize_graph(graph_data)

        assert result is not None
        assert "html" in result

    def test_visualize_graph_empty(self, graph_service):
        result = graph_service.visualize_graph({"nodes": [], "edges": []})

        assert result is not None
        assert "html" in result

    def test_export_graph(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.export_graph(graph_data, "json")

        assert result is not None

    def test_export_graph_invalid_format(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.export_graph(graph_data, "invalid")

        assert result is None

    def test_export_graph_xml(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.export_graph(graph_data, "xml")

        assert result is not None

    def test_export_graph_dot(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.export_graph(graph_data, "dot")

        assert result is not None

    def test_get_centrality_scores(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}],
            "edges": [{"source": "n1", "target": "n2"}]
        }

        result = graph_service.get_centrality_scores(graph_data)

        assert result is not None
        assert "n1" in result
        assert "n2" in result

    def test_get_centrality_scores_empty(self, graph_service):
        result = graph_service.get_centrality_scores({"nodes": [], "edges": []})

        assert result is not None
        assert len(result) == 0

    def test_get_community_detection(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"}
            ]
        }

        result = graph_service.get_community_detection(graph_data)

        assert result is not None
        assert "communities" in result

    def test_get_community_detection_empty(self, graph_service):
        result = graph_service.get_community_detection({"nodes": [], "edges": []})

        assert result is not None

    def test_get_shortest_path(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"}
            ]
        }

        result = graph_service.get_shortest_path(graph_data, "n1", "n3")

        assert result is not None
        assert "path" in result

    def test_get_shortest_path_no_path(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}],
            "edges": []
        }

        result = graph_service.get_shortest_path(graph_data, "n1", "n2")

        assert result is not None
        assert result["path"] is None

    def test_get_shortest_path_same_node(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.get_shortest_path(graph_data, "n1", "n1")

        assert result is not None
        assert result["path"] == ["n1"]

    def test_get_node_degree(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n1", "target": "n3"}
            ]
        }

        result = graph_service.get_node_degree(graph_data, "n1")

        assert result == 2

    def test_get_node_degree_isolated(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.get_node_degree(graph_data, "n1")

        assert result == 0

    def test_get_node_degree_nonexistent(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}],
            "edges": []
        }

        result = graph_service.get_node_degree(graph_data, "n2")

        assert result == 0

    def test_generate_force_directed_data(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}],
            "edges": [{"source": "n1", "target": "n2"}]
        }

        result = graph_service.generate_force_directed_data(graph_data)

        assert result is not None
        assert "nodes" in result
        assert "links" in result

    def test_generate_force_directed_data_empty(self, graph_service):
        result = graph_service.generate_force_directed_data({"nodes": [], "edges": []})

        assert result is not None
        assert result["nodes"] == []
        assert result["links"] == []

    def test_get_graph_statistics(self, graph_service):
        graph_data = {
            "nodes": [{"id": "n1"}, {"id": "n2"}],
            "edges": [{"source": "n1", "target": "n2"}]
        }

        result = graph_service.get_graph_statistics(graph_data)

        assert result is not None
        assert "node_count" in result
        assert "edge_count" in result
        assert "density" in result
        assert "avg_degree" in result

    def test_get_graph_statistics_empty(self, graph_service):
        result = graph_service.get_graph_statistics({"nodes": [], "edges": []})

        assert result is not None
        assert result["node_count"] == 0
        assert result["edge_count"] == 0
