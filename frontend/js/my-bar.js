/**
 * My Bar Page - Inventory Management
 * Handles ingredient selection, filtering, and cocktail matching
 */

(function() {
    'use strict';
    
    // Mock ingredient data (will be replaced with API call later)
    const mockIngredients = [
        // Spirits
        { id: 1, name: "Vodka", category: "spirits", image: "🥃" },
        { id: 2, name: "Gin", category: "spirits", image: "🍸" },
        { id: 3, name: "Rhum Blanc", category: "spirits", image: "🥃" },
        { id: 4, name: "Rhum Brun", category: "spirits", image: "🥃" },
        { id: 5, name: "Tequila", category: "spirits", image: "🥃" },
        { id: 6, name: "Whisky", category: "spirits", image: "🥃" },
        { id: 7, name: "Bourbon", category: "spirits", image: "🥃" },
        { id: 8, name: "Cognac", category: "spirits", image: "🥃" },
        
        // Liqueurs
        { id: 9, name: "Triple Sec", category: "liqueurs", image: "🍊" },
        { id: 10, name: "Cointreau", category: "liqueurs", image: "🍊" },
        { id: 11, name: "Amaretto", category: "liqueurs", image: "🌰" },
        { id: 12, name: "Kahlúa", category: "liqueurs", image: "☕" },
        { id: 13, name: "Baileys", category: "liqueurs", image: "🥛" },
        { id: 14, name: "Campari", category: "liqueurs", image: "🍷" },
        { id: 15, name: "Vermouth Sec", category: "liqueurs", image: "🍷" },
        { id: 16, name: "Vermouth Doux", category: "liqueurs", image: "🍷" },
        
        // Mixers
        { id: 17, name: "Jus de Citron", category: "mixers", image: "🍋" },
        { id: 18, name: "Jus de Lime", category: "mixers", image: "🍋" },
        { id: 19, name: "Jus d'Orange", category: "mixers", image: "🍊" },
        { id: 20, name: "Jus de Cranberry", category: "mixers", image: "🫐" },
        { id: 21, name: "Jus d'Ananas", category: "mixers", image: "🍍" },
        { id: 22, name: "Soda", category: "mixers", image: "🥤" },
        { id: 23, name: "Tonic", category: "mixers", image: "🥤" },
        { id: 24, name: "Cola", category: "mixers", image: "🥤" },
        { id: 25, name: "Ginger Beer", category: "mixers", image: "🥤" },
        
        // Fresh
        { id: 26, name: "Citron", category: "fresh", image: "🍋" },
        { id: 27, name: "Lime", category: "fresh", image: "🍋" },
        { id: 28, name: "Menthe", category: "fresh", image: "🌿" },
        { id: 29, name: "Sucre", category: "fresh", image: "🧂" },
        { id: 30, name: "Sirop Simple", category: "fresh", image: "🍯" },
        { id: 31, name: "Angostura Bitters", category: "fresh", image: "💧" },
        { id: 32, name: "Glaçons", category: "fresh", image: "🧊" },
        
        // Garnish
        { id: 33, name: "Cerises", category: "garnish", image: "🍒" },
        { id: 34, name: "Olives", category: "garnish", image: "🫒" },
        { id: 35, name: "Sel", category: "garnish", image: "🧂" },
        { id: 36, name: "Sucre de Canne", category: "garnish", image: "🧂" }
    ];
    
    // Mock cocktail data with ingredients
    const mockCocktails = [
        { id: 1, name: "Mojito", image: "🍹", ingredients: ["Rhum Blanc", "Lime", "Menthe", "Sucre", "Soda", "Glaçons"] },
        { id: 2, name: "Margarita", image: "🍹", ingredients: ["Tequila", "Triple Sec", "Jus de Lime", "Sel", "Glaçons"] },
        { id: 3, name: "Cosmopolitan", image: "🍸", ingredients: ["Vodka", "Triple Sec", "Jus de Lime", "Jus de Cranberry", "Glaçons"] },
        { id: 4, name: "Gin Tonic", image: "🍸", ingredients: ["Gin", "Tonic", "Citron", "Glaçons"] },
        { id: 5, name: "Old Fashioned", image: "🥃", ingredients: ["Bourbon", "Sucre", "Angostura Bitters", "Cerises", "Glaçons"] },
        { id: 6, name: "Manhattan", image: "🍸", ingredients: ["Whisky", "Vermouth Doux", "Angostura Bitters", "Cerises", "Glaçons"] },
        { id: 7, name: "Martini", image: "🍸", ingredients: ["Gin", "Vermouth Sec", "Olives", "Glaçons"] },
        { id: 8, name: "Piña Colada", image: "🍹", ingredients: ["Rhum Blanc", "Jus d'Ananas", "Glaçons"] },
        { id: 9, name: "Daiquiri", image: "🍹", ingredients: ["Rhum Blanc", "Jus de Lime", "Sirop Simple", "Glaçons"] },
        { id: 10, name: "Moscow Mule", image: "🍺", ingredients: ["Vodka", "Ginger Beer", "Lime", "Glaçons"] },
        { id: 11, name: "Negroni", image: "🍷", ingredients: ["Gin", "Campari", "Vermouth Doux", "Glaçons"] },
        { id: 12, name: "Whisky Sour", image: "🥃", ingredients: ["Whisky", "Jus de Citron", "Sirop Simple", "Glaçons"] },
        { id: 13, name: "Cuba Libre", image: "🥃", ingredients: ["Rhum Blanc", "Cola", "Lime", "Glaçons"] },
        { id: 14, name: "Screwdriver", image: "🍊", ingredients: ["Vodka", "Jus d'Orange", "Glaçons"] },
        { id: 15, name: "Tequila Sunrise", image: "🌅", ingredients: ["Tequila", "Jus d'Orange", "Glaçons"] }
    ];
    
    // State
    let selectedIngredients = new Set();
    let currentCategory = 'all';
    let currentIngredients = mockIngredients;
    
    /**
     * Initialize the My Bar page
     */
    function init() {
        renderIngredients();
        setupEventListeners();
        console.log('My Bar page initialized');
    }
    
    /**
     * Setup all event listeners
     */
    function setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('ingredientSearch');
        if (searchInput) {
            searchInput.addEventListener('input', handleSearch);
        }
        
        // Category filters
        document.querySelectorAll('.category-filter').forEach(btn => {
            btn.addEventListener('click', handleCategoryFilter);
        });
        
        // Clear all button
        const clearButton = document.getElementById('clearAll');
        if (clearButton) {
            clearButton.addEventListener('click', clearAllIngredients);
        }
        
        // Find cocktails button
        const findButton = document.getElementById('findCocktails');
        if (findButton) {
            findButton.addEventListener('click', findCocktails);
        }
        
        // Sort select
        const sortSelect = document.getElementById('sortBy');
        if (sortSelect) {
            sortSelect.addEventListener('change', handleSortChange);
        }
    }
    
    /**
     * Handle search input
     */
    function handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        const filtered = mockIngredients.filter(ing => 
            ing.name.toLowerCase().includes(searchTerm)
        );
        renderIngredients(filtered);
    }
    
    /**
     * Handle category filter clicks
     */
    function handleCategoryFilter(e) {
        document.querySelectorAll('.category-filter').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentCategory = e.target.dataset.category;
        filterByCategory(currentCategory);
    }
    
    /**
     * Filter ingredients by category
     */
    function filterByCategory(category) {
        if (category === 'all') {
            currentIngredients = mockIngredients;
        } else {
            currentIngredients = mockIngredients.filter(ing => ing.category === category);
        }
        renderIngredients(currentIngredients);
    }
    
    /**
     * Clear all selected ingredients
     */
    function clearAllIngredients() {
        selectedIngredients.clear();
        updateSelectionCount();
        renderIngredients();
    }
    
    /**
     * Render ingredients list
     */
    function renderIngredients(ingredients = currentIngredients) {
        const container = document.getElementById('ingredientList');
        if (!container) return;
        
        container.innerHTML = '';
        
        ingredients.forEach(ingredient => {
            const div = document.createElement('div');
            div.className = 'ingredient-item';
            div.innerHTML = `
                <label class="ingredient-checkbox">
                    <input type="checkbox" 
                           id="ing-${ingredient.id}" 
                           value="${ingredient.name}"
                           ${selectedIngredients.has(ingredient.name) ? 'checked' : ''}>
                    <span class="ingredient-icon">${ingredient.image}</span>
                    <span class="ingredient-name">${ingredient.name}</span>
                    <span class="checkmark"></span>
                </label>
            `;
            
            const checkbox = div.querySelector('input');
            checkbox.addEventListener('change', (e) => handleIngredientToggle(e, ingredient.name));
            
            container.appendChild(div);
        });
    }
    
    /**
     * Handle ingredient checkbox toggle
     */
    function handleIngredientToggle(e, ingredientName) {
        if (e.target.checked) {
            selectedIngredients.add(ingredientName);
        } else {
            selectedIngredients.delete(ingredientName);
        }
        updateSelectionCount();
    }
    
    /**
     * Update selection count display
     */
    function updateSelectionCount() {
        const countElement = document.getElementById('selectionCount');
        if (countElement) {
            countElement.textContent = `${selectedIngredients.size} ingrédient(s) sélectionné(s)`;
        }
    }
    
    /**
     * Find cocktails based on selected ingredients
     */
    function findCocktails() {
        if (selectedIngredients.size === 0) {
            alert('Veuillez sélectionner au moins un ingrédient');
            return;
        }
        
        const results = mockCocktails.map(cocktail => {
            const missingIngredients = cocktail.ingredients.filter(ing => 
                !selectedIngredients.has(ing)
            );
            const matchingIngredients = cocktail.ingredients.filter(ing => 
                selectedIngredients.has(ing)
            );
            
            return {
                ...cocktail,
                missingCount: missingIngredients.length,
                missingIngredients,
                matchingIngredients,
                canMake: missingIngredients.length === 0
            };
        });
        
        sortAndRenderResults(results);
    }
    
    /**
     * Handle sort change
     */
    function handleSortChange() {
        const resultsContainer = document.getElementById('cocktailResults');
        if (resultsContainer && resultsContainer.querySelectorAll('.my-bar-cocktail-card').length > 0) {
            findCocktails();
        }
    }
    
    /**
     * Sort and render cocktail results
     */
    function sortAndRenderResults(results) {
        const sortBy = document.getElementById('sortBy')?.value || 'makeable';
        
        results.sort((a, b) => {
            if (sortBy === 'makeable') {
                if (a.canMake !== b.canMake) return a.canMake ? -1 : 1;
                return a.missingCount - b.missingCount;
            } else if (sortBy === 'missing') {
                return a.missingCount - b.missingCount;
            } else {
                return a.name.localeCompare(b.name);
            }
        });
        
        renderCocktailResults(results);
    }
    
    /**
     * Render cocktail results
     */
    function renderCocktailResults(results) {
        const container = document.getElementById('cocktailResults');
        if (!container) return;
        
        container.innerHTML = '';
        
        const makeable = results.filter(r => r.canMake);
        const almostMakeable = results.filter(r => !r.canMake && r.missingCount <= 2);
        
        if (makeable.length > 0) {
            const section = createResultSection('✅ Cocktails Réalisables', makeable);
            container.appendChild(section);
        }
        
        if (almostMakeable.length > 0) {
            const section = createResultSection('⚠️ Presque Réalisables', almostMakeable);
            container.appendChild(section);
        }
        
        if (makeable.length === 0 && almostMakeable.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa fa-frown-o"></i>
                    <p>Aucun cocktail ne correspond à votre sélection</p>
                    <small>Essayez d'ajouter plus d'ingrédients à votre bar</small>
                </div>
            `;
        }
    }
    
    /**
     * Create a result section
     */
    function createResultSection(title, cocktails) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `<h3 class="result-section-title">${title} (${cocktails.length})</h3>`;
        
        cocktails.forEach(cocktail => {
            section.appendChild(createCocktailCard(cocktail));
        });
        
        return section;
    }
    
    /**
     * Create cocktail card element
     */
    function createCocktailCard(cocktail) {
        const div = document.createElement('div');
        div.className = `my-bar-cocktail-card ${cocktail.canMake ? 'can-make' : 'almost-make'}`;
        
        const missingText = cocktail.canMake 
            ? '<span class="badge-success">Tous les ingrédients disponibles !</span>'
            : `<span class="badge-warning">Il manque ${cocktail.missingCount} ingrédient(s): ${cocktail.missingIngredients.join(', ')}</span>`;
        
        div.innerHTML = `
            <div class="cocktail-icon">${cocktail.image}</div>
            <div class="cocktail-info">
                <h4 class="cocktail-name">${cocktail.name}</h4>
                <div class="cocktail-status">${missingText}</div>
                <div class="ingredient-chips">
                    ${cocktail.ingredients.map(ing => 
                        `<span class="chip ${selectedIngredients.has(ing) ? 'chip-have' : 'chip-need'}">${ing}</span>`
                    ).join('')}
                </div>
            </div>
        `;
        
        return div;
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
