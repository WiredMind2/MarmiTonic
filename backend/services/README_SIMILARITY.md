# Guide d'utilisation du système de recherche par similitude

## Vue d'ensemble

Le système de recherche par similitude utilise **FAISS** (Facebook AI Similarity Search) et **RAG** (Retrieval-Augmented Generation) pour proposer des cocktails similaires basés sur leur contenu sémantique.

## Architecture

### 1. Service de Similarité (`similarity_service.py`)

Le service principal qui gère:
- **Embeddings**: Utilise `sentence-transformers/all-MiniLM-L6-v2` pour créer des représentations vectorielles des cocktails
- **Index FAISS**: Stocke et recherche efficacement dans l'espace vectoriel
- **Cache**: Sauvegarde l'index pour éviter de le reconstruire à chaque démarrage

### 2. Endpoints API

#### `/cocktails/similar/{cocktail_id}`
Trouve les cocktails similaires à un cocktail donné.
```bash
GET /cocktails/similar/http://dbpedia.org/resource/Mojito?top_k=5
```

#### `/cocktails/search-semantic`
Recherche sémantique par texte libre (RAG).
```bash
GET /cocktails/search-semantic?query=cocktail fruité et rafraîchissant&top_k=5
```

#### `/cocktails/similar-by-ingredients`
Trouve des cocktails similaires basés sur des ingrédients.
```bash
GET /cocktails/similar-by-ingredients?ingredients=vodka&ingredients=citron&top_k=5
```

#### `/cocktails/build-index` (POST)
Construit ou reconstruit l'index FAISS.
```bash
POST /cocktails/build-index?force_rebuild=false
```

## Installation

### 1. Installer les dépendances

```bash
pip install -r backend/requirements.txt
```

Nouvelles dépendances ajoutées:
- `faiss-cpu==1.7.4`: Bibliothèque de recherche par similitude
- `sentence-transformers==2.2.2`: Modèles d'embeddings
- `numpy==1.24.3`: Calculs numériques

### 2. Construire l'index initial

Avant d'utiliser la recherche par similitude, vous devez construire l'index:

```python
# Démarrer le serveur
uvicorn backend.main:app --reload

# Dans un autre terminal ou via l'interface web
curl -X POST http://localhost:8000/cocktails/build-index
```

Ou via l'interface web sur [similar.html](http://localhost:8000/pages/similar.html), cliquer sur "Construire/Actualiser l'Index".

## Utilisation

### Interface Web

1. Ouvrez `frontend/pages/similar.html`
2. Choisissez un type de recherche:
   - **Recherche Textuelle (RAG)**: Décrivez ce que vous cherchez en langage naturel
   - **Par Cocktail**: Sélectionnez un cocktail pour trouver des similaires
   - **Par Ingrédients**: Entrez des ingrédients séparés par des virgules

### Exemples d'utilisation

#### Recherche sémantique
```javascript
const results = await searchCocktailsSemantic(
    "cocktail tropical avec du rhum et des fruits exotiques", 
    10
);
```

#### Cocktails similaires
```javascript
const results = await fetchSimilarCocktails(
    "http://dbpedia.org/resource/Mojito", 
    5
);
```

#### Recherche par ingrédients
```javascript
const results = await fetchSimilarByIngredients(
    ["vodka", "citron", "sucre"], 
    5
);
```

## Comment ça marche ?

### 1. Création des embeddings

Pour chaque cocktail, on crée une représentation textuelle contenant:
- Nom
- Ingrédients
- Catégorie
- Description
- Instructions

Cette représentation est transformée en vecteur dense par le modèle `sentence-transformers`.

### 2. Index FAISS

FAISS utilise la recherche par produit scalaire (Inner Product) pour trouver les vecteurs les plus similaires. Les vecteurs sont normalisés, ce qui rend le produit scalaire équivalent à la similarité cosinus.

### 3. Recherche

Quand vous faites une recherche:
1. Le texte de recherche est converti en embedding
2. FAISS trouve les k vecteurs les plus proches
3. Les cocktails correspondants sont retournés avec leur score de similarité

## Optimisation

### Performances

- **Index en mémoire**: L'index est chargé en mémoire pour des recherches ultra-rapides
- **Cache sur disque**: L'index est sauvegardé dans `backend/data/` pour éviter de le reconstruire
- **Normalisation**: Les vecteurs normalisés permettent d'utiliser le produit scalaire au lieu de la distance euclidienne

### Amélioration de la qualité

Pour améliorer les résultats:
1. Utilisez un modèle d'embedding plus performant (ex: `all-mpnet-base-v2`)
2. Enrichissez la représentation textuelle des cocktails
3. Ajoutez plus de métadonnées (alcool fort, goût, occasion, etc.)

### Mettre à jour l'index

L'index doit être reconstruit quand:
- De nouveaux cocktails sont ajoutés
- Les données des cocktails sont modifiées
- Vous changez de modèle d'embedding

```bash
curl -X POST http://localhost:8000/cocktails/build-index?force_rebuild=true
```

## Fichiers générés

Le système crée automatiquement:
- `backend/data/faiss_index.bin`: Index FAISS binaire
- `backend/data/cocktails_cache.pkl`: Cache des objets Cocktail
- `backend/data/embeddings_cache.pkl`: Cache des embeddings

Ces fichiers peuvent être supprimés sans danger, ils seront recréés automatiquement.

## Troubleshooting

### L'index n'est pas construit
```
Erreur: Index not built
```
**Solution**: Appelez l'endpoint `/cocktails/build-index` POST

### Pas de résultats trouvés
**Causes possibles**:
- L'index est vide (pas de cocktails dans la base)
- La requête est trop spécifique
- Le cocktail ID est invalide

### Erreur de mémoire
Si vous avez beaucoup de cocktails, vous pourriez manquer de RAM.
**Solution**: Utilisez `faiss-gpu` au lieu de `faiss-cpu` ou utilisez un index quantifié (IndexIVFFlat)

## Évolutions futures

Améliorations possibles:
- [ ] Filtrage par catégorie/ingrédients
- [ ] Recherche hybride (sémantique + filtres)
- [ ] Support multi-langues
- [ ] Index quantifié pour économiser la mémoire
- [ ] API de recommandation personnalisée basée sur l'historique
- [ ] Fine-tuning du modèle sur des données de cocktails
