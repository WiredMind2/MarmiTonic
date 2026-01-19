import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles




def mount_frontend(app: FastAPI):
    """
    Mounts the frontend static files to the FastAPI app.
    This replaces the standalone HTTP server approach.
    """
    # Calculate the path to the frontend directory
    # utils -> backend -> root -> frontend
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')
    frontend_dir = os.path.normpath(frontend_dir)

    if not os.path.isdir(frontend_dir):
        print(f"Warning: Frontend directory not found at: {frontend_dir}")
        return

    print(f"Mounting frontend from: {frontend_dir}")
    
    # Mount the frontend directory at the root path "/"
    # html=True allows serving index.html automatically
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


