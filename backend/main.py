# backend/main.py
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse # Added JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from typing import List
from importlib import import_module
import logging # For logging
import traceback # For logging stack trace

from routes.rules import router as rules_router
from routes.webhooks import router as webhook_router
from routes.integrations import router as integrations_router

from db import async_session, init_db
from models.rule import Rule

app = FastAPI()

# Define allowed origins in a list for consistency
ALLOWED_ORIGINS = [
    "https://supportops-frontend-production.up.railway.app",
    "http://localhost:5173",
]

# Global Exception Handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log the exception with a traceback
    logging.error(f"Unhandled exception for request {request.method} {request.url}: {exc}")
    logging.error(traceback.format_exc())

    response_content = {"detail": "Internal Server Error"}
    status_code = 500

    if isinstance(exc, HTTPException):
        # If it's an HTTPException, use its status code and detail
        status_code = exc.status_code
        response_content = {"detail": exc.detail}

    response = JSONResponse(
        status_code=status_code,
        content=response_content,
    )

    origin = request.headers.get("origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # These should ideally match the CORSMiddleware configuration for consistency
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        # If your CORSMiddleware exposes specific headers, add them here too
        # response.headers["Access-Control-Expose-Headers"] = "X-Custom-Header"

    return response

# Configure CORS Middleware
# This is still crucial for preflight requests and non-error responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, # Use the defined list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log incoming request origins for CORS debugging (keep this as it's useful)
@app.middleware("http")
async def log_origin(request: Request, call_next): # Added type hint for request
    origin = request.headers.get("origin")
    logging.info(f"Request from origin: {origin} for {request.method} {request.url}") # Changed to logging.info
    response = await call_next(request)
    return response

# Include routers
app.include_router(rules_router, prefix="/rules", tags=["rules"])
app.include_router(webhook_router, tags=["webhooks"])
app.include_router(integrations_router, tags=["integrations"])

@app.on_event("startup")
async def on_startup():
    await init_db()

async def get_session():
    async with async_session() as session:
        yield session

@app.get("/")
def read_root():
    return {"message": "SupportOps Automator backend is running"}

# GET /rules and POST /rules are now in routes/rules.py, so remove from here if they were duplicated
# The original main.py already had them removed from here, which is good.

# Base interfaces for trigger and action modules (keep as is)
def load_trigger_module(name: str):
    if name == "zendesk":
        from modules.zendesk.trigger import handle_trigger
        return handle_trigger
    elif name == "freshdesk":
        from modules.freshdesk.trigger import handle_trigger
        return handle_trigger
    raise ValueError(f"Unknown trigger module: {name}")

def load_action_module(name: str):
    if name == "slack":
        from modules.slack.action import execute_action
        return execute_action
    if name == "trello":
        from modules.trello.action import execute_action
        return execute_action
    raise ValueError(f"Unknown action module: {name}")

# This function is now in services/rule_engine.py (keep as is)
# Keeping this here for backward compatibility
async def process_rule(rule: Rule):
    from services.rule_engine import process_rule as engine_process_rule
    await engine_process_rule(rule)

# Optional: Local-only test entry point (keep as is)
if __name__ == "__main__":
    # ... (no changes to this part)
    pass # Placeholder if the original main had content here
