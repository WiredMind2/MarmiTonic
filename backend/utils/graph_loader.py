from rdflib import Graph
from pathlib import Path
import threading

_graph_instance = None
_lock = threading.Lock()

def get_shared_graph():
    global _graph_instance
    with _lock:
        if _graph_instance is None:
            _graph_instance = Graph()
            # Try to find the file
            root_dir = Path(__file__).parent.parent.parent
            rdf_file = root_dir / "data" / "iba_export.ttl"
            
            if not rdf_file.exists():
                # Fallback to backend/data if that's where someone thinks it is
                rdf_file = root_dir / "backend" / "data" / "iba_export.ttl"
                
            if rdf_file.exists():
                print(f"Loading shared RDF data from {rdf_file}...")
                try:
                    _graph_instance.parse(str(rdf_file), format="turtle")
                    print(f"✓ Shared graph loaded with {len(_graph_instance)} triples")
                except Exception as e:
                    print(f"Error loading shared RDF data: {e}")
            else:
                print(f"Warning: Shared RDF data file not found at {rdf_file}")
        
        return _graph_instance
