from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import cocktails, ingredients, planner, insights, llm
from .routes.graphs import router as graphs
from .utils.front_server import start_frontend_server_once
from .utils.graph_loader import get_shared_graph
from rdflib import Graph
from pathlib import Path

# Start frontend server
start_frontend_server_once()

app = FastAPI()

# Load RDF graph once at startup using shared loader
RDF_GRAPH = get_shared_graph()


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
