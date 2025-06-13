import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_API_URL = "https://slack.com/api/chat.postMessage"

def execute_action(payload: dict):
    channel = payload.get("channel")
    message = payload.get("message")

    if not channel or not message:
        return {"error": "Missing channel or message"}

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "channel": channel,
        "text": message
    }

    response = requests.post(SLACK_API_URL, headers=headers, json=body)
    try:
        return response.json()
    except Exception as e:
        return {"error": str(e), "status_code": response.status_code}
