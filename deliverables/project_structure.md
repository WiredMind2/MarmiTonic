# Project Structure 📂

This document outlines the file organization for the **MarmiTonic** repository.

## Root Directory

| File/Folder | Description |
|-------------|-------------|
| `backend/` | Source code for the FastAPI server and semantic services. |
| `frontend/` | Source code for the web interface (HTML/CSS/JS). |
| `deliverables/` | Documentation, specifications, and architecture diagrams. |
| `README.md` | Project overview and setup instructions. |
| `pytest.ini` | Configuration for the Pytest testing framework. |

## Backend Structure (`backend/`)

| File/Folder | Description |
|-------------|-------------|
| `main.py` | Application entry point. Configures API routes and middleware. |
| `models/` | Pydantic models for data validation and schema definition. |
| `routes/` | API route handlers (Controllers) segregated by feature. |
| `services/` | Business logic layer (Cocktails, Planner, Graph, SPARQL). |
| `utils/` | Helper functions and graph loading utilities. |
| `data/` | Data storage (Turtle files, JSON caches). |
| `tests/` | Unit and integration tests. |

## Frontend Structure (`frontend/`)

| File/Folder | Description |
|-------------|-------------|
| `index.html` | Entry point for the Single Page Application. |
| `assets/` | Static images and icons. |
| `css/` | Stylesheet files. |
| `js/` | JavaScript modules for UI logic and API interaction. |
| `pages/` | HTML fragments or templates for different application views. |

## Deliverables (`deliverables/`)

| File | Description |
|------|-------------|
| `ARCHITECTURE.md` | High-level system design and component interaction. |
| `SPECIFICATIONS.md` | Detailed functional and non-functional requirements. |
| `SPARQL-QUERIES.md` | Documentation of SPARQL queries used in the project. |
| `PROJECT_STRUCTURE.md` | This file. |
