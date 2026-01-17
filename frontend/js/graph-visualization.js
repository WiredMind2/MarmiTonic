// Graph Visualization Page JavaScript
// Handles D3.js graph visualization with interactive controls

class GraphVisualizationPage {
    constructor() {
        this.graph = null;
        this.currentData = null;
        this.isGraphLoaded = false;
        
        // DOM elements
        this.elements = {
            graphContainer: document.getElementById('graph-container'),
            loadBtn: document.getElementById('load-graph'),
            highlightBtn: document.getElementById('highlight-components'),
            clearBtn: document.getElementById('clear-graph'),
            forceSlider: document.getElementById('force-strength'),
            distanceSlider: document.getElementById('distance'),
            chargeSlider: document.getElementById('charge'),
            forceValue: document.getElementById('force-value'),
            distanceValue: document.getElementById('distance-value'),
            chargeValue: document.getElementById('charge-value'),
            metricsSection: document.getElementById('metrics-section'),
            legendSection: document.getElementById('legend-section'),
            nodesCount: document.getElementById('nodes-count'),
            linksCount: document.getElementById('links-count'),
            cocktailsCount: document.getElementById('cocktails-count'),
            ingredientsCount: document.getElementById('ingredients-count'),
            
            // NL & SPARQL controls
            nlInput: document.getElementById('nl-query-input'),
            nlToSparqlBtn: document.getElementById('nl-to-sparql-btn'),
            sparqlOutput: document.getElementById('sparql-output'),
            executeSparqlBtn: document.getElementById('execute-sparql-btn')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Main control buttons
        this.elements.loadBtn.addEventListener('click', () => this.loadGraph());
        this.elements.highlightBtn.addEventListener('click', () => this.highlightComponents());
        this.elements.clearBtn.addEventListener('click', () => this.clearGraph());
        
        // Slider controls
        this.elements.forceSlider.addEventListener('input', (e) => {
            this.elements.forceValue.textContent = e.target.value;
            this.updateForceParameters();
        });
        
        this.elements.distanceSlider.addEventListener('input', (e) => {
            this.elements.distanceValue.textContent = e.target.value;
            this.updateForceParameters();
        });
        
        this.elements.chargeSlider.addEventListener('input', (e) => {
            this.elements.chargeValue.textContent = e.target.value;
            this.updateForceParameters();
        });
        
        // API-based data buttons
        if (this.elements.apiAllCocktails) {
            this.elements.apiAllCocktails.addEventListener('click', () => this.loadAllCocktails());
        }

        // NL & SPARQL listeners
        if (this.elements.nlToSparqlBtn) {
            this.elements.nlToSparqlBtn.addEventListener('click', () => this.convertNlToSparql());
        }
        if (this.elements.executeSparqlBtn) {
            this.elements.executeSparqlBtn.addEventListener('click', () => this.executeSparqlGraph());
        }
    }
    
    async convertNlToSparql() {
        const prompt = this.elements.nlInput.value.trim();
        if (!prompt) {
            alert('Veuillez entrer une question.');
            return;
        }

        this.elements.nlToSparqlBtn.disabled = true;
        this.elements.nlToSparqlBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Conversion...';

        try {
            const response = await fetch('http://localhost:8000/llm/nl2sparql', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: prompt })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erreur lors de la conversion');
            }

            const data = await response.json();
            this.elements.sparqlOutput.value = data.sparql_query;
            this.elements.executeSparqlBtn.disabled = false;
        } catch (error) {
            console.error('Error converting to SPARQL:', error);
            alert(`Erreur: ${error.message}`);
        } finally {
            this.elements.nlToSparqlBtn.disabled = false;
            this.elements.nlToSparqlBtn.innerHTML = '<i class="fa fa-magic"></i> NL -> SPARQL';
        }
    }

    async executeSparqlGraph() {
        const query = this.elements.sparqlOutput.value.trim();
        if (!query) {
            alert('Aucune requête SPARQL à exécuter.');
            return;
        }

        this.elements.executeSparqlBtn.disabled = true;
        this.elements.executeSparqlBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Exécution...';
        this.showLoadingState();

        try {
            const response = await fetch('http://localhost:8000/graphs/sparql', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erreur lors de l\'exécution');
            }

            const data = await response.json();
            
            if (data && data.nodes && data.nodes.length > 0) {
                this.loadData(data);
                console.log(`Loaded ${data.nodes.length} nodes from SPARQL`);
            } else {
                alert('Aucun résultat trouvé pour cette requête (ou format incompatible avec le graphe).');
                this.clearGraph();
            }

        } catch (error) {
            console.error('Error executing SPARQL graph:', error);
            alert(`Erreur: ${error.message}`);
        } finally {
            this.elements.executeSparqlBtn.disabled = false;
            this.elements.executeSparqlBtn.innerHTML = '<i class="fa fa-play"></i> Exécuter SPARQL';
            this.hideLoadingState();
        }
    }
    
    async loadAllCocktails() {
        this.showLoadingState();
        
        try {
            // Fetch all cocktails
            const cocktails = await fetchCocktails();
            
            if (!cocktails || cocktails.length === 0) {
                throw new Error('No cocktails found');
            }
            
            // Try to fetch ingredients, but continue if they fail
            let ingredients = [];
            try {
                ingredients = await fetchIngredients();
            } catch (ingredientError) {
                console.warn('Could not fetch ingredients, using cocktail data only:', ingredientError);
            }
            
            // Build comprehensive graph data
            const data = this.buildComprehensiveGraph(cocktails, ingredients);
            
            if (data && data.nodes.length > 0) {
                this.loadData(data);
            } else {
                throw new Error('No valid graph data could be constructed');
            }
        } catch (error) {
            console.error('Error loading all cocktails:', error);
            alert(`Erreur lors du chargement des données: ${error.message}`);
        } finally {
            this.hideLoadingState();
        }
    }
    
    buildCocktailGraph(cocktail) {
        const nodes = [];
        const links = [];
        
        // Add cocktail node
        nodes.push({
            id: cocktail.name,
            name: cocktail.name,
            type: 'cocktail'
        });
        
        // Add ingredient nodes and links
        const ingredients = cocktail.parsed_ingredients || cocktail.ingredients;
        if (ingredients && Array.isArray(ingredients)) {
            ingredients.forEach(ingredientRef => {
                const ingredientName = typeof ingredientRef === 'string' ? ingredientRef : ingredientRef.name;
                
                // Add ingredient node if not exists
                if (!nodes.find(n => n.id === ingredientName)) {
                    nodes.push({
                        id: ingredientName,
                        name: ingredientName,
                        type: 'ingredient'
                    });
                }
                
                // Add link
                links.push({
                    source: cocktail.name,
                    target: ingredientName,
                    value: 1
                });
            });
        }
        
        return { nodes, links };
    }
    
    buildComprehensiveGraph(cocktails) {
        const nodes = [];
        const links = [];
        const nodeIds = new Set();
        
        // Add all cocktails
        cocktails.forEach(cocktail => {
            if (!nodeIds.has(cocktail.name)) {
                nodes.push({
                    id: cocktail.name,
                    name: cocktail.name,
                    type: 'cocktail'
                });
                nodeIds.add(cocktail.name);
            }
        });
        
        // Add all ingredients and their connections
        cocktails.forEach(cocktail => {
            const ingredients = cocktail.parsed_ingredients || cocktail.ingredients;
            if (ingredients && Array.isArray(ingredients)) {
                ingredients.forEach(ingredientRef => {
                    const ingredientName = typeof ingredientRef === 'string' ? ingredientRef : ingredientRef.name;
                    
                    // Add ingredient node
                    if (!nodeIds.has(ingredientName)) {
                        nodes.push({
                            id: ingredientName,
                            name: ingredientName,
                            type: 'ingredient'
                        });
                        nodeIds.add(ingredientName);
                    }
                    
                    // Add link
                    links.push({
                        source: cocktail.name,
                        target: ingredientName,
                        value: 1
                    });
                });
            }
        });
        
        return { nodes, links };
    }
    
    showLoadingState() {
        if (this.elements.loadBtn) {
            this.elements.loadBtn.classList.add('loading');
            this.elements.loadBtn.disabled = true;
        }
    }
    
    hideLoadingState() {
        if (this.elements.loadBtn) {
            this.elements.loadBtn.classList.remove('loading');
            this.elements.loadBtn.disabled = false;
        }
    }
    
    
    async loadGraph() {
        await this.loadAllCocktails();
    }
    
    loadData(data) {
        if (!data || !data.nodes || !data.links) {
            console.error('Invalid data format');
            return;
        }
        
        this.currentData = data;
        
        // Clear existing graph
        if (this.graph) {
            this.graph.destroy();
        }
        
        // Remove empty state
        this.elements.graphContainer.innerHTML = '';
        
        // Initialize new graph
        const width = this.elements.graphContainer.clientWidth;
        const height = this.elements.graphContainer.clientHeight;
        
        this.graph = new D3DisjointForceGraph('#graph-container', width, height);
        this.graph.updateData(data);
        
        // Update UI state
        this.isGraphLoaded = true;
        this.updateUIState();
        this.updateMetrics(data);
        
        console.log('Graph loaded successfully:', data);
    }
    
    highlightComponents() {
        if (!this.graph || !this.isGraphLoaded) return;
        
        this.graph.highlightDisjointComponents();
    }
    
    clearGraph() {
        if (this.graph) {
            this.graph.destroy();
            this.graph = null;
        }
        
        this.currentData = null;
        this.isGraphLoaded = false;
        
        // Restore empty state
        this.elements.graphContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa fa-project-diagram"></i>
                <h3>Aucun graphe chargé</h3>
                <p>Cliquez sur "Charger le Graphe" pour visualiser les relations entre cocktails et ingrédients</p>
            </div>
        `;
        
        this.updateUIState();
    }
    
    updateForceParameters() {
        if (!this.graph || !this.isGraphLoaded) return;
        
        const forceStrength = parseFloat(this.elements.forceSlider.value);
        const distance = parseInt(this.elements.distanceSlider.value);
        const charge = parseInt(this.elements.chargeSlider.value);
        
        this.graph.setForceParameters(forceStrength, distance, charge);
    }
    
    updateUIState() {
        const controls = [
            this.elements.highlightBtn,
            this.elements.clearBtn,
            this.elements.forceSlider,
            this.elements.distanceSlider,
            this.elements.chargeSlider
        ];
        
        controls.forEach(control => {
            if (control) {
                control.disabled = !this.isGraphLoaded;
            }
        });
        
        // Show/hide sections
        if (this.elements.metricsSection) {
            this.elements.metricsSection.style.display = this.isGraphLoaded ? 'block' : 'none';
        }
        
        if (this.elements.legendSection) {
            this.elements.legendSection.style.display = this.isGraphLoaded ? 'block' : 'none';
        }
    }
    
    updateMetrics(data) {
        if (!data || !data.nodes || !data.links) return;
        
        const nodesCount = data.nodes.length;
        const linksCount = data.links.length;
        const cocktailsCount = data.nodes.filter(n => n.type === 'cocktail').length;
        const ingredientsCount = data.nodes.filter(n => n.type === 'ingredient').length;
        
        if (this.elements.nodesCount) {
            this.elements.nodesCount.textContent = nodesCount;
        }
        if (this.elements.linksCount) {
            this.elements.linksCount.textContent = linksCount;
        }
        if (this.elements.cocktailsCount) {
            this.elements.cocktailsCount.textContent = cocktailsCount;
        }
        if (this.elements.ingredientsCount) {
            this.elements.ingredientsCount.textContent = ingredientsCount;
        }
    }
}

// Initialize the page when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new GraphVisualizationPage();
    console.log('Graph Visualization Page initialized');
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    const graphContainer = document.getElementById('graph-container');
    if (graphContainer && window.graphVisualizationPage) {
        // Cleanup any D3 simulations
        const svg = graphContainer.querySelector('svg');
        if (svg) {
            svg.remove();
        }
    }
});