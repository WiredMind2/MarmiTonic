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

// Recherche de cocktails similaires par ID
async function fetchSimilarCocktails(cocktailId, topK = 5) {
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails/similar/${cocktailId}?top_k=${topK}`);
        if (!response.ok) {
            throw new Error('Failed to fetch similar cocktails');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching similar cocktails:', error);
        return { similar_cocktails: [] };
    }
}

// Recherche sémantique de cocktails
async function searchCocktailsSemantic(query, topK = 5) {
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails/search-semantic?query=${encodeURIComponent(query)}&top_k=${topK}`);
        if (!response.ok) {
            throw new Error('Failed to perform semantic search');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error in semantic search:', error);
        return { results: [] };
    }
}

// Recherche de cocktails similaires par ingrédients
async function fetchSimilarByIngredients(ingredients, topK = 5) {
    try {
        const params = new URLSearchParams();
        ingredients.forEach(ingredient => {
            params.append('ingredients', ingredient);
        });
        params.append('top_k', topK);
        
        const response = await fetch(`${API_BASE_URL}/cocktails/similar-by-ingredients?${params}`);
        if (!response.ok) {
            throw new Error('Failed to fetch similar cocktails by ingredients');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching similar cocktails by ingredients:', error);
        return { similar_cocktails: [] };
    }
}

// Construire l'index de similarité
async function buildSimilarityIndex(forceRebuild = false) {
    try {
        console.log('Building similarity index...');
        const response = await fetch(`${API_BASE_URL}/cocktails/build-index?force_rebuild=${forceRebuild}`, {
            method: 'POST'
        });
        if (!response.ok) {
            throw new Error('Failed to build similarity index');
        }
        console.log('Similarity index built successfully');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error building similarity index:', error);
        return { status: 'error', message: error.message };
    }
}