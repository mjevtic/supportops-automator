import os
import json
import requests

def execute_action(action_data):
    """
    Execute a Discord action to send a message to a channel via webhook.
    
    Expected action_data format:
    {
        "platform": "discord",
        "action": "send_message",
        "webhook_url": "your-webhook-url", # Can be stored in env or passed directly
        "content": "Message content",
        "username": "Custom Bot Name", # Optional
        "avatar_url": "https://example.com/avatar.png", # Optional
        "embeds": [ # Optional
            {
                "title": "Embed Title",
                "description": "Embed Description",
                "color": 5814783, # Decimal color value
                "fields": [
                    {
                        "name": "Field Name",
                        "value": "Field Value",
                        "inline": true
                    }
                ]
            }
        ]
    }
    """
    try:
        # Validate action data
        if action_data.get("action") != "send_message":
            return {"status": "error", "message": "Unsupported action for Discord"}
        
        # Get webhook URL from action data or environment variables
        webhook_url = action_data.get("webhook_url") or os.environ.get("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            return {"status": "error", "message": "Discord webhook URL not configured"}
        
        content = action_data.get("content")
        username = action_data.get("username")
        avatar_url = action_data.get("avatar_url")
        embeds = action_data.get("embeds", [])
        
        if not content and not embeds:
            return {"status": "error", "message": "Message must have content or embeds"}
        
        # Prepare the payload for Discord webhook
        payload = {}
        
        if content:
            payload["content"] = content
        
        if username:
            payload["username"] = username
            
        if avatar_url:
            payload["avatar_url"] = avatar_url
            
        if embeds:
            payload["embeds"] = embeds
        
        # Make the request to the Discord webhook
        response = requests.post(
            webhook_url,
            json=payload
        )
        
        # Check if the request was successful
        if response.status_code == 204:  # Discord returns 204 No Content on success
            return {
                "status": "success",
                "message": "Sent Discord message"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send Discord message: {response.status_code}",
                "details": response.text if response.content else None
            }
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute Discord action: {str(e)}"}
