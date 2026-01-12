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
    
    // Initialize
    function init() {
        if (menuNoNavbar) {
            menuNoNavbar.style.display = 'none';
            setupMenuToggle();
        }
        
        setupScrollBehavior();
        setupSearchFunctionality();
    }
    
    // Setup menu toggle functionality
    function setupMenuToggle() {
        menuNoNavbar.onclick = function() {
            if (navbar) {
                navbar.classList.remove('hide');
                menuNoNavbar.style.display = 'none';
            }
        };
    }
    
    // Fonctionnalité de recherche
    function setupSearchFunctionality() {
        if (!searchInput) return;
        
        let searchTimeout;
        let searchResultsDropdown;
        
        // Créer le dropdown des résultats de recherche
        function createDropdown() {
            const dropdown = document.createElement('div');
            dropdown.className = 'search-results-dropdown';
            dropdown.style.display = 'none';
            searchInput.parentElement.appendChild(dropdown);
            return dropdown;
        }
        
        searchResultsDropdown = createDropdown();
        
        // Gérer les changements d'entrée
        searchInput.addEventListener('input', async (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length === 0) {
                searchResultsDropdown.style.display = 'none';
                return;
            }
            
            // ébouncer la recherche
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
        
        // Fermer le dropdown au blur
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                searchResultsDropdown.style.display = 'none';
            }, 200);
        });
        
        // Focus to show results again
        searchInput.addEventListener('focus', async (e) => {
            const query = e.target.value.trim();
            if (query.length > 0 && searchResultsDropdown.innerHTML !== '') {
                searchResultsDropdown.style.display = 'block';
            }
        });
    }
    
    // Score de recherche floue - trouve les lettres n'importe où dans la chaîne
    function fuzzyScore(text, query) {
        text = text.toLowerCase();
        query = query.toLowerCase();
        
        let score = 0;
        let lastIndex = -1;
        
        // Vérifier si la requête commence par le texte (priorité la plus élevée)
        if (text.startsWith(query)) {
            return 1000 + text.length - query.length;
        }
        
        // Vérifier chaque caractère de la requête dans le texte
        for (let i = 0; i < query.length; i++) {
            const char = query[i];
            const index = text.indexOf(char, lastIndex + 1);
            
            if (index === -1) {
                return -1; // Caractère non trouvé
            }
            
            // Préférer les caractères consécutifs (score élevé)
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
    
    // Mettre en évidence les caractères correspondants dans le texte
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
    
    // Afficher les résultats de recherche dans le dropdown
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
            return `
            <div class="search-result-item" data-index="${index}">
                <div class="search-result-image">
                    <img src="https://via.placeholder.com/40x40?text=${encodeURIComponent(cocktail.name)}" alt="${cocktail.name}" onerror="this.src='https://images.unsplash.com/photo-1536935338788-846bb9981813?w=40&h=40&fit=crop'">
                </div>
                <div class="search-result-info">
                    <div class="search-result-name">${highlightedName}</div>
                    <div class="search-result-category">${cocktail.description ? cocktail.description.substring(0, 50) : 'Cocktail classique'}</div>
                </div>
            </div>
        `
        }).join('');
        
        dropdown.style.display = 'block';
        
        // Ajouter les gestionnaires de clic aux résultats
        dropdown.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(item.dataset.index);
                const selectedCocktail = limitedResults[index];
                navigateToCocktailDetail(selectedCocktail);
            });
        });
    }
    
    // Naviguer vers la page de détail du cocktail
    function navigateToCocktailDetail(cocktail) {
        // Stocker le cocktail sélectionné dans sessionStorage
        sessionStorage.setItem('selectedCocktail', JSON.stringify(cocktail));
        
        // Obtenir le chemin relatif en fonction de l'emplacement actuel
        let detailPagePath = '../pages/cocktail-detail.html';
        
        // Si nous sommes déjà dans le répertoire des pages, ajuster le chemin
        if (window.location.pathname.includes('/pages/')) {
            detailPagePath = './cocktail-detail.html';
        }
        // Si nous sommes sur la page d'accueil (index.html), utiliser le répertoire des pages
        else if (window.location.pathname.endsWith('/index.html') || window.location.pathname.endsWith('/')) {
            detailPagePath = 'pages/cocktail-detail.html';
        }
        
        // Naviguer vers la page de détail
        window.location.href = detailPagePath + '?id=' + encodeURIComponent(cocktail.id);
    }
    
    // Setup scroll behavior to hide/show navbar
    function setupScrollBehavior() {
        window.addEventListener('scroll', function() {
            const currentScrollPos = window.pageYOffset;
            
            if (navbar && menuNoNavbar) {
                if (prevScrollPos > currentScrollPos || currentScrollPos < 50) {
                    // Scrolling up or at top - show navbar
                    navbar.classList.remove('hide');
                    menuNoNavbar.style.display = 'none';
                } else {
                    // Scrolling down - hide navbar, show menu button
                    navbar.classList.add('hide');
                    menuNoNavbar.style.display = 'flex';
                }
            }
            
            prevScrollPos = currentScrollPos;
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
