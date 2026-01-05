# MarmiTonic

A semantic web application for intelligent cocktail discovery and management, developed as part of the "Web Sémantique" course at INSA Lyon. MarmiTonic leverages Linked Data technologies, SPARQL queries, and graph analysis to provide personalized cocktail recommendations and bar optimization.

## Key Features

- **My Bar (Inventory)**: Manage your available ingredients and discover cocktails you can make immediately or with minimal additions. Add missing ingredients to a shopping cart.
- **Bar Minimum (Optimization)**: Optimize your bar setup with two modes - maximize cocktails with N ingredients (Party mode) or minimize ingredients for desired cocktails (Playlist mode).
- **Discovery**: Explore cocktail recommendations similar to Spotify, including similar cocktails, vibe clusters, and style bridges based on ingredients and relationships.
- **SPARQL Explorer**: Execute custom SPARQL queries against DBpedia for advanced exploration.
- **Insights**: Visualize and analyze cocktail-ingredient graphs, including centrality metrics, communities, and export to Gephi.
- **Bonus Features**: Intelligent ingredient substitutions, dietary filters, and consolidated shopping lists.

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Backend Setup
1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup
The frontend is a static web application. Simply open `frontend/index.html` in your web browser. Ensure the backend is running for API functionality.

## Usage

1. **Discover**: Search for cocktails or ingredients, explore trending items.
2. **My Bar**: Check off your available ingredients to see feasible cocktails.
3. **Planner**: Use optimization tools to plan your bar or shopping list.
4. **Insights**: View graph analytics and export data.
5. **SPARQL Explorer**: Run custom queries.

## Technical Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Sources**: DBpedia via SPARQL
- **Graph Analysis**: NetworkX, Matplotlib
- **Visualization**: D3.js
- **Optional AI**: OpenAI/Anthropic APIs or local Ollama for generative features

## License

This project is developed for academic purposes and does not include a specific license.