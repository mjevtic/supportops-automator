import os
import json
import requests

def execute_action(action_data):
    """
    Execute a Notion action to create a database item.
    
    Expected action_data format:
    {
        "platform": "notion",
        "action": "create_database_item",
        "database_id": "your-database-id",
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "New item title"
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": "Not started"
                }
            },
            "Priority": {
                "select": {
                    "name": "High"
                }
            }
            // Other properties as needed
        }
    }
    """
    try:
        # Validate action data
        if action_data.get("action") != "create_database_item":
            return {"status": "error", "message": "Unsupported action for Notion"}
        
        database_id = action_data.get("database_id")
        properties = action_data.get("properties", {})
        
        if not database_id:
            return {"status": "error", "message": "Missing database_id in action data"}
        
        if not properties:
            return {"status": "error", "message": "Missing properties in action data"}
        
        # Get Notion API token from environment variables
        notion_token = os.environ.get("NOTION_API_TOKEN")
        if not notion_token:
            return {"status": "error", "message": "Notion API token not configured"}
        
        # Set up the API request
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # Use the latest API version
        }
        
        # Prepare the request payload
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        # Make the API request to create a database item
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=payload
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "message": "Created Notion database item",
                "details": {
                    "page_id": result.get("id"),
                    "url": result.get("url")
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to create Notion database item: {response.status_code}",
                "details": response.json()
            }
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute Notion action: {str(e)}"}
