from fastapi import APIRouter, Request, Depends
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db import async_session
from models.rule import Rule
from services import rule_engine
import json

router = APIRouter()

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/trigger/zendesk")
async def zendesk_trigger(request: Request, session: AsyncSession = Depends(get_session)):
    payload = await request.json()
    print("[Webhook] Received Zendesk payload:", payload)
    
    # Process the webhook using the Zendesk module
    from modules.zendesk.trigger import handle_trigger
    trigger_result = handle_trigger(payload)
    
    # If the trigger was successful, find and execute matching rules
    if trigger_result.get("status") == "success":
        # Find rules that match this trigger
        result = await session.execute(select(Rule).where(
            Rule.trigger_platform == "zendesk"
        ))
        rules = result.scalars().all()
        
        executed_rules = 0
        for rule in rules:
            try:
                # Check if the rule matches the event
                rule_data = json.loads(rule.trigger_data)
                trigger_event = rule.trigger_event
                
                # Handle different types of triggers
                if trigger_event == "ticket_created":
                    # Execute rule for new tickets
                    print(f"[Webhook] Trigger match: rule {rule.id}, new ticket created")
                    await rule_engine.process_rule(rule, session)
                    executed_rules += 1
                    
                elif trigger_event == "ticket_status_changed":
                    # Check if status matches the expected status in the rule
                    ticket_status = payload.get("ticket", {}).get("status")
                    expected_status = rule_data.get("status")
                    if expected_status and ticket_status and expected_status.lower() == ticket_status.lower():
                        print(f"[Webhook] Trigger match: rule {rule.id}, status changed to '{ticket_status}'")
                        await rule_engine.process_rule(rule, session)
                        executed_rules += 1
                        
                elif trigger_event == "ticket_tag_added":
                    # Check if any tags match
                    tags = payload.get("ticket", {}).get("tags", [])
                    expected_tag = rule_data.get("tag")
                    if expected_tag and tags and expected_tag in tags:
                        print(f"[Webhook] Trigger match: rule {rule.id}, tag '{expected_tag}'")
                        await rule_engine.process_rule(rule, session)
                        executed_rules += 1
                        
            except Exception as e:
                print(f"[Webhook] Failed to evaluate rule {rule.id}:", e)
                import traceback
                traceback.print_exc()
        
        return {
            "status": "processed",
            "rules_executed": executed_rules
        }
    else:
        # Return the error from the trigger handler
        return {
            "status": "error",
            "message": trigger_result.get("message", "Unknown error processing webhook")
        }

@router.post("/trigger/freshdesk")
async def freshdesk_trigger(request: Request, session: AsyncSession = Depends(get_session)):
    payload = await request.json()
    print("[Webhook] Received Freshdesk payload:", payload)
    
    # Process the webhook using the Freshdesk module
    from modules.freshdesk.trigger import handle_trigger
    trigger_result = handle_trigger(payload)
    
    # If the trigger was successful, find and execute matching rules
    if trigger_result.get("status") == "success":
        # Get ticket data from the trigger result
        ticket_data = trigger_result.get("data", {})
        ticket_id = ticket_data.get("ticket_id")
        ticket_status = ticket_data.get("ticket_status")
        
        # Find rules that match this trigger
        result = await session.execute(select(Rule).where(
            Rule.trigger_platform == "freshdesk"
        ))
        rules = result.scalars().all()
        
        executed_rules = 0
        for rule in rules:
            try:
                # Check if the rule matches the event
                rule_data = json.loads(rule.trigger_data)
                trigger_event = rule.trigger_event
                
                # Handle different types of triggers
                if trigger_event == "ticket_created" and "ticket_id" in ticket_data:
                    # Execute rule for new tickets
                    print(f"[Webhook] Trigger match: rule {rule.id}, new ticket created")
                    await rule_engine.process_rule(rule, session)
                    executed_rules += 1
                    
                elif trigger_event == "ticket_status_changed" and ticket_status:
                    # Check if status matches the expected status in the rule
                    expected_status = rule_data.get("status")
                    if expected_status and expected_status.lower() == ticket_status.lower():
                        print(f"[Webhook] Trigger match: rule {rule.id}, status changed to '{ticket_status}'")
                        await rule_engine.process_rule(rule, session)
                        executed_rules += 1
                        
                elif trigger_event == "ticket_tag_added":
                    # Check if any tags match
                    tags = payload.get("freshdesk_webhook", {}).get("tags", [])
                    expected_tag = rule_data.get("tag")
                    if expected_tag and tags and expected_tag in tags:
                        print(f"[Webhook] Trigger match: rule {rule.id}, tag '{expected_tag}'")
                        await rule_engine.process_rule(rule, session)
                        executed_rules += 1
                        
            except Exception as e:
                print(f"[Webhook] Failed to evaluate rule {rule.id}:", e)
                import traceback
                traceback.print_exc()
        
        return {
            "status": "processed",
            "rules_executed": executed_rules,
            "ticket_id": ticket_id
        }
    else:
        # Return the error from the trigger handler
        return {
            "status": "error",
            "message": trigger_result.get("message", "Unknown error processing webhook")
        }
