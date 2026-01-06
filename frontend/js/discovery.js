/**
 * Discovery Page - Spotify-like cocktail browsing
 * Handles horizontal scrolling, shuffle functionality, and cocktail interactions
 */

(function() {
    'use strict';
    
    // Initialize discovery page
    function init() {
        setupScrollArrows();
        setupShuffleButton();
        console.log('Discovery page initialized');
    }
    
    /**
     * Setup horizontal scroll arrows for cocktail rows
     */
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
            
            // Initial state
            updateArrowStates();
            
            // Update on scroll
            row.addEventListener('scroll', updateArrowStates);
        });
    }
    
    /**
     * Setup shuffle button for random cocktail
     */
    function setupShuffleButton() {
        const shuffleButton = document.querySelector('.shuffle-button');
        
        if (shuffleButton) {
            shuffleButton.addEventListener('click', (e) => {
                e.preventDefault();
                // TODO: Implement shuffle functionality with backend API
                console.log('Shuffle clicked - will fetch random cocktail from backend');
                
                // Animate the refresh icon
                const icon = shuffleButton.querySelector('i');
                if (icon) {
                    icon.style.transform = 'rotate(360deg)';
                    setTimeout(() => {
                        icon.style.transform = 'rotate(0deg)';
                    }, 600);
                }
            });
        }
    }
    
    /**
     * Handle cocktail card clicks
     */
    function setupCocktailCards() {
        const cocktailCards = document.querySelectorAll('.cocktail-card, .recent-cocktail-card');
        
        cocktailCards.forEach(card => {
            card.addEventListener('click', () => {
                // TODO: Navigate to cocktail detail page or open modal
                const cocktailName = card.querySelector('h3')?.textContent;
                console.log(`Cocktail clicked: ${cocktailName}`);
            });
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
