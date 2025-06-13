import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
print("[DEBUG] Loading environment variables")
load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_URL = "https://api.trello.com/1/cards"

print(f"[DEBUG] TRELLO_API_KEY is {'set' if TRELLO_API_KEY else 'NOT SET'}")
print(f"[DEBUG] TRELLO_TOKEN is {'set' if TRELLO_TOKEN else 'NOT SET'}")


def execute_action(payload: dict):
    list_id = payload.get("list_id")
    name = payload.get("name")
    desc = payload.get("desc", "")

    if not list_id or not name:
        return {"error": "Missing list_id or name"}

    # Debug info
    print(f"[DEBUG] Using TRELLO_API_KEY: {TRELLO_API_KEY[:5]}...")
    print(f"[DEBUG] Using TRELLO_TOKEN: {TRELLO_TOKEN[:5]}...")
    print(f"[DEBUG] List ID: {list_id}")

    params = {
        "idList": list_id,
        "name": name,
        "desc": desc,
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }

    print(f"[DEBUG] Sending request to {TRELLO_API_URL}")
    response = requests.post(TRELLO_API_URL, params=params)
    print(f"[DEBUG] Response status code: {response.status_code}")
    print(f"[DEBUG] Response text: {response.text[:200]}..." if len(response.text) > 200 else f"[DEBUG] Response text: {response.text}")

    try:
        return response.json()
    except Exception as e:
        print(f"[DEBUG] Exception parsing JSON: {e}")
        return {
            "error": "Non-JSON response from Trello",
            "status_code": response.status_code,
            "response_text": response.text
        }
