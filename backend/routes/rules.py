from fastapi import APIRouter, Depends
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
    return result.scalars().all()

@router.post("/rules", response_model=Rule)
async def create_rule(rule: Rule, session: AsyncSession = Depends(get_session)):
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule
