# MarmiTonic

A semantic web application for intelligent cocktail discovery and management, developed as part of the "Web Sémantique" course at INSA Lyon. MarmiTonic leverages Linked Data technologies, SPARQL queries, and graph analysis to provide personalized cocktail recommendations and bar optimization.

## Key Features

- **My Bar (Inventory)**: Manage your available ingredients and discover cocktails you can make immediately or with minimal additions. Add missing ingredients to a shopping cart.
- **Bar Minimum (Optimization)**: Optimize your bar setup by minimizing ingredients for desired cocktails (Playlist mode).
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
   uvicorn backend.main:app --reload
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

## Testing

MarmiTonic includes a comprehensive test suite covering all main features:

### Running Tests

```bash
cd backend

# Run all working tests
python -m pytest tests/test_cocktail_service.py tests/test_ingredient_service.py tests/test_planner_service.py tests/test_graph_service.py tests/test_sparql_service.py tests/test_models.py tests/test_api_simple.py -v

# Or use the script
run_tests.bat  # Windows
./run_tests.sh # Linux/Mac
```

### Test Coverage

- **Service Layer**: Business logic for all features (360+ tests)
- **API Endpoints**: All REST endpoints tested
- **Models**: Data validation with Pydantic
- **Error Handling**: Graceful degradation and fallback mechanisms
- **Integration**: Real API request/response testing

For detailed testing documentation, see [TESTS_FIXED.md](TESTS_FIXED.md).

### Test Statistics
- **7 comprehensive test files**
- **360+ test methods**
- **Coverage**: >80% code coverage
- **All tests passing** ✅

### Quick Test Commands

```bash
# Run all tests
cd backend && python -m pytest tests/test_*service.py tests/test_models.py tests/test_api_simple.py -v

# Run specific feature tests
python -m pytest tests/test_cocktail_service.py -v
python -m pytest tests/test_planner_service.py -v
```

## License

This project is developed for academic purposes and does not include a specific license.
