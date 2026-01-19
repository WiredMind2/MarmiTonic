// Planner Page JavaScript - Spotify-inspired with Backend Integration

// State
let allCocktails = [];
let userPlaylists = [];
let marmitonicUserId = null;
let userInventory = new Set(); // User's ingredient inventory from my-bar

// User ID handling
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

// Load/Save playlists from localStorage
function loadPlaylists() {
    const saved = localStorage.getItem(`marmitonic_playlists_${marmitonicUserId}`);
    if (saved) {
        try {
            userPlaylists = JSON.parse(saved);
        } catch (e) {
            userPlaylists = [];
        }
    } else {
        userPlaylists = [];
    }
}

function savePlaylists() {
    localStorage.setItem(`marmitonic_playlists_${marmitonicUserId}`, JSON.stringify(userPlaylists));
}

// Load user's ingredient inventory from backend
async function loadUserInventory() {
    if (!marmitonicUserId) return;
    try {
        const res = await fetch(`${API_BASE_URL}/ingredients/inventory/${marmitonicUserId}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data && Array.isArray(data.ingredients)) {
            userInventory = new Set(data.ingredients);
        }
    } catch (err) {
        console.error('Failed to load inventory:', err);
    }
}

// Save user's ingredient inventory to backend
async function saveUserInventory() {
    if (!marmitonicUserId) return;
    try {
        const body = { user_id: marmitonicUserId, ingredients: Array.from(userInventory) };
        await fetch(`${API_BASE_URL}/ingredients/inventory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
    } catch (err) {
        console.error('Failed to save inventory:', err);
    }
}

// Toggle ingredient in user's inventory
function toggleIngredient(ingredientName) {
    if (userInventory.has(ingredientName)) {
        userInventory.delete(ingredientName);
    } else {
        userInventory.add(ingredientName);
    }
    saveUserInventory();
}

// Get cocktail by ID, or name
function findCocktail(idOrName) {
    return allCocktails.find(c => 
        c.id === idOrName || 
        c.name === idOrName
    );
}

function getPlaylist(playlistId) {
    if (playlistId === 'liked') {
        const likedIds = JSON.parse(localStorage.getItem(`marmitonic_liked_${marmitonicUserId}`) || '[]');
        return {
            id: 'liked',
            name: 'Cocktails Favoris',
            description: 'Tous vos cocktails préférés en un seul endroit',
            cocktailIds: likedIds
        };
    }
    return userPlaylists.find(p => p.id === playlistId);
}

document.addEventListener('DOMContentLoaded', async () => {
    marmitonicUserId = getOrCreateUserId();
    
    // Load cocktails and user inventory from backend
    try {
        const [cocktails] = await Promise.all([
            fetchCocktails(),
            loadUserInventory()
        ]);
        allCocktails = cocktails;
        console.log(`Loaded ${allCocktails.length} cocktails from backend`);
        console.log(`Loaded ${userInventory.size} ingredients from inventory`);
    } catch (err) {
        console.error('Failed to load data:', err);
        allCocktails = [];
    }
    
    // Load playlists from localStorage
    loadPlaylists();
    
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
    renderPlaylistsGrid();
    setupCreatePlaylistModal();
    updateLikedCount();
}

// Render all playlists in grid
function renderPlaylistsGrid() {
    const playlistsGrid = document.getElementById('playlistsGrid');
    if (!playlistsGrid) return;
    
    playlistsGrid.innerHTML = '';
    
    userPlaylists.forEach(playlist => {
        const card = createPlaylistCard(playlist);
        playlistsGrid.appendChild(card);
    });
    
    setupPlaylistCards();
}

// Create a playlist card element
function createPlaylistCard(playlist) {
    const card = document.createElement('div');
    card.className = 'playlist-card';
    card.dataset.playlistId = playlist.id;
    
    // Get first cocktail image or use default
    let imageUrl = 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=300&h=300&fit=crop';
    if (playlist.cocktailIds && playlist.cocktailIds.length > 0) {
        const firstCocktail = findCocktail(playlist.cocktailIds[0]);
        if (firstCocktail && firstCocktail.image) {
            imageUrl = firstCocktail.image;
        }
    }
    
    card.innerHTML = `
        <div class="playlist-image">
            <img src="${imageUrl}" alt="Playlist">
            <div class="playlist-overlay">
                <button class="play-button" title="Optimize ingredients">
                    <i class="fa fa-shopping-basket"></i>
                </button>
            </div>
        </div>
        <div class="playlist-card-info">
            <h3 class="playlist-name">${playlist.name}</h3>
            <p class="playlist-meta">${playlist.cocktailIds ? playlist.cocktailIds.length : 0} cocktails</p>
        </div>
    `;
    
    return card;
}

// Update liked count display
function updateLikedCount() {
    const likedIds = JSON.parse(localStorage.getItem(`marmitonic_liked_${marmitonicUserId}`) || '[]');
    const likedCount = document.getElementById('likedCount');
    if (likedCount) {
        likedCount.textContent = `${likedIds.length} cocktails`;
    }
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
async function openPlaylistModal(playlistId) {
    const playlist = getPlaylist(playlistId);
    if (!playlist) return;

    const modal = document.getElementById('playlistModal');
    const modalTitle = document.getElementById('modalPlaylistName');
    const modalCount = document.getElementById('modalCocktailCount');
    const cocktailsGrid = document.getElementById('modalCocktailsGrid');
    const ingredientsList = document.getElementById('modalIngredientsList');

    modalTitle.textContent = playlist.name;
    
    const cocktails = (playlist.cocktailIds || []).map(id => findCocktail(id)).filter(c => c);
    modalCount.textContent = cocktails.length;

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
    if (cocktails.length === 0) {
        cocktailsGrid.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Aucun cocktail dans cette playlist</p>';
    } else {
        cocktails.forEach(cocktail => {
            const card = createModalCocktailCard(cocktail, playlistId);
            cocktailsGrid.appendChild(card);
        });
    }

    // Calculate and populate ingredients using backend optimization
    ingredientsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 1rem;">Calcul des ingrédients...</p>';
    
    try {
        const cocktailNames = cocktails.map(c => c.name);
        console.log('Optimizing ingredients for cocktails:', cocktailNames);
        if (cocktailNames.length > 0) {
            const optimization = await optimizePlaylistMode(cocktailNames);
            console.log('Optimization result:', optimization);
            displayOptimizedIngredients(ingredientsList, optimization);
        } else {
            ingredientsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 1rem;">Aucun ingrédient nécessaire</p>';
        }
    } catch (err) {
        console.error('Failed to optimize ingredients:', err);
        ingredientsList.innerHTML = `<p style="text-align: center; color: #ff6b6b; padding: 1rem;">Erreur lors du calcul des ingrédients: ${err.message}</p>`;
    }

    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Setup close handlers
    setupModalCloseHandlers(modal);
}

// Display optimized ingredients from backend
function displayOptimizedIngredients(container, optimization) {
    container.innerHTML = '';
    
    if (!optimization.selected_ingredients || optimization.selected_ingredients.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 1rem;">Aucun ingrédient nécessaire</p>';
        return;
    }
    
    const ownedCount = optimization.selected_ingredients.filter(ing => userInventory.has(ing)).length;
    const totalCount = optimization.selected_ingredients.length;
    
    container.innerHTML = `
        <div style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(56, 142, 60, 0.1); border-radius: 8px; color: var(--primary-color); font-size: 0.9rem;">
            <i class="fa fa-check-circle"></i> ${ownedCount}/${totalCount} ingrédients possédés
        </div>
    `;
    
    optimization.selected_ingredients.forEach((ingredient, index) => {
        const item = document.createElement('div');
        item.className = 'ingredient-needed-item';
        const isOwned = userInventory.has(ingredient);
        
        item.innerHTML = `
            <input type="checkbox" id="ingredient-${index}" ${isOwned ? 'checked' : ''}>
            <label class="ingredient-needed-name" for="ingredient-${index}">${ingredient}</label>
            <span class="ingredient-needed-count">
                <i class="fa fa-flask" style="font-size: 0.8rem; opacity: 0.7;"></i>
            </span>
        `;
        
        const checkbox = item.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', (e) => {
            toggleIngredient(ingredient);
            const newOwnedCount = optimization.selected_ingredients.filter(ing => userInventory.has(ing)).length;
            const summary = container.querySelector('div');
            summary.innerHTML = `<i class="fa fa-check-circle"></i> ${newOwnedCount}/${totalCount} ingrédients possédés`;
        });
        
        container.appendChild(item);
    });
}

function createModalCocktailCard(cocktail, playlistId) {
    const card = document.createElement('div');
    card.className = 'modal-cocktail-card';
    
    const imageUrl = cocktail.image || 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=300&h=300&fit=crop';
    
    card.innerHTML = `
        <div class="modal-cocktail-image">
            <img src="${imageUrl}" alt="${cocktail.name}">
        </div>
        <div class="modal-cocktail-info">
            <h4 class="modal-cocktail-name">${cocktail.name}</h4>
            <button class="modal-cocktail-remove" data-cocktail-id="${cocktail.id}">
                <i class="fa fa-times"></i> Retirer
            </button>
        </div>
    `;

    card.addEventListener('click', (e) => {
        if (!e.target.closest('.modal-cocktail-remove')) {
            // Use id if available
            const identifier = cocktail.id;
            window.location.href = `cocktail-detail.html?id=${identifier}`;
        }
    });

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

function updateModalCount() {
    const cocktailsGrid = document.getElementById('modalCocktailsGrid');
    const count = cocktailsGrid.children.length;
    document.getElementById('modalCocktailCount').textContent = count;
    
    // Recalculate ingredients
    const modal = document.getElementById('playlistModal');
    if (modal.classList.contains('active')) {
        const modalTitle = document.getElementById('modalPlaylistName').textContent;
        // Find which playlist this is
        let currentPlaylistId = null;
        if (modalTitle === 'Cocktails Favoris') {
            currentPlaylistId = 'liked';
        } else {
            const playlist = userPlaylists.find(p => p.name === modalTitle);
            if (playlist) currentPlaylistId = playlist.id;
        }
        
        if (currentPlaylistId) {
            const playlist = getPlaylist(currentPlaylistId);
            const cocktails = (playlist.cocktailIds || []).map(id => findCocktail(id)).filter(c => c);
            const ingredientsList = document.getElementById('modalIngredientsList');
            
            if (cocktails.length > 0) {
                ingredientsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 1rem;">Recalcul des ingrédients...</p>';
                optimizePlaylistMode(cocktails.map(c => c.name))
                    .then(optimization => displayOptimizedIngredients(ingredientsList, optimization))
                    .catch(err => {
                        console.error('Failed to optimize:', err);
                        ingredientsList.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 1rem;">Erreur</p>';
                    });
            } else {
                ingredientsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 1rem;">Aucun ingrédient nécessaire</p>';
            }
        }
    }
}

function removeFromPlaylist(playlistId, cocktailId) {
    if (playlistId === 'liked') {
        const likedIds = JSON.parse(localStorage.getItem(`marmitonic_liked_${marmitonicUserId}`) || '[]');
        const filtered = likedIds.filter(id => id !== cocktailId);
        localStorage.setItem(`marmitonic_liked_${marmitonicUserId}`, JSON.stringify(filtered));
        updateLikedCount();
    } else {
        const playlist = userPlaylists.find(p => p.id === playlistId);
        if (playlist) {
            playlist.cocktailIds = (playlist.cocktailIds || []).filter(id => id !== cocktailId);
            savePlaylists();
            renderPlaylistsGrid();
        }
    }
    
    showNotification('Cocktail retiré de la playlist', 'success');
}

function setupModalCloseHandlers(modal) {
    const closeBtn = modal.querySelector('.modal-close');
    const backdrop = modal.querySelector('.modal-backdrop');

    const closeModal = () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    };

    closeBtn.onclick = closeModal;
    backdrop.onclick = closeModal;

    const escHandler = (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

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
    const newPlaylist = {
        id: Date.now().toString(),
        name: name,
        description: description || '',
        cocktailIds: []
    };
    
    userPlaylists.push(newPlaylist);
    savePlaylists();
    
    const playlistsGrid = document.getElementById('playlistsGrid');
    const newCard = createPlaylistCard(newPlaylist);
    
    playlistsGrid.insertBefore(newCard, playlistsGrid.firstChild);
    
    newCard.addEventListener('click', (e) => {
        if (!e.target.closest('.play-button')) {
            openPlaylistModal(newCard.dataset.playlistId);
        }
    });

    showNotification(`Playlist "${name}" créée avec succès !`, 'success');
    
    newCard.style.animation = 'slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
}

// Add cocktail to playlist
function addCocktailToPlaylist(cocktailId, playlistId) {
    if (playlistId === 'liked') {
        const likedIds = JSON.parse(localStorage.getItem(`marmitonic_liked_${marmitonicUserId}`) || '[]');
        if (!likedIds.includes(cocktailId)) {
            likedIds.push(cocktailId);
            localStorage.setItem(`marmitonic_liked_${marmitonicUserId}`, JSON.stringify(likedIds));
            updateLikedCount();
            showNotification('Ajouté aux Cocktails Favoris !', 'success');
        } else {
            showNotification('Déjà dans les Cocktails Favoris', 'info');
        }
    } else {
        const playlist = userPlaylists.find(p => p.id === playlistId);
        if (playlist) {
            if (!playlist.cocktailIds) playlist.cocktailIds = [];
            if (!playlist.cocktailIds.includes(cocktailId)) {
                playlist.cocktailIds.push(cocktailId);
                savePlaylists();
                renderPlaylistsGrid();
                showNotification(`Ajouté à "${playlist.name}" !`, 'success');
            } else {
                showNotification('Déjà dans cette playlist', 'info');
            }
        }
    }
}

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
    
    // Add liked playlist
    dropdownHTML += `
        <div class="dropdown-item" data-playlist-id="liked">
            <i class="fa fa-heart"></i>
            <span>Cocktails Favoris</span>
        </div>
    `;
    
    // Add user playlists
    userPlaylists.forEach(playlist => {
        dropdownHTML += `
            <div class="dropdown-item" data-playlist-id="${playlist.id}">
                <i class="fa fa-list"></i>
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

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    Object.assign(notification.style, {
        position: 'fixed',
        top: '100px',
        right: '20px',
        padding: '16px 24px',
        background: type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'info' ? '#17a2b8' : '#6c757d',
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

window.PlannerAPI = {
    openAddToPlaylistDropdown: function(cocktailId, buttonElement) {
        showPlaylistDropdown(cocktailId, buttonElement);
    },
    addCocktailToPlaylist: addCocktailToPlaylist,
    getPlaylists: function() {
        return [getPlaylist('liked'), ...userPlaylists];
    }
};

function showPlaylistDropdown(cocktailId, buttonElement) {
    const existingDropdown = document.querySelector('.playlist-dropdown');
    if (existingDropdown) {
        existingDropdown.remove();
        return;
    }

    const dropdown = document.createElement('div');
    dropdown.className = 'playlist-dropdown';
    
    let dropdownHTML = '<div class="dropdown-header">Ajouter à une playlist</div>';
    
    dropdownHTML += `
        <div class="dropdown-item" data-playlist-id="liked">
            <i class="fa fa-heart"></i>
            <span>Cocktails Favoris</span>
        </div>
    `;
    
    userPlaylists.forEach(playlist => {
        dropdownHTML += `
            <div class="dropdown-item" data-playlist-id="${playlist.id}">
                <i class="fa fa-list"></i>
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
        console.log(`Adding cocktail ${cocktailId} to playlist ${playlistId}`);
    }
}
