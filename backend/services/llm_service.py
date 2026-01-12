from openai import OpenAI
from os import getenv
from dotenv import load_dotenv

class LLMService:
    def __init__(self):
        load_dotenv()
        API_KEY = getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=API_KEY)
    
    def example(self, prompt: str):
        response = self.client.chat.completions.create(
            model="mistralai/devstral-2512:free",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def nl2sparql(self, prompt: str):
        header = """You are a SPARQL query generator for cocktail data in RDF/Turtle format.

IMPORTANT: The RDF graph contains 56 cocktails with 2419 triples. Cocktails are NOT declared with 'a dbo:Cocktail' (no rdf:type declaration). Instead, cocktails are identified by having properties like dbp:ingredients, dbp:prep, etc.

Namespaces available:
- dbr: http://dbpedia.org/resource/
- dbo: http://dbpedia.org/ontology/
- dbp: http://dbpedia.org/property/
- rdfs: http://www.w3.org/2000/01/rdf-schema#
- dct: http://purl.org/dc/terms/
- foaf: http://xmlns.com/foaf/0.1/

Properties available in the graph:
1. rdfs:label - cocktail names (in @en and @fr)
2. dbo:description - cocktail descriptions (in @en and @fr)
3. dbp:ingredients - complete ingredients list as text (in @en)
4. dbp:prep - preparation instructions (in @en)
5. dbp:garnish - garnish information
6. dbp:served - how the cocktail is served (e.g., "rocks", "straight")
7. dbp:name - short name (in @en)
8. dbp:sourcelink - source reference
9. dbo:wikiPageWikiLink - related resources (e.g., ingredients, related cocktails)
10. dct:subject - categories (e.g., dbc:Cocktails_with_gin, dbc:Cocktails_with_vodka)
11. foaf:depiction - image URLs

HOW TO QUERY COCKTAILS:
- To get all cocktails: SELECT ?cocktail WHERE { ?cocktail dbp:ingredients ?ingredients. }
- To search by ingredient: Use FILTER(CONTAINS(LCASE(?ingredients), "vodka")) on dbp:ingredients
- To filter by language: Use FILTER(LANG(?label) = "en") or FILTER(LANG(?label) = "fr")

Examples of cocktails in the graph: Black Russian, Moscow mule, Bloody Mary, Cosmopolitan, Espresso martini, French martini, Long Island iced tea, Vesper, Martini, Mojito, Margarita, Daiquiri, etc.

Generate a valid SPARQL SELECT query that answers the natural language question. Use the actual structure of the graph. Do NOT use 'a dbo:Cocktail' as it doesn't exist in this graph. Return only the SPARQL query without explanations or markdown formatting."""
        response = self.client.chat.completions.create(
            model="mistralai/devstral-2512:free",
            messages=[
                {"role": "system", "content": header},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
if __name__ == "__main__":
    llm_service = LLMService()
    result = llm_service.nl2sparql("donne moi tous les cocktails avec de la vodka")
    print(result)