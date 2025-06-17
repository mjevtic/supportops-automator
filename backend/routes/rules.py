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
    import logging # Ensure logging is imported
    # Ensure json is imported if it's used and not at top-level of file already (it is in this file)
    logging.warning(f"--- Updating rule ID: {rule_id} ---")
    logging.warning(f"Received rule_update payload (exclude_unset=False to see all fields from model): {rule_update.dict(exclude_unset=False)}")
    logging.warning(f"Received rule_update payload (exclude_none=True to see only provided non-null fields): {rule_update.dict(exclude_none=True)}")
    db_rule = await session.get(Rule, rule_id)
    if not db_rule:
        logging.error(f"Rule {rule_id} not found for update.")
        return JSONResponse(status_code=404, content={"message": "Rule not found"})
    
    logging.warning(f"DB rule.actions BEFORE any update: {db_rule.actions}")
    logging.warning(f"DB rule full object BEFORE any update: {db_rule.dict()}")

    update_data = rule_update.dict(exclude_unset=True)
    logging.warning(f"Update_data (from rule_update.dict(exclude_unset=True)): {update_data}")
    
    if 'actions' in update_data:
        logging.warning(f"'actions' field IS PRESENT in update_data. Value: {update_data['actions']}, Type: {type(update_data['actions'])}")
        if update_data['actions'] is not None:
            # This is where the list of actions should be converted to a JSON string
            actions_as_json_string = json.dumps(update_data['actions'])
            update_data['actions'] = actions_as_json_string # Modify update_data to hold the string for the loop below
            logging.warning(f"Converted 'actions' to JSON string for storage: {actions_as_json_string}")
        else:
            # If 'actions' was explicitly passed as null in the payload
            logging.warning(f"'actions' field in update_data is None. It will be set as null/None on db_rule if 'actions' key is iterated.")
            # SQLModel/SQLAlchemy might store this as Python None, which becomes SQL NULL.
            # For a string field, storing '[]' for empty or 'null' string might be preferable.
            # Let's ensure it's a string if the db field is string.
            update_data['actions'] = "[]" # Default to empty JSON array string if payload sends null for actions
            logging.warning(f"'actions' was None in payload, will store as '[]'.")
    else:
        logging.warning(f"'actions' field IS NOT PRESENT in update_data (was not in PUT request or was default). db_rule.actions will not be changed by this update.")

    # Apply all changes from update_data to db_rule
    for key, value in update_data.items():
        if hasattr(db_rule, key):
            setattr(db_rule, key, value)
            logging.warning(f"Set db_rule.{key} = {repr(value)}")
        else:
            logging.warning(f"Attempted to set unknown attribute {key} on db_rule.")
    
    logging.warning(f"DB rule.actions JUST BEFORE commit: {db_rule.actions}")
    logging.warning(f"Full db_rule object JUST BEFORE commit: {db_rule.dict()}")
    
    session.add(db_rule)
    await session.commit()
    await session.refresh(db_rule)

    logging.warning(f"DB rule.actions AFTER commit and refresh: {db_rule.actions}")
    logging.warning(f"Full db_rule object AFTER commit and refresh: {db_rule.dict()}")
    logging.warning(f"--- Finished updating rule ID: {rule_id} ---")
    return db_rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, session: AsyncSession = Depends(get_session)):
    rule = await session.get(Rule, rule_id)
    if not rule:
        return JSONResponse(status_code=404, content={"message": "Rule not found"})
    
    await session.delete(rule)
    await session.commit()
    return Response(status_code=204)
