from rdflib import Graph
from rdflib.term import URIRef
from typing import Optional, Union

# Importer le parser IBA
from backend.data.ttl_parser import IBADataParser
from backend.utils.graph_loader import get_shared_graph

class SparqlService:
    def __init__(self, local_graph: Optional[Union[str, Graph]] = None):
        # ONLY LOCAL GRAPH - NO EXTERNAL DBPEDIA QUERIES ALLOWED
        self.local_graph_path = "data.ttl"

        # If local_graph is a Graph object, use it directly
        if isinstance(local_graph, Graph):
            self.local_graph = local_graph
            self.parser = None
            return

        # Use the singleton parser - it handles caching internally
        try:
            self.parser = IBADataParser()
            self.local_graph = self.parser.graph
        except Exception as e:
            print(f"Error loading parser: {e}")
            # Fallback to shared graph if parser fails
            self.local_graph = get_shared_graph()
            self.parser = None

    def execute_query(self, query: str):
        """Execute SPARQL query - ONLY ON LOCAL GRAPH"""
        # All queries go to local graph - no external access
        return self.execute_local_query(query)

    def execute_local_query(self, query: str):
        """Execute SPARQL query on local RDF graph"""
        print(f"DEBUG: execute_local_query called")
        if self.local_graph is None:
            print("DEBUG: Local graph not loaded")
            return None

        try:
            print("DEBUG: Executing query on local graph")
            # Execute query on local graph
            result = self.local_graph.query(query)

            # Convert to SPARQL results JSON format
            bindings = []
            for row in result:
                binding = {}
                for var, value in zip(result.vars, row):
                    if value is not None:
                        if hasattr(value, 'n3'):
                            binding[str(var)] = {"value": str(value), "type": "uri" if isinstance(value, URIRef) else "literal"}
                        else:
                            binding[str(var)] = {"value": str(value), "type": "literal"}
                    else:
                        binding[str(var)] = {"value": None}
                bindings.append(binding)

            print(f"DEBUG: Query executed successfully, {len(bindings)} results")
            return {
                "head": {"vars": [str(var) for var in result.vars]},
                "results": {"bindings": bindings}
            }
        except Exception as e:
            print(f"DEBUG: Error executing local SPARQL query: {e}")
            return None

    def query_local_data(self, query_type: str, uri: str = None, additional_properties: list = None):
        """Query local data with optional parameters"""
        prefixes = """
            PREFIX : <http://dbpedia.org/resource/>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        """
        
        if query_type == "cocktails":
            query = prefixes + """
            SELECT ?cocktail WHERE {
                ?cocktail a :Cocktail .
            }
            """
        elif query_type == "cocktail":
            query = prefixes + f"""
            SELECT ?property ?value WHERE {{
                <{uri}> ?property ?value .
            }}
            """
        elif query_type == "ingredients":
            query = prefixes + """
            SELECT ?ingredient WHERE {
                ?ingredient a :Ingredient .
            }
            """
        else:
            query = prefixes + """
            SELECT ?s ?p ?o WHERE {
                ?s ?p ?o .
            }
            """
        
        return self.execute_local_query(query)
