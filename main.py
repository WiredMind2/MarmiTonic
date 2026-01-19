import uvicorn
from backend.main import app

if __name__ == "__main__":
    # Run the application using uvicorn
    # The string "backend.main:app" allows for reloading to work correctly
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
