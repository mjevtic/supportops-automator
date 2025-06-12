from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from typing import List
from importlib import import_module

from db import async_session, init_db
from models import Rule

app = FastAPI()

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
    # Add more trigger modules here as needed
    raise ValueError(f"Unknown trigger module: {name}")

def load_action_module(name: str):
    if name == "slack":
        from modules.slack.action import execute_action
        return execute_action
    # Add more action modules here as needed
    raise ValueError(f"Unknown action module: {name}")

import json

async def process_rule(rule: Rule):
    try:
        actions = json.loads(rule.actions)
        for action in actions:
            platform = action.get("platform")
            if not platform:
                continue
            action_fn = load_action_module(platform)
            result = action_fn(action)
            print(f"[INFO] Action executed for platform '{platform}':", result)
    except Exception as e:
        print("[ERROR] Failed to process rule:", e)

# Optional: Local-only test entry point
if __name__ == "__main__":
    rule = Rule(
        id=1,
        user_id=1,
        trigger_platform="zendesk",
        trigger_event="ticket_tag_added",
        trigger_data='{"tag": "urgent"}',
        actions='[{"platform": "slack", "type": "send_message", "channel": "#support", "message": "Test ticket"}]'
    )

    import asyncio
    asyncio.run(process_rule(rule))


