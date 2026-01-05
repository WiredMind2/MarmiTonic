from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from typing import Optional

class SparqlService:
    def __init__(self, local_graph_path: Optional[str] = None):
        self.local_graph = None
        if local_graph_path:
            self.local_graph = Graph()
            try:
                self.local_graph.parse(local_graph_path, format="turtle")
            except Exception as e:
                print(f"Error loading local graph: {e}")
                self.local_graph = None

    def execute_query(self, query: str):
        """Execute SPARQL query on DBpedia"""
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results

    def execute_local_query(self, query: str):
        """Execute SPARQL query on local RDF graph"""
        if not self.local_graph:
            raise ValueError("Local graph not loaded")

        results = self.local_graph.query(query)
        # Convert to similar format as SPARQLWrapper for consistency
        bindings = []
        for row in results:
            binding = {}
            for var in results.vars:
                value = row[var]
                if value is not None:
                    binding[str(var)] = {"value": str(value), "type": "uri" if hasattr(value, 'n3') and value.n3().startswith('<') else "literal"}
                else:
                    binding[str(var)] = {"value": None}
            bindings.append(binding)

        return {"results": {"bindings": bindings}}