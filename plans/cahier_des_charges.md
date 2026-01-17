# Cahier des Charges - MarmiTonic

## 1. Introduction

### 1.1 Contexte du Projet
Le projet MarmiTonic est une application web sémantique développée dans le cadre du cours "Web Sémantique" (4-IF-WS) à l'INSA Lyon. L'objectif est de créer une plateforme intelligente capable de naviguer dans le Web de données (Linked Data), d'extraire des structures complexes et d'utiliser l'IA générative pour offrir une expérience utilisateur augmentée.

### 1.2 Domaine d'Application
L'application se concentre sur le domaine des cocktails, permettant aux utilisateurs de découvrir des recettes basées sur leurs ingrédients disponibles, d'optimiser leur bar et d'explorer des recommandations personnalisées.

### 1.3 Équipe
Elise Bachet
Andy Gonzales
Lou Reina--Kuntziger
William Michaud
Louis Labory
Jason Laval

## 2. Objectifs

### 2.1 Objectif Général
Développer une application web qui dépasse la recherche textuelle simple pour proposer une exploration relationnelle et sémantique des cocktails, en exploitant les technologies du Web Sémantique et de l'analyse de données.

### 2.2 Objectifs Spécifiques
- Interroger des sources de données liées (DBpedia) via SPARQL
- Construire et analyser des graphes de connaissances cocktail-ingrédient
- Offrir une interface utilisateur intuitive pour la gestion du bar personnel
- Implémenter des algorithmes d'optimisation pour la planification du bar
- Fournir des recommandations de découverte similaires à Spotify
- Intégrer optionnellement des fonctionnalités d'IA générative

## 3. Exigences Fonctionnelles

### 3.1 Fonctionnalités Principales

#### 3.1.1 Mon Bar (Inventaire)
- L'utilisateur peut cocher/rechercher les ingrédients qu'il possède
- L'application retourne :
  - Cocktails faisables immédiatement (0 ingrédient manquant)
  - Cocktails presque faisables (1 ou 2 ingrédients manquants)
- Bouton "ajouter au panier" pour les ingrédients manquants
- Exploitation : Graphe cocktail-ingrédient + requêtes SPARQL

#### 3.1.2 Bar Minimum (Optimisation)
- Mode "Playlist" : Pour une liste de cocktails souhaités, minimiser les ingrédients nécessaires
Sortie : Liste optimisée + nombre de cocktails couverts + presque couverts

#### 3.1.3 Découverte (Type Spotify)
Sur la fiche d'un cocktail :
- "Similaires" (même style/ingrédients) avec score
- "Dans la même vibe" (cluster)
- "Pont vers d'autres styles" (cocktails connectant des familles)

#### 3.1.4 SPARQL Explorer
- Interface pour exécuter des requêtes SPARQL personnalisées
- Affichage des résultats de requêtes

### 3.2 Fonctionnalités Bonus

#### 3.2.1 Substitutions Intelligentes
- Suggestion d'alternatives plausibles pour ingrédients manquants
- Méthode : Similarité par co-occurrence d'ingrédients + catégories

#### 3.2.2 Filtres Réels
- Filtres par restrictions alimentaires : sans œuf, sans lait/crème, sans sucre ajouté
- Filtres par saveurs : citrus, mint, coffee, bitter
- Implémentation via tags dérivés

#### 3.2.3 Shopping List Consolidée
- Sélection de cocktails → liste d'ingrédients uniques
- Mise en évidence des ingrédients "rentables" (débloquant le plus de cocktails)

### 3.3 Fonctionnalités Techniques

#### 3.3.1 Analyse de Données
- Génération et visualisation de graphes (réseau cocktail-ingrédient)
- Calcul de métriques : centralité, communautés, modularité
- Export vers Gephi
- Algorithmes d'optimisation (set cover greedy pour Bar Minimum)

#### 3.3.2 IA Générative (Optionnel)
- NL→SPARQL : Traduction de questions naturelles en requêtes SPARQL
- Synthèse de connaissances : Résumé des résultats SPARQL
- Analyse de graphe assistée : Interprétation textuelle des statistiques
- GraphRAG : Enrichissement des recommandations via graphe de connaissance

