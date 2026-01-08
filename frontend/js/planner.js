// Planner Page JavaScript - Spotify-inspired

// Sample data - Replace with API calls
const samplePlaylists = [
    {
        id: 'liked',
        name: 'Cocktails Favoris',
        cocktails: [
            { id: 1, name: 'Mojito', image: 'https://images.unsplash.com/photo-1536935338788-846bb9981813?w=300&h=300&fit=crop' },
            { id: 2, name: 'Margarita', image: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300&h=300&fit=crop' },
            { id: 3, name: 'Piña Colada', image: 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=300&h=300&fit=crop' },
        ]
    },
    {
        id: '1',
        name: "Soirée d'Été",
        cocktails: [
            { id: 1, name: 'Mojito', image: 'https://images.unsplash.com/photo-1536935338788-846bb9981813?w=300&h=300&fit=crop' },
            { id: 4, name: 'Cosmopolitan', image: 'https://images.unsplash.com/photo-1481671703460-040cb8a2d909?w=300&h=300&fit=crop' },
            { id: 5, name: 'Aperol Spritz', image: 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=300&h=300&fit=crop' },
        ]
    },
    {
        id: '2',
        name: 'Classiques',
        cocktails: [
            { id: 6, name: 'Negroni', image: 'https://images.unsplash.com/photo-1517093728432-30d17e9f6d9d?w=300&h=300&fit=crop' },
            { id: 2, name: 'Margarita', image: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300&h=300&fit=crop' },
        ]
    },
    {
        id: '3',
        name: 'Cocktails Tropicaux',
        cocktails: [
            { id: 3, name: 'Piña Colada', image: 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=300&h=300&fit=crop' },
            { id: 7, name: 'Mai Tai', image: 'https://images.unsplash.com/photo-1541544181051-e46607bc22a4?w=300&h=300&fit=crop' },
        ]
    },
    {
        id: '4',
        name: 'Apéritif',
        cocktails: [
            { id: 6, name: 'Negroni', image: 'https://images.unsplash.com/photo-1517093728432-30d17e9f6d9d?w=300&h=300&fit=crop' },
            { id: 5, name: 'Aperol Spritz', image: 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=300&h=300&fit=crop' },
        ]
    }
];

const sampleIngredients = {
    'Rhum blanc': { cocktails: ['Mojito', 'Mai Tai', 'Piña Colada'], unit: 'ml' },
    'Tequila': { cocktails: ['Margarita'], unit: 'ml' },
    'Vodka': { cocktails: ['Cosmopolitan'], unit: 'ml' },
    'Gin': { cocktails: ['Negroni'], unit: 'ml' },
    'Aperol': { cocktails: ['Aperol Spritz', 'Negroni'], unit: 'ml' },
    'Jus de citron vert': { cocktails: ['Mojito', 'Margarita', 'Mai Tai'], unit: 'ml' },
    'Menthe fraîche': { cocktails: ['Mojito'], unit: 'feuilles' },
    'Triple sec': { cocktails: ['Margarita', 'Mai Tai'], unit: 'ml' },
    'Crème de coco': { cocktails: ['Piña Colada'], unit: 'ml' },
    'Jus d\'ananas': { cocktails: ['Piña Colada'], unit: 'ml' },
    'Vermouth rouge': { cocktails: ['Negroni'], unit: 'ml' },
    'Prosecco': { cocktails: ['Aperol Spritz'], unit: 'ml' }
};

document.addEventListener('DOMContentLoaded', () => {
    initializePlanner();
    
    // Check if we should open create playlist modal from URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('create') === 'true') {
        setTimeout(() => {
            document.getElementById('createPlaylistBtn').click();
        }, 500);
    }
});

function initializePlanner() {
    setupPlaylistCards();
    setupCreatePlaylistModal();
    loadPlaylists();
}

// Setup Playlist Cards Click Events
function setupPlaylistCards() {
    const playlistCards = document.querySelectorAll('.playlist-card');
    
    playlistCards.forEach(card => {
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.play-button')) {
                const playlistId = card.dataset.playlistId;
                openPlaylistModal(playlistId);
            }
        });
    });
}

// Open Playlist Modal
function openPlaylistModal(playlistId) {
    const playlist = samplePlaylists.find(p => p.id === playlistId);
    if (!playlist) return;

    const modal = document.getElementById('playlistModal');
    const modalTitle = document.getElementById('modalPlaylistName');
    const modalCount = document.getElementById('modalCocktailCount');
    const cocktailsGrid = document.getElementById('modalCocktailsGrid');
    const ingredientsList = document.getElementById('modalIngredientsList');

    // Update modal header
    modalTitle.textContent = playlist.name;
    modalCount.textContent = playlist.cocktails.length;

    // Update modal icon for liked playlist
    const modalIcon = modal.querySelector('.modal-playlist-icon i');
    if (playlistId === 'liked') {
        modalIcon.className = 'fa fa-heart';
        modal.querySelector('.modal-playlist-icon').style.background = 'linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)';
    } else {
        modalIcon.className = 'fa fa-list';
        modal.querySelector('.modal-playlist-icon').style.background = 'linear-gradient(135deg, var(--primary-color) 0%, #1a5c30 100%)';
    }

    // Populate cocktails
    cocktailsGrid.innerHTML = '';
    playlist.cocktails.forEach(cocktail => {
        const card = createModalCocktailCard(cocktail, playlistId);
        cocktailsGrid.appendChild(card);
    });

    // Calculate and populate ingredients
    const neededIngredients = calculateNeededIngredients(playlist.cocktails);
    ingredientsList.innerHTML = '';
    Object.entries(neededIngredients).forEach(([name, data]) => {
        const item = createIngredientItem(name, data);
        ingredientsList.appendChild(item);
    });

    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Setup close handlers
    setupModalCloseHandlers(modal);
}

// Create Modal Cocktail Card
function createModalCocktailCard(cocktail, playlistId) {
    const card = document.createElement('div');
    card.className = 'modal-cocktail-card';
    
    card.innerHTML = `
        <div class="modal-cocktail-image">
            <img src="${cocktail.image}" alt="${cocktail.name}">
        </div>
        <div class="modal-cocktail-info">
            <h4 class="modal-cocktail-name">${cocktail.name}</h4>
            <button class="modal-cocktail-remove" data-cocktail-id="${cocktail.id}">
                <i class="fa fa-times"></i> Retirer
            </button>
        </div>
    `;

    // Add click to view cocktail detail
    card.addEventListener('click', (e) => {
        if (!e.target.closest('.modal-cocktail-remove')) {
            window.location.href = `cocktail-detail.html?id=${cocktail.id}`;
        }
    });

    // Remove from playlist
    const removeBtn = card.querySelector('.modal-cocktail-remove');
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        removeFromPlaylist(playlistId, cocktail.id);
        card.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            card.remove();
            updateModalCount();
        }, 300);
    });

    return card;
}

