from SPARQLWrapper import SPARQLWrapper, JSON

class SparqlService:
    def __init__(self):
        pass
    
    def execute_query(self, query: str):
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results