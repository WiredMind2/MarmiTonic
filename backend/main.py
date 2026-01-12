from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import cocktails, ingredients, planner, insights
from utils.front_server import start_frontend_server_once
from rdflib import Graph
from pathlib import Path

start_frontend_server_once()

app = FastAPI()

# Load RDF graph once at startup
RDF_GRAPH = Graph()
# Data is in the root data directory, so we need to go up one level from backend/
rdf_file = Path(__file__).parent.parent / "data" / "iba_export.ttl"
print(f"Loading RDF data from {rdf_file}...")
try:
    # Use file:// URI format to avoid parsing issues
    import urllib.parse
    file_uri = rdf_file.as_uri()
    print(f"Using file URI: {file_uri}")
    RDF_GRAPH.parse(file_uri, format="turtle")
    print(f"✓ Loaded {len(RDF_GRAPH)} triples")
except Exception as e:
    print(f"✗ Error loading RDF data: {e}")
    # Fallback: try with data.ttl if iba_export.ttl fails
    try:
        fallback_file = Path(__file__).parent.parent / "data" / "data.ttl"
        print(f"Trying fallback file: {fallback_file}")
        fallback_uri = fallback_file.as_uri()
        RDF_GRAPH.parse(fallback_uri, format="turtle")
        print(f"✓ Loaded {len(RDF_GRAPH)} triples from fallback")
    except Exception as fallback_e:
        print(f"✗ Error loading fallback RDF data: {fallback_e}")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cocktails, prefix="/cocktails", tags=["cocktails"])
app.include_router(ingredients, prefix="/ingredients", tags=["ingredients"])
app.include_router(planner, prefix="/planner", tags=["planner"])
app.include_router(insights, prefix="/insights", tags=["insights"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MarmiTonic API"}
