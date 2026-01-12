import sys
sys.path.insert(0, '/mnt/c/Louistravail/4IF/WS/projet/MarmiTonic')

from backend.services.sparql_service import SparqlService

service = SparqlService()

if service.local_graph:
    output_file = "graph_content.txt"
    
    print(f"Exportation du graphe dans {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("CONTENU DU GRAPHE RDF LOCAL\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Nombre total de triplets: {len(service.local_graph)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("FORMAT TURTLE\n")
        f.write("=" * 80 + "\n\n")
        
        # Sérialiser le graphe en format Turtle (lisible)
        turtle_content = service.local_graph.serialize(format='turtle')
        f.write(turtle_content)
        
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("LISTE DES SUJETS (RESSOURCES)\n")
        f.write("=" * 80 + "\n\n")
        
        # Lister tous les sujets uniques
        subjects = set(service.local_graph.subjects())
        f.write(f"Nombre de sujets: {len(subjects)}\n\n")
        for i, subject in enumerate(sorted(subjects, key=str)[:50], 1):
            f.write(f"{i}. {subject}\n")
        
        if len(subjects) > 50:
            f.write(f"\n... et {len(subjects) - 50} autres sujets\n")
        
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("LISTE DES PRÉDICATS (PROPRIÉTÉS)\n")
        f.write("=" * 80 + "\n\n")
        
        # Lister tous les prédicats uniques
        predicates = set(service.local_graph.predicates())
        f.write(f"Nombre de prédicats: {len(predicates)}\n\n")
        for i, predicate in enumerate(sorted(predicates, key=str), 1):
            f.write(f"{i}. {predicate}\n")
    
    print(f"✓ Graphe exporté avec succès dans {output_file}")
    print(f"  - Nombre de triplets: {len(service.local_graph)}")
    print(f"  - Nombre de sujets: {len(set(service.local_graph.subjects()))}")
    print(f"  - Nombre de prédicats: {len(set(service.local_graph.predicates()))}")
else:
    print("✗ Aucun graphe chargé")
