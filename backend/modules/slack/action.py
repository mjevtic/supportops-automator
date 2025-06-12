def execute_action(payload):
    print("[MOCK] Slack action received payload:")
    print(payload)
    return {
        "status": "success",
        "message": "Mock Slack action executed"
    }
