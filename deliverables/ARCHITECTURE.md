# MarmiTonic Architecture 🏗️

## Overview

MarmiTonic is a web application bridging the gap between cocktail enthusiasts and the Semantic Web. It uses a **Client-Server** model where the backend acts as an intelligent mediator between the frontend and Linked Data sources (DBpedia).

## System Design

```mermaid
graph TD
    User[User] -->|HTTP / REST| Frontend[Frontend SPA]
    
    subgraph "Frontend Layer (Browser)"
        Frontend -->|Fetch API| API_Client[API Client (JS)]
        Frontend -->|D3.js| Visualizer[Graph Visualizer]
    end
    
    API_Client -->|JSON| Backend[Backend API (FastAPI)]
    
    subgraph "Backend Layer (Python)"
        Backend --> Router[API Router]
        Router --> Svc_Cocktail[Cocktail Service]
        Router --> Svc_Planner[Planner Service]
        Router --> Svc_Graph[Graph Service]
        
        Svc_Cocktail -->|Query| SPARQL_Eng[SPARQL Engine]
        Svc_Graph -->|Analyze| Graph_Lib[NetworkX]
        
        SPARQL_Eng -->|Query| RDF_Store[RDF Graph (In-Memory)]
    end
    
    subgraph "Data Layer"
        RDF_Store <-->|Load| DataFile[data.ttl]
        RDF_Store <-->|Import| DBpedia[DBpedia SPARQL Endpoint]
    end
```

*(Note: If Mermaid is not rendered, imagine a flow from User -> Frontend -> FastAPI Backend -> Services -> RDF Data)*

## Component Breakdown

### 1. Frontend (Client)
Likely a Single Page Application (SPA) structure served statically.
- **Technology**: HTML5, CSS3, JavaScript (Modules).
- **Visualization**: `D3.js` for interactive graph rendering of cocktail-ingredient networks.
- **Communication**: Communicates with the backend via REST API calls.

### 2. Backend (Server)
The core logic engine.
- **Technology**: Python, FastAPI.
- **Roles**:
  - **API Provider**: Exposes endpoints for cocktails, ingredients, and planning.
  - **Semantic Engine**: Parses and queries RDF data using `rdflib`.
  - **Graph Analyst**: Uses `NetworkX` to calculate centrality, communities, and recommendations.
  - **Static Server**: Serves the frontend files.

### 3. Data Layer
- **Source**: DBpedia (Wikipedia's semantic twin).
- **Format**: Turtle (`.ttl`).
- **Storage**: Data is extracted via SPARQL `CONSTRUCT` queries and stored locally in `data/data.ttl` for performance and offline capability.
- **Model**: Custom ontology leveraging standard vocabularies (`dbo`, `dbp`, `foaf`).

## Key Workflows

### Initialization
1. Backend starts.
2. Loads `data.ttl` into an in-memory `rdflib.Graph`.
3. Pre-computes graph metrics (similarity scores, clusters) for fast retrieval.

### Cocktail Discovery
1. User requests a cocktail details.
2. Backend queries the RDF graph for specific properties (ingredients, glass, preparation).
3. Backend calculates "similar" cocktails based on ingredient overlap and structural graph proximity.
4. Returns JSON response.

### Bar Optimization (Planner)
1. User submits a list of desired cocktails.
2. Backend runs a "Set Cover" approximation algorithm.
3. Identifies the minimum set of ingredients needed to make the maximum number of selected cocktails.