// Calculate Needed Ingredients
function calculateNeededIngredients(cocktails) {
    const ingredients = {};
    
    cocktails.forEach(cocktail => {
        Object.entries(sampleIngredients).forEach(([ingredient, data]) => {
            if (data.cocktails.includes(cocktail.name)) {
                if (!ingredients[ingredient]) {
                    ingredients[ingredient] = {
                        count: 1,
                        cocktails: [cocktail.name],
                        unit: data.unit
                    };
                } else if (!ingredients[ingredient].cocktails.includes(cocktail.name)) {
                    ingredients[ingredient].count++;
                    ingredients[ingredient].cocktails.push(cocktail.name);
                }
            }
        });
    });

    return ingredients;
}

// Create Ingredient Item
function createIngredientItem(name, data) {
    const item = document.createElement('div');
    item.className = 'ingredient-needed-item';
    
    item.innerHTML = `
        <input type="checkbox" id="ingredient-${name.replace(/\s/g, '-')}">
        <label class="ingredient-needed-name" for="ingredient-${name.replace(/\s/g, '-')}">${name}</label>
        <span class="ingredient-needed-count">${data.count} cocktail${data.count > 1 ? 's' : ''}</span>
    `;

    return item;
}

// Update Modal Count
function updateModalCount() {
    const cocktailsGrid = document.getElementById('modalCocktailsGrid');
    const count = cocktailsGrid.children.length;
    document.getElementById('modalCocktailCount').textContent = count;
}

// Remove from Playlist
function removeFromPlaylist(playlistId, cocktailId) {
    // TODO: Implement API call
    console.log(`Removing cocktail ${cocktailId} from playlist ${playlistId}`);
    showNotification('Cocktail retiré de la playlist', 'success');
}

// Setup Modal Close Handlers
function setupModalCloseHandlers(modal) {
    const closeBtn = modal.querySelector('.modal-close');
    const backdrop = modal.querySelector('.modal-backdrop');

    const closeModal = () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    };

    closeBtn.onclick = closeModal;
    backdrop.onclick = closeModal;

    // ESC key to close
    const escHandler = (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

// Create Playlist Modal
function setupCreatePlaylistModal() {
    const createBtn = document.getElementById('createPlaylistBtn');
    const modal = document.getElementById('createPlaylistModal');
    const closeBtn = document.getElementById('closeCreateModal');
    const cancelBtn = document.getElementById('cancelCreatePlaylist');
    const confirmBtn = document.getElementById('confirmCreatePlaylist');
    const backdrop = modal.querySelector('.modal-backdrop');

    const openModal = () => {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        document.getElementById('playlistName').focus();
    };

    const closeModal = () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        // Reset form
        document.getElementById('playlistName').value = '';
        document.getElementById('playlistDescription').value = '';
    };

    createBtn.addEventListener('click', openModal);
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);

    confirmBtn.addEventListener('click', () => {
        const name = document.getElementById('playlistName').value.trim();
        const description = document.getElementById('playlistDescription').value.trim();

        if (!name) {
            showNotification('Veuillez entrer un nom de playlist', 'error');
            return;
        }

        createPlaylist(name, description);
        closeModal();
    });

    // Enter key to create
    document.getElementById('playlistName').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            confirmBtn.click();
        }
    });
}

