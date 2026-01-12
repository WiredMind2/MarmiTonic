import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Try to import from backend.main if running from root
try:
    from backend.main import app
    from backend.models.cocktail import Cocktail
    from backend.models.ingredient import Ingredient
except ImportError:
    # Fallback for other environments
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from main import app
    from models.cocktail import Cocktail
    from models.ingredient import Ingredient

@pytest.fixture
def client():
    return TestClient(app)

class TestGraphApi:
    
    @patch('backend.routes.graphs.GraphService')
    def test_get_basic_graph_with_links(self, mock_service_class, client):
        """Test that the basic graph API returns nodes and links"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Mock data from service
        mock_graph_data = {
            'nodes': [
                {'id': 'cocktail1', 'name': 'Martini', 'type': 'cocktail'},
                {'id': 'ing1', 'name': 'Gin', 'type': 'ingredient'}
            ],
            'edges': [
                {'source': 'cocktail1', 'target': 'ing1', 'type': 'cocktail_ingredient'}
            ]
        }
        mock_service.build_graph.return_value = mock_graph_data
        
        response = client.get("/graphs/basic")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify nodes
        assert 'nodes' in data
        assert len(data['nodes']) == 2
        assert data['nodes'][0]['id'] == 'cocktail1'
        
        # Verify links (mapping from edges)
        assert 'links' in data
        assert len(data['links']) == 1
        assert data['links'][0]['source'] == 'cocktail1'
        assert data['links'][0]['target'] == 'ing1'
        assert data['links'][0]['value'] == 1

    @patch('backend.routes.graphs.GraphService')
    def test_get_force_directed_graph_with_links(self, mock_service_class, client):
        """Test that the force-directed graph API returns nodes and links"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Mock build_graph data
        mock_graph_data = {
            'nodes': [{'id': 'A', 'name': 'A', 'type': 'test'}],
            'edges': []
        }
        mock_service.build_graph.return_value = mock_graph_data
        
        # Mock generate_force_directed_data
        mock_force_data = {
            'nodes': [{'id': 'node1', 'name': 'Node 1'}],
            'links': [{'source': 'node1', 'target': 'node2', 'value': 2}]
        }
        mock_service.generate_force_directed_data.return_value = mock_force_data
        
        response = client.get("/graphs/force-directed")
        
        assert response.status_code == 200
        data = response.json()
        assert 'nodes' in data
        assert 'links' in data
        assert len(data['links']) == 1
        assert data['links'][0]['value'] == 2

    @patch('backend.routes.graphs.GraphService')
    def test_sparql_graph_with_links(self, mock_service_class, client):
        """Test that the SPARQL graph API returns nodes and links"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Mock data from service
        mock_graph_data = {
            'nodes': [
                {'id': 'uri1', 'name': 'n1', 'type': 'resource'},
                {'id': 'uri2', 'name': 'n2', 'type': 'resource'}
            ],
            'edges': [
                {'source': 'uri1', 'target': 'uri2'}
            ]
        }
        mock_service.get_graph_data.return_value = mock_graph_data
        
        response = client.post("/graphs/sparql", json={"query": "SELECT * WHERE { ?s ?p ?o }"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'nodes' in data
        assert 'links' in data
        assert len(data['links']) == 1
        assert data['links'][0]['source'] == 'uri1'
        assert data['links'][0]['target'] == 'uri2'
