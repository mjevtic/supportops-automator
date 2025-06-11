from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from typing import List

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
