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
The data contains information about cocktails from DBpedia, using the following namespaces:
- dbr: http://dbpedia.org/resource/
- dbo: http://dbpedia.org/ontology/
- dbp: http://dbpedia.org/property/
- rdfs: http://www.w3.org/2000/01/rdf-schema#
- dct: http://purl.org/dc/terms/

Common properties include:
- rdfs:label (cocktail names in different languages)
- dbo:description (descriptions)
- dbp:ingredients (list of ingredients as text)
- dbp:prep (preparation instructions)
- dbp:garnish (garnish information)
- dbp:served (how it's served)
- dbo:wikiPageWikiLink (related links)

Generate a valid SPARQL SELECT query that answers the natural language question. Do not hallucinate or add information not present in the data. Return only the SPARQL query without explanations."""
        response = self.client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
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