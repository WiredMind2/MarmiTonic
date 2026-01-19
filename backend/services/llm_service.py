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
        return response.choices[0].message.content
    
if __name__ == "__main__":
    llm_service = LLMService()
    result = llm_service.nl2sparql("donne moi tous les cocktails avec de la vodka")
    print(result)