## 4. Exigences Non-Fonctionnelles

### 4.1 Performance
- Temps de réponse < 2 secondes pour les requêtes simples
- Temps de réponse < 5 secondes pour les analyses complexes
- Capacité à traiter au moins 1000 cocktails et 500 ingrédients

### 4.2 Sécurité
- Validation des entrées utilisateur
- Protection contre les injections SPARQL
- Gestion sécurisée des clés API (si utilisées)

### 4.3 Utilisabilité
- Interface simple et efficace
- Navigation intuitive entre les onglets
- Responsive design pour mobile et desktop

### 4.4 Maintenabilité
- Code modulaire et bien documenté
- Tests unitaires et d'intégration
- Architecture respectant les principes SOLID

### 4.5 Compatibilité
- Navigateurs modernes : Chrome, Firefox, Safari, Edge
- Serveur : Compatible avec Python 3.8+

## 5. Spécifications Techniques

### 5.1 Technologies
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla, sans framework)
- **Backend** : Python avec FastAPI
- **Base de données** : Données extraites de DBpedia via SPARQL
- **Analyse de données** : NetworkX, Matplotlib pour graphes
- **Visualisation** : D3.js ou équivalent pour frontend
- **IA** : APIs OpenAI/Anthropic/Mistral ou Ollama local (optionnel)

### 5.2 Architecture
- Architecture client-serveur
- API RESTful avec FastAPI
- Séparation claire : Modèles, Routes, Services, Utilitaires
- Intégration SPARQL via client DBpedia

### 5.3 Sources de Données
- **Primaire** : DBpedia (endpoint SPARQL officiel)
- **Secondaire** : HAL archives-ouvertes (si pertinent)
- **Local** : Cache optionnel pour performances

## 6. Interface Utilisateur

### 6.1 Structure Générale
4 onglets principaux :
1. **Discover** : Recherche cocktail/ingrédient, tendances (centraux, familles, random)
2. **My Bar** : Liste d'ingrédients avec recherche, résultats faisables/presque faisables
3. **Planner** : Bar minimum (slider N), playlist → ingrédients minimaux, export shopping list
4. **Insights** : Stats graphe (top ingrédients, communautés), export Gephi
5. **SPARQL Explorer** : Interface de requête SPARQL

### 6.2 Maquettes
- Design simple et efficace
- Navigation cohérente
- Éléments interactifs : checkboxes, sliders, boutons

## 7. Livrables

### 7.1 Code Source
- Archive contenant le code source complet
- Instructions d'installation et d'utilisation
- Tests et documentation

### 7.2 Rapport de Synthèse
- Architecture et choix techniques
- Difficultés rencontrées (alignement d'ontologies, limites LLM)
- Analyses réalisées (visualisations, métriques, interprétations)

### 7.3 Présentation
- Démonstration live de l'outil
- Présentation de la démarche scientifique

## 8. Contraintes et Risques

### 8.1 Contraintes
- Utilisation obligatoire de SPARQL et Linked Data
- Analyse de données obligatoire
- IA générative optionnelle
- Délai : Fin du semestre

### 8.2 Risques
- Disponibilité et qualité des données DBpedia
- Complexité des requêtes SPARQL
- Performance des analyses de graphes
- Intégration de l'IA (clés API non fournies)

### 8.3 Mesures d'Atténuation
- Validation précoce des requêtes SPARQL
- Prototypage rapide des fonctionnalités clés
- Plan B pour l'IA (utilisation d'Ollama local si disponible)

## 9. Critères d'Acceptation
- Toutes les fonctionnalités principales implémentées et testées
- Code de qualité (tests, documentation, bonnes pratiques)
- Respect des exigences sémantiques et d'analyse de données
- Interface utilisateur fonctionnelle et intuitive
- Rapport complet et présentation réussie

## 10. Glossaire
- **SPARQL** : Langage de requête pour RDF
- **Linked Data** : Données interconnectées sur le Web
- **DBpedia** : Base de connaissances extraite de Wikipedia
- **Graphe de connaissances** : Représentation des relations entre entités
- **NL→SPARQL** : Traduction du langage naturel vers SPARQL
- **GraphRAG** : Retrieval-Augmented Generation utilisant un graphe