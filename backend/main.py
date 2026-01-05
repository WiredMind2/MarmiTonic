from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import cocktails, ingredients, planner, insights
from .utils.front_server import start_frontend_server
from rdflib import Graph
from pathlib import Path

start_frontend_server()

app = FastAPI()

# Load RDF graph once at startup
RDF_GRAPH = Graph()
rdf_file = Path(__file__).parent / "data" / "iba_export.ttl"
print(f"Loading RDF data from {rdf_file}...")
RDF_GRAPH.parse(rdf_file, format="turtle")
print(f"✓ Loaded {len(RDF_GRAPH)} triples")


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
