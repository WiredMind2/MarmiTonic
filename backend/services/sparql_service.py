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
        """Execute SPARQL query on local RDF graph - returns direct Python list"""
        print(f"DEBUG: execute_local_query called")
        if self.local_graph is None:
            print("DEBUG: Local graph not loaded")
            return None

        try:
            print("DEBUG: Executing query on local graph")
            # Execute query on local graph
            result = self.local_graph.query(query)

            # Convert directly to Python list of dicts
            rows = []
            for row in result:
                row_dict = {}
                for var, value in zip(result.vars, row):
                    if value is not None:
                        row_dict[str(var)] = {
                            "value": str(value),
                            "type": "uri" if isinstance(value, URIRef) else "literal"
                        }
                    else:
                        row_dict[str(var)] = {"value": None, "type": "literal"}
                rows.append(row_dict)

            print(f"DEBUG: Query executed successfully, {len(rows)} results")
            return rows
        except Exception as e:
            print(f"DEBUG: Error executing local SPARQL query: {e}")
            return None
