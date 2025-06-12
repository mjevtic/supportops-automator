import json
from models.rule import Rule
from routes.modules import load_action_module

async def process_rule(rule: Rule):
    try:
        actions = json.loads(rule.actions)
        for action in actions:
            platform = action.get("platform")
            if not platform:
                continue
            action_fn = load_action_module(platform)
            result = action_fn(action)
            print(f"[INFO] Action executed for platform '{platform}':", result)
    except Exception as e:
        print("[ERROR] Failed to process rule:", e)
