from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import cocktails, ingredients, sparql, planner, insights
from .utils.front_server import start_frontend_server

start_frontend_server()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cocktails.router, prefix="/cocktails", tags=["cocktails"])
app.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
app.include_router(sparql.router, prefix="/sparql", tags=["sparql"])
app.include_router(planner.router, prefix="/planner", tags=["planner"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MarmiTonic API"}
