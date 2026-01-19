from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
import hashlib
import time
from backend.models.cocktail import Cocktail
from backend.models.vibe_cluster import VibeCluster
from backend.services.cocktail_service import CocktailService
from backend.services.llm_service import LLMService, SimpleCache


class SimilarityService:
    """Service de recherche de cocktails similaires avec FAISS et RAG."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", cache_ttl: int = 3600, cache_size: int = 100):
        self.cocktail_service = CocktailService()
        self.llm_service = LLMService(cache_ttl=cache_ttl, cache_size=cache_size)
        self.model = SentenceTransformer(model_name)
        self.index: Optional[faiss.Index] = None
        self.cocktails: List[Cocktail] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index_path = "backend/data/faiss_index.bin"
        self.cocktails_path = "backend/data/cocktails_cache.pkl"
        self.embeddings_path = "backend/data/embeddings_cache.pkl"
        # Create custom cache for cluster title generation
        self.title_cache = SimpleCache(ttl=cache_ttl, max_size=cache_size)
        # Create cache for clusters
        self.clusters_cache = SimpleCache(ttl=cache_ttl, max_size=cache_size)
    
    def _get_cluster_cache_key(self, cocktails: List[Cocktail]) -> str:
        # Generate a unique cache key based on cocktail IDs
        cocktail_ids = sorted([cocktail.id for cocktail in cocktails])
        key_string = "|".join(cocktail_ids)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
        self.embeddings_path = "backend/data/embeddings_cache.pkl"
        
    def _create_cocktail_text(self, cocktail: Cocktail) -> str:
        ingredients = cocktail.ingredients or []
        ingredients_str = ', '.join(str(i) for i in ingredients if i)
        parts = [f"Nom: {cocktail.name}", f"Ingrédients: {ingredients_str}"]
        if cocktail.description:
            parts.append(f"Description: {cocktail.description}")
        if cocktail.alternative_names:
            alt_names_str = ', '.join(cocktail.alternative_names)
            parts.append(f"Noms alternatifs: {alt_names_str}")
        if cocktail.categories:
            categories_str = ', '.join(cocktail.categories)
            parts.append(f"Catégories: {categories_str}")
        if cocktail.related_ingredients:
            related_str = ', '.join(cocktail.related_ingredients)
            parts.append(f"Ingrédients liés: {related_str}")
        return " | ".join(parts)
    
    def build_index(self, force_rebuild: bool = False) -> None:
        if not force_rebuild and os.path.exists(self.index_path) and os.path.exists(self.cocktails_path):
            print("Chargement de l'index existant...")
            self.load_index()
            return
        
        print("Construction de l'index FAISS...")
        self.cocktails = self.cocktail_service.get_all_cocktails()
        print(f"Nombre de cocktails récupérés: {len(self.cocktails)}")
        
        if not self.cocktails:
            print("Aucun cocktail trouvé")
            return
        
        print("Génération des textes des cocktails pour les embeddings...")
        cocktail_texts = [self._create_cocktail_text(c) for c in self.cocktails]
        print("Génération des embeddings...")
        self.embeddings = self.model.encode(cocktail_texts, show_progress_bar=True)
        faiss.normalize_L2(self.embeddings)
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.embeddings)
        
        print(f"Index construit avec {self.index.ntotal} cocktails")
        
        self.save_index()
    
    def save_index(self) -> None:
        if self.index is None:
            return
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.cocktails_path, 'wb') as f:
            pickle.dump(self.cocktails, f)
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print("Index sauvegardé")
    
    def load_index(self) -> bool:
        try:
            if not os.path.exists(self.index_path) or not os.path.exists(self.cocktails_path):
                return False
            self.index = faiss.read_index(self.index_path)
            with open(self.cocktails_path, 'rb') as f:
                self.cocktails = pickle.load(f)
            if os.path.exists(self.embeddings_path):
                with open(self.embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
            print(f"Index chargé: {len(self.cocktails)} cocktails")
            return True
        except Exception as e:
            print(f"Erreur chargement index: {e}")
            return False
    
    def find_similar_cocktails(self, cocktail_id: str, top_k: int = 5, exclude_self: bool = True) -> List[Dict[str, Any]]:
        if self.index is None or not self.cocktails:
            self.build_index()
        if self.index is None or not self.cocktails:
            return []
        
        original_cocktail_idx = None
        for idx, cocktail in enumerate(self.cocktails):
            if cocktail.id == cocktail_id:
                original_cocktail_idx = idx
                break
        if original_cocktail_idx is None:
            return []
        
        query_embedding = self.embeddings[original_cocktail_idx:original_cocktail_idx+1]
        k = top_k + 1 if exclude_self else top_k
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, (distance, result_idx) in enumerate(zip(distances[0], indices[0])):
            if exclude_self and result_idx == original_cocktail_idx:
                continue
            if len(results) >= top_k:
                break
            cocktail = self.cocktails[result_idx]
            results.append({"cocktail": cocktail, "similarity_score": float(distance), "rank": len(results) + 1})
        return results
    
    def find_similar_by_text(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Recherche sémantique de cocktails par texte libre (RAG)."""
        if self.index is None or not self.cocktails:
            self.build_index()
        if self.index is None or not self.cocktails:
            return []
        
        query_embedding = self.model.encode([query_text])
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx, (distance, cocktail_idx) in enumerate(zip(distances[0], indices[0])):
            cocktail = self.cocktails[cocktail_idx]
            results.append({"cocktail": cocktail, "similarity_score": float(distance), "rank": idx + 1})
        return results
    
    def find_similar_by_ingredients(self, ingredients: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        query_text = f"Cocktail avec les ingrédients: {', '.join(ingredients)}"
        return self.find_similar_by_text(query_text, top_k)
    
    def _generate_cluster_title(self, cocktails: List[Cocktail]) -> str:
        """Generate a vibe/title for a cluster using LLM based on cocktail characteristics."""
        # Check cache first
        cache_key = self._get_cluster_cache_key(cocktails)
        cached_title = self.title_cache.get(cache_key)
        if cached_title:
            return cached_title

        # Create a summary of the cocktails in the cluster
        cocktail_info = []
        for cocktail in cocktails[:5]:  # Use top 5 closest cocktails
            info_parts = [f"- {cocktail.name}"]
            if cocktail.description:
                info_parts.append(f": {cocktail.description[:100]}..." if len(cocktail.description) > 100 else f": {cocktail.description}")
            if cocktail.ingredients:
                ingredients_str = ", ".join(str(i) for i in cocktail.ingredients[:5])  # Limit to 5 ingredients
                info_parts.append(f" (Ingredients: {ingredients_str})")
            if cocktail.categories:
                info_parts.append(f" [Categories: {', '.join(cocktail.categories[:3])}]")
            cocktail_info.append("".join(info_parts))
        
        cocktails_text = "\n".join(cocktail_info)
        
        prompt = f"""Based on these cocktails, generate a short, catchy title (2-4 words) that captures the common vibe or theme of the group. The title should be evocative and creative, like "Tropical Paradise", "Classic Elegance", "Bold & Spicy", "Citrus Dreams", etc.
                     Cocktails: 
                     {cocktails_text}
                     Respond with ONLY the title, nothing else."""
        
        try:
            title = self.llm_service.example(prompt).strip()
            # Remove quotes if present
            title = title.strip('"').strip("'")
            # Cache the result
            self.title_cache.set(cache_key, title)
            return title
        except Exception as e:
            print(f"Error generating cluster title: {e}")
            return f"Cluster Vibe"
    
    def create_cocktails_clusters(self, n_clusters: int = 6) -> Dict[int, VibeCluster]:
        """Regroupe les cocktails en clusters basés sur leurs embeddings."""
        # Check cache first
        cache_key = f"clusters_{n_clusters}"
        cached_clusters = self.clusters_cache.get(cache_key)
        if cached_clusters:
            print(f"Using cached clusters (n_clusters={n_clusters})")
            return cached_clusters

        if self.index is None or not self.cocktails:
            self.build_index()
        if self.index is None or not self.cocktails:
            return {}
        
        d = self.embeddings.shape[1]

        kmeans = faiss.Kmeans(
            d=d,
            k=n_clusters,
            niter=50,
            nredo=5,
            verbose=True,
            gpu=False
        )
        kmeans.train(self.embeddings)
        labels = kmeans.index.search(self.embeddings, 1)[1].flatten()
        distances = kmeans.index.search(self.embeddings, 1)[0].flatten()

        #create clusters dictionary
        clusters: Dict[int, VibeCluster] = {}
        for idx, label in enumerate(labels):
            cocktail = self.cocktails[idx]
            distance = float(distances[idx])  # Convert numpy to Python float
            label_int = int(label)  # Convert numpy.int64 to Python int
            if label_int not in clusters:
                clusters[label_int] = VibeCluster(
                    cluster_id=label_int,
                    title=None,
                    center=None,
                    cocktail_ids=[],
                    closest_to_center=[]
                )
            clusters[label_int].cocktail_ids.append(cocktail.id)
            cocktail.vibe_id = label_int
        
        # Keep track of closest cocktails to center
        centroids = kmeans.centroids
        index_centroid = faiss.IndexFlatIP(d)
        index_centroid.add(self.embeddings)

        D, I = index_centroid.search(
            centroids,
            10  # Top 10 closest to center
        )

        for cluster_id, cluster in clusters.items():
            closest_ids = I[cluster_id]
            closest_cocktail_ids = [self.cocktails[int(i)].id for i in closest_ids if self.cocktails[int(i)].id in cluster.cocktail_ids]
            cluster.closest_to_center = closest_cocktail_ids
            # Convert centroid to Python list of floats
            cluster.center = centroids[cluster_id].tolist()

        for cluster_id, cluster in clusters.items():
            closest_cocktails = [c for c in self.cocktails if c.id in cluster.closest_to_center[:5]]
            if closest_cocktails:
                cluster.title = self._generate_cluster_title(closest_cocktails)
                print(f"Cluster {cluster_id}: '{cluster.title}' with {len(cluster.cocktail_ids)} cocktails.")
            else:
                cluster.title = f"Vibe {cluster_id}"
                print(f"Cluster {cluster_id} has {len(cluster.cocktail_ids)} cocktails.")

        # Cache the clusters
        self.clusters_cache.set(cache_key, clusters)
        print(f"Clusters cached (n_clusters={n_clusters})")
        
        return clusters