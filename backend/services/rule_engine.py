import json
import importlib
from models.rule import Rule

# Define our own module loader to avoid circular imports
def load_action_module(name: str):
    if name == "slack":
        from modules.slack.action import execute_action
        return execute_action
    if name == "trello":
        from modules.trello.action import execute_action
        return execute_action
    # Add more action modules here as needed
    raise ValueError(f"Unknown action module: {name}")

async def process_rule(rule: Rule):
    try:
        actions = json.loads(rule.actions)
        for action in actions:
            platform = action.get("platform")
            if not platform:
                continue
            print(f"[DEBUG] Processing action for platform '{platform}'")
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
