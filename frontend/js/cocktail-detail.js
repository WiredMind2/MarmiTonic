// Cocktail Detail Page JavaScript

document.addEventListener('DOMContentLoaded', () => {
    initializeCocktailDetail();
});

function initializeCocktailDetail() {
    // Get cocktail ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const cocktailId = urlParams.get('id');

    if (cocktailId) {
        loadCocktailData(cocktailId);
    }

    // Initialize interactive elements
    initializeActionButtons();
    initializeIngredientTracking();
    initializeInstructionSteps();
}

// Action Buttons
function initializeActionButtons() {
    const addToPlaylistBtn = document.getElementById('addToPlaylistBtn');
    const favoriteBtn = document.getElementById('favoriteBtn');
    const shareBtn = document.getElementById('shareBtn');

    if (addToPlaylistBtn) {
        addToPlaylistBtn.addEventListener('click', handleAddToPlaylist);
    }

    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', handleToggleFavorite);
        
        // Check if already favorited
        const isFavorited = checkIfFavorited();
        if (isFavorited) {
            favoriteBtn.classList.add('active');
            favoriteBtn.querySelector('i').classList.remove('fa-heart-o');
            favoriteBtn.querySelector('i').classList.add('fa-heart');
        }
    }

    if (shareBtn) {
        shareBtn.addEventListener('click', handleShare);
    }
}

function handleAddToPlaylist(event) {
    const btn = document.getElementById('addToPlaylistBtn');
    
    // Add animation
    btn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        btn.style.transform = '';
    }, 150);

    // Get cocktail ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const cocktailId = urlParams.get('id') || '1';
    
    // Show playlist dropdown
    showPlaylistDropdown(cocktailId, btn);
}

function showPlaylistDropdown(cocktailId, buttonElement) {
    // Remove existing dropdown if any
    const existingDropdown = document.querySelector('.playlist-dropdown');
    if (existingDropdown) {
        existingDropdown.remove();
        return;
    }

    // Sample playlists - In production, fetch from API
    const playlists = [
        { id: 'liked', name: 'Cocktails Favoris', icon: 'fa-heart' },
        { id: '1', name: "Soirée d'Été", icon: 'fa-list' },
        { id: '2', name: 'Classiques', icon: 'fa-list' },
        { id: '3', name: 'Cocktails Tropicaux', icon: 'fa-list' },
        { id: '4', name: 'Apéritif', icon: 'fa-list' }
    ];

    const dropdown = document.createElement('div');
    dropdown.className = 'playlist-dropdown';
    
    let dropdownHTML = '<div class="dropdown-header">Ajouter à une playlist</div>';
    
    playlists.forEach(playlist => {
        dropdownHTML += `
            <div class="dropdown-item" data-playlist-id="${playlist.id}">
                <i class="fa ${playlist.icon}"></i>
                <span>${playlist.name}</span>
            </div>
        `;
    });
    
    dropdownHTML += `
        <div class="dropdown-divider"></div>
        <div class="dropdown-item create-new-playlist">
            <i class="fa fa-plus-circle"></i>
            <span>Créer une nouvelle playlist</span>
        </div>
    `;
    
    dropdown.innerHTML = dropdownHTML;
    
    // Position dropdown
    const rect = buttonElement.getBoundingClientRect();
    Object.assign(dropdown.style, {
        position: 'fixed',
        top: `${rect.bottom + 10}px`,
        left: `${rect.left}px`,
        zIndex: '10000'
    });
    
    document.body.appendChild(dropdown);
    
    // Animate in
    setTimeout(() => dropdown.classList.add('show'), 10);
    
    // Setup item click handlers
    dropdown.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains('create-new-playlist')) {
                dropdown.remove();
                window.location.href = 'planner.html?create=true';
            } else {
                const playlistId = item.dataset.playlistId;
                const playlistName = item.querySelector('span').textContent;
                addCocktailToPlaylist(cocktailId, playlistId, playlistName);
                dropdown.remove();
            }
        });
    });
    
    // Click outside to close
    setTimeout(() => {
        document.addEventListener('click', function closeDropdown(e) {
            if (!dropdown.contains(e.target) && e.target !== buttonElement) {
                dropdown.classList.remove('show');
                setTimeout(() => dropdown.remove(), 200);
                document.removeEventListener('click', closeDropdown);
            }
        });
    }, 100);
}

function addCocktailToPlaylist(cocktailId, playlistId, playlistName) {
    // TODO: Implement API call
    console.log(`Adding cocktail ${cocktailId} to playlist ${playlistId}`);
    showNotification(`Ajouté à "${playlistName}" !`, 'success');
}

function handleToggleFavorite() {
    const btn = document.getElementById('favoriteBtn');
    const icon = btn.querySelector('i');
    const isActive = btn.classList.contains('active');

    if (isActive) {
        btn.classList.remove('active');
        icon.classList.remove('fa-heart');
        icon.classList.add('fa-heart-o');
        showNotification('Retiré des favoris', 'info');
    } else {
        btn.classList.add('active');
        icon.classList.remove('fa-heart-o');
        icon.classList.add('fa-heart');
        showNotification('Ajouté aux favoris !', 'success');
        
        // Add heart animation
        btn.style.transform = 'scale(1.2)';
        setTimeout(() => {
            btn.style.transform = '';
        }, 200);
    }

    // TODO: Persist to localStorage or backend
}

