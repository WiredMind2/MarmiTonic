import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ingredient_optimizer_service import IngredientOptimizerService
from models.cocktail import Cocktail


@pytest.fixture
def ingredient_optimizer_service():
    with patch('services.ingredient_optimizer_service.CocktailService') as mock_cocktail_service, \
         patch('services.ingredient_optimizer_service.IngredientService') as mock_ingredient_service:
        
        mock_cocktail_service_instance = MagicMock()
        mock_ingredient_service_instance = MagicMock()
        
        mock_cocktail_service.return_value = mock_cocktail_service_instance
        mock_ingredient_service.return_value = mock_ingredient_service_instance
        
        service = IngredientOptimizerService()
        service.cocktail_service = mock_cocktail_service_instance
        service.ingredient_service = mock_ingredient_service_instance
        
        return service


@pytest.fixture
def mock_cocktails():
    """Fixture that returns mock cocktail data with parsed ingredients"""
    cocktail1 = Cocktail(
        uri="http://example.com/cocktail1",
        id="cocktail1",
        name="Cocktail 1",
        parsed_ingredients=["Gin", "Vermouth", "Bitters"]
    )
    
    cocktail2 = Cocktail(
        uri="http://example.com/cocktail2",
        id="cocktail2",
        name="Cocktail 2",
        parsed_ingredients=["Gin", "Vermouth", "Lemon"]
    )
    
    cocktail3 = Cocktail(
        uri="http://example.com/cocktail3",
        id="cocktail3",
        name="Cocktail 3",
        parsed_ingredients=["Vodka", "Orange Juice"]
    )
    
    return [cocktail1, cocktail2, cocktail3]


def test_ingredient_optimizer_initialization(ingredient_optimizer_service):
    """Test that the ingredient optimizer service initializes correctly"""
    assert hasattr(ingredient_optimizer_service, 'cocktail_service')
    assert hasattr(ingredient_optimizer_service, 'ingredient_service')


def test_find_optimal_ingredients_with_valid_n(ingredient_optimizer_service, mock_cocktails):
    """Test finding optimal ingredients with valid N value"""
    ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails
    
    result = ingredient_optimizer_service.find_optimal_ingredients(2)
    
    assert "ingredients" in result
    assert "cocktail_count" in result
    assert "cocktails" in result
    
    assert len(result["ingredients"]) == 2
    
    # Should select Vodka and Orange Juice, which allow us to make 1 cocktail (Cocktail 3)
    # This is better than Gin and Vermouth, which allow us to make 0 cocktails
    assert set(result["ingredients"]) == set(["Vodka", "Orange Juice"])
    assert result["cocktail_count"] == 1


def test_find_optimal_ingredients_with_n_3(ingredient_optimizer_service, mock_cocktails):
    """Test finding optimal ingredients with N=3"""
    ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails
    
    result = ingredient_optimizer_service.find_optimal_ingredients(3)
    
    assert len(result["ingredients"]) == 3
    
    # Should select Gin, Vermouth, and either Bitters or Lemon (or Vodka/Orange Juice)
    # Let's check if we can make at least 1 cocktail
    assert result["cocktail_count"] >= 1


def test_find_optimal_ingredients_with_no_cocktails(ingredient_optimizer_service):
    """Test finding optimal ingredients when there are no cocktails"""
    ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = []
    
    result = ingredient_optimizer_service.find_optimal_ingredients(2)
    
    assert len(result["ingredients"]) == 0
    assert result["cocktail_count"] == 0


def test_find_optimal_ingredients_with_n_0(ingredient_optimizer_service, mock_cocktails):
    """Test finding optimal ingredients when N=0"""
    ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails
    
    result = ingredient_optimizer_service.find_optimal_ingredients(0)
    
    assert len(result["ingredients"]) == 0
    assert result["cocktail_count"] == 0


def test_find_optimal_ingredients_with_cocktails_requiring_more_ingredients(ingredient_optimizer_service):
    """Test finding optimal ingredients when all cocktails require more than N ingredients"""
    cocktails = [
        Cocktail(
            uri="http://example.com/cocktail1",
            id="cocktail1",
            name="Cocktail 1",
            parsed_ingredients=["Gin", "Vermouth", "Bitters", "Lemon"]
        ),
        Cocktail(
            uri="http://example.com/cocktail2",
            id="cocktail2",
            name="Cocktail 2",
            parsed_ingredients=["Vodka", "Orange Juice", "Cranberry Juice"]
        )
    ]
    
    ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = cocktails
    
    result = ingredient_optimizer_service.find_optimal_ingredients(2)
    
    assert len(result["ingredients"]) == 0
    assert result["cocktail_count"] == 0
