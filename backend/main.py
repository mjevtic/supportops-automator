from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from typing import List
from importlib import import_module
from routes.rules import router as rules_router
from routes.webhooks import router as webhook_router
from routes.integrations import router as integrations_router

from db import async_session, init_db
from models.rule import Rule

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://supportops-frontend-production.up.railway.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log incoming request origins for CORS debugging
@app.middleware("http")
async def log_origin(request, call_next):
    origin = request.headers.get("origin")
    print(f"Request from origin: {origin}")
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

@app.get("/rules", response_model=List[Rule])
async def get_rules(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Rule))
    return result.scalars().all()

@app.post("/rules", response_model=Rule)
async def create_rule(rule: Rule, session: AsyncSession = Depends(get_session)):
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule

# Base interfaces for trigger and action modules
def load_trigger_module(name: str):
    if name == "zendesk":
        from modules.zendesk.trigger import handle_trigger
        return handle_trigger
    elif name == "freshdesk":
        from modules.freshdesk.trigger import handle_trigger
        return handle_trigger
    # Add more trigger modules here as needed
    raise ValueError(f"Unknown trigger module: {name}")

def load_action_module(name: str):
    if name == "slack":
        from modules.slack.action import execute_action
        return execute_action
    if name == "trello":
        from modules.trello.action import execute_action
        return execute_action
    # Add more action modules here as needed
    raise ValueError(f"Unknown action module: {name}")

import json

# This function is now in services/rule_engine.py
# Keeping this here for backward compatibility
async def process_rule(rule: Rule):
    from services.rule_engine import process_rule as engine_process_rule
    await engine_process_rule(rule)

# Optional: Local-only test entry point
if __name__ == "__main__":
    rule = Rule(
        id=1,
        user_id=1,
        trigger_platform="zendesk",
        trigger_event="ticket_tag_added",
        trigger_data='{"tag": "urgent"}',
        actions='[{"platform": "trello", "type": "create_card", "name": "New urgent ticket", "desc": "Ticket #123 from customer with high priority"}]'
    )

    import asyncio
    asyncio.run(process_rule(rule))


