// API calls to the backend
const API_BASE_URL = 'http://localhost:8000';

async function fetchCocktails() {
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails`);
        if (!response.ok) {
            throw new Error('Failed to fetch cocktails');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error executing SPARQL query:', error);
        return [];
    }
}

async function optimizePlaylistMode(cocktailNames) {
    try {
        const response = await fetch(`${API_BASE_URL}/planner/playlist-mode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cocktail_names: cocktailNames }),
        });
        if (!response.ok) {
            throw new Error('Failed to optimize playlist mode');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error optimizing playlist mode:', error);
        throw error;
    }
}

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

// Rechercher un cocktail avec son nom
async function searchCocktails(query) {
    if (!query || query.trim() === '') {
        return [];
    }
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Failed to search cocktails');
        }
        const data = await response.json();
        
        // Si la reponse est un tableau, le retourner directement   
        if (Array.isArray(data)) {
            return data;
        }

        if (data && typeof data === 'object' && Array.isArray(data.data)) {
            return data.data;
        }

        if (data && typeof data === 'object' && data.id) {
            return [data];
        }
        
        console.warn('Unexpected search response format:', data);
        return [];
    } catch (error) {
        console.error('Error searching cocktails:', error);
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

// Get a random cocktail
async function fetchRandomCocktail() {
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails/random`);
        if (!response.ok) {
            throw new Error('Failed to fetch random cocktail');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching random cocktail:', error);
        return null;
    }
}

// Get vibe clusters with cocktails
async function fetchVibeClusters(nClusters = 3) {
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails/clusters?n_clusters=${nClusters}&with_cocktails=true`);
        if (!response.ok) {
            throw new Error('Failed to fetch vibe clusters');
        }
        const data = await response.json();
        return data.clusters || [];
    } catch (error) {
        console.error('Error fetching vibe clusters:', error);
        return [];
    }
}