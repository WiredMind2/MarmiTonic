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
    from backend.main import app
    from backend.models.cocktail import Cocktail
    from backend.models.ingredient import Ingredient

@pytest.fixture
def client():
    return TestClient(app)

class TestGraphApi:
    
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
