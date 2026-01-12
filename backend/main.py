from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import cocktails, ingredients, planner, insights, llm
from .routes.graphs import router as graphs
from .utils.front_server import start_frontend_server_once
from rdflib import Graph
from pathlib import Path

start_frontend_server_once()

app = FastAPI()

# Load RDF graph once at startup
RDF_GRAPH = Graph()
data_folder = Path(__file__).parent / "data"
rdf_file = data_folder / "iba_export.ttl"
print(f"Loading RDF data from {rdf_file}...")
try:
    # Use file path directly
    RDF_GRAPH.parse(str(rdf_file), format="turtle")
    print(f"✓ Loaded {len(RDF_GRAPH)} triples")
except Exception as e:
    print(f"✗ Error loading RDF data: {e}")
    # Fallback: try with data.ttl if iba_export.ttl fails
    try:
        fallback_file = data_folder / "data.ttl"
        print(f"Trying fallback file: {fallback_file}")
        RDF_GRAPH.parse(str(fallback_file), format="turtle")
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
app.include_router(graphs, prefix="/graphs", tags=["graphs"])
app.include_router(llm, prefix="/llm", tags=["llm"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MarmiTonic API"}
