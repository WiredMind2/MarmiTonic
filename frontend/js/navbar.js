/**
 * Navbar functionality - Shared across all pages
 * Handles navbar scroll behavior and menu toggle
 */

(function() {
    'use strict';
    
    let prevScrollPos = window.pageYOffset;
    const navbar = document.getElementById('navbar');
    const menuNoNavbar = document.getElementById('no-navbar-menu');
    
    // Initialize
    function init() {
        if (menuNoNavbar) {
            menuNoNavbar.style.display = 'none';
            setupMenuToggle();
        }
        
        setupScrollBehavior();
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
