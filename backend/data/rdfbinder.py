# This script queries the DBpedia SPARQL endpoint to extract data about IBA official cocktails and saves the results in Turtle format.

import requests
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

query = """
PREFIX dbr:  <http://dbpedia.org/resource/>
PREFIX dbo:  <http://dbpedia.org/ontology/>
PREFIX dbp:  <http://dbpedia.org/property/>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

CONSTRUCT {
  # Liste IBA -> cocktails
  dbr:List_of_IBA_official_cocktails dbo:wikiPageWikiLink ?cocktail .

  # Propriétés cocktail (comme sur ton schéma)
  ?cocktail rdfs:label ?label .
  ?cocktail dbo:description ?desc .
  ?cocktail foaf:depiction ?img .
  ?cocktail dbp:garnish ?garnish .
  ?cocktail dbp:ingredients ?ingredients .
  ?cocktail dbp:name ?name .
  ?cocktail dbp:served ?served .
  ?cocktail dbp:sourcelink ?sourcelink .
  ?cocktail dbp:prep ?prep .
  ?cocktail dct:subject ?subject .

  # Liens wiki sortants du cocktail (2e bloc dbo:wikiPageWikiLink sur ton dessin)
  ?cocktail dbo:wikiPageWikiLink ?outLink .
}
WHERE {
  # 1) Récupère les cocktails depuis la page-liste
  dbr:List_of_IBA_official_cocktails dbo:wikiPageWikiLink ?cocktail .

  # Évite les liens parasites
  FILTER(STRSTARTS(STR(?cocktail), "http://dbpedia.org/resource/"))
  FILTER(!CONTAINS(STR(?cocktail), "File:"))
  FILTER(!CONTAINS(STR(?cocktail), "Category:"))

  # 1bis) GARDE UNIQUEMENT ceux qui ont dbp:iba = "yes" (casse/typage tolérés)
  ?cocktail dbp:iba ?iba .
  FILTER(
    LCASE(STR(?iba)) = "yes" ||
    STR(?iba) = "1" || STR(?iba) = "true"
  )

  # 2) rdfs:label (souvent multi-langues)
  OPTIONAL {
    ?cocktail rdfs:label ?label .
    FILTER(lang(?label) = "en" || lang(?label) = "fr")
  }

  # 3) dbo:description (souvent multi-langues)
  OPTIONAL {
    ?cocktail dbo:description ?desc .
    FILTER(lang(?desc) = "en" || lang(?desc) = "fr")
  }

  # 4) Image
  OPTIONAL { ?cocktail foaf:depiction ?img . }

  # 5) Infobox properties (dbp:*)
  OPTIONAL { ?cocktail dbp:garnish ?garnish . }
  OPTIONAL { ?cocktail dbp:ingredients ?ingredients . }
  OPTIONAL { ?cocktail dbp:name ?name . }
  OPTIONAL { ?cocktail dbp:served ?served . }
  OPTIONAL { ?cocktail dbp:sourcelink ?sourcelink . }
  OPTIONAL { ?cocktail dbp:prep ?prep . }

  # 6) Catégories
  OPTIONAL { ?cocktail dct:subject ?subject . }

  # 7) Liens wiki sortants
  OPTIONAL {
    ?cocktail dbo:wikiPageWikiLink ?outLink .
    FILTER(!CONTAINS(STR(?outLink), "File:"))
    FILTER(!CONTAINS(STR(?outLink), "Category:"))
  }
}
"""

endpoint = "https://dbpedia.org/sparql"

session = requests.Session()

headers = {
    "Accept": "text/turtle",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MarmiTonic/1.0"
}

print("Querying DBpedia SPARQL endpoint...")
print("This can take a moment (but won't ahah)...")

try:
    r = session.get(
        endpoint,
        params={"query": query, "format": "text/turtle", "timeout": "120000"},
        headers=headers,
        timeout=120,
    )
    r.raise_for_status()

    with open("iba_export.ttl", "wb") as f:
        f.write(r.content)

    print(f"✓ Success! Saved {len(r.content)} bytes to iba_export.ttl")
    sys.exit(0)

except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")
    sys.exit(1)
