from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db import async_session
from models.rule import Rule
from typing import List

router = APIRouter()


async def get_session():
    async with async_session() as session:
        yield session

@router.get("/rules", response_model=List[Rule])
async def get_rules(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Rule))
    rules = result.scalars().all()
    return [rule for rule in rules]

import json
from pydantic import BaseModel

class RuleCreate(BaseModel):
    user_id: int
    trigger_platform: str
    trigger_event: str
    trigger_data: str
    actions: list
    name: str = "New Rule"
    description: str = ""

@router.post("/rules", response_model=Rule)
async def create_rule(rule: RuleCreate, session: AsyncSession = Depends(get_session)):
    import logging, json
    logging.warning(f"Incoming rule payload: {rule}")
    actions_val = rule.actions if hasattr(rule, 'actions') else []
    if not actions_val:
        actions_str = "[]"
    elif isinstance(actions_val, str):
        actions_str = actions_val
    else:
        actions_str = json.dumps(actions_val)
    db_rule = Rule(
        user_id=rule.user_id,
        trigger_platform=rule.trigger_platform,
        trigger_event=rule.trigger_event,
        trigger_data=rule.trigger_data,
        actions=actions_str,
        name=rule.name,
        description=rule.description
    )
    session.add(db_rule)
    await session.commit()
    await session.refresh(db_rule)
    logging.warning(f"Saved rule to DB: {db_rule}")
    return db_rule
