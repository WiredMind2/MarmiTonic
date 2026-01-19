// Cocktail Detail Page JavaScript

let marmitonicUserId = null;
let currentCocktail = null;

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

    add(cocktail) {
        try {
            if (!cocktail || !cocktail.id) return;
            let recent = this.get();
            recent = recent.filter(c => c.id !== cocktail.id);
            recent.unshift({
                id: cocktail.id,
                name: cocktail.name,
                image: cocktail.image,
                timestamp: Date.now()
            });
            recent = recent.slice(0, this.maxItems);
            localStorage.setItem(this.key, JSON.stringify(recent));
        } catch (e) {
            console.error('Error saving recently viewed:', e);
        }
    },

    clear() {
        localStorage.removeItem(this.key);
    }
};

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

document.addEventListener('DOMContentLoaded', () => {
    marmitonicUserId = getOrCreateUserId();
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
        
        // Check if already favorited - will be set after cocktail loads
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

    // Use id if available
    const cocktailId = currentCocktail?.id;
    
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

    const userPlaylists = JSON.parse(localStorage.getItem(`marmitonic_playlists_${marmitonicUserId}`) || '[]');
    
    const playlists = [
        { id: 'liked', name: 'Cocktails Favoris', icon: 'fa-heart' },
        ...userPlaylists.map(p => ({ id: p.id, name: p.name, icon: 'fa-list' }))
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
    if (playlistId === 'liked') {
        const likedIds = JSON.parse(localStorage.getItem(`marmitonic_liked_${marmitonicUserId}`) || '[]');
        if (!likedIds.includes(cocktailId)) {
            likedIds.push(cocktailId);
            localStorage.setItem(`marmitonic_liked_${marmitonicUserId}`, JSON.stringify(likedIds));
            showNotification('Ajouté aux Cocktails Favoris !', 'success');
        } else {
            showNotification('Déjà dans les Cocktails Favoris', 'info');
        }
    } else {
        const userPlaylists = JSON.parse(localStorage.getItem(`marmitonic_playlists_${marmitonicUserId}`) || '[]');
        const playlist = userPlaylists.find(p => p.id === playlistId);
        if (playlist) {
            if (!playlist.cocktailIds) playlist.cocktailIds = [];
            if (!playlist.cocktailIds.includes(cocktailId)) {
                playlist.cocktailIds.push(cocktailId);
                localStorage.setItem(`marmitonic_playlists_${marmitonicUserId}`, JSON.stringify(userPlaylists));
                showNotification(`Ajouté à "${playlistName}" !`, 'success');
            } else {
                showNotification('Déjà dans cette playlist', 'info');
            }
        }
    }
}

function handleToggleFavorite() {
    const btn = document.getElementById('favoriteBtn');
    const icon = btn.querySelector('i');
    const isActive = btn.classList.contains('active');
    
    // Use id if available
    const cocktailId = currentCocktail?.id;
    
    const likedIds = JSON.parse(localStorage.getItem(`marmitonic_liked_${marmitonicUserId}`) || '[]');

    if (isActive) {
        btn.classList.remove('active');
        icon.classList.remove('fa-heart');
        icon.classList.add('fa-heart-o');
        const filtered = likedIds.filter(id => id !== cocktailId);
        localStorage.setItem(`marmitonic_liked_${marmitonicUserId}`, JSON.stringify(filtered));
        showNotification('Retiré des favoris', 'info');
    } else {
        btn.classList.add('active');
        icon.classList.remove('fa-heart-o');
        icon.classList.add('fa-heart');
        if (!likedIds.includes(cocktailId)) {
            likedIds.push(cocktailId);
            localStorage.setItem(`marmitonic_liked_${marmitonicUserId}`, JSON.stringify(likedIds));
        }
        showNotification('Ajouté aux favoris !', 'success');
        
        // Add heart animation
        btn.style.transform = 'scale(1.2)';
        setTimeout(() => {
            btn.style.transform = '';
        }, 200);
    }
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

// Update Difficulty based on ingredient count
function updateDifficulty(ingredients) {
    const difficultyEl = document.getElementById('difficulty');
    if (!difficultyEl) return;
    
    const ingredientCount = ingredients ? ingredients.length : 0;
    let difficulty = '';
    
    if (ingredientCount <= 3) {
        difficulty = 'Facile';
    } else if (ingredientCount >= 4 && ingredientCount <= 6) {
        difficulty = 'Moyen';
    } else { // 7+
        difficulty = 'Difficile';
    }
    
    difficultyEl.textContent = difficulty;
}

// Load Cocktail Data
async function loadCocktailData(cocktailId) {
    try {
        // Fetch cocktail from backend
        const cocktails = await fetchCocktails();
        // Try to find by ID
        const cocktail = cocktails.find(c => 
            c.id === cocktailId
        );
        
        if (cocktail) {
            currentCocktail = cocktail;
            populateCocktailData(cocktail);
            // Save to recently viewed so detail page records visits from anywhere
            try {
                RecentlyViewed.add({ id: cocktail.id, name: cocktail.name, image: cocktail.image });
            } catch (e) {
                console.error('Error adding to recently viewed:', e);
            }
        } else {
            showNotification('Cocktail non trouvé', 'error');
            setTimeout(() => window.location.href = 'discovery.html', 2000);
        }
        
    } catch (error) {
        console.error('Error loading cocktail:', error);
        showNotification('Erreur lors du chargement du cocktail', 'error');
    }
}

function populateCocktailData(data) {
    // Update title
    const nameEl = document.getElementById('cocktailName');
    if (nameEl) nameEl.textContent = data.name;
    
    // Update difficulty based on ingredient count
    updateDifficulty(data.parsed_ingredients);
    
    // Update meta information
    const servedEl = document.getElementById('servedType');
    if (servedEl) servedEl.textContent = data.served || 'N/A';
    
    const garnishEl = document.getElementById('garnishType');
    if (garnishEl) garnishEl.textContent = data.garnish || 'N/A';
    
    // Update image
    const imageEl = document.getElementById('cocktailImage');
    if (imageEl && data.image) {
        imageEl.src = data.image;
        imageEl.alt = data.name;
    }
    
    // Update description
    const descEl = document.getElementById('cocktailDescription');
    if (descEl) {
        descEl.textContent = data.description || data.descriptions?.en || 'No description available';
    }
    
    // Update ingredients
    const ingredientsList = document.getElementById('ingredientsList');
    if (ingredientsList && data.parsed_ingredients) {
        ingredientsList.innerHTML = '';
        data.parsed_ingredients.forEach(ingredient => {
            const item = createIngredientItem(ingredient);
            ingredientsList.appendChild(item);
        });
    }
    
    // Update instructions
    const instructionsList = document.getElementById('instructionsList');
    if (instructionsList && data.preparation) {
        instructionsList.innerHTML = '';
        const steps = data.preparation.split(/\d+\./).filter(s => s.trim());
        steps.forEach((instruction, index) => {
            const step = createInstructionStep(instruction.trim(), index + 1);
            instructionsList.appendChild(step);
        });
    }
    
    // Re-initialize interactive elements
    initializeIngredientTracking();
    initializeInstructionSteps();
    
    // Update favorite button state
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (favoriteBtn && data.id) {
        const cocktailId = data.id;
        const likedIds = JSON.parse(localStorage.getItem(`marmitonic_liked_${marmitonicUserId}`) || '[]');
        const isFavorited = likedIds.includes(cocktailId);
        
        if (isFavorited) {
            favoriteBtn.classList.add('active');
            favoriteBtn.querySelector('i').classList.remove('fa-heart-o');
            favoriteBtn.querySelector('i').classList.add('fa-heart');
        }
    }
    
    // Load similar cocktails
    loadSimilarCocktails(data);
}

async function loadSimilarCocktails(currentCocktail) {
    try {
        const allCocktails = await fetchCocktails();
        
        // Calculate similarity based on shared ingredients
        const similarities = allCocktails
            .filter(c => c.id !== currentCocktail.id) // Exclude current cocktail
            .map(cocktail => {
                const currentIngredients = new Set(currentCocktail.parsed_ingredients || []);
                const otherIngredients = new Set(cocktail.parsed_ingredients || []);
                
                // Count shared ingredients
                let sharedCount = 0;
                currentIngredients.forEach(ing => {
                    if (otherIngredients.has(ing)) sharedCount++;
                });
                
                return {
                    cocktail,
                    sharedCount,
                    totalIngredients: otherIngredients.size
                };
            })
            .filter(item => item.sharedCount > 0) // Only keep cocktails with at least 1 shared ingredient
            .sort((a, b) => b.sharedCount - a.sharedCount) // Sort by most shared ingredients
            .slice(0, 3); // Take top 3
        
        if (similarities.length > 0) {
            const similarSection = document.getElementById('similarSection');
            const similarCocktails = document.getElementById('similarCocktails');
            
            if (similarSection && similarCocktails) {
                similarCocktails.innerHTML = '';
                
                similarities.forEach(({ cocktail, sharedCount, totalIngredients }) => {
                    const card = createSimilarCocktailCard(cocktail, sharedCount, totalIngredients);
                    similarCocktails.appendChild(card);
                });
                
                similarSection.style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Error loading similar cocktails:', error);
    }
}

function createSimilarCocktailCard(cocktail, sharedCount, totalIngredients) {
    const a = document.createElement('a');
    a.className = 'similar-card';
    a.href = `cocktail-detail.html?id=${cocktail.id}`;
    
    const imageUrl = cocktail.image || 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=150&h=150&fit=crop';
    
    a.innerHTML = `
        <img src="${imageUrl}" alt="${cocktail.name}">
        <div class="similar-info">
            <h4>${cocktail.name}</h4>
            <span class="similar-meta">${sharedCount}/${totalIngredients} ingrédients similaires</span>
        </div>
    `;
    
    return a;
}

function createIngredientItem(ingredient) {
    const div = document.createElement('div');
    div.className = 'ingredient-item';
    
    // ingredient is just a string (name) from parsed_ingredients
    const ingredientName = typeof ingredient === 'string' ? ingredient : ingredient.name || ingredient;
    
    div.innerHTML = `
        <div class="ingredient-icon">
            <i class="fa fa-flask"></i>
        </div>
        <div class="ingredient-info">
            <span class="ingredient-name">${ingredientName}</span>
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
