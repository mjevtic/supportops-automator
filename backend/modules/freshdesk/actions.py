import requests
from typing import Dict, Any, Optional

def test_connection(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test connection to Freshdesk API
    
    Args:
        config: Dictionary containing 'domain' and 'api_key'
    
    Returns:
        Dict with 'success' boolean and optional 'message'
    """
    domain = config.get('domain')
    api_key = config.get('api_key')
    
    if not domain or not api_key:
        return {
            "success": False,
            "message": "Missing required configuration: domain and api_key"
        }
    
    # Remove https:// if included
    if domain.startswith('https://'):
        domain = domain[8:]
    
    # Remove trailing slash if present
    if domain.endswith('/'):
        domain = domain[:-1]
    
    url = f"https://{domain}/api/v2/tickets"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Use API key as basic auth
        response = requests.get(
            url, 
            headers=headers,
            auth=(api_key, 'X')  # Freshdesk uses API key as username and X as password
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
    Create a ticket in Freshdesk
    
    Args:
        config: Dictionary containing 'domain' and 'api_key'
        ticket_data: Dictionary with ticket details
    
    Returns:
        Dict with ticket information or error details
    """
    domain = config.get('domain')
    api_key = config.get('api_key')
    
    if not domain or not api_key:
        return {
            "success": False,
            "message": "Missing required configuration: domain and api_key"
        }
    
    # Remove https:// if included
    if domain.startswith('https://'):
        domain = domain[8:]
    
    # Remove trailing slash if present
    if domain.endswith('/'):
        domain = domain[:-1]
    
    url = f"https://{domain}/api/v2/tickets"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers,
            auth=(api_key, 'X'),
            json=ticket_data
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
    Update a ticket in Freshdesk
    
    Args:
        config: Dictionary containing 'domain' and 'api_key'
        ticket_id: ID of the ticket to update
        update_data: Dictionary with fields to update
    
    Returns:
        Dict with updated ticket information or error details
    """
    domain = config.get('domain')
    api_key = config.get('api_key')
    
    if not domain or not api_key:
        return {
            "success": False,
            "message": "Missing required configuration: domain and api_key"
        }
    
    # Remove https:// if included
    if domain.startswith('https://'):
        domain = domain[8:]
    
    # Remove trailing slash if present
    if domain.endswith('/'):
        domain = domain[:-1]
    
    url = f"https://{domain}/api/v2/tickets/{ticket_id}"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(
            url, 
            headers=headers,
            auth=(api_key, 'X'),
            json=update_data
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

def add_note(config: Dict[str, Any], ticket_id: int, note_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a note to a ticket in Freshdesk
    
    Args:
        config: Dictionary containing 'domain' and 'api_key'
        ticket_id: ID of the ticket to add note to
        note_data: Dictionary with note details (body, private)
    
    Returns:
        Dict with note information or error details
    """
    domain = config.get('domain')
    api_key = config.get('api_key')
    
    if not domain or not api_key:
        return {
            "success": False,
            "message": "Missing required configuration: domain and api_key"
        }
    
    # Remove https:// if included
    if domain.startswith('https://'):
        domain = domain[8:]
    
    # Remove trailing slash if present
    if domain.endswith('/'):
        domain = domain[:-1]
    
    url = f"https://{domain}/api/v2/tickets/{ticket_id}/notes"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers,
            auth=(api_key, 'X'),
            json=note_data
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
            "message": f"Error adding note: {str(e)}"
        }
