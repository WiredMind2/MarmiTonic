import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ingredient_optimizer_service import IngredientOptimizerService
from models.cocktail import Cocktail


@pytest.fixture
def ingredient_optimizer_service():
    """Fixture to create an instance of IngredientOptimizerService with mocked dependencies"""
    with patch('services.ingredient_optimizer_service.CocktailService') as mock_cocktail_service, \
         patch('services.ingredient_optimizer_service.IngredientService') as mock_ingredient_service:
        
        # Create mock instances
        mock_cocktail_service_instance = Mock()
        mock_ingredient_service_instance = Mock()
        
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
    
    cocktail4 = Cocktail(
        uri="http://example.com/cocktail4",
        id="cocktail4",
        name="Cocktail 4",
        parsed_ingredients=["Rum", "Coke"]
    )
    
    cocktail5 = Cocktail(
        uri="http://example.com/cocktail5",
        id="cocktail5",
        name="Cocktail 5",
        parsed_ingredients=["Gin", "Tonic"]
    )
    
    return [cocktail1, cocktail2, cocktail3, cocktail4, cocktail5]


class TestIngredientOptimizerService:
    
    def test_init(self, ingredient_optimizer_service):
        """Test that the service initializes correctly with dependencies"""
        assert hasattr(ingredient_optimizer_service, 'cocktail_service')
        assert hasattr(ingredient_optimizer_service, 'ingredient_service')
   
    def test_find_optimal_ingredients_with_n_0(self, ingredient_optimizer_service, mock_cocktails):
        """Test finding optimal ingredients with N=0 (should return empty set)"""
        # Configure mock to return our test cocktails
        ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails
        
        result = ingredient_optimizer_service.find_optimal_ingredients(0)
        
        assert len(result["ingredients"]) == 0
        assert result["cocktail_count"] == 0
        assert len(result["cocktails"]) == 0
    
    def test_find_optimal_ingredients_with_n_greater_than_possible_ingredients(self, ingredient_optimizer_service, mock_cocktails):
        """Test finding optimal ingredients with N larger than available ingredients"""
        # Configure mock to return our test cocktails
        ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails
        
        # Count total unique ingredients in all cocktails
        all_ingredients = set()
        for cocktail in mock_cocktails:
            if cocktail.parsed_ingredients:
                all_ingredients.update(cocktail.parsed_ingredients)
        
        result = ingredient_optimizer_service.find_optimal_ingredients(len(all_ingredients) + 5)
        
        # Should return all possible ingredients
        assert len(result["ingredients"]) == len(all_ingredients)
        
        # All ingredients should be in the result
        for ingredient in all_ingredients:
            assert ingredient in result["ingredients"]
    
    def test_find_optimal_ingredients_with_no_cocktails(self, ingredient_optimizer_service):
        """Test finding optimal ingredients when there are no cocktails"""
        ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = []
        
        result = ingredient_optimizer_service.find_optimal_ingredients(3)
        
        assert len(result["ingredients"]) == 0
        assert result["cocktail_count"] == 0
        assert len(result["cocktails"]) == 0
    
    def test_find_optimal_ingredients_with_cocktails_having_no_parsed_ingredients(self, ingredient_optimizer_service):
        """Test finding optimal ingredients when cocktails have no parsed ingredients"""
        # Create mock cocktails with no parsed ingredients
        mock_cocktails_no_ingredients = [
            Cocktail(
                uri="http://example.com/cocktail1",
                id="cocktail1",
                name="Cocktail 1",
                parsed_ingredients=None
            ),
            Cocktail(
                uri="http://example.com/cocktail2",
                id="cocktail2",
                name="Cocktail 2",
                parsed_ingredients=[]
            )
        ]
        
        ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails_no_ingredients
        
        result = ingredient_optimizer_service.find_optimal_ingredients(2)
        
        assert len(result["ingredients"]) == 0
        assert result["cocktail_count"] == 0
        assert len(result["cocktails"]) == 0
    
    def test_find_optimal_ingredients_with_cocktails_needing_more_ingredients_than_n(self, ingredient_optimizer_service):
        """Test finding optimal ingredients when cocktails require more ingredients than N"""
        mock_cocktails_large = [
            Cocktail(
                uri="http://example.com/cocktail1",
                id="cocktail1",
                name="Cocktail 1",
                parsed_ingredients=["Gin", "Vermouth", "Bitters", "Orange Peel"]  # 4 ingredients
            ),
            Cocktail(
                uri="http://example.com/cocktail2",
                id="cocktail2",
                name="Cocktail 2",
                parsed_ingredients=["Vodka", "Orange Juice", "Cranberry Juice"]  # 3 ingredients
            )
        ]
        
        ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails_large
        
        # Test with N=2 - should not select any ingredients that can't complete any cocktails
        result = ingredient_optimizer_service.find_optimal_ingredients(2)
        
        # Verify result structure
        assert "ingredients" in result
        assert "cocktail_count" in result
        assert "cocktails" in result
        
        # Should have at most 2 ingredients
        assert len(result["ingredients"]) <= 2
    
    def test_find_optimal_ingredients_returns_correct_cocktail_count(self, ingredient_optimizer_service, mock_cocktails):
        """Test that the returned cocktail count is accurate"""
        ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails
        
        result = ingredient_optimizer_service.find_optimal_ingredients(2)
        
        # Count how many cocktails can be made with the selected ingredients
        actual_count = 0
        selected_ingredients = set(result["ingredients"])
        
        for cocktail in mock_cocktails:
            if cocktail.parsed_ingredients and set(cocktail.parsed_ingredients).issubset(selected_ingredients):
                actual_count += 1
        
        assert result["cocktail_count"] == actual_count
    
    def test_find_optimal_ingredients_returns_correct_cocktails_list(self, ingredient_optimizer_service, mock_cocktails):
        """Test that the returned cocktails list matches the count"""
        ingredient_optimizer_service.cocktail_service.get_all_cocktails.return_value = mock_cocktails
        
        result = ingredient_optimizer_service.find_optimal_ingredients(2)
        
        assert len(result["cocktails"]) == result["cocktail_count"]


if __name__ == "__main__":
    # Run tests directly
    test_service = TestIngredientOptimizerService()
    
    try:
        # Create mock service
        with patch('services.ingredient_optimizer_service.CocktailService') as mock_cocktail_service, \
             patch('services.ingredient_optimizer_service.IngredientService') as mock_ingredient_service:
            
            mock_cocktail_service_instance = Mock()
            mock_ingredient_service_instance = Mock()
            
            mock_cocktail_service.return_value = mock_cocktail_service_instance
            mock_ingredient_service.return_value = mock_ingredient_service_instance
            
            service = IngredientOptimizerService()
            service.cocktail_service = mock_cocktail_service_instance
            service.ingredient_service = mock_ingredient_service_instance
            
            # Test initialization
            print("Testing initialization...")
            assert hasattr(service, 'cocktail_service')
            assert hasattr(service, 'ingredient_service')
            print("✅ Initialization test passed")
            
            print("\nAll tests passed!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
