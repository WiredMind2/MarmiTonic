(function() {
    'use strict';
        
    // State
    let vibeClusters = [];
    let currentRandomCocktail = null;
    
    const RecentlyViewed = {
        key: 'marmitonic_recently_viewed',
        maxItems: 12,
        
        get() {
            try {
                const data = localStorage.getItem(this.key);
                return data ? JSON.parse(data) : [];
            } catch (e) {
                console.error('Error loading recently viewed:', e);
                return [];
            }
        },
    };
    
    async function init() {
        console.log('Discovery page initializing...');
        console.log('API functions check:');
        console.log('- fetchRandomCocktail:', typeof fetchRandomCocktail);
        console.log('- fetchVibeClusters:', typeof fetchVibeClusters);
        console.log('- API_BASE_URL:', typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : 'UNDEFINED');
                
        // Load data
        try {
            console.log('Starting to load data...');
            await Promise.all([
                loadVibeClusters(),
                loadRandomCocktail(),
                loadRecentlyViewed()
            ]);
            console.log('All data loaded successfully');
        } catch (error) {
            console.error('Error during initialization:', error);
        }
        
        // Setup interactions
        setupScrollArrows();
        setupShuffleButton();
        setupCocktailCards();
        
        console.log('Discovery page initialized');
    }
    
    function showErrorState(message) {
        const sections = document.querySelectorAll('.cocktails-section');
        sections.forEach((section, index) => {
            if (index >= 2) { // Only update cluster sections
                const header = section.querySelector('.section-header h2');
                if (header) {
                    header.textContent = message;
                    header.style.color = '#999';
                }
            }
        });
    }
    
    async function loadVibeClusters() {
        try {
            console.log('Fetching vibe clusters...');
            vibeClusters = await fetchVibeClusters(3); // Get 3 main clusters
            console.log('Loaded vibe clusters:', vibeClusters);
            
            if (!vibeClusters || vibeClusters.length === 0) {
                console.warn('No clusters returned, building similarity index...');
                await buildSimilarityIndex();
                vibeClusters = await fetchVibeClusters(3);
            }
            
            renderVibeClusters();
        } catch (error) {
            console.error('Error loading vibe clusters:', error);
            showErrorState('Unable to load cocktail collections');
        }
    }
    
    async function loadRandomCocktail() {
        try {
            currentRandomCocktail = await fetchRandomCocktail();
            console.log('Loaded random cocktail:', currentRandomCocktail);
            renderRandomCocktail();
        } catch (error) {
            console.error('Error loading random cocktail:', error);
        }
    }
    
    async function loadRecentlyViewed() {
        const recent = RecentlyViewed.get();
        console.log('Recently viewed:', recent);
        renderRecentlyViewed(recent);
    }
    
    function renderRecentlyViewed(recentCocktails) {
        const grid = document.querySelector('.recent-cocktails-grid');
        if (!grid) return;
        
        if (!recentCocktails || recentCocktails.length === 0) {
            grid.innerHTML = `
                <div class="empty-recent-state" style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #999;">
                    <p style="margin: 0;">Aucun cocktail consulté récemment</p>
                    <small>Explorez les cocktails ci-dessous pour commencer</small>
                </div>
            `;
            return;
        }
        // Show only the last 6 recently viewed items (most recent first)
        const toShow = recentCocktails.slice(0, 6);

        grid.innerHTML = toShow.map(cocktail => `
            <div class="recent-cocktail-card" data-cocktail-id="${cocktail.id}">
                <img src="${getCocktailImage(cocktail)}" alt="${cocktail.name}" onerror="this.src='https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300&h=300&fit=crop'">
                <div class="recent-cocktail-info">
                    <h3>${cocktail.name}</h3>
                </div>
            </div>
        `).join('');
    }
    

    function renderRandomCocktail() {
        if (!currentRandomCocktail) return;
        
        const container = document.querySelector('.random-cocktail-container');
        if (!container) return;
        
        const description = currentRandomCocktail.description || 
                          `Un délicieux cocktail ${currentRandomCocktail.categories ? currentRandomCocktail.categories.join(', ') : 'à découvrir'}`;
        
        container.innerHTML = `
            <div class="random-cocktail-card" data-cocktail-id="${currentRandomCocktail.id}">
                <div class="random-cocktail-image">
                    <img src="${getCocktailImage(currentRandomCocktail)}" alt="${currentRandomCocktail.name}" onerror="this.src='https://images.unsplash.com/photo-1551024601-bec78aea704b?w=800&h=500&fit=crop'">
                    <div class="random-overlay"></div>
                </div>
                <div class="random-cocktail-info">
                    <h3>${currentRandomCocktail.name}</h3>
                    <p class="cocktail-description">${description}</p>
                </div>
            </div>
        `;
    }
    
    function renderVibeClusters() {
        if (!vibeClusters || vibeClusters.length === 0) {
            console.warn('No vibe clusters to render');
            return;
        }
        
        // Get the section containers (skip recently watched and random sections)
        const sections = document.querySelectorAll('.cocktails-section');
        const clusterSections = Array.from(sections).slice(2); // Skip first 2 sections
        
        vibeClusters.forEach((cluster, index) => {
            if (index >= clusterSections.length) return;
            
            const section = clusterSections[index];
            
            // Update section header with backend title
            const header = section.querySelector('.section-header h2');
            if (header) {
                // Use the title from the backend, or fallback to generic title
                const title = cluster.title || `Collection ${cluster.cluster_id + 1}`;
                header.textContent = title;
            }
            
            // Render cocktails
            const cocktailsRow = section.querySelector('.cocktails-row');
            if (cocktailsRow && cluster.cocktails) {
                cocktailsRow.innerHTML = cluster.cocktails.map(cocktail => `
                    <div class="cocktail-card" data-cocktail-id="${cocktail.id}">
                        <div class="cocktail-card-image">
                            <img src="${getCocktailImage(cocktail)}" alt="${cocktail.name}" onerror="this.src='https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300&h=300&fit=crop'">
                        </div>
                        <h3>${cocktail.name}</h3>
                    </div>
                `).join('');
            }
            
            section.style.opacity = '1';
        });
    }
    
    function getCocktailImage(cocktail) {
        if (cocktail.image && cocktail.image.startsWith('http')) {
            return cocktail.image;
        }
    }
    
    function setupScrollArrows() {
        const scrollContainers = document.querySelectorAll('.cocktails-scroll-container');
        
        scrollContainers.forEach(container => {
            const leftArrow = container.querySelector('.scroll-arrow-left');
            const rightArrow = container.querySelector('.scroll-arrow-right');
            const row = container.querySelector('.cocktails-row');
            
            if (!leftArrow || !rightArrow || !row) return;
            
            // Scroll amount (width of approximately 2 cards)
            const scrollAmount = 400;
            
            // Left arrow click
            leftArrow.addEventListener('click', () => {
                row.scrollBy({
                    left: -scrollAmount,
                    behavior: 'smooth'
                });
            });
            
            // Right arrow click
            rightArrow.addEventListener('click', () => {
                row.scrollBy({
                    left: scrollAmount,
                    behavior: 'smooth'
                });
            });
            
            // Update arrow states on scroll
            function updateArrowStates() {
                const isAtStart = row.scrollLeft <= 0;
                const isAtEnd = row.scrollLeft + row.clientWidth >= row.scrollWidth - 1;
                
                leftArrow.disabled = isAtStart;
                rightArrow.disabled = isAtEnd;
            }
            
            updateArrowStates();
            
            row.addEventListener('scroll', updateArrowStates);
        });
    }
    
    function setupShuffleButton() {
        const shuffleButton = document.querySelector('.shuffle-button');
        
        if (shuffleButton) {
            shuffleButton.addEventListener('click', async (e) => {
                e.preventDefault();
                
                // Animate the refresh icon
                const icon = shuffleButton.querySelector('i');
                if (icon) {
                    icon.style.transition = 'transform 0.6s ease';
                    icon.style.transform = 'rotate(360deg)';
                    setTimeout(() => {
                        icon.style.transform = 'rotate(0deg)';
                    }, 600);
                }
                
                // Fetch new random cocktail
                await loadRandomCocktail();
            });
        }
    }
    
    function setupCocktailCards() {
        document.addEventListener('click', (e) => {
            const card = e.target.closest('.cocktail-card, .recent-cocktail-card, .random-cocktail-card');
            if (!card) return;
            
            const cocktailId = card.dataset.cocktailId;
            if (cocktailId) {
                handleCocktailClick(cocktailId, card);
            }
        });
    }
    
    function handleCocktailClick(cocktailId, cardElement) {
        console.log(`Cocktail clicked: ${cocktailId}`);
        
        // Find cocktail data
        let cocktail = null;
        
        // Check in random cocktail
        if (currentRandomCocktail && currentRandomCocktail.id === cocktailId) {
            cocktail = currentRandomCocktail;
        }
        
        // Check in clusters
        if (!cocktail) {
            for (const cluster of vibeClusters) {
                cocktail = cluster.cocktails?.find(c => c.id === cocktailId);
                if (cocktail) break;
            }
        }
        
        // Check in recently viewed
        if (!cocktail) {
            const recent = RecentlyViewed.get();
            cocktail = recent.find(c => c.id === cocktailId);
        }
        
        if (cocktail) {
            // Navigate to detail page (or open modal in future)
            // For now, just log and potentially redirect
            console.log('Navigate to cocktail detail:', cocktail);

            window.location.href = `cocktail-detail.html?id=${cocktailId}`;
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
