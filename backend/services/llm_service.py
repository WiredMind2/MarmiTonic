from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
import hashlib
import time

class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, ttl: int = 3600, max_size: int = 100):
        self.ttl = ttl
        self.max_size = max_size
        self.cache = {}  # key: (value, timestamp)
    
    def _cleanup(self):
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [key for key, (_, timestamp) in self.cache.items() 
                      if current_time - timestamp > self.ttl]
        for key in expired_keys:
            del self.cache[key]
    
    def get(self, key):
        """Get value from cache if not expired."""
        self._cleanup()
        if key in self.cache:
            value, timestamp = self.cache[key]
            return value
        return None
    
    def set(self, key, value):
        """Set value in cache with current timestamp."""
        self._cleanup()
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_key]
        self.cache[key] = (value, time.time())


class LLMService:
    def __init__(self, cache_ttl: int = 3600, cache_size: int = 100):
        load_dotenv()
        API_KEY = getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=API_KEY)
        # Create custom cache instance
        self.cache = SimpleCache(ttl=cache_ttl, max_size=cache_size)
    
    def _get_cache_key(self, prompt: str, method: str) -> str:
        # Generate a unique cache key based on prompt and method
        key_string = f"{method}:{prompt}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def example(self, prompt: str):
        cache_key = self._get_cache_key(prompt, "example")
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        response = self.client.chat.completions.create(
            model="mistralai/devstral-2512:free",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content
        self.cache.set(cache_key, result)
        return result
    
    def nl2sparql(self, prompt: str):
        header = """Tu es un générateur de requêtes SPARQL pour un graphe RDF local.

CONTEXTE:
- Tu interroges un graphe RDF de 56 cocktails en mémoire
- Le graphe est local, pas DBpedia en ligne
- Les ingrédients sont stockés comme texte dans dbp:ingredients

PREFIXES OBLIGATOIRES:
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>

STRUCTURE DU GRAPHE:
- Tous les cocktails ont: dbp:ingredients (texte avec liste d'ingrédients)
- Tous les cocktails ont: rdfs:label en anglais et français
- Propriétés optionnelles: dbo:description, dbp:prep, dbp:served, dbp:garnish

RÈGLES:
1. Toujours retourner ?cocktail (URI) et ?name (label anglais)
2. Filtrer les labels: FILTER(LANG(?name) = "en")
3. Pour chercher des ingrédients: FILTER(CONTAINS(LCASE(?ing), "mot"))

EXEMPLES:

Tous les cocktails:
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cocktail ?name WHERE {
  ?cocktail dbp:ingredients ?ing .
  ?cocktail rdfs:label ?name .
  FILTER(LANG(?name) = "en")
}

Cocktails avec vodka:
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cocktail ?name WHERE {
  ?cocktail dbp:ingredients ?ing .
  FILTER(CONTAINS(LCASE(?ing), "vodka"))
  ?cocktail rdfs:label ?name .
  FILTER(LANG(?name) = "en")
}

Retourne UNIQUEMENT la requête SPARQL avec les PREFIX. Pas de markdown, pas d'explication."""


        response = self.client.chat.completions.create(
            model="mistralai/devstral-2512:free",
            messages=[
                {"role": "system", "content": header},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        self.cache.set(cache_key, result)
        return result
    
if __name__ == "__main__":
    llm_service = LLMService()
    result = llm_service.nl2sparql("donne moi tous les cocktails avec de la vodka")
    print(result)