function handleShare() {
    const cocktailName = document.getElementById('cocktailName').textContent;
    const url = window.location.href;

    if (navigator.share) {
        navigator.share({
            title: `${cocktailName} - MarmiTonic`,
            text: `Découvre cette recette de ${cocktailName} sur MarmiTonic !`,
            url: url
        }).then(() => {
            showNotification('Partagé avec succès !', 'success');
        }).catch((error) => {
            console.log('Error sharing:', error);
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Lien copié dans le presse-papier !', 'success');
        }).catch(() => {
            showNotification('Erreur lors de la copie', 'error');
        });
    }
}

// Ingredient Tracking
function initializeIngredientTracking() {
    const ingredientItems = document.querySelectorAll('.ingredient-item');
    
    ingredientItems.forEach(item => {
        item.addEventListener('click', () => {
            item.style.transform = 'scale(1.02)';
            setTimeout(() => {
                item.style.transform = '';
            }, 150);
        });
    });
}

// Instruction Steps - Interactive Checkoff
function initializeInstructionSteps() {
    const steps = document.querySelectorAll('.instruction-step');
    
    steps.forEach((step, index) => {
        step.addEventListener('click', () => {
            step.classList.toggle('completed');
            
            const stepNumber = step.querySelector('.step-number');
            if (step.classList.contains('completed')) {
                stepNumber.innerHTML = '<i class="fa fa-check"></i>';
                stepNumber.style.background = 'linear-gradient(135deg, #28a745 0%, #20923e 100%)';
            } else {
                stepNumber.textContent = index + 1;
                stepNumber.style.background = '';
            }
        });

        // Add hover effect
        step.style.cursor = 'pointer';
        step.addEventListener('mouseenter', () => {
            if (!step.classList.contains('completed')) {
                step.style.transform = 'translateX(4px)';
            }
        });
        step.addEventListener('mouseleave', () => {
            step.style.transform = '';
        });
    });
}

// Load Cocktail Data
async function loadCocktailData(cocktailId) {
    try {
        // TODO: Replace with actual API call
        // const response = await fetch(`/api/cocktails/${cocktailId}`);
        // const data = await response.json();
        
        // For now, use placeholder data
        console.log('Loading cocktail:', cocktailId);
        
        // You can populate the page dynamically here when you have the API
        // populateCocktailData(data);
        
    } catch (error) {
        console.error('Error loading cocktail:', error);
        showNotification('Erreur lors du chargement du cocktail', 'error');
    }
}

function populateCocktailData(data) {
    // Update title
    document.getElementById('cocktailName').textContent = data.name;
    
    // Update meta information
    document.getElementById('servedType').textContent = data.servedType;
    document.getElementById('garnishType').textContent = data.garnishType;
    document.getElementById('category').textContent = data.category;
    document.getElementById('difficulty').textContent = data.difficulty;
    
    // Update image
    document.getElementById('cocktailImage').src = data.image;
    document.getElementById('cocktailImage').alt = data.name;
    
    // Update description
    document.getElementById('cocktailDescription').textContent = data.description;
    
    // Update ingredients
    const ingredientsList = document.getElementById('ingredientsList');
    ingredientsList.innerHTML = '';
    data.ingredients.forEach(ingredient => {
        const item = createIngredientItem(ingredient);
        ingredientsList.appendChild(item);
    });
    
    // Update instructions
    const instructionsList = document.getElementById('instructionsList');
    instructionsList.innerHTML = '';
    data.instructions.forEach((instruction, index) => {
        const step = createInstructionStep(instruction, index + 1);
        instructionsList.appendChild(step);
    });
}

function createIngredientItem(ingredient) {
    const div = document.createElement('div');
    div.className = 'ingredient-item';
    
    const available = ingredient.available;
    const iconClass = available ? 'fa-check-circle available' : 'fa-times-circle unavailable';
    
    div.innerHTML = `
        <div class="ingredient-icon">
            <i class="fa ${iconClass}"></i>
        </div>
        <div class="ingredient-info">
            <span class="ingredient-name">${ingredient.name}</span>
            <span class="ingredient-quantity">${ingredient.quantity}</span>
        </div>
    `;
    
    return div;
}

function createInstructionStep(text, number) {
    const div = document.createElement('div');
    div.className = 'instruction-step';
    
    div.innerHTML = `
        <div class="step-number">${number}</div>
        <div class="step-content">
            <p>${text}</p>
        </div>
    `;
    
    return div;
}

// Utility Functions
function checkIfFavorited() {
    // TODO: Check localStorage or backend
    const favorites = JSON.parse(localStorage.getItem('favoriteCocktails') || '[]');
    const urlParams = new URLSearchParams(window.location.search);
    const cocktailId = urlParams.get('id');
    return favorites.includes(cocktailId);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '100px',
        right: '20px',
        padding: '16px 24px',
        background: type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8',
        color: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
        zIndex: '10000',
        fontSize: '0.95rem',
        fontWeight: '500',
        animation: 'slideInRight 0.3s ease-out',
        maxWidth: '300px'
    });
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Smooth scroll to sections
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
