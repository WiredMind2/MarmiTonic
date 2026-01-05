# Refined Project Structure Plan for MarmiTonic

## Overview
This document outlines the refined folder structure and template files for the MarmiTonic project, incorporating semantic web and SPARQL requirements, data analysis, and optional generative AI features.

## Folder Structure

### Frontend
- `frontend/`
  - `index.html`: Main entry point for the application.
  - `css/`
    - `styles.css`: Main stylesheet.
  - `js/`
    - `app.js`: Main JavaScript file for handling frontend logic.
    - `api.js`: JavaScript file for API calls to the backend.
    - `sparql.js`: JavaScript file for SPARQL queries.
    - `visualization.js`: JavaScript file for data visualization.
  - `pages/`
    - `my-bar.html`: Template for the "My Bar" feature.
    - `discovery.html`: Template for the "Discovery" feature.
    - `planner.html`: Template for the "Planner" feature.
    - `insights.html`: Template for the "Insights" feature.
    - `sparql-explorer.html`: Template for the SPARQL Explorer feature.

### Backend
- `backend/`
  - `main.py`: Main FastAPI application file.
  - `models/`
    - `cocktail.py`: Model for cocktails.
    - `ingredient.py`: Model for ingredients.
    - `sparql_query.py`: Model for SPARQL queries.
  - `routes/`
    - `cocktails.py`: Routes for cocktail-related endpoints.
    - `ingredients.py`: Routes for ingredient-related endpoints.
    - `sparql.py`: Routes for SPARQL-related endpoints.
  - `services/`
    - `cocktail_service.py`: Service for cocktail-related operations.
    - `ingredient_service.py`: Service for ingredient-related operations.
    - `sparql_service.py`: Service for SPARQL queries.
    - `graph_service.py`: Service for graph analysis.
  - `data/`
    - `cocktails.json`: Sample data for cocktails.
    - `ingredients.json`: Sample data for ingredients.
  - `utils/`
    - `dbpedia_client.py`: Utility for querying DBpedia.
    - `graph_utils.py`: Utility for graph analysis and visualization.

## Template Files

### Frontend Templates

#### `frontend/index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarmiTonic</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header>
        <h1>MarmiTonic</h1>
        <nav>
            <ul>
                <li><a href="pages/my-bar.html">My Bar</a></li>
                <li><a href="pages/discovery.html">Discovery</a></li>
                <li><a href="pages/planner.html">Planner</a></li>
                <li><a href="pages/insights.html">Insights</a></li>
                <li><a href="pages/sparql-explorer.html">SPARQL Explorer</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="welcome">
            <h2>Welcome to MarmiTonic</h2>
            <p>Discover cocktails based on your ingredients and optimize your bar inventory.</p>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 MarmiTonic</p>
    </footer>
    <script src="js/app.js"></script>
</body>
</html>
```

#### `frontend/css/styles.css`
```css
/* Global Styles */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f9;
    color: #333;
}

header {
    background-color: #333;
    color: #fff;
    padding: 1rem;
    text-align: center;
}

nav ul {
    list-style-type: none;
    padding: 0;
    display: flex;
    justify-content: center;
    gap: 1rem;
}

nav a {
    color: #fff;
    text-decoration: none;
}

main {
    padding: 1rem;
}

footer {
    background-color: #333;
    color: #fff;
    text-align: center;
    padding: 1rem;
    position: fixed;
    bottom: 0;
    width: 100%;
}
```

#### `frontend/js/app.js`
```javascript
// Main application logic
console.log("MarmiTonic app initialized");

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    
    // Add event listeners or other initialization logic here
});
```

#### `frontend/js/api.js`
```javascript
// API calls to the backend
const API_BASE_URL = 'http://localhost:8000';

