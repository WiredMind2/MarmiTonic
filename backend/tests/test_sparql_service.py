import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
from rdflib import URIRef

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.sparql_service import SparqlService


@pytest.fixture
def sparql_service():
    # Pass None to avoid loading the real graph during initialization for most tests
    service = SparqlService()
    return service


class TestSparqlService:

    def test_init(self, sparql_service):
        assert sparql_service.endpoint == 'https://dbpedia.org/sparql'
        assert sparql_service.local_graph_path == 'data/data.ttl'
        assert sparql_service.local_endpoint == 'http://localhost:3030/marmitonic'

    def test_execute_query_success(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': {'bindings': [{'test': {'value': 'test_value'}}]}}

        with patch('services.sparql_service.requests.get', return_value=mock_response) as mock_get:
            result = sparql_service.execute_query('SELECT * WHERE { ?s ?p ?o }')

            mock_get.assert_called_once()
            # assert 'SELECT' in mock_get.call_args[0][0]
            assert result['results']['bindings'][0]['test']['value'] == 'test_value'

    def test_execute_query_http_error(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception('HTTP 500 Error')

        with patch('services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.execute_query('SELECT * WHERE { ?s ?p ?o }')

            assert result is None

    def test_execute_query_timeout(self, sparql_service):
        import requests
        with patch('services.sparql_service.requests.get', side_effect=requests.Timeout()):
            result = sparql_service.execute_query('SELECT * WHERE { ?s ?p ?o }')
            assert result is None

    def test_execute_local_query_success(self, sparql_service):
        mock_graph = Mock()
        sparql_service.local_graph = mock_graph
        
        # Mock result from graph.query
        # rdflib.query.Result row is iterable
        mock_result = Mock()
        mock_result.vars = ['test']
        mock_result.__iter__ = Mock(return_value=iter([['local_value']]))
        mock_graph.query.return_value = mock_result

        result = sparql_service.execute_local_query('SELECT * WHERE { ?s ?p ?o }')

        assert result is not None
        assert result['results']['bindings'][0]['test']['value'] == 'local_value'

    def test_execute_local_query_error(self, sparql_service):
        mock_graph = Mock()
        sparql_service.local_graph = mock_graph
        mock_graph.query.side_effect = Exception('Query error')

        result = sparql_service.execute_local_query('INVALID QUERY')
        assert result is None

    def test_query_local_data_cocktails(self, sparql_service):
        mock_graph = Mock()
        sparql_service.local_graph = mock_graph
        
        mock_result = Mock()
        mock_result.vars = ['cocktail']
        mock_result.__iter__ = Mock(return_value=iter([[URIRef('http://example.com/c1')]]))
        mock_graph.query.return_value = mock_result

        result = sparql_service.query_local_data('cocktails')

        assert result is not None
        assert 'c1' in str(result)
        mock_graph.query.assert_called()

    def test_query_local_data_with_params(self, sparql_service):
        mock_graph = Mock()
        sparql_service.local_graph = mock_graph
        
        mock_result = Mock()
        mock_result.vars = ['property', 'value']
        mock_result.__iter__ = Mock(return_value=iter([[URIRef('http://purl.org/dc/terms/title'), 'Test']]))
        mock_graph.query.return_value = mock_result

        result = sparql_service.query_local_data('cocktail', uri='http://example.com/c1')

        assert result is not None
        assert 'results' in result

    def test_get_all_cocktails_from_dbpedia(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {'cocktail': {'value': 'http://dbpedia.org/resource/Mojito'}},
                    {'cocktail': {'value': 'http://dbpedia.org/resource/Martini'}}
                ]
            }
        }

        with patch('services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.get_all_cocktails_from_dbpedia()

            assert len(result) == 2
            assert 'Mojito' in str(result)
            assert 'Martini' in str(result)

    def test_get_all_cocktails_from_dbpedia_empty(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': {'bindings': []}}

        with patch('services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.get_all_cocktails_from_dbpedia()
            assert result == []

    def test_get_all_cocktails_from_dbpedia_error(self, sparql_service):
        import requests
        with patch('services.sparql_service.requests.get', side_effect=requests.ConnectionError()):
            result = sparql_service.get_all_cocktails_from_dbpedia()
            assert result is None
