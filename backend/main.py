from fastapi import FastAPI
from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from db import async_session, init_db
from models import Rule

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def read_root():
    return {"message": "SupportOps Automator backend is running"}
