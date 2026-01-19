"""
Parser centralisé pour charger et interroger les données IBA en mémoire
Charge le fichier data.ttl et parse correctement les ingrédients depuis dbp:ingredients
Retourne des instances de classes Pydantic définies dans backend/models
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path.resolve()))

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS
from typing import List, Dict, Any, Optional, Set
import os
import re

from backend.models.cocktail import Cocktail
from backend.models.ingredient import Ingredient

# Définition des namespaces DBpedia
DBR = Namespace("http://dbpedia.org/resource/")
DBO = Namespace("http://dbpedia.org/ontology/")
DBP = Namespace("http://dbpedia.org/property/")
DCT = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")


class IBADataParser:
    """Parser pour les données IBA en format Turtle avec extraction d'ingrédients"""
    
    _instance = None
    _lock = __import__('threading').Lock()
    
    def __new__(cls, ttl_file_path: str = "data.ttl"):
        """Singleton pattern to ensure only one parser instance exists"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(IBADataParser, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, ttl_file_path: str = "data.ttl"):
        """
        Initialise le parser et charge le fichier TTL en mémoire
        
        Args:
            ttl_file_path: Chemin vers le fichier TTL (relatif au répertoire data/)
        """
        # Only initialize once
        if self._initialized:
            return
            
        print(f"Initializing IBADataParser (singleton) with ttl_file_path: '{ttl_file_path}'")
        self.graph = Graph()
        self.ttl_file_path = ttl_file_path
        self._ingredients_cache = None  # Cache pour les ingrédients dédupliqués
        self._cocktails_cache = None     # Cache pour les cocktails
        self._load_data()
        self._initialized = True
        print(f"✅ IBADataParser initialized with {len(self.graph)} triples")
    
    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate a URL-friendly slug from cocktail name"""
        slug = name.lower()
        slug = re.sub(r'\([^)]*\)', '', slug)
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def _load_data(self):
        """Charge le fichier TTL dans le graph RDFLib"""
        import time
        # Utiliser un chemin absolu basé sur la racine du projet
        project_root = Path(__file__).parent.parent.parent  # Remonte de data/ vers backend/ vers racine
        file_path = project_root / "backend" / "data" / self.ttl_file_path
        
        try:
            print(f"Loading TTL file: {file_path}...")
            start_time = time.time()
            self.graph.parse(str(file_path), format="turtle", encoding="utf-8")
            load_time = time.time() - start_time
            print(f"✅ Loaded {len(self.graph)} triples in {load_time:.3f}s")
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            raise
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            raise
    
    def _parse_ingredients_text(self, ingredients_text: str) -> List[str]:
        """
        Parse le texte des ingrédients pour extraire les noms
        Format typique: "* 30 ml gin\n* 30 ml vermouth\n* splash soda"
        
        Args:
            ingredients_text: Texte brut contenant les ingrédients
            
        Returns:
            Liste des noms d'ingrédients normalisés
        """
        if not ingredients_text:
            return []
        
        ingredients = []
        
        # Séparer par lignes
        lines = ingredients_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Enlever les bullets (* ou -)
            line = re.sub(r'^[\*\-]\s*', '', line)

            # Enlever les quantités (nombres + unités)
            # Ex: "30 ml gin" -> "gin", "1 dash bitters" -> "bitters"
            line = re.sub(r'^\d+\.?\d*\s*(ml|cl|oz|dash|dashes|barspoon|teaspoon|tsp|tablespoon|tbsp|drop|drops|splash|piece|pieces|cube|cubes|slice|slices|splash|teaspoons|of)?\s+', '', line, flags=re.IGNORECASE)
            
            # Nettoyer les espaces multiples    
            line = re.sub(r'\s+', ' ', line).strip()

            
            #Cas particulier, 1/4 barspoon Absinthe supprimer le 1/4
            line = re.sub(r'^\d+\/\d+\s*(ml|cl|oz|dash|dashes|barspoon|teaspoon|tsp|tablespoon|tbsp|drop|drops|splash|piece|pieces|cube|cubes|slice|slices)?\s+', '', line, flags=re.IGNORECASE)

            #Les cas rares Select/Aperol/Campari/Cynar garder que Cynar
            line = re.sub(r'^(Select)\/', '', line, flags=re.IGNORECASE)
            line = re.sub(r'^(Aperol)\/', '', line, flags=re.IGNORECASE)
            line = re.sub(r'^(Campari)\/', '', line, flags=re.IGNORECASE)

            #5.049216E8 supprimer cette ligne si elle est présente
            line = re.sub(r'^5\.049216E8$', '', line, flags=re.IGNORECASE)

            #Supprimer les splash
            line = re.sub(r'^(splash of|splash|a splash of)\s+', '', line, flags=re.IGNORECASE)


            #supprimer les barspoon of bar spoon
            line = re.sub(r'^(barspoon of|bar spoon of|barspoon|bar spoon|bar spoons)\s+', '', line, flags=re.IGNORECASE)
            
            #supprimer les lignes qui commencent par 100%
            line = re.sub(r'^(100%|100 %)\s+', '', line, flags=re.IGNORECASE)
            
            #Remplacer of Worcestershire sauce par Worcestershire sauce
            line = re.sub(r'^(of)\s+Worcestershire sauce', 'Worcestershire sauce', line, flags=re.IGNORECASE)
           
            #to 8 mint leaves -> mint leaves
            line = re.sub(r'^(to\s+8|to\s+6|to\s+4|to\s+2|to\s+1)\s+', '', line, flags=re.IGNORECASE)
            
            #Two dashes Peychaud's Bitters -> Peychaud's Bitters and Few dashes Angostura bitters -> Angostura bitters
            line = re.sub(r'^(two|few|one|three|four|five|six|seven|eight|nine|ten)\s+dashes\s+', '', line, flags=re.IGNORECASE)
            line = re.sub(r'^(two|few|one|three|four|five|six|seven|eight|nine|ten)\s+dash\s+', '', line, flags=re.IGNORECASE)

            #Few drops of egg white -> egg white
            line = re.sub(r'^(few|one|two|three|four|five|six|seven|eight|nine|ten)\s+drops?\s+(of\s+)?', '', line, flags=re.IGNORECASE)

            if line and len(line) > 1:  # Ignorer les lignes vides ou trop courtes
                ingredients.append(line)
        
        return ingredients
    
    def _normalize_ingredient_name(self, name: str) -> str:
        """
        Normalise le nom d'un ingrédient pour la déduplication
        
        Args:
            name: Nom brut de l'ingrédient
            
        Returns:
            Nom normalisé (minuscules, sans espaces superflus)
        """
        # Minuscules
        normalized = name.lower().strip()
        
        # Remplacer certaines variations courantes
        replacements = {
            'fresh ': '',
            'freshly ': '',
            'squeezed ': '',
            'simple ': '',
            ' syrup': ' syrup',  # Garder tel quel
            'sweet red ': 'sweet ',
            'dry ': '',
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        normalized = normalized.strip()
        
        return normalized
    
    def _extract_all_ingredients(self) -> Dict[str, Dict[str, Any]]:
        """
        Extrait tous les ingrédients uniques depuis les cocktails
        Parse dbp:ingredients de chaque cocktail et déduplique
        
        Returns:
            Dictionnaire {nom_normalisé: {name, count, cocktails}}
        """
        ingredients_dict = {}
        
        # Récupérer tous les cocktails avec leurs ingrédients
        query = """
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?cocktail ?cocktailLabel ?ingredients
        WHERE {
            dbr:List_of_IBA_official_cocktails dbo:wikiPageWikiLink ?cocktail .
            OPTIONAL { ?cocktail rdfs:label ?cocktailLabel . FILTER(lang(?cocktailLabel) = "en") }
            OPTIONAL { ?cocktail dbp:ingredients ?ingredients }
        }
        """
        
        results = self.graph.query(query)
        
        for row in results:
            if not row.ingredients:
                continue
            
            cocktail_uri = str(row.cocktail)
            cocktail_name = str(row.cocktailLabel) if row.cocktailLabel else cocktail_uri.split("/")[-1]
            ingredients_text = str(row.ingredients)
            
            # Parser le texte des ingrédients
            ingredient_names = self._parse_ingredients_text(ingredients_text)
            
            for ingredient_name in ingredient_names:
                normalized = self._normalize_ingredient_name(ingredient_name)
                
                if normalized not in ingredients_dict:
                    # Créer un nouvel ingrédient
                    ingredients_dict[normalized] = {
                        "name": ingredient_name,  # Garder la première occurrence pour l'affichage
                        "normalized": normalized,
                        "count": 0,
                        "cocktails": []
                    }
                
                # Incrémenter le compteur et ajouter le cocktail
                ingredients_dict[normalized]["count"] += 1
                if cocktail_uri not in ingredients_dict[normalized]["cocktails"]:
                    ingredients_dict[normalized]["cocktails"].append(cocktail_uri)
        
        return ingredients_dict
    
    def get_all_cocktails(self) -> List[Cocktail]:
        """
        Retourne tous les cocktails IBA avec leurs ingrédients parsés
        
        Returns:
            Liste d'instances Cocktail
        """
        if self._cocktails_cache:
            print(f"Using cached cocktails ({len(self._cocktails_cache)} items)")
            return self._cocktails_cache
        
        print(f"Building cocktails cache...")
        
        query = """
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT DISTINCT ?cocktail ?label ?labelFr ?desc ?descFr ?ingredients ?prep ?served ?garnish ?sourcelink ?img
        WHERE {
            ?cocktail dbp:ingredients ?ingredients .
            OPTIONAL { ?cocktail rdfs:label ?label . FILTER(lang(?label) = "en") }
            OPTIONAL { ?cocktail rdfs:label ?labelFr . FILTER(lang(?labelFr) = "fr") }
            OPTIONAL { ?cocktail dbo:description ?desc . FILTER(lang(?desc) = "en") }
            OPTIONAL { ?cocktail dbo:description ?descFr . FILTER(lang(?descFr) = "fr") }
            OPTIONAL { ?cocktail dbp:prep ?prep }
            OPTIONAL { ?cocktail dbp:served ?served }
            OPTIONAL { ?cocktail dbp:garnish ?garnish }
            OPTIONAL { ?cocktail dbp:sourcelink ?sourcelink }
            OPTIONAL { ?cocktail foaf:depiction ?img }
        }
        ORDER BY ?label
        """
        
        results = self.graph.query(query)
        cocktails_dict = {}  # Dédupliquer par URI
        
        for row in results:
            cocktail_uri = str(row.cocktail)
            
            # Si déjà dans le dict, on l'ignore (on garde la première occurence)
            if cocktail_uri in cocktails_dict:
                continue
            
            # Parser les ingrédients
            parsed_ingredients = []
            ingredients_raw = None
            if row.ingredients:
                ingredients_raw = str(row.ingredients)
                raw_ingredients = self._parse_ingredients_text(ingredients_raw)
                # Normalize and Title Case for consistency
                parsed_ingredients = [self._normalize_ingredient_name(ing).title() for ing in raw_ingredients]
            
            # Construire les labels multilingues
            labels = {}
            if row.label:
                labels["en"] = str(row.label)
            if row.labelFr:
                labels["fr"] = str(row.labelFr)
            
            # Construire les descriptions multilingues
            descriptions = {}
            if row.desc:
                descriptions["en"] = str(row.desc)
            if row.descFr:
                descriptions["fr"] = str(row.descFr)
            
            # Récupérer les catégories
            categories = [str(cat) for cat in self.graph.objects(URIRef(cocktail_uri), DCT.subject)]
            
            # Générer le nom du cocktail
            cocktail_name = str(row.label) if row.label else cocktail_uri.split("/")[-1].replace("_", " ")
            
            # Créer l'instance Cocktail
            cocktail = Cocktail(
                uri=cocktail_uri,
                id=self.generate_slug(cocktail_name),
                name=cocktail_name,
                description=str(row.desc) if row.desc else None,
                image=str(row.img) if row.img else None,
                ingredients=ingredients_raw,
                parsed_ingredients=parsed_ingredients,
                preparation=str(row.prep) if row.prep else None,
                source_link=str(row.sourcelink) if row.sourcelink else None,
                categories=categories if categories else None
            )
            cocktails_dict[cocktail_uri] = cocktail
        
        # Convertir en liste
        cocktails = list(cocktails_dict.values())
        self._cocktails_cache = cocktails
        return cocktails
    
    def get_cocktail_details(self, cocktail_uri: str) -> Optional[Dict[str, Any]]:
        """
        Retourne les détails complets d'un cocktail
        
        Args:
            cocktail_uri: URI du cocktail (ex: "http://dbpedia.org/resource/Martini_(cocktail)")
        
        Returns:
            Dictionnaire avec toutes les propriétés du cocktail
        """
        cocktail_ref = URIRef(cocktail_uri)
        
        # Vérifier que le cocktail existe
        if (DBR.List_of_IBA_official_cocktails, DBO.wikiPageWikiLink, cocktail_ref) not in self.graph:
            return None
        
        details = {
            "uri": cocktail_uri,
            "id": cocktail_uri.split("/")[-1],
            "labels": {},
            "descriptions": {},
            "images": [],
            "ingredients_raw": None,
            "ingredients_parsed": [],
            "preparation": None,
            "garnish": None,
            "served": None,
            "name": None,
            "sourcelink": None,
            "categories": [],
            "related_links": []
        }
        
        # Labels (multilingues)
        for label in self.graph.objects(cocktail_ref, RDFS.label):
            if isinstance(label, Literal) and label.language:
                details["labels"][label.language] = str(label)
        
        # Descriptions (multilingues)
        for desc in self.graph.objects(cocktail_ref, DBO.description):
            if isinstance(desc, Literal) and desc.language:
                details["descriptions"][desc.language] = str(desc)
        
        # Images
        for img in self.graph.objects(cocktail_ref, FOAF.depiction):
            details["images"].append(str(img))
        
        # Ingrédients bruts
        ingredients_value = self.graph.value(cocktail_ref, DBP.ingredients)
        if ingredients_value:
            details["ingredients_raw"] = str(ingredients_value)
            # Parser les ingrédients
            raw_ingredients = self._parse_ingredients_text(details["ingredients_raw"])
            details["ingredients_parsed"] = [self._normalize_ingredient_name(ing).title() for ing in raw_ingredients]
        
        # Autres propriétés DBpedia
        for prop, key in [
            (DBP.prep, "preparation"),
            (DBP.name, "name"),
            (DBP.sourcelink, "sourcelink")
        ]:
            value = self.graph.value(cocktail_ref, prop)
            if value:
                details[key] = str(value)
        
        # Catégories
        for cat in self.graph.objects(cocktail_ref, DCT.subject):
            details["categories"].append(str(cat))
        
        # Liens wiki sortants
        for link in self.graph.objects(cocktail_ref, DBO.wikiPageWikiLink):
            details["related_links"].append(str(link))
        
        return details
    
    def get_all_ingredients(self) -> List[Ingredient]:
        """
        Retourne tous les ingrédients uniques extraits des cocktails
        Dédupliqués et triés par fréquence d'utilisation
        
        Returns:
            Liste d'instances Ingredient
        """
        if self._ingredients_cache:
            print(f"Using cached ingredients ({len(self._ingredients_cache)} items)")
            return self._ingredients_cache
        
        print(f"Building ingredients cache...")
        
        ingredients_dict = self._extract_all_ingredients()
        
        # Convertir en liste d'instances Ingredient
        ingredient_list = []
        for normalized, data in ingredients_dict.items():
            # Créer un ID unique basé sur le nom normalisé
            ingredient_id = f"http://marmitonic.local/ingredient/{normalized.replace(' ', '_')}"
            
            # Créer l'instance Ingredient
            ingredient = Ingredient(
                id=ingredient_id,
                name=normalized.title(), # Use normalized name for consistency (e.g. "Dry Vermouth" -> "Vermouth")
                description=f"Utilisé dans {data['count']} cocktails IBA",
                categories=[f"Count:{data['count']}"]  # Stocker le count dans les catégories temporairement
            )
            ingredient_list.append(ingredient)
        
        # Trier par fréquence d'utilisation (plus utilisé en premier) puis alphabétique
        def sort_key(ing):
            if ing.categories and ing.categories[0].startswith('Count:'):
                count = int(ing.categories[0].split(':')[1])
                return (-count, ing.name.lower())
            return (0, ing.name.lower())
        
        ingredient_list.sort(key=sort_key)
        
        self._ingredients_cache = ingredient_list
        return ingredient_list
    
    def get_cocktails_by_ingredients(self, ingredient_names: List[str]) -> List[Cocktail]:
        """
        Trouve les cocktails qui contiennent tous les ingrédients donnés
        
        Args:
            ingredient_names: Liste de noms d'ingrédients (normalisés)
        
        Returns:
            Liste d'instances Cocktail correspondantes
        """
        # Normaliser les noms d'ingrédients recherchés
        search_ingredients = set(self._normalize_ingredient_name(ing) for ing in ingredient_names)
        
        matching_cocktails = []
        
        for cocktail in self.get_all_cocktails():
            cocktail_ingredients = set(cocktail.parsed_ingredients or [])
            
            # Vérifier si tous les ingrédients recherchés sont présents
            if search_ingredients.issubset(cocktail_ingredients):
                matching_cocktails.append(cocktail)
        
        return matching_cocktails
    
    def search_cocktails(self, query_text: str) -> List[Cocktail]:
        """
        Recherche des cocktails par nom
        
        Args:
            query_text: Texte à rechercher dans les noms
        
        Returns:
            Liste d'instances Cocktail correspondantes
        """
        all_cocktails = self.get_all_cocktails()
        query_lower = query_text.lower()
        
        return [
            c for c in all_cocktails
            if query_lower in c.name.lower()
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur les données
        
        Returns:
            Dictionnaire avec les statistiques
        """
        cocktails = self.get_all_cocktails()
        ingredients = self.get_all_ingredients()
        
        # Calculer le nombre moyen d'ingrédients par cocktail
        total_ingredients = sum(len(c.parsed_ingredients or []) for c in cocktails)
        avg_ingredients = total_ingredients / len(cocktails) if cocktails else 0
        
        return {
            "total_triples": len(self.graph),
            "total_cocktails": len(cocktails),
            "total_unique_ingredients": len(ingredients),
            "avg_ingredients_per_cocktail": round(avg_ingredients, 2),
            "most_used_ingredient": ingredients[0].name if ingredients else None
        }
    
    def execute_sparql(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        Exécute une requête SPARQL arbitraire sur le graph
        
        Args:
            sparql_query: Requête SPARQL à exécuter
        
        Returns:
            Résultats de la requête
        """
        results = self.graph.query(sparql_query)
        
        result_list = []
        for row in results:
            row_dict = {}
            for var in results.vars:
                row_dict[str(var)] = str(row[var]) if row[var] else None
            result_list.append(row_dict)
        
        return result_list


# Instance globale (singleton) pour éviter de recharger le fichier à chaque fois
def get_parser() -> IBADataParser:
    """
    Retourne l'instance singleton du parser
    
    Returns:
        Instance du parser IBA
    """
    return IBADataParser()


# Fonctions d'accès rapide
def get_all_cocktails() -> List[Cocktail]:
    """Retourne tous les cocktails"""
    return get_parser().get_all_cocktails()

def get_cocktail_details(cocktail_uri: str) -> Optional[Dict[str, Any]]:
    """Retourne les détails d'un cocktail"""
    return get_parser().get_cocktail_details(cocktail_uri)

def get_all_ingredients() -> List[Ingredient]:
    """Retourne tous les ingrédients"""
    return get_parser().get_all_ingredients()

def search_cocktails(query: str) -> List[Cocktail]:
    """Recherche des cocktails"""
    return get_parser().search_cocktails(query)

def get_cocktails_by_ingredients(ingredients: List[str]) -> List[Cocktail]:
    """Trouve les cocktails par ingrédients"""
    return get_parser().get_cocktails_by_ingredients(ingredients)

def get_stats() -> Dict[str, Any]:
    """Retourne les statistiques"""
    return get_parser().get_stats()

def execute_sparql(query: str) -> List[Dict[str, Any]]:
    """Exécute une requête SPARQL"""
    return get_parser().execute_sparql(query)


if __name__ == "__main__":
    # Test du parser
    print("\n=== Test du parser IBA ===\n")
    
    parser = IBADataParser()
    
    # Stats
    stats = parser.get_stats()
    print(f"📊 Statistiques:")
    print(f"   - Triples: {stats['total_triples']}")
    print(f"   - Cocktails: {stats['total_cocktails']}")
    print(f"   - Ingrédients uniques: {stats['total_unique_ingredients']}")
    print(f"   - Moyenne ingrédients/cocktail: {stats['avg_ingredients_per_cocktail']}")
    print(f"   - Ingrédient le plus utilisé: {stats['most_used_ingredient']} ({stats['most_used_ingredient_count']} cocktails)")
    
    # Quelques cocktails
    print(f"\n🍸 Premiers cocktails:")
    for cocktail in parser.get_all_cocktails()[:5]:
        ing_count = len(cocktail.parsed_ingredients) if cocktail.parsed_ingredients else 0
        print(f"   - {cocktail.name} ({ing_count} ingrédients)")
    
    # Top 20 ingrédients
    print(f"\n🥃 Top 20 ingrédients les plus utilisés:")
    for i, ingredient in enumerate(parser.get_all_ingredients()[:20], 1):
        # Extract count from categories if available
        count = int(ingredient.categories[0].split(':')[1]) if ingredient.categories and ingredient.categories[0].startswith('Count:') else 0
        print(f"   {i:2d}. {ingredient.name:30s} (utilisé dans {count} cocktails)")
    
    # Détails d'un cocktail
    cocktails = parser.get_all_cocktails()
    if cocktails:
        first = cocktails[0]
        print(f"\n📋 Détails de {first.name}:")
        print(f"   ID: {first.id}")
        if first.parsed_ingredients:
            print(f"   Ingrédients parsés:")
            for ing in first.parsed_ingredients:
                print(f"      - {ing}")
        if first.preparation:
            print(f"   Préparation: {first.preparation[:100]}...")
    
    # Recherche par ingrédient
    print(f"\n🔍 Cocktails contenant 'gin' et 'vermouth':")
    gin_cocktails = parser.get_cocktails_by_ingredients(['gin', 'vermouth'])
    for cocktail in gin_cocktails[:5]:
        print(f"   - {cocktail.name}")
