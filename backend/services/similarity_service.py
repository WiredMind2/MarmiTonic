from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from ..models.cocktail import Cocktail
from .cocktail_service import CocktailService


class SimilarityService:
    """Service de recherche de cocktails similaires avec FAISS et RAG."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.cocktail_service = CocktailService()
        self.model = SentenceTransformer(model_name)
        self.index: Optional[faiss.Index] = None
        self.cocktails: List[Cocktail] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index_path = "backend/data/faiss_index.bin"
        self.cocktails_path = "backend/data/cocktails_cache.pkl"
        self.embeddings_path = "backend/data/embeddings_cache.pkl"
        
    def _create_cocktail_text(self, cocktail: Cocktail) -> str:
        parts = [f"Nom: {cocktail.name}", f"Ingrédients: {', '.join(cocktail.ingredients)}"]
        if cocktail.category:
            parts.append(f"Catégorie: {cocktail.category}")
        if cocktail.description:
            parts.append(f"Description: {cocktail.description}")
        if cocktail.instructions:
            parts.append(f"Instructions: {cocktail.instructions}")
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
        
        cocktail_idx = None
        for idx, cocktail in enumerate(self.cocktails):
            if cocktail.id == cocktail_id:
                cocktail_idx = idx
                break
        if cocktail_idx is None:
            return []
        
        query_embedding = self.embeddings[cocktail_idx:cocktail_idx+1]
        k = top_k + 1 if exclude_self else top_k
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, (distance, cocktail_idx) in enumerate(zip(distances[0], indices[0])):
            if exclude_self and cocktail_idx == cocktail_idx:
                continue
            if len(results) >= top_k:
                break
            cocktail = self.cocktails[cocktail_idx]
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
