from fastapi import APIRouter, Request, Depends
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db import async_session
from models.rule import Rule
from services.rule_engine import process_rule
import json

router = APIRouter()

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/trigger/zendesk")
async def zendesk_trigger(request: Request, session: AsyncSession = Depends(get_session)):
    payload = await request.json()
    print("[Webhook] Received Zendesk payload:", payload)

    tags = payload.get("ticket", {}).get("tags", [])
    if not tags:
        return {"status": "ignored", "reason": "No tags in payload"}

    result = await session.execute(select(Rule).where(
        Rule.trigger_platform == "zendesk",
        Rule.trigger_event == "ticket_tag_added"
    ))
    rules = result.scalars().all()

    for rule in rules:
        try:
            rule_data = json.loads(rule.trigger_data)
            expected_tag = rule_data.get("tag")
            if expected_tag in tags:
                print(f"[Webhook] Trigger match: rule {rule.id}, tag '{expected_tag}'")
                await process_rule(rule)
        except Exception as e:
            print(f"[Webhook] Failed to evaluate rule {rule.id}:", e)

    return {"status": "processed"}
