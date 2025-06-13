import json
import importlib
from typing import Dict, Any, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from models.rule import Rule
from repositories.integration_repository import IntegrationRepository

# Define our own module loader to avoid circular imports
def load_action_module(name: str):
    if name == "slack":
        from modules.slack.action import execute_action
        return execute_action
    if name == "trello":
        from modules.trello.action import execute_action
        return execute_action
    if name == "google_sheets":
        from modules.google_sheets.action import execute_action
        return execute_action
    if name == "notion":
        from modules.notion.action import execute_action
        return execute_action
    if name == "linear":
        from modules.linear.action import execute_action
        return execute_action
    if name == "discord":
        from modules.discord.action import execute_action
        return execute_action
    # Add more action modules here as needed
    raise ValueError(f"Unknown action module: {name}")

async def execute_integration_action(
    platform: str, 
    action_type: str, 
    action_data: Dict[str, Any],
    integration_id: int,
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Execute an action using an integration
    
    Args:
        platform: Integration platform (zendesk, freshdesk, etc.)
        action_type: Type of action (create_ticket, update_ticket, etc.)
        action_data: Data for the action
        integration_id: ID of the integration to use
        session: Database session
    
    Returns:
        Dict with action result
    """
    try:
        # Get integration from database
        repository = IntegrationRepository(session)
        integration = await repository.get_integration(integration_id)
        
        if not integration:
            return {
                "success": False,
                "message": f"Integration with ID {integration_id} not found"
            }
        
        # Get decrypted config
        config = repository.get_decrypted_config(integration)
        
        # Execute action based on platform and action_type
        if platform == "zendesk":
            from modules.zendesk.actions import create_ticket, update_ticket, add_comment
            
            if action_type == "create_ticket":
                return create_ticket(config, action_data)
            elif action_type == "update_ticket":
                ticket_id = action_data.pop("ticket_id", None)
                if not ticket_id:
                    return {
                        "success": False,
                        "message": "Missing ticket_id for update_ticket action"
                    }
                return update_ticket(config, ticket_id, action_data)
            elif action_type == "add_comment":
                ticket_id = action_data.pop("ticket_id", None)
                comment = action_data.pop("comment", "")
                public = action_data.pop("public", True)
                if not ticket_id:
                    return {
                        "success": False,
                        "message": "Missing ticket_id for add_comment action"
                    }
                return add_comment(config, ticket_id, comment, public)
            else:
                return {
                    "success": False,
                    "message": f"Unsupported action type for Zendesk: {action_type}"
                }
                
        elif platform == "freshdesk":
            from modules.freshdesk.actions import create_ticket, update_ticket, add_note
            
            if action_type == "create_ticket":
                return create_ticket(config, action_data)
            elif action_type == "update_ticket":
                ticket_id = action_data.pop("ticket_id", None)
                if not ticket_id:
                    return {
                        "success": False,
                        "message": "Missing ticket_id for update_ticket action"
                    }
                return update_ticket(config, ticket_id, action_data)
            elif action_type == "add_note":
                ticket_id = action_data.pop("ticket_id", None)
                note_data = {
                    "body": action_data.pop("body", ""),
                    "private": action_data.pop("private", True)
                }
                if not ticket_id:
                    return {
                        "success": False,
                        "message": "Missing ticket_id for add_note action"
                    }
                return add_note(config, ticket_id, note_data)
            else:
                return {
                    "success": False,
                    "message": f"Unsupported action type for Freshdesk: {action_type}"
                }
        elif platform == "slack":
            from modules.slack.actions import send_message
            
            if action_type == "send_message":
                return send_message(config, action_data)
            else:
                return {
                    "success": False,
                    "message": f"Unsupported action type for Slack: {action_type}"
                }
        else:
            return {
                "success": False,
                "message": f"Unsupported integration platform: {platform}"
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error executing integration action: {str(e)}"
        }

async def process_rule(rule: Rule, session: AsyncSession = None):
    try:
        actions = json.loads(rule.actions)
        for action in actions:
            platform = action.get("platform")
            if not platform:
                continue
                
            print(f"[DEBUG] Processing action for platform '{platform}'")
            
            # Check if this is an integration action
            if platform in ["zendesk", "freshdesk"]:
                if not session:
                    print(f"[ERROR] Database session required for integration actions")
                    continue
                    
                action_type = action.get("action_type")
                action_data = action.get("data", {})
                integration_id = action.get("integration_id")
                
                if not action_type or not integration_id:
                    print(f"[ERROR] Missing action_type or integration_id for {platform} action")
                    continue
                
                result = await execute_integration_action(
                    platform, 
                    action_type, 
                    action_data, 
                    integration_id,
                    session
                )
            elif platform == "slack":
                # Handle Slack actions using integration from database
                if not session:
                    print(f"[ERROR] Database session required for Slack integration actions")
                    result = {
                        "success": False,
                        "message": "Database session required for Slack actions"
                    }
                    continue
                    
                action_type = action.get("action")
                integration_id = action.get("integration_id")
                
                if not action_type or not integration_id:
                    print(f"[ERROR] Missing action_type or integration_id for Slack action")
                    result = {
                        "success": False,
                        "message": "Missing action_type or integration_id for Slack action"
                    }
                    continue
                
                # Get integration from database
                repository = IntegrationRepository(session)
                integration = await repository.get_integration(integration_id)
                
                if not integration:
                    result = {
                        "success": False,
                        "message": f"Slack integration with ID {integration_id} not found"
                    }
                    continue
                
                # Get decrypted config
                config = repository.get_decrypted_config(integration)
                
                # Extract parameters from action
                params = {}
                for key, value in action.items():
                    if key not in ["platform", "action", "integration_id"]:
                        params[key] = value
                
                # Import and execute action
                from modules.slack.actions import send_message
                
                if action_type == "send_message":
                    result = send_message(config, params)
                else:
                    result = {
                        "success": False,
                        "message": f"Unsupported Slack action: {action_type}"
                    }
            else:
                # Handle legacy action modules
                action_fn = load_action_module(platform)
                result = action_fn(action)
            
            print(f"[DEBUG] Raw result type: {type(result)}")
            print(f"[DEBUG] Raw result content: {result}")
            
            # Check if result is a dictionary with a 'message' key containing 'missing scopes'
            if isinstance(result, dict) and result.get('message') == 'missing scopes':
                print(f"[DEBUG] Found 'missing scopes' message in result")
            
            print(f"[INFO] Action executed for platform '{platform}':", result)
    except Exception as e:
        print("[ERROR] Failed to process rule:", e)
        import traceback
        traceback.print_exc()
