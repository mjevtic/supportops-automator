from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db import async_session
from models.rule import Rule
from typing import List, Optional

router = APIRouter()


async def get_session():
    async with async_session() as session:
        yield session

@router.get("/", response_model=List[Rule])  # Changed from "/rules" to "/"
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

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_platform: Optional[str] = None
    trigger_event: Optional[str] = None
    trigger_data: Optional[str] = None
    actions: Optional[list] = None

@router.post("/", response_model=Rule)  # Changed from "/rules" to "/"
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
        name=rule.name,
        description=rule.description,
        trigger_platform=rule.trigger_platform,
        trigger_event=rule.trigger_event,
        trigger_data=rule.trigger_data,
        actions=actions_str
    )
    session.add(db_rule)
    await session.commit()
    await session.refresh(db_rule)
    logging.warning(f"Saved rule to DB: {db_rule}")
    return db_rule

@router.get("/{rule_id}", response_model=Rule)
async def get_rule(rule_id: int, session: AsyncSession = Depends(get_session)):
    rule = await session.get(Rule, rule_id)
    if not rule:
        return JSONResponse(status_code=404, content={"message": "Rule not found"})
    return rule

@router.put("/{rule_id}", response_model=Rule)
async def update_rule(rule_id: int, rule_update: RuleUpdate, session: AsyncSession = Depends(get_session)):
    db_rule = await session.get(Rule, rule_id)
    if not db_rule:
        return JSONResponse(status_code=404, content={"message": "Rule not found"})
    
    update_data = rule_update.dict(exclude_unset=True)
    
    if 'actions' in update_data and update_data['actions'] is not None:
        update_data['actions'] = json.dumps(update_data['actions'])

    for key, value in update_data.items():
        setattr(db_rule, key, value)
    
    session.add(db_rule)
    await session.commit()
    await session.refresh(db_rule)
    return db_rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, session: AsyncSession = Depends(get_session)):
    rule = await session.get(Rule, rule_id)
    if not rule:
        return JSONResponse(status_code=404, content={"message": "Rule not found"})
    
    await session.delete(rule)
    await session.commit()
    return Response(status_code=204)
