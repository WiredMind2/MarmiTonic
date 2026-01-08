/**
 * My Bar Page - Inventory Management
 * Handles ingredient selection, filtering, and cocktail matching
 */

(function() {
    'use strict';
    
    // User ID handling: generate or read from localStorage
    let marmitonicUserId = null;
    function getOrCreateUserId() {
        const key = 'marmitonic_user_id';
        let id = localStorage.getItem(key);
        if (!id) {
            if (window.crypto && crypto.randomUUID) id = crypto.randomUUID();
            else id = 'u-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2,10);
            localStorage.setItem(key, id);
        }
        return id;
    }

    // Save inventory to backend (debounced)
    let saveTimer = null;
    function scheduleSaveInventory(delay = 800) {
        if (!marmitonicUserId) return;
        if (saveTimer) clearTimeout(saveTimer);
        saveTimer = setTimeout(() => saveInventory(), delay);
    }

    async function saveInventory() {
        if (!marmitonicUserId) return;
        try {
            const body = { user_id: marmitonicUserId, ingredients: Array.from(selectedIngredients) };
            await fetch(`${API_BASE_URL}/ingredients/inventory`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        } catch (err) {
            console.error('Failed to save inventory:', err);
        }
    }

    async function loadInventory() {
        if (!marmitonicUserId) return;
        try {
            const res = await fetch(`${API_BASE_URL}/ingredients/inventory/${marmitonicUserId}`);
            if (!res.ok) return;
            const data = await res.json();
            if (data && Array.isArray(data.ingredients)) {
                selectedIngredients = new Set(data.ingredients);
                updateSelectionCount();
            }
        } catch (err) {
            console.error('Failed to load inventory:', err);
        }
    }
    
    // State
    let selectedIngredients = new Set();
    let currentCategory = 'all';
    let currentIngredients = [];
    let allCocktails = [];
    
    /**
     * Initialize the My Bar page
     */
    async function init() {
        marmitonicUserId = getOrCreateUserId();
        setupEventListeners();
        // Load data from backend
        try {
            const [ings, cocktails] = await Promise.all([fetchIngredients(), fetchCocktails()]);
            // Normalize ingredients list
            currentIngredients = (ings || []).map(i => ({
                id: i.id,
                name: i.name,
                image: i.image || '🍸',
                categories: i.categories || []
            }));
            allCocktails = (cocktails || []).map(c => c);
        } catch (err) {
            console.error('Failed to load ingredients or cocktails:', err);
            currentIngredients = [];
            allCocktails = [];
        }

        // Load saved inventory then render
        await loadInventory();
        renderIngredients();
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
        const filtered = currentIngredients.filter(ing => 
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
            // keep full list loaded from backend
        } else {
            // Filter by categories array if present
            currentIngredients = currentIngredients.filter(ing => Array.isArray(ing.categories) && ing.categories.some(c => c.toLowerCase().includes(category.toLowerCase())));
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
        // Persist change to backend (debounced)
        scheduleSaveInventory();
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
    function normalizeName(s) {
        return (s || '').toString().toLowerCase().trim();
    }

    function getCocktailIngredientNames(cocktail) {
        if (Array.isArray(cocktail.parsed_ingredients) && cocktail.parsed_ingredients.length) return cocktail.parsed_ingredients;
        if (typeof cocktail.ingredients === 'string' && cocktail.ingredients.length) {
            // crude parse: split lines and remove bullets/quantities
            return cocktail.ingredients.split('\n').map(l => l.replace(/^\s*[\*\-•]?\s*/, '').replace(/^[0-9\.]+\s*(ml|cl|oz|dash|tsp|teaspoon|tablespoon)?\s*/i, '').trim()).filter(Boolean);
        }
        return [];
    }

    function findCocktails() {
        if (selectedIngredients.size === 0) {
            alert('Veuillez sélectionner au moins un ingrédient');
            return;
        }

        // use normalized selected set for comparisons
        const selectedNorm = new Set(Array.from(selectedIngredients).map(normalizeName));

        const results = allCocktails.map(cocktail => {
            const ingNames = getCocktailIngredientNames(cocktail);
            const missing = ingNames.filter(ing => !selectedNorm.has(normalizeName(ing)));
            const matching = ingNames.filter(ing => selectedNorm.has(normalizeName(ing)));
            return {
                ...cocktail,
                ingredients: ingNames,
                missingCount: missing.length,
                missingIngredients: missing,
                matchingIngredients: matching,
                canMake: missing.length === 0
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
        const almostMakeable = results.filter(r => !r.canMake && r.missingCount === 1 && Array.isArray(r.matchingIngredients) && r.matchingIngredients.length > 0);
        
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
                    ${ (cocktail.ingredients || []).map(ing => 
                        `<span class="chip ${selectedIngredients.has(ing) || selectedIngredients.has(ing) ? 'chip-have' : 'chip-need'}">${ing}</span>`
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
