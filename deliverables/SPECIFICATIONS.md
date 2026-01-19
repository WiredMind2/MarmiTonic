# Product Specifications (Cahier des Charges) 📝

## 1. Introduction

### 1.1 Context
 **MarmiTonic** is a semantic web project for the "Web Sémantique" (4-IF-WS) course at INSA Lyon. It aims to demonstrate the power of Linked Data by creating an intelligent cocktail application that goes beyond simple text search.

### 1.2 Scope
The application focuses on the cocktail domain, enabling users to:
- Navigate semantic relationships between drinks and ingredients.
- Optimize their home bar inventory.
- Discover new recipes using graph-based recommendation algorithms.

## 2. Global Objectives

1.  **Semantic Integration**: Query and utilize Linked Data (DBpedia) via SPARQL.
2.  **Graph Analysis**: Construct and analyze knowledge graphs to derive insights (centrality, communities).
3.  **User Experience**: Provide a modern, intuitive interface for bar management.
4.  **Optimization**: Implement algorithms to minimize ingredient purchase for maximum cocktail output.

## 3. Functional Requirements

### 3.1 Core Modules

#### 3.1.1 "My Bar" (Inventory)
- **User Action**: Select owned ingredients from a catalog.
- **System Output**:
  - **Doable**: Cocktails require 0 new ingredients.
  - **Almost Doable**: Cocktails requiring 1-2 new ingredients.
  - **Shopping List**: Generate a list of missing items.

#### 3.1.2 Optimization (Planner)
- **Feature**: "Playlist Mode".
- **Logic**: Given a list of user-selected cocktails, calculate the *minimum* set of ingredients required to make them.
- **Algorithm**: Set Cover Problem (Greedy approach).

#### 3.1.3 Discovery Engine
- **Similarity**: Recommend cocktails based on shared ingredients.
- **Vibe Clusters**: Group cocktails by style (e.g., "Tropical", "Strong", "Creamy") using community detection.
- **Bridges**: Suggest cocktails that serve as "bridges" to explore new styles based on current preferences.

#### 3.1.4 SPARQL Explorer
- **Interface**: A raw query editor for power users.
- **Capability**: Execute `SELECT` queries against the local RDF graph or DBpedia endpoint.

### 3.2 Advanced Features

- **Ingredient Substitution**: Suggest alternatives based on semantic proximity (e.g., Lime Juice ≈ Lemon Juice).
- **Dietary Filters**: Semantic filters for "Vegan", "Non-Alcoholic" (derived from ingredient properties).
- **Visual Insights**: Interactive node-link diagrams showing the cocktail universe.

## 4. Non-Functional Requirements

- **Performance**: Recommendations should load in < 2 seconds.
- **Reliability**: The system must handle the IBA (International Bartenders Association) official list (~100+ cocktails) robustly.
- **Usability**: Clean, responsive UI suitable for desktop and tablet.

## 5. Technical Constraints

- **Language**: Python (Backend), Javascript (Frontend).
- **Standards**: RDF, SPARQL.
- **Libraries**: `rdflib` (Semantic Web), `FastAPI` (Web), `NetworkX` (Graph).
