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

@router.post("/rules", response_model=Rule)
async def create_rule(rule: Rule, response: Response, session: AsyncSession = Depends(get_session)):
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return add_cors_headers(JSONResponse(content=rule.dict()))
