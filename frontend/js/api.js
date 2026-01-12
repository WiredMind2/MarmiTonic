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
        
        // Gérer différents formats de réponse
        // Si la reponse est un tableau, le retourner directement   
        if (Array.isArray(data)) {
            return data;
        }

        // Si la réponse est un objet avec une clé 'data' qui est un tableau, le retourner
        if (data && typeof data === 'object' && Array.isArray(data.data)) {
            return data.data;
        }

        // Si la réponse est un objet, le mettre dans un tableau
        if (data && typeof data === 'object' && data.id) {
            return [data];
        }
        
        // Default: return empty array
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