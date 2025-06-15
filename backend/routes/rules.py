from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db import async_session
from models.rule import Rule
from typing import List

router = APIRouter()

@router.options("/rules", status_code=200)
async def options_rules(response: Response):
    return add_cors_headers(Response(status_code=200))

# Helper function to add CORS headers to responses
def add_cors_headers(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

async def get_session():
    async with async_session() as session:
        yield session

@router.get("/rules", response_model=List[Rule])
async def get_rules(response: Response, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Rule))
    rules = result.scalars().all()
    return add_cors_headers(JSONResponse(content=[rule.dict() for rule in rules]))

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
async def create_rule(rule: RuleCreate, response: Response, session: AsyncSession = Depends(get_session)):
    # Serialize actions to JSON string for DB
    db_rule = Rule(
        user_id=rule.user_id,
        trigger_platform=rule.trigger_platform,
        trigger_event=rule.trigger_event,
        trigger_data=rule.trigger_data,
        actions=json.dumps(rule.actions),
        name=rule.name,
        description=rule.description
    )
    session.add(db_rule)
    await session.commit()
    await session.refresh(db_rule)
    return add_cors_headers(JSONResponse(content=db_rule.dict()))
