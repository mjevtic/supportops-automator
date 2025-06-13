from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    """
    Configure CORS for the application
    """
    origins = [
        "*",  # For development
        "http://localhost:5173",
        "http://localhost:3000",
        "https://supportops-frontend-production.up.railway.app",
    ]
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    return app
