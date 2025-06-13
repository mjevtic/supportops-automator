import requests
from typing import Dict, Any, Optional

def test_connection(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test connection to Zendesk API
    
    Args:
        config: Dictionary containing 'subdomain', 'email', and 'api_token'
    
    Returns:
        Dict with 'success' boolean and optional 'message'
    """
    subdomain = config.get('subdomain')
    email = config.get('email')
    api_token = config.get('api_token')
    
    if not subdomain or not email or not api_token:
        return {
            "success": False,
            "message": "Missing required configuration: subdomain, email, and api_token"
        }
    
    # Remove https:// if included
    if subdomain.startswith('https://'):
        subdomain = subdomain[8:]
    
    # Remove .zendesk.com if included
    if '.zendesk.com' in subdomain:
        subdomain = subdomain.split('.zendesk.com')[0]
    
    url = f"https://{subdomain}.zendesk.com/api/v2/tickets"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Use email/token auth
        auth = f"{email}/token:{api_token}"
        response = requests.get(
            url, 
            headers=headers,
            auth=(email + "/token", api_token)
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Connection successful"
            }
        else:
            return {
                "success": False,
                "message": f"API Error: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection error: {str(e)}"
        }

def create_ticket(config: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a ticket in Zendesk
    
    Args:
        config: Dictionary containing 'subdomain', 'email', and 'api_token'
        ticket_data: Dictionary with ticket details
    
    Returns:
        Dict with ticket information or error details
    """
    subdomain = config.get('subdomain')
    email = config.get('email')
    api_token = config.get('api_token')
    
    if not subdomain or not email or not api_token:
        return {
            "success": False,
            "message": "Missing required configuration: subdomain, email, and api_token"
        }
    
    # Remove https:// if included
    if subdomain.startswith('https://'):
        subdomain = subdomain[8:]
    
    # Remove .zendesk.com if included
    if '.zendesk.com' in subdomain:
        subdomain = subdomain.split('.zendesk.com')[0]
    
    url = f"https://{subdomain}.zendesk.com/api/v2/tickets"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Zendesk expects ticket data in a specific format
    payload = {"ticket": ticket_data}
    
    try:
        response = requests.post(
            url, 
            headers=headers,
            auth=(email + "/token", api_token),
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": f"API Error: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating ticket: {str(e)}"
        }

def update_ticket(config: Dict[str, Any], ticket_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a ticket in Zendesk
    
    Args:
        config: Dictionary containing 'subdomain', 'email', and 'api_token'
        ticket_id: ID of the ticket to update
        update_data: Dictionary with fields to update
    
    Returns:
        Dict with updated ticket information or error details
    """
    subdomain = config.get('subdomain')
    email = config.get('email')
    api_token = config.get('api_token')
    
    if not subdomain or not email or not api_token:
        return {
            "success": False,
            "message": "Missing required configuration: subdomain, email, and api_token"
        }
    
    # Remove https:// if included
    if subdomain.startswith('https://'):
        subdomain = subdomain[8:]
    
    # Remove .zendesk.com if included
    if '.zendesk.com' in subdomain:
        subdomain = subdomain.split('.zendesk.com')[0]
    
    url = f"https://{subdomain}.zendesk.com/api/v2/tickets/{ticket_id}"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Zendesk expects ticket data in a specific format
    payload = {"ticket": update_data}
    
    try:
        response = requests.put(
            url, 
            headers=headers,
            auth=(email + "/token", api_token),
            json=payload
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": f"API Error: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating ticket: {str(e)}"
        }

def add_comment(config: Dict[str, Any], ticket_id: int, comment: str, public: bool = True) -> Dict[str, Any]:
    """
    Add a comment to a ticket in Zendesk
    
    Args:
        config: Dictionary containing 'subdomain', 'email', and 'api_token'
        ticket_id: ID of the ticket to add comment to
        comment: Comment text
        public: Whether the comment is public or internal
    
    Returns:
        Dict with comment information or error details
    """
    subdomain = config.get('subdomain')
    email = config.get('email')
    api_token = config.get('api_token')
    
    if not subdomain or not email or not api_token:
        return {
            "success": False,
            "message": "Missing required configuration: subdomain, email, and api_token"
        }
    
    # Remove https:// if included
    if subdomain.startswith('https://'):
        subdomain = subdomain[8:]
    
    # Remove .zendesk.com if included
    if '.zendesk.com' in subdomain:
        subdomain = subdomain.split('.zendesk.com')[0]
    
    url = f"https://{subdomain}.zendesk.com/api/v2/tickets/{ticket_id}"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Zendesk expects comment data in a specific format
    payload = {
        "ticket": {
            "comment": {
                "body": comment,
                "public": public
            }
        }
    }
    
    try:
        response = requests.put(
            url, 
            headers=headers,
            auth=(email + "/token", api_token),
            json=payload
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": f"API Error: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding comment: {str(e)}"
        }
