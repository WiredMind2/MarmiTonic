"""
Comprehensive pytest tests for Pydantic models.
Tests Cocktail, Ingredient, and SparqlQuery models for data validation,
field constraints, and default values.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from models.cocktail import Cocktail
from models.ingredient import Ingredient
from models.sparql_query import SparqlQuery


class TestCocktailModel:
    """Tests for the Cocktail Pydantic model."""

    def test_valid_cocktail_creation(self):
        """Test creating a Cocktail with valid required fields."""
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Margarita",
            name="Margarita"
        )
        assert cocktail.id == "http://dbpedia.org/resource/Margarita"
        assert cocktail.name == "Margarita"
        assert cocktail.alternative_names is None
        assert cocktail.description is None

    def test_cocktail_with_all_fields(self):
        """Test creating a Cocktail with all optional fields populated."""
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Mojito",
            name="Mojito",
            alternative_names=["Cuba Libre"],
            description="A Cuban cocktail",
            image="http://example.com/mojito.jpg",
            ingredients="White rum, sugar, lime juice, soda water, mint",
            parsed_ingredients=["White rum", "Sugar", "Lime juice", "Soda water", "Mint"],
            ingredient_uris=["http://dbpedia.org/resource/Rum"],
            preparation="Mix all ingredients",
            served="In a highball glass",
            garnish="Mint sprig",
            source_link="http://example.com/mojito-recipe",
            categories=["Cocktail", "Rum cocktail"],
            related_ingredients=["Rum", "Mint"],
            labels={"en": "Mojito", "es": "Mojito"},
            descriptions={"en": "A refreshing Cuban cocktail"}
        )
        assert cocktail.id == "http://dbpedia.org/resource/Mojito"
        assert cocktail.name == "Mojito"
        assert len(cocktail.parsed_ingredients) == 5
        assert cocktail.labels["en"] == "Mojito"

    def test_cocktail_missing_required_id(self):
        """Test that Cocktail rejects data without required id field."""
        with pytest.raises(ValueError):
            Cocktail(name="Margarita")

    def test_cocktail_missing_required_name(self):
        """Test that Cocktail rejects data without required name field."""
        with pytest.raises(ValueError):
            Cocktail(id="http://dbpedia.org/resource/Margarita")

    def test_cocktail_empty_name_rejected(self):
        """Test that Cocktail rejects empty name string due to min_length constraint."""
        with pytest.raises(ValueError):
            Cocktail(
                id="http://dbpedia.org/resource/Margarita",
                name=""
            )

    def test_cocktail_whitespace_only_name_accepted(self):
        """Test that Cocktail accepts whitespace-only name string (Pydantic min_length allows whitespace)."""
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Margarita",
            name="   "
        )
        assert cocktail.name == "   "

    def test_cocktail_invalid_type_for_id(self):
        """Test that Cocktail rejects non-string type for id field."""
        with pytest.raises(ValueError):
            Cocktail(
                id=123,  # type: ignore
                name="Margarita"
            )

    def test_cocktail_invalid_type_for_name(self):
        """Test that Cocktail rejects non-string type for name field."""
        with pytest.raises(ValueError):
            Cocktail(
                id="http://dbpedia.org/resource/Margarita",
                name=["Margarita"]  # type: ignore
            )

    def test_cocktail_invalid_type_for_parsed_ingredients(self):
        """Test that Cocktail rejects non-list type for parsed_ingredients field."""
        with pytest.raises(ValueError):
            Cocktail(
                id="http://dbpedia.org/resource/Margarita",
                name="Margarita",
                parsed_ingredients="rum, lime"  # type: ignore
            )

    def test_cocktail_invalid_type_for_ingredient_uris(self):
        """Test that Cocktail rejects non-list type for ingredient_uris field."""
        with pytest.raises(ValueError):
            Cocktail(
                id="http://dbpedia.org/resource/Margarita",
                name="Margarita",
                ingredient_uris="http://example.com"  # type: ignore
            )

    def test_cocktail_invalid_type_for_categories(self):
        """Test that Cocktail rejects non-list type for categories field."""
        with pytest.raises(ValueError):
            Cocktail(
                id="http://dbpedia.org/resource/Margarita",
                name="Margarita",
                categories="Cocktail"  # type: ignore
            )

    def test_cocktail_invalid_type_for_labels(self):
        """Test that Cocktail rejects non-dict type for labels field."""
        with pytest.raises(ValueError):
            Cocktail(
                id="http://dbpedia.org/resource/Margarita",
                name="Margarita",
                labels=["en", "Margarita"]  # type: ignore
            )

    def test_cocktail_invalid_uri_format(self):
        """Test that Cocktail accepts URIs (no validation, but should accept string)."""
        # Pydantic doesn't validate URI format by default, but string should be accepted
        cocktail = Cocktail(
            id="not-a-valid-uri",
            name="Test Cocktail"
        )
        assert cocktail.id == "not-a-valid-uri"

    def test_cocktail_default_values(self):
        """Test that optional fields have correct default values."""
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Margarita",
            name="Margarita"
        )
        assert cocktail.alternative_names is None
        assert cocktail.description is None
        assert cocktail.image is None
        assert cocktail.ingredients is None
        assert cocktail.parsed_ingredients is None
        assert cocktail.ingredient_uris is None
        assert cocktail.preparation is None
        assert cocktail.served is None
        assert cocktail.garnish is None
        assert cocktail.source_link is None
        assert cocktail.categories is None
        assert cocktail.related_ingredients is None
        assert cocktail.labels is None
        assert cocktail.descriptions is None


class TestIngredientModel:
    """Tests for the Ingredient Pydantic model."""

    def test_valid_ingredient_creation(self):
        """Test creating an Ingredient with valid required fields."""
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Rum",
            name="Rum"
        )
        assert ingredient.id == "http://dbpedia.org/resource/Rum"
        assert ingredient.name == "Rum"
        assert ingredient.alternative_names is None
        assert ingredient.description is None

    def test_ingredient_with_all_fields(self):
        """Test creating an Ingredient with all optional fields populated."""
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Gin",
            name="Gin",
            alternative_names=["Genever", "Juniper spirit"],
            description="A distilled alcoholic spirit flavoured with juniper berries",
            image="http://example.com/gin.jpg",
            categories=["Spirits", "Distilled beverages"],
            related_concepts=["Juniper", "Botanicals"],
            labels={"en": "Gin", "de": "Gin", "fr": "Gin"},
            descriptions={"en": "A distilled alcoholic spirit"}
        )
        assert ingredient.id == "http://dbpedia.org/resource/Gin"
        assert ingredient.name == "Gin"
        assert len(ingredient.categories) == 2
        assert ingredient.related_concepts == ["Juniper", "Botanicals"]

    def test_ingredient_missing_required_id(self):
        """Test that Ingredient rejects data without required id field."""
        with pytest.raises(ValueError):
            Ingredient(name="Rum")

    def test_ingredient_missing_required_name(self):
        """Test that Ingredient rejects data without required name field."""
        with pytest.raises(ValueError):
            Ingredient(id="http://dbpedia.org/resource/Rum")

    def test_ingredient_empty_name_rejected(self):
        """Test that Ingredient rejects empty name string due to min_length constraint."""
        with pytest.raises(ValueError):
            Ingredient(
                id="http://dbpedia.org/resource/Rum",
                name=""
            )

    def test_ingredient_whitespace_only_name_accepted(self):
        """Test that Ingredient accepts whitespace-only name string (Pydantic min_length allows whitespace)."""
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Rum",
            name="   "
        )
        assert ingredient.name == "   "

    def test_ingredient_invalid_type_for_id(self):
        """Test that Ingredient rejects non-string type for id field."""
        with pytest.raises(ValueError):
            Ingredient(
                id=["http://dbpedia.org/resource/Rum"],  # type: ignore
                name="Rum"
            )

    def test_ingredient_invalid_type_for_name(self):
        """Test that Ingredient rejects non-string type for name field."""
        with pytest.raises(ValueError):
            Ingredient(
                id="http://dbpedia.org/resource/Rum",
                name=123  # type: ignore
            )

    def test_ingredient_invalid_type_for_alternative_names(self):
        """Test that Ingredient rejects non-list type for alternative_names field."""
        with pytest.raises(ValueError):
            Ingredient(
                id="http://dbpedia.org/resource/Rum",
                name="Rum",
                alternative_names="Genever"  # type: ignore
            )

    def test_ingredient_invalid_type_for_categories(self):
        """Test that Ingredient rejects non-list type for categories field."""
        with pytest.raises(ValueError):
            Ingredient(
                id="http://dbpedia.org/resource/Rum",
                name="Rum",
                categories="Spirits"  # type: ignore
            )

    def test_ingredient_invalid_type_for_related_concepts(self):
        """Test that Ingredient rejects non-list type for related_concepts field."""
        with pytest.raises(ValueError):
            Ingredient(
                id="http://dbpedia.org/resource/Rum",
                name="Rum",
                related_concepts={"0": "Juniper"}  # type: ignore
            )

    def test_ingredient_invalid_type_for_labels(self):
        """Test that Ingredient rejects non-dict type for labels field."""
        with pytest.raises(ValueError):
            Ingredient(
                id="http://dbpedia.org/resource/Rum",
                name="Rum",
                labels=["en", "Rum"]  # type: ignore
            )

    def test_ingredient_default_values(self):
        """Test that optional fields have correct default values."""
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Rum",
            name="Rum"
        )
        assert ingredient.alternative_names is None
        assert ingredient.description is None
        assert ingredient.image is None
        assert ingredient.categories is None
        assert ingredient.related_concepts is None
        assert ingredient.labels is None
        assert ingredient.descriptions is None


class TestSparqlQueryModel:
    """Tests for the SparqlQuery Pydantic model."""

    def test_valid_sparql_query_creation(self):
        """Test creating a SparqlQuery with valid query string."""
        query = SparqlQuery(
            query="SELECT * WHERE { ?s ?p ?o } LIMIT 10"
        )
        assert query.query == "SELECT * WHERE { ?s ?p ?o } LIMIT 10"

    def test_sparql_query_with_complex_query(self):
        """Test creating a SparqlQuery with a complex SPARQL query."""
        complex_query = """
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        
        SELECT ?cocktail ?name WHERE {
            ?cocktail a dbo:Cocktail .
            ?cocktail dbo:name ?name .
            FILTER(LANG(?name) = 'en')
        }
        LIMIT 50
        """
        sparql_query = SparqlQuery(query=complex_query)
        assert sparql_query.query == complex_query

    def test_sparql_query_empty_string_accepted(self):
        """Test that SparqlQuery accepts empty string (no min_length constraint)."""
        sparql_query = SparqlQuery(query="")
        assert sparql_query.query == ""

    def test_sparql_query_missing_required_query(self):
        """Test that SparqlQuery rejects data without required query field."""
        with pytest.raises(ValueError):
            SparqlQuery()

    def test_sparql_query_invalid_type(self):
        """Test that SparqlQuery rejects non-string type for query field."""
        with pytest.raises(ValueError):
            SparqlQuery(query=["SELECT * WHERE { ?s ?p ?o }"])  # type: ignore

    def test_sparql_query_with_none_value(self):
        """Test that SparqlQuery rejects None for query field."""
        with pytest.raises(ValueError):
            SparqlQuery(query=None)  # type: ignore

    def test_sparql_query_unicode_content(self):
        """Test that SparqlQuery accepts unicode characters in query."""
        unicode_query = "SELECT ?nom WHERE { ?sujet ?propriété ?nom }"
        sparql_query = SparqlQuery(query=unicode_query)
        assert sparql_query.query == unicode_query


class TestModelJsonSerialization:
    """Tests for JSON serialization of models."""

    def test_cocktail_json_serialization(self):
        """Test that Cocktail can be serialized to JSON."""
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Margarita",
            name="Margarita"
        )
        json_str = cocktail.json()
        assert "Margarita" in json_str
        assert "http://dbpedia.org/resource/Margarita" in json_str

    def test_ingredient_json_serialization(self):
        """Test that Ingredient can be serialized to JSON."""
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Rum",
            name="Rum"
        )
        json_str = ingredient.json()
        assert "Rum" in json_str
        assert "http://dbpedia.org/resource/Rum" in json_str

    def test_sparql_query_json_serialization(self):
        """Test that SparqlQuery can be serialized to JSON."""
        sparql_query = SparqlQuery(
            query="SELECT * WHERE { ?s ?p ?o }"
        )
        json_str = sparql_query.json()
        assert "SELECT * WHERE { ?s ?p ?o }" in json_str


class TestModelEquality:
    """Tests for model equality comparison."""

    def test_cocktail_equality(self):
        """Test that two Cocktail instances with same data are equal."""
        cocktail1 = Cocktail(
            id="http://dbpedia.org/resource/Margarita",
            name="Margarita"
        )
        cocktail2 = Cocktail(
            id="http://dbpedia.org/resource/Margarita",
            name="Margarita"
        )
        assert cocktail1 == cocktail2

    def test_ingredient_equality(self):
        """Test that two Ingredient instances with same data are equal."""
        ingredient1 = Ingredient(
            id="http://dbpedia.org/resource/Rum",
            name="Rum"
        )
        ingredient2 = Ingredient(
            id="http://dbpedia.org/resource/Rum",
            name="Rum"
        )
        assert ingredient1 == ingredient2

    def test_sparql_query_equality(self):
        """Test that two SparqlQuery instances with same data are equal."""
        query1 = SparqlQuery(query="SELECT * WHERE { ?s ?p ?o }")
        query2 = SparqlQuery(query="SELECT * WHERE { ?s ?p ?o }")
        assert query1 == query2


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_cocktail_very_long_name(self):
        """Test that Cocktail accepts very long name strings."""
        long_name = "A" * 10000
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Test",
            name=long_name
        )
        assert len(cocktail.name) == 10000

    def test_ingredient_very_long_name(self):
        """Test that Ingredient accepts very long name strings."""
        long_name = "B" * 10000
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Test",
            name=long_name
        )
        assert len(ingredient.name) == 10000

    def test_cocktail_special_characters_in_name(self):
        """Test that Cocktail accepts special characters in name."""
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Test",
            name="Café-Ümläut's Drink #1!"
        )
        assert cocktail.name == "Café-Ümläut's Drink #1!"

    def test_ingredient_special_characters_in_name(self):
        """Test that Ingredient accepts special characters in name."""
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Test",
            name="Sucre de canne"
        )
        assert ingredient.name == "Sucre de canne"

    def test_cocktail_nested_list_in_labels(self):
        """Test Cocktail with complex nested structure in labels."""
        cocktail = Cocktail(
            id="http://dbpedia.org/resource/Test",
            name="Test",
            labels={"en": "Test", "fr": "Test FR", "es": "Test ES"}
        )
        assert len(cocktail.labels) == 3

    def test_ingredient_empty_lists(self):
        """Test Ingredient with empty lists for optional list fields."""
        ingredient = Ingredient(
            id="http://dbpedia.org/resource/Test",
            name="Test",
            alternative_names=[],
            categories=[]
        )
        assert ingredient.alternative_names == []
        assert ingredient.categories == []
