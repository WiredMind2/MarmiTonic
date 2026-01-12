# MarmiTonic Test Suite

Comprehensive test coverage for all main features of the MarmiTonic application.

## Test Structure

```
backend/tests/
├── conftest.py                    # Shared pytest configuration
├── test_api_routes.py            # API endpoint tests (NEW)
├── test_cocktail_service.py      # Cocktail service tests
├── test_ingredient_service.py    # Ingredient service tests
├── test_planner_service.py       # Planner service tests
├── test_graph_service.py         # Graph analysis tests
├── test_sparql_service.py        # SPARQL service tests
├── test_models.py                # Pydantic model tests
└── test_error_handling.py        # Error handling tests
```

## Test Coverage

### API Routes (`test_api_routes.py`)
- ✅ **Cocktails Endpoints**
  - GET /cocktails/ - List all cocktails
  - GET /cocktails/?q=query - Search cocktails
  - GET /cocktails/feasible/{user_id} - Get feasible cocktails for user
  - GET /cocktails/almost-feasible/{user_id} - Get almost feasible cocktails
  - GET /cocktails/by-ingredients - Filter by ingredients
  - GET /cocktails/by-uris - Filter by ingredient URIs
  - GET /cocktails/similar/{id} - Find similar cocktails
  - GET /cocktails/same-vibe/{id} - Find cocktails in same vibe cluster
  - GET /cocktails/bridge - Find bridge cocktails

- ✅ **Ingredients Endpoints**
  - GET /ingredients/ingredients - List all ingredients
  - GET /ingredients/ingredients/search?q= - Search ingredients
  - POST /ingredients/ingredients/inventory - Update user inventory
  - GET /ingredients/ingredients/inventory/{user_id} - Get user inventory

- ✅ **Planner Endpoints**
  - POST /planner/planner/party-mode - Optimize for maximum cocktails
  - POST /planner/planner/playlist-mode - Optimize for specific cocktails
  - POST /planner/planner/union-ingredients - Get ingredients union

- ✅ **Insights Endpoints**
  - GET /insights/insights/graph - Get graph analysis metrics
  - GET /insights/insights/visualization - Get D3.js visualization data
  - GET /insights/insights/export - Export graph as GEXF
  - GET /insights/insights/components - Analyze disjoint components

### Service Layer Tests

#### Cocktail Service (`test_cocktail_service.py`)
- ✅ Initialization and RDF graph loading
- ✅ Parsing cocktails from RDF graph
- ✅ Getting all cocktails
- ✅ Searching cocktails by name
- ✅ Getting feasible cocktails based on user inventory
- ✅ Getting almost-feasible cocktails (missing 1-2 ingredients)
- ✅ Finding cocktails by ingredients
- ✅ Finding cocktails by ingredient URIs
- ✅ Finding similar cocktails (Jaccard similarity)
- ✅ Finding same-vibe cocktails (community detection)
- ✅ Finding bridge cocktails (spanning communities)
- ✅ Parsing ingredient names from text
- ✅ Extracting ingredient URIs from graph

#### Ingredient Service (`test_ingredient_service.py`)
- ✅ Getting all ingredients from local and DBpedia
- ✅ Searching ingredients by name
- ✅ Getting ingredient by URI
- ✅ Managing user inventories (add, remove, clear)
- ✅ Getting ingredients for cocktails
- ✅ Handling duplicate URIs
- ✅ Fallback to DBpedia when local fails

#### Planner Service (`test_planner_service.py`)
- ✅ Party mode optimization (maximize cocktails with N ingredients)
- ✅ Playlist mode optimization (minimize ingredients for cocktails)
- ✅ Getting union of ingredients for cocktails
- ✅ Handling edge cases (empty lists, invalid names)
- ✅ Greedy set cover algorithm
- ✅ Budget constraints

#### Graph Service (`test_graph_service.py`)
- ✅ Building bipartite graph (cocktails-ingredients)
- ✅ Computing centrality metrics (degree, betweenness, closeness)
- ✅ Community detection (Louvain algorithm)
- ✅ Analyzing disjoint components
- ✅ Generating D3.js visualization data
- ✅ Exporting to GEXF format
- ✅ Finding shortest paths
- ✅ Computing graph statistics

#### SPARQL Service (`test_sparql_service.py`)
- ✅ Executing remote SPARQL queries (DBpedia)
- ✅ Executing local SPARQL queries (RDF graph)
- ✅ Building SPARQL queries
- ✅ Handling timeouts and network errors
- ✅ Parsing query results
- ✅ Loading and parsing Turtle files