// Create Playlist
function createPlaylist(name, description) {
    // TODO: Implement API call
    console.log('Creating playlist:', { name, description });
    
    // Add new playlist card to grid
    const playlistsGrid = document.getElementById('playlistsGrid');
    const newCard = document.createElement('div');
    newCard.className = 'playlist-card';
    newCard.dataset.playlistId = Date.now().toString();
    
    newCard.innerHTML = `
        <div class="playlist-image">
            <img src="https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=300&h=300&fit=crop" alt="Playlist">
            <div class="playlist-overlay">
                <button class="play-button">
                    <i class="fa fa-play"></i>
                </button>
            </div>
        </div>
        <div class="playlist-card-info">
            <h3 class="playlist-name">${name}</h3>
            <p class="playlist-meta">0 cocktails</p>
        </div>
    `;

    playlistsGrid.insertBefore(newCard, playlistsGrid.firstChild);
    
    // Setup click handler for new card
    newCard.addEventListener('click', (e) => {
        if (!e.target.closest('.play-button')) {
            openPlaylistModal(newCard.dataset.playlistId);
        }
    });

    showNotification(`Playlist "${name}" créée avec succès !`, 'success');
    
    // Animate new card
    newCard.style.animation = 'slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
}

// Load Playlists (for dynamic loading from API)
function loadPlaylists() {
    // TODO: Replace with actual API call
    // This would fetch playlists from backend and populate the grid
    console.log('Playlists loaded');
}

// Utility: Show Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
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
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add fade out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: scale(1);
        }
        to {
            opacity: 0;
            transform: scale(0.9);
        }
    }
    
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

// Export functions for use in other pages
window.PlannerAPI = {
    openAddToPlaylistDropdown: function(cocktailId, buttonElement) {
        // This will be called from cocktail-detail.js
        showPlaylistDropdown(cocktailId, buttonElement);
    }
};

// Show Playlist Dropdown for "Add to Playlist"
function showPlaylistDropdown(cocktailId, buttonElement) {
    // Remove existing dropdown if any
    const existingDropdown = document.querySelector('.playlist-dropdown');
    if (existingDropdown) {
        existingDropdown.remove();
        return;
    }

    const dropdown = document.createElement('div');
    dropdown.className = 'playlist-dropdown';
    
    let dropdownHTML = '<div class="dropdown-header">Ajouter à une playlist</div>';
    
    // Add playlists
    samplePlaylists.forEach(playlist => {
        dropdownHTML += `
            <div class="dropdown-item" data-playlist-id="${playlist.id}">
                <i class="fa ${playlist.id === 'liked' ? 'fa-heart' : 'fa-list'}"></i>
                <span>${playlist.name}</span>
            </div>
        `;
    });
    
    dropdownHTML += `
        <div class="dropdown-divider"></div>
        <div class="dropdown-item create-new-playlist">
            <i class="fa fa-plus"></i>
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
    dropdown.style.animation = 'slideUp 0.2s ease-out';
    
    // Setup item click handlers
    dropdown.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains('create-new-playlist')) {
                dropdown.remove();
                document.getElementById('createPlaylistBtn').click();
            } else {
                const playlistId = item.dataset.playlistId;
                addCocktailToPlaylist(cocktailId, playlistId);
                dropdown.remove();
            }
        });
    });
    
    // Click outside to close
    setTimeout(() => {
        document.addEventListener('click', function closeDropdown(e) {
            if (!dropdown.contains(e.target) && e.target !== buttonElement) {
                dropdown.remove();
                document.removeEventListener('click', closeDropdown);
            }
        });
    }, 100);
}

function addCocktailToPlaylist(cocktailId, playlistId) {
    const playlist = samplePlaylists.find(p => p.id === playlistId);
    if (playlist) {
        showNotification(`Ajouté à "${playlist.name}" !`, 'success');
        // TODO: Implement API call to add cocktail to playlist
        console.log(`Adding cocktail ${cocktailId} to playlist ${playlistId}`);
    }
}
