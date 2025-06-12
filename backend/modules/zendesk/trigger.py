def handle_trigger(payload):
    print("[MOCK] Zendesk trigger received payload:")
    print(payload)
    return {
        "status": "success",
        "message": "Mock Zendesk trigger executed"
    }
