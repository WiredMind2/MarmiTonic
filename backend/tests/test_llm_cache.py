"""Test the LLM service caching functionality"""
import time
from services.llm_service import LLMService
from services.similarity_service import SimilarityService


def test_llm_service_caching():
    """Test that LLMService methods return cached results for the same input"""
    print("Testing LLMService caching...")
    
    # Create LLMService instance with short TTL for testing
    llm_service = LLMService(cache_ttl=10, cache_size=50)
    
    # Test nl2sparql method caching
    query = "donne moi tous les cocktails avec de la vodka"
    result1 = llm_service.nl2sparql(query)
    print(f"nl2sparql first call: {result1}")
    
    result2 = llm_service.nl2sparql(query)
    print(f"nl2sparql second call: {result2}")
    
    assert result1 == result2
    print("nl2sparql caching working correctly")
    
    # Test example method caching
    prompt = "What is the capital of France?"
    result1 = llm_service.example(prompt)
    print(f"example first call: {result1}")
    
    result2 = llm_service.example(prompt)
    print(f"example second call: {result2}")
    
    assert result1 == result2
    print("example method caching working correctly")


def test_similarity_service_caching():
    """Test that SimilarityService cluster title generation uses caching"""
    print("\nTesting SimilarityService cluster title caching...")
    
    # Create SimilarityService instance with short TTL for testing
    similarity_service = SimilarityService(cache_ttl=10, cache_size=50)
    
    # Build index
    similarity_service.build_index()
    
    # Get some cocktails for testing
    if not similarity_service.cocktails:
        print("⚠️  No cocktails found, skipping cluster title caching test")
        return
    
    # Take first 5 cocktails as a test cluster
    test_cocktails = similarity_service.cocktails[:5]
    
    # Get cluster title twice
    title1 = similarity_service._generate_cluster_title(test_cocktails)
    print(f"First cluster title: {title1}")
    
    title2 = similarity_service._generate_cluster_title(test_cocktails)
    print(f"Second cluster title: {title2}")
    
    assert title1 == title2
    print("Cluster title generation caching working correctly")


def test_cache_expiration():
    """Test that cache entries expire after TTL"""
    print("\nTesting cache expiration...")
    
    llm_service = LLMService(cache_ttl=2, cache_size=50)
    prompt = "Say 'yes' in French."
    
    result1 = llm_service.example(prompt)
    print(f"First call result: {result1}")
    
    # Verify cache has the entry
    cache_key = llm_service._get_cache_key(prompt, "example")
    cached = llm_service.cache.get(cache_key)
    assert cached is not None, "Entry should be in cache"
    
    # Wait for cache to expire
    time.sleep(3)
    
    # Cache should be expired now
    cached_after_expiry = llm_service.cache.get(cache_key)
    assert cached_after_expiry is None, "Entry should be expired"
    
    # This should trigger a new API call
    result2 = llm_service.example(prompt)
    print(f"Call after expiration: {result2}")
    
    # Both should have some content (don't compare exact text)
    assert result1 is not None and len(result1) > 0
    assert result2 is not None and len(result2) > 0
    print("Cache expiration working correctly")


if __name__ == "__main__":
    try:
        test_llm_service_caching()
        test_similarity_service_caching()
        test_cache_expiration()
        print("\nAll caching tests passed!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        print(traceback.format_exc())
