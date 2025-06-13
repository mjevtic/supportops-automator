from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CORSHeaderMiddleware(BaseHTTPMiddleware):
    """
    Simple middleware that adds CORS headers to every response
    """
    
    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to every response
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response

def add_cors_headers(app: FastAPI):
    """
    Add CORS headers middleware to the application
    """
    app.add_middleware(CORSHeaderMiddleware)
    return app
