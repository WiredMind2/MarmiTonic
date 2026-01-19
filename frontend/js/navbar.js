/**
 * Navbar functionality - Shared across all pages
 * Handles navbar scroll behavior, menu toggle, and search functionality
 */

(function() {
    'use strict';
    
    let prevScrollPos = window.pageYOffset;
    const navbar = document.getElementById('navbar');
    const menuNoNavbar = document.getElementById('no-navbar-menu');
    const searchInput = document.querySelector('.navbar-right input[type="text"]');
    
    function init() {
        if (menuNoNavbar) {
            menuNoNavbar.style.display = 'none';
            setupMenuToggle();
        }
        
        setupScrollBehavior();
        setupSearchFunctionality();
    }
    
    function setupMenuToggle() {
        menuNoNavbar.onclick = function() {
            if (navbar) {
                navbar.classList.remove('hide');
                menuNoNavbar.style.display = 'none';
            }
        };
    }
    
    function setupSearchFunctionality() {
        if (!searchInput) return;
        
        let searchTimeout;
        let searchResultsDropdown;
        
        function createDropdown() {
            const dropdown = document.createElement('div');
            dropdown.className = 'search-results-dropdown';
            dropdown.style.display = 'none';
            searchInput.parentElement.appendChild(dropdown);
            return dropdown;
        }
        
        searchResultsDropdown = createDropdown();
        
        searchResultsDropdown.addEventListener('mouseenter', () => {
            searchResultsDropdown.classList.add('dropdown-hovered');
        });
        
        searchResultsDropdown.addEventListener('mouseleave', () => {
            searchResultsDropdown.classList.remove('dropdown-hovered');
            searchResultsDropdown.style.display = 'none';
        });
        
        searchInput.addEventListener('input', async (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length === 0) {
                searchResultsDropdown.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(async () => {
                try {
                    const results = await searchCocktails(query);
                    console.log('Search results for "' + query + '":', results);
                    displaySearchResults(results, searchResultsDropdown);
                } catch (error) {
                    console.error('Search error:', error);
                    searchResultsDropdown.innerHTML = '<div class="search-no-results">Erreur lors de la recherche</div>';
                    searchResultsDropdown.style.display = 'block';
                }
            }, 300);
        });
        
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                if (!searchResultsDropdown.classList.contains('dropdown-hovered')) {
                    searchResultsDropdown.style.display = 'none';
                }
            }, 300);
        });
        
        searchInput.addEventListener('focus', async (e) => {
            const query = e.target.value.trim();
            if (query.length > 0 && searchResultsDropdown.innerHTML !== '') {
                searchResultsDropdown.style.display = 'block';
            }
        });
    }
    
    function fuzzyScore(text, query) {
        text = text.toLowerCase();
        query = query.toLowerCase();
        
        let score = 0;
        let lastIndex = -1;
        
        if (text.startsWith(query)) {
            return 1000 + text.length - query.length;
        }
        
        for (let i = 0; i < query.length; i++) {
            const char = query[i];
            const index = text.indexOf(char, lastIndex + 1);
            
            if (index === -1) {
                return -1; // Caractère non trouvé
            }
            
            if (lastIndex === -1 || index === lastIndex + 1) {
                score += 10;
            }
            // Préférer les caractères près du début
            else if (index < text.length / 2) {
                score += 5;
            } else {
                score += 2;
            }
            
            lastIndex = index;
        }
        
        return score;
    }
    
    function highlightMatches(text, query) {
        const lowerText = text.toLowerCase();
        const lowerQuery = query.toLowerCase();
        let queryIndex = 0;
        let result = '';
        
        for (let i = 0; i < text.length; i++) {
            if (queryIndex < lowerQuery.length && lowerText[i] === lowerQuery[queryIndex]) {
                result += `<span class="search-highlight">${text[i]}</span>`;
                queryIndex++;
            } else {
                result += text[i];
            }
        }
        
        return result;
    }
    
    function displaySearchResults(results, dropdown) {
        const query = searchInput.value.trim();
        
        console.log('Affichage des résultats:', {
            query,
            resultsCount: results ? results.length : 0,
            resultsType: Array.isArray(results) ? 'array' : typeof results
        });
        
        if (!results || results.length === 0) {
            dropdown.innerHTML = '<div class="search-no-results">Aucun cocktail trouvé</div>';
            dropdown.style.display = 'block';
            return;
        }
        
        // Scorer et trier les résultats selon la recherche floue
        const scoredResults = results.map(cocktail => ({
            cocktail,
            score: fuzzyScore(cocktail.name, query)
        })).filter(item => item.score > 0);
        
        console.log('Après scoring fuzzy:', {
            scoredCount: scoredResults.length,
            scores: scoredResults.map(r => ({ name: r.cocktail.name, score: r.score }))
        });
        
        // Trier par score décroissant
        scoredResults.sort((a, b) => b.score - a.score);
        
        // Limiter à 8 résultats
        const limitedResults = scoredResults.slice(0, 8).map(item => item.cocktail);
        
        dropdown.innerHTML = limitedResults.map((cocktail, index) => {
            const highlightedName = highlightMatches(cocktail.name, query);
            // Utiliser l'image du cocktail ou une image par défaut
            const imageUrl = cocktail.image || `https://images.unsplash.com/photo-1536935338788-846bb9981813?w=200&h=200&fit=crop`;
            
            return `
            <div class="search-result-item" data-index="${index}">
                <div class="search-result-image">
                    <img src="${imageUrl}" alt="${cocktail.name}" onerror="this.src='https://images.unsplash.com/photo-1536935338788-846bb9981813?w=200&h=200&fit=crop'">
                </div>
                <div class="search-result-info">
                    <div class="search-result-name">${highlightedName}</div>
                    <div class="search-result-category">${cocktail.description ? cocktail.description.substring(0, 60) : 'Cocktail classique'}</div>
                </div>
            </div>
        `
        }).join('');
        
        dropdown.style.display = 'block';
        
        dropdown.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Empêcher le blur de l'input
                const index = parseInt(item.dataset.index);
                const selectedCocktail = limitedResults[index];
                navigateToCocktailDetail(selectedCocktail);
            });
        });
    }
    
    // Naviguer vers la page de détail du cocktail
    function navigateToCocktailDetail(cocktail) {
        sessionStorage.setItem('selectedCocktail', JSON.stringify(cocktail));
        
        let detailPagePath = '../pages/cocktail-detail.html';
        
        if (window.location.pathname.includes('/pages/')) {
            detailPagePath = './cocktail-detail.html';
        }
        else if (window.location.pathname.endsWith('/index.html') || window.location.pathname.endsWith('/')) {
            detailPagePath = 'pages/cocktail-detail.html';
        }
        
        window.location.href = detailPagePath + '?id=' + encodeURIComponent(cocktail.id);
    }
    
    function setupScrollBehavior() {
        window.addEventListener('scroll', function() {
            const currentScrollPos = window.pageYOffset;
            
            if (navbar && menuNoNavbar) {
                if (prevScrollPos > currentScrollPos || currentScrollPos < 50) {
                    navbar.classList.remove('hide');
                    menuNoNavbar.style.display = 'none';
                } else {
                    navbar.classList.add('hide');
                    menuNoNavbar.style.display = 'flex';
                }
            }
            
            prevScrollPos = currentScrollPos;
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