### Model Tests (`test_models.py`)
- ✅ Cocktail model validation
- ✅ Ingredient model validation
- ✅ SparqlQuery model validation
- ✅ Required field validation
- ✅ Type validation
- ✅ JSON serialization
- ✅ Model equality
- ✅ Edge cases (long strings, special characters, unicode)

### Error Handling Tests (`test_error_handling.py`)
- ✅ SPARQL service errors (missing files, corrupted data, network timeouts)
- ✅ Cocktail service errors (malformed data, missing graph)
- ✅ Ingredient service errors (service failures, empty results)
- ✅ Graph service errors (build failures, analysis errors)
- ✅ Planner service errors (invalid inputs, optimization failures)
- ✅ Cross-service error propagation
- ✅ Fallback mechanisms
- ✅ Graceful degradation

## Running Tests

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests
```bash
# Simple test run
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Using the provided scripts
./run_tests.sh        # Linux/Mac
run_tests.bat         # Windows
```

### Run Specific Test Files
```bash
# Test API routes only
python -m pytest tests/test_api_routes.py -v

# Test cocktail service only
python -m pytest tests/test_cocktail_service.py -v

# Test a specific test class
python -m pytest tests/test_api_routes.py::TestCocktailsEndpoints -v

# Test a specific test method
python -m pytest tests/test_api_routes.py::TestCocktailsEndpoints::test_get_all_cocktails -v
```

### Run Tests with Different Verbosity
```bash
# Minimal output
python -m pytest tests/ -q

# Verbose output
python -m pytest tests/ -v

# Very verbose (show print statements)
python -m pytest tests/ -vv -s
```

### Run Tests with Coverage
```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=. --cov-report=html

# View report (opens in browser)
# Look in htmlcov/index.html

# Generate terminal coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing
```

### Run Tests by Marker (if using markers)
```bash
# Run only fast tests
python -m pytest tests/ -m fast

# Run only slow tests
python -m pytest tests/ -m slow

# Skip slow tests
python -m pytest tests/ -m "not slow"
```

## Test Statistics

- **Total Test Files**: 8
- **Total Test Classes**: 40+
- **Total Test Methods**: 300+
- **Coverage Target**: >80%

## Key Features Tested

### Discovery Features
✅ Search cocktails by name
✅ Find similar cocktails (ingredient similarity)
✅ Find cocktails in same vibe (community clusters)
✅ Find bridge cocktails (spanning communities)
✅ Search ingredients

### My Bar Features
✅ Manage ingredient inventory
✅ Find feasible cocktails (can make now)
✅ Find almost-feasible cocktails (missing 1-2 ingredients)
✅ Add/remove ingredients from inventory

### Bar Minimum (Optimization)
✅ Party mode - maximize cocktails with N ingredients
✅ Playlist mode - minimize ingredients for specific cocktails
✅ Get union of ingredients for cocktails
✅ Greedy set cover algorithm

### Insights Features
✅ Graph analysis (centrality metrics)
✅ Community detection
✅ Disjoint component analysis
✅ D3.js visualization data generation
✅ GEXF export for Gephi

### Data Layer
✅ Local RDF graph loading (Turtle format)
✅ SPARQL queries (local and DBpedia)
✅ Error handling and fallbacks
✅ Data validation (Pydantic models)

## Continuous Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r backend/requirements.txt
    cd backend
    python -m pytest tests/ -v --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

## Troubleshooting

### Import Errors
If you see import errors, make sure you're running pytest from the backend directory:
```bash
cd backend
python -m pytest tests/
```

### Missing Dependencies
Install all test dependencies:
```bash
pip install pytest pytest-cov httpx rdflib
```

### Slow Tests
Some tests may be slow due to graph operations. To skip slow tests:
```bash
python -m pytest tests/ -k "not slow"
```

## Test Development Guidelines

1. **Naming**: Test methods should start with `test_`
2. **Isolation**: Each test should be independent
3. **Mocking**: Use mocks for external dependencies (DBpedia, file I/O)
4. **Assertions**: Use clear, descriptive assertions
5. **Coverage**: Aim for >80% code coverage
6. **Documentation**: Add docstrings to test classes and methods
7. **Edge Cases**: Test boundary conditions and error cases

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if adding new test files
