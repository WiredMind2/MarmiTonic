from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.cocktails import router as cocktails
from backend.routes.ingredients import router as ingredients
from backend.routes.planner import router as planner
from backend.routes.llm import router as llm
from backend.routes.graphs import router as graphs
from backend.utils.front_server import start_frontend_server_once
from backend.utils.graph_loader import get_shared_graph
from rdflib import Graph
from pathlib import Path
from contextlib import asynccontextmanager
import time

# Start frontend server
start_frontend_server_once()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\nMarmiTonic API Starting...")
    start_time = time.time()
    
    print("Loading RDF graph...")
    RDF_GRAPH = get_shared_graph()
    
    print("Pre-warming data caches...")
    from backend.data.ttl_parser import get_all_cocktails, get_all_ingredients
    
    cache_start = time.time()
    cocktails = get_all_cocktails()
    print(f"   ✅ Loaded {len(cocktails)} cocktails")
    
    ingredients = get_all_ingredients()
    print(f"   ✅ Loaded {len(ingredients)} ingredients")
    
    cache_time = time.time() - cache_start
    total_time = time.time() - start_time
    
    print(f"Cache pre-warmed in {cache_time:.3f}s")
    print(f"Server ready in {total_time:.3f}s - All subsequent requests will be instant!\n")
    
    yield
    
    # Shutdown
    print("\nMarmiTonic API Shutting down...")

app = FastAPI(lifespan=lifespan)

# Load RDF graph reference (already loaded in lifespan)
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
app.include_router(graphs, prefix="/graphs", tags=["graphs"])
app.include_router(llm, prefix="/llm", tags=["llm"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MarmiTonic API"}
