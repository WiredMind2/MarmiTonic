import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.cocktail_service import CocktailService
from models.cocktail import Cocktail
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDFS, RDF
import rdflib


@pytest.fixture
def mock_sparql_service():
    mock = Mock()
    mock.local_graph_path = "data/data.ttl"
    return mock


@pytest.fixture
def mock_ingredient_service():
    return Mock()


@pytest.fixture
def cocktail_service(mock_sparql_service, mock_ingredient_service):
    with patch('services.cocktail_service.SparqlService', return_value=mock_sparql_service), \
         patch('services.cocktail_service.IngredientService', return_value=mock_ingredient_service):
        service = CocktailService()
        return service


class TestCocktailService:

    def test_init(self, mock_sparql_service, mock_ingredient_service):
        with patch('services.cocktail_service.SparqlService', return_value=mock_sparql_service), \
             patch('services.cocktail_service.IngredientService', return_value=mock_ingredient_service):
            service = CocktailService()
            assert service.sparql_service == mock_sparql_service
            assert service.ingredient_service == mock_ingredient_service
            assert service.graph is not None  # Assuming _load_local_data sets it

    def test_load_local_data_success(self, cocktail_service, mock_sparql_service):
        cocktail_service._load_local_data()
        assert cocktail_service.graph == mock_sparql_service.local_graph

    def test_load_local_data_failure(self, cocktail_service, mock_sparql_service):
        mock_sparql_service.local_graph = None
        cocktail_service._load_local_data()
        assert cocktail_service.graph is None

    def test_parse_cocktail_from_graph(self, cocktail_service):
        mock_graph = Mock()
        cocktail_service.graph = mock_graph
        cocktail_uri = URIRef("http://example.com/cocktail")

        # Mock the _get_property calls
        cocktail_service._get_property = Mock(side_effect=[
            "Mojito",  # name
            None,  # image
            "Ingredients text",  # ingredients
            "Preparation text",  # preparation
            "Served text",  # served
            "Garnish text",  # garnish
            "Source link"  # source_link
        ])

        # Mock objects for labels, descriptions, categories, related, alt_names
        mock_graph.objects.side_effect = [
            [Literal("Mojito", lang="en")],  # labels
            [Literal("A refreshing cocktail", lang="en")],  # descriptions
            [URIRef("http://example.com/category")],  # categories
            [URIRef("http://example.com/ingredient")],  # related
            [Literal("Alternative Name")]  # alt_names
        ]

        cocktail = cocktail_service._parse_cocktail_from_graph(cocktail_uri)

        assert isinstance(cocktail, Cocktail)
        assert cocktail.name == "Mojito"
        assert cocktail.labels == {"en": "Mojito"}
        assert cocktail.descriptions == {"en": "A refreshing cocktail"}
        assert cocktail.categories == ["http://example.com/category"]
        assert cocktail.related_ingredients == ["http://example.com/ingredient"]
        assert cocktail.alternative_names == ["Alternative Name"]

    def test_parse_cocktail_from_graph_no_graph(self, cocktail_service):
        cocktail_service.graph = None
        assert cocktail_service._parse_cocktail_from_graph(URIRef("http://example.com")) is None

    def test_get_property(self, cocktail_service):
        mock_graph = Mock()
        cocktail_service.graph = mock_graph
        subject = URIRef("http://example.com")
        predicate = RDFS.label

        # Mock objects returning literals
        mock_graph.objects.return_value = [Literal("Value", lang="en"), Literal("Value2", lang="fr")]

        result = cocktail_service._get_property(subject, predicate, "en")
        assert result == "Value"

        # No lang filter
        result = cocktail_service._get_property(subject, predicate)
        assert result == "Value, Value2"

        # No graph
        cocktail_service.graph = None
        assert cocktail_service._get_property(subject, predicate) is None

    def test_get_all_cocktails(self, cocktail_service, mock_sparql_service):
        mock_results = {
            "results": {
                "bindings": [
                    {
                        "cocktail": {"value": "http://example.com/cocktail1"},
                        "name": {"value": "Cocktail1"},
                        "desc": {"value": "Description1"},
                        "ingredients": {"value": "* 45 ml Rum\n* 20 ml Lime"},
                        "prep": {"value": "Mix and serve"},
                        "served": {"value": "On the rocks"},
                        "garnish": {"value": "Lime wedge"},
                        "source": {"value": "http://source.com"}
                    }
                ]
            }
        }
        mock_sparql_service.execute_local_query.return_value = mock_results

        # Mock _parse_ingredient_names and _extract_ingredient_uris
        cocktail_service._parse_ingredient_names = Mock(return_value=["Rum", "Lime"])
        cocktail_service._extract_ingredient_uris = Mock(return_value=["http://example.com/rum"])

        cocktails = cocktail_service.get_all_cocktails()

        assert len(cocktails) == 1
        assert cocktails[0].name == "Cocktail1"
        assert cocktails[0].parsed_ingredients == ["Rum", "Lime"]
        assert cocktails[0].ingredient_uris == ["http://example.com/rum"]

    def test_get_all_cocktails_sparql_error(self, cocktail_service, mock_sparql_service):
        mock_sparql_service.execute_local_query.side_effect = Exception("Query failed")
        cocktail_service.graph.subjects.return_value = []
        cocktails = cocktail_service.get_all_cocktails()
        assert cocktails == []

    def test_search_cocktails(self, cocktail_service):
        mock_cocktail1 = Mock()
        mock_cocktail1.name = "Mojito"
        mock_cocktail1.alternative_names = ["Mint Julep"]

        mock_cocktail2 = Mock()
        mock_cocktail2.name = "Martini"
        mock_cocktail2.alternative_names = None

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_cocktail1, mock_cocktail2])

        # Search for "moj"
        results = cocktail_service.search_cocktails("moj")
        assert len(results) == 1
        assert results[0] == mock_cocktail1

        # Search for "mint"
        results = cocktail_service.search_cocktails("mint")
        assert len(results) == 1

        # Empty query
        results = cocktail_service.search_cocktails("")
        assert len(results) == 2

    def test_get_feasible_cocktails(self, cocktail_service, mock_ingredient_service):
        mock_cocktail1 = Mock()
        mock_cocktail1.ingredients = "* Rum\n* Lime"

        mock_cocktail2 = Mock()
        mock_cocktail2.ingredients = "* Vodka\n* Orange"

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_cocktail1, mock_cocktail2])
        mock_ingredient_service.get_inventory.return_value = ["Rum", "Lime", "Vodka"]

        cocktail_service._parse_ingredient_names = Mock(side_effect=[["Rum", "Lime"], ["Vodka", "Orange"]])

        feasible = cocktail_service.get_feasible_cocktails("user1")
        assert len(feasible) == 1
        assert feasible[0] == mock_cocktail1

    def test_get_feasible_cocktails_empty_inventory(self, cocktail_service, mock_ingredient_service):
        mock_cocktail = Mock()
        mock_cocktail.ingredients = "* Rum"

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        mock_ingredient_service.get_inventory.return_value = []

        cocktail_service._parse_ingredient_names = Mock(return_value=["Rum"])

        feasible = cocktail_service.get_feasible_cocktails("user1")
        assert len(feasible) == 0

    def test_get_almost_feasible_cocktails(self, cocktail_service, mock_ingredient_service):
        mock_cocktail1 = Mock()
        mock_cocktail1.ingredients = "* Rum\n* Lime\n* Mint"

        mock_cocktail2 = Mock()
        mock_cocktail2.ingredients = "* Vodka\n* Orange\n* Cranberry\n* Lime"

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_cocktail1, mock_cocktail2])
        mock_ingredient_service.get_inventory.return_value = ["Rum", "Lime", "Vodka", "Orange"]

        cocktail_service._parse_ingredient_names = Mock(side_effect=[["Rum", "Lime", "Mint"], ["Vodka", "Orange", "Cranberry", "Lime"]])

        almost_feasible = cocktail_service.get_almost_feasible_cocktails("user1")
        assert len(almost_feasible) == 2
        assert almost_feasible[0]["cocktail"] == mock_cocktail1
        assert almost_feasible[0]["missing"] == ["Mint"]
        assert almost_feasible[1]["cocktail"] == mock_cocktail2
        assert almost_feasible[1]["missing"] == ["Cranberry"]

    def test_parse_ingredient_names(self, cocktail_service):
        ingredients_text = "* 45 ml White Rum\n* 20 ml Fresh Lime Juice\n• 15 ml Sugar Syrup"
        result = cocktail_service._parse_ingredient_names(ingredients_text)
        assert result == ["White Rum", "Fresh Lime Juice", "Sugar Syrup"]

        # Empty
        assert cocktail_service._parse_ingredient_names("") == []

        # None
        assert cocktail_service._parse_ingredient_names(None) == []

        # No bullets
        assert cocktail_service._parse_ingredient_names("Just text") == []

    def test_extract_ingredient_uris(self, cocktail_service):
        mock_graph = Mock()
        cocktail_service.graph = mock_graph
        cocktail_uri = "http://example.com/cocktail"

        mock_graph.objects.return_value = [URIRef("http://example.com/ing1"), URIRef("http://example.com/ing2")]

        uris = cocktail_service._extract_ingredient_uris(cocktail_uri)
        assert uris == ["http://example.com/ing1", "http://example.com/ing2"]

        # No graph
        cocktail_service.graph = None
        assert cocktail_service._extract_ingredient_uris(cocktail_uri) == []

    def test_get_cocktails_by_ingredients(self, cocktail_service):
        mock_cocktail1 = Mock()
        mock_cocktail1.ingredients = "* Rum\n* Lime"

        mock_cocktail2 = Mock()
        mock_cocktail2.ingredients = "* Vodka\n* Orange"

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_cocktail1, mock_cocktail2])
        cocktail_service._parse_ingredient_names = Mock(side_effect=lambda x: ["Rum", "Lime"] if "Rum" in x else ["Vodka", "Orange"])

        results = cocktail_service.get_cocktails_by_ingredients(["Rum"])
        assert len(results) == 1
        assert results[0] == mock_cocktail1

        # Multiple ingredients
        results = cocktail_service.get_cocktails_by_ingredients(["Rum", "Lime"])
        assert len(results) == 1

        # No match
        results = cocktail_service.get_cocktails_by_ingredients(["Gin"])
        assert len(results) == 0

    def test_get_cocktails_by_uris(self, cocktail_service):
        mock_cocktail1 = Mock()
        mock_cocktail1.ingredient_uris = ["http://example.com/rum", "http://example.com/lime"]

        mock_cocktail2 = Mock()
        mock_cocktail2.ingredient_uris = ["http://example.com/vodka"]

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_cocktail1, mock_cocktail2])

        results = cocktail_service.get_cocktails_by_uris(["http://example.com/rum"])
        assert len(results) == 1
        assert results[0] == mock_cocktail1

        # No match
        results = cocktail_service.get_cocktails_by_uris(["http://example.com/gin"])
        assert len(results) == 0

    def test_get_similar_cocktails(self, cocktail_service):
        mock_target = Mock()
        mock_target.id = "target_id"
        mock_target.parsed_ingredients = ["Rum", "Lime", "Mint"]

        mock_similar = Mock()
        mock_similar.id = "similar_id"
        mock_similar.parsed_ingredients = ["Rum", "Lime", "Sugar"]

        mock_different = Mock()
        mock_different.id = "different_id"
        mock_different.parsed_ingredients = ["Vodka", "Orange"]

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_target, mock_similar, mock_different])

        results = cocktail_service.get_similar_cocktails("target_id", limit=5)
        assert len(results) == 2
        assert results[0]["cocktail"] == mock_similar
        assert results[0]["similarity_score"] == 2/4  # intersection 2, union 4
        assert results[1]["cocktail"] == mock_different
        assert results[1]["similarity_score"] == 0.0

        # No target
        results = cocktail_service.get_similar_cocktails("nonexistent")
        assert results == []

        # No parsed ingredients
        mock_target.parsed_ingredients = None
        results = cocktail_service.get_similar_cocktails("target_id")
        assert results == []

    def test_get_same_vibe_cocktails(self, cocktail_service):
        mock_target = Mock()
        mock_target.id = "target_id"
        mock_target.name = "Mojito"

        mock_same_vibe = Mock()
        mock_same_vibe.id = "same_id"
        mock_same_vibe.name = "Caipirinha"

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_target, mock_same_vibe])

        with patch('services.cocktail_service.GraphService') as mock_graph_service_class:
            mock_graph_service = Mock()
            mock_graph_service_class.return_value = mock_graph_service
            mock_graph_service.analyze_graph.return_value = {
                "communities": {
                    "Mojito": 1,
                    "Caipirinha": 1,
                    "Martini": 2
                }
            }

            results = cocktail_service.get_same_vibe_cocktails("target_id", limit=5)
            assert len(results) == 1
            assert results[0] == mock_same_vibe

    def test_get_same_vibe_cocktails_no_target(self, cocktail_service):
        cocktail_service.get_all_cocktails = Mock(return_value=[])
        results = cocktail_service.get_same_vibe_cocktails("nonexistent")
        assert results == []

    def test_get_bridge_cocktails(self, cocktail_service):
        mock_bridge = Mock()
        mock_bridge.parsed_ingredients = ["Rum", "Lime", "Vodka"]  # Spans communities

        mock_non_bridge = Mock()
        mock_non_bridge.parsed_ingredients = ["Rum", "Lime"]  # Same community

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_bridge, mock_non_bridge])

        with patch('services.cocktail_service.GraphService') as mock_graph_service_class:
            mock_graph_service = Mock()
            mock_graph_service_class.return_value = mock_graph_service
            mock_graph_service.analyze_graph.return_value = {
                "communities": {
                    "Rum": 1,
                    "Lime": 1,
                    "Vodka": 2
                }
            }

            results = cocktail_service.get_bridge_cocktails(limit=5)
            assert len(results) == 1
            assert results[0] == mock_bridge

    def test_get_bridge_cocktails_no_parsed_ingredients(self, cocktail_service):
        mock_cocktail = Mock()
        mock_cocktail.parsed_ingredients = None

        cocktail_service.get_all_cocktails = Mock(return_value=[mock_cocktail])

        with patch('services.cocktail_service.GraphService') as mock_graph_service_class:
            mock_graph_service = Mock()
            mock_graph_service_class.return_value = mock_graph_service
            mock_graph_service.analyze_graph.return_value = {"communities": {}}

            results = cocktail_service.get_bridge_cocktails()
            assert results == []