// Example API call to fetch cocktails
async function fetchCocktails() {
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails`);
        if (!response.ok) {
            throw new Error('Failed to fetch cocktails');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching cocktails:', error);
        return [];
    }
}

// Example API call to fetch ingredients
async function fetchIngredients() {
    try {
        const response = await fetch(`${API_BASE_URL}/ingredients`);
        if (!response.ok) {
            throw new Error('Failed to fetch ingredients');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching ingredients:', error);
        return [];
    }
}

// Example API call to execute SPARQL query
async function executeSparqlQuery(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/sparql`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        if (!response.ok) {
            throw new Error('Failed to execute SPARQL query');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error executing SPARQL query:', error);
        return [];
    }
}
```

#### `frontend/js/sparql.js`
```javascript
// SPARQL query utilities
async function queryCocktails() {
    const query = `
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        
        SELECT ?cocktail ?ingredient WHERE {
            ?cocktail a dbo:Cocktail .
            ?cocktail dbp:ingredient ?ingredient .
        }
    `;
    
    const results = await executeSparqlQuery(query);
    return results;
}

async function queryIngredients() {
    const query = `
        PREFIX dbo: <http://dbpedia.org/ontology/>
        
        SELECT ?ingredient WHERE {
            ?ingredient a dbo:Ingredient .
        }
    `;
    
    const results = await executeSparqlQuery(query);
    return results;
}
```

#### `frontend/js/visualization.js`
```javascript
// Data visualization utilities
function visualizeGraph(data) {
    // Placeholder for graph visualization logic
    console.log("Visualizing graph:", data);
}

function calculateMetrics(data) {
    // Placeholder for calculating graph metrics
    console.log("Calculating metrics:", data);
    return {};
}
```

#### `frontend/pages/sparql-explorer.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPARQL Explorer - MarmiTonic</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <header>
        <h1>SPARQL Explorer</h1>
        <nav>
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="my-bar.html">My Bar</a></li>
                <li><a href="discovery.html">Discovery</a></li>
                <li><a href="planner.html">Planner</a></li>
                <li><a href="insights.html">Insights</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="sparql-explorer">
            <h2>Explore SPARQL Queries</h2>
            <div id="sparql-query">
                <textarea id="query-input" rows="10" cols="50"></textarea>
                <button id="execute-query">Execute Query</button>
            </div>
            <div id="query-results">
                <!-- Query results will be displayed here -->
            </div>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 MarmiTonic</p>
    </footer>
    <script src="../js/app.js"></script>
    <script src="../js/api.js"></script>
    <script src="../js/sparql.js"></script>
</body>
</html>
```

### Backend Templates

#### `backend/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import cocktails, ingredients, sparql

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

@app.get("/")
def read_root():
    return {"message": "Welcome to MarmiTonic API"}
```

#### `backend/models/sparql_query.py`
```python
from pydantic import BaseModel

class SparqlQuery(BaseModel):
    query: str
```

#### `backend/routes/sparql.py`
```python
from fastapi import APIRouter, HTTPException
from ..models.sparql_query import SparqlQuery
from ..services.sparql_service import SparqlService

router = APIRouter()

@router.post("/query")
def execute_sparql_query(query: SparqlQuery):
    try:
        results = SparqlService().execute_query(query.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### `backend/services/sparql_service.py`
```python
from ..utils.dbpedia_client import query_dbpedia

class SparqlService:
    def __init__(self):
        pass
    
    def execute_query(self, query: str):
        results = query_dbpedia(query)
        return results
```

#### `backend/services/graph_service.py`
```python
class GraphService:
    def __init__(self):
        pass
    
    def analyze_graph(self, data):
        # Placeholder for graph analysis logic
        return {}
    
    def visualize_graph(self, data):
        # Placeholder for graph visualization logic
        return {}
```

#### `backend/utils/dbpedia_client.py`
```python
import requests

DBPEDIA_ENDPOINT = "http://dbpedia.org/sparql"

def query_dbpedia(query: str):
    headers = {
        "Accept": "application/sparql-results+json"
    }
    
    response = requests.get(DBPEDIA_ENDPOINT, params={"query": query}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to query DBpedia: {response.status_code}")
```

#### `backend/utils/graph_utils.py`
```python
import networkx as nx
import matplotlib.pyplot as plt

def create_graph(data):
    # Placeholder for creating a graph from data
    G = nx.Graph()
    return G

def calculate_metrics(graph):
    # Placeholder for calculating graph metrics
    return {}

def visualize_graph(graph):
    # Placeholder for visualizing a graph
    nx.draw(graph)
    plt.show()
```

## Next Steps
1. Review the refined plan with the user.
2. Implement the refined plan by creating the necessary files and directories.