import os
import requests

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_URL = "https://api.trello.com/1/cards"

def execute_action(payload: dict):
    list_id = payload.get("list_id")
    name = payload.get("name")
    desc = payload.get("desc", "")

    if not list_id or not name:
        return {"error": "Missing list_id or name"}

    params = {
        "idList": list_id,
        "name": name,
        "desc": desc,
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }

    response = requests.post(TRELLO_API_URL, params=params)

    try:
        return response.json()
    except Exception:
        return {
            "error": "Non-JSON response from Trello",
            "status_code": response.status_code,
            "response_text": response.text
        }
