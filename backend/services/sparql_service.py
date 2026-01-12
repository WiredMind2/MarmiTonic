import os
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from rdflib.term import URIRef
from typing import Optional, Union
import sys
from pathlib import Path

# Importer le parser IBA
from ..data.ttl_parser import IBADataParser
from ..utils.graph_loader import get_shared_graph

class SparqlService:
    _shared_parser = None
    _shared_graph_path = None

    def __init__(self, local_graph: Optional[Union[str, Graph]] = None):
        self.endpoint = "https://dbpedia.org/sparql"
        self.local_endpoint = "http://localhost:3030/marmitonic"

        # If local_graph is a Graph object, use it directly
        if isinstance(local_graph, Graph):
            self.local_graph = local_graph
            self.parser = None
            return

        # Set local_graph_path based on parameter or default
        if isinstance(local_graph, str):
            self.local_graph_path = local_graph
        else:
            # Try to find data.ttl
            data_file = Path(__file__).parent.parent / "data" / "data.ttl"
            if not data_file.exists():
                data_file = Path(__file__).parent.parent / "data" / "iba_export.ttl"
            self.local_graph_path = str(data_file) if data_file.exists() else "data.ttl"

        # Load shared parser if not already loaded or path changed
        if SparqlService._shared_graph_path != self.local_graph_path or SparqlService._shared_parser is None:
            SparqlService._shared_graph_path = self.local_graph_path
            try:
                print(f"DEBUG: Loading IBA data parser with file: {self.local_graph_path}")
                SparqlService._shared_parser = IBADataParser(self.local_graph_path)
                print(f"DEBUG: Parser loaded successfully with {len(SparqlService._shared_parser.graph)} triples")
            except Exception as e:
                print(f"DEBUG: Error loading parser: {e}")
                # Fallback to shared graph if parser fails
                self.local_graph = get_shared_graph()
                self.parser = None
                return

        self.parser = SparqlService._shared_parser
        self.local_graph = SparqlService._shared_parser.graph if SparqlService._shared_parser else get_shared_graph()

    def execute_query(self, query: str):
        """Execute SPARQL query on DBpedia"""
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            return results
        except Exception as e:
            print(f"Error executing SPARQL query: {e}")
            # Fallback to requests if SPARQLWrapper fails
            params = {
                'query': query,
                'format': 'application/sparql-results+json'
            }
            headers = {
                'Accept': 'application/sparql-results+json'
            }
            try:
                response = requests.get("https://dbpedia.org/sparql", params=params, headers=headers, timeout=30)
                if response.status_code >= 400:
                    return None
                return response.json()
            except:
                return None

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

    def get_all_cocktails_from_dbpedia(self):
        """Get all cocktails from DBpedia"""
        query = """
        SELECT ?cocktail WHERE {
            ?cocktail rdf:type dbo:Cocktail .
        } LIMIT 100
        """
        result = self.execute_query(query)
        if result and "results" in result and "bindings" in result["results"]:
            return [binding["cocktail"]["value"] for binding in result["results"]["bindings"]]
        elif result is None:
            return None
        else:
            return []

    @staticmethod
    def _build_query(query_type: str, uri: str, additional_properties: list = None):
        """Build SPARQL query based on type and parameters"""
        if additional_properties is None:
            additional_properties = []
        
        if query_type == "cocktail":
            # Basic cocktail query
            properties = " ?name ?description " + " ".join([f"?{prop.split(':')[-1]}" for prop in additional_properties])
            optional_clauses = "\n                ".join([f"OPTIONAL {{ <{uri}> {prop} ?{prop.split(':')[-1]} }}" for prop in additional_properties])
            query = f"""SELECT {properties} WHERE {{
                <{uri}> rdfs:label ?name .
                OPTIONAL {{ <{uri}> dbo:abstract ?description . FILTER(LANG(?description) = "en") }}
                {optional_clauses}
            }}"""
        elif query_type == "ingredients":
            # Ingredients query
            query = f"""SELECT ?ingredient WHERE {{
                <{uri}> dbo:ingredient ?ingredient .
            }}"""
        elif query_type == "":
            # Empty query type - include rdf:type and additional properties if provided
            if additional_properties:
                properties = " ?type " + " ".join([f"?{prop.split(':')[-1]}" for prop in additional_properties])
                optional_clauses = "\n                ".join([f"OPTIONAL {{ <{uri}> {prop} ?{prop.split(':')[-1]} }}" for prop in additional_properties])
                query = f"""SELECT {properties} WHERE {{
                    <{uri}> rdf:type ?type .
                    {optional_clauses}
                }}"""
            else:
                query = f"""SELECT ?property ?value WHERE {{
                    <{uri}> rdf:type ?type .
                    <{uri}> ?property ?value .
                }}"""
        else:
            # Generic query
            query = f"""SELECT ?property ?value WHERE {{
                <{uri}> ?property ?value .
            }}"""
        
        return query
