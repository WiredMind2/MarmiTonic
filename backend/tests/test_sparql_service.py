import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
from rdflib import URIRef

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.sparql_service import SparqlService


@pytest.fixture
def sparql_service():
    # Pass None to avoid loading the real graph during initialization for most tests
    service = SparqlService()
    return service


class TestSparqlService:

    def test_init(self, sparql_service):
        assert sparql_service.local_graph is not None
        assert hasattr(sparql_service, 'parser')

    def test_execute_query_redirects_to_local(self, sparql_service):
        # Test that execute_query redirects to execute_local_query
        query = 'SELECT ?s WHERE { ?s ?p ?o } LIMIT 1'
        result = sparql_service.execute_query(query)
        # Should return same as execute_local_query (list format)
        assert result is not None
        assert isinstance(result, list)

    def test_execute_query_invalid_syntax(self, sparql_service):
        # Test with invalid SPARQL syntax
        query = 'INVALID QUERY SYNTAX'
        result = sparql_service.execute_query(query)
        # Should handle error gracefully
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
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['test']['value'] == 'local_value'

    def test_execute_local_query_error(self, sparql_service):
        mock_graph = Mock()
        sparql_service.local_graph = mock_graph
        mock_graph.query.side_effect = Exception('Query error')

        result = sparql_service.execute_local_query('INVALID QUERY')
        assert result is None
