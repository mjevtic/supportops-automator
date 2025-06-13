"""
Slack integration actions module
"""
import requests
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def test_connection(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test the connection to Slack using the provided configuration
    
    Args:
        config: Dictionary containing Slack webhook URL or token
        
    Returns:
        Dict with success status and optional error message
    """
    try:
        # For webhook-based integration
        if 'webhook_url' in config:
            # Send a test message
            response = requests.post(
                config['webhook_url'],
                json={
                    "text": "Test connection from SupportOps Automator"
                }
            )
            
            if response.status_code == 200:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "message": f"Failed to connect to Slack: {response.status_code} - {response.text}"
                }
        
        # For token-based integration
        elif 'token' in config:
            # Test auth with Slack API
            headers = {
                "Authorization": f"Bearer {config['token']}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = requests.get(
                "https://slack.com/api/auth.test",
                headers=headers
            )
            
            data = response.json()
            if data.get('ok'):
                return {"success": True}
            else:
                return {
                    "success": False,
                    "message": f"Failed to authenticate with Slack: {data.get('error')}"
                }
        else:
            return {
                "success": False,
                "message": "Missing required configuration: webhook_url or token"
            }
            
    except Exception as e:
        logger.error(f"Error testing Slack connection: {str(e)}")
        return {
            "success": False,
            "message": f"Error connecting to Slack: {str(e)}"
        }

def send_message(config: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a message to a Slack channel
    
    Args:
        config: Dictionary containing Slack webhook URL or token
        params: Dictionary containing message parameters (channel, message, etc.)
        
    Returns:
        Dict with success status and optional error message
    """
    try:
        message = params.get('message', 'Message from SupportOps Automator')
        
        # For webhook-based integration
        if 'webhook_url' in config:
            payload = {
                "text": message
            }
            
            # Add optional blocks/attachments if provided
            if 'blocks' in params:
                payload['blocks'] = params['blocks']
                
            if 'attachments' in params:
                payload['attachments'] = params['attachments']
                
            response = requests.post(config['webhook_url'], json=payload)
            
            if response.status_code == 200:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "message": f"Failed to send Slack message: {response.status_code} - {response.text}"
                }
        
        # For token-based integration
        elif 'token' in config:
            headers = {
                "Authorization": f"Bearer {config['token']}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            channel = params.get('channel', '#general')
            
            payload = {
                "channel": channel,
                "text": message
            }
            
            # Add optional blocks/attachments if provided
            if 'blocks' in params:
                payload['blocks'] = params['blocks']
                
            if 'attachments' in params:
                payload['attachments'] = params['attachments']
            
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers=headers,
                json=payload
            )
            
            data = response.json()
            if data.get('ok'):
                return {"success": True}
            else:
                return {
                    "success": False,
                    "message": f"Failed to send Slack message: {data.get('error')}"
                }
        else:
            return {
                "success": False,
                "message": "Missing required configuration: webhook_url or token"
            }
            
    except Exception as e:
        logger.error(f"Error sending Slack message: {str(e)}")
        return {
            "success": False,
            "message": f"Error sending Slack message: {str(e)}"
        }
