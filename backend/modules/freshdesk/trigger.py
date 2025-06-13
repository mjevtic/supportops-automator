def handle_trigger(payload):
    """
    Handle incoming webhook from Freshdesk
    
    Payload structure example:
    {
        "freshdesk_webhook": {
            "ticket_id": 123,
            "ticket_url": "https://domain.freshdesk.com/tickets/123",
            "ticket_type": "Incident",
            "ticket_subject": "Support Needed",
            "ticket_description": "I need help with...",
            "ticket_status": "Open",
            "ticket_priority": 1,
            "requester_name": "John Doe",
            "requester_email": "john@example.com"
        }
    }
    """
    print("[FRESHDESK] Trigger received payload:")
    print(payload)
    
    try:
        # Extract ticket information
        ticket_data = payload.get("freshdesk_webhook", {})
        ticket_id = ticket_data.get("ticket_id")
        ticket_status = ticket_data.get("ticket_status")
        
        if not ticket_id:
            return {
                "status": "error",
                "message": "Invalid payload: missing ticket_id"
            }
        
        # Process the webhook data
        # This would typically involve checking rules and executing actions
        
        return {
            "status": "success",
            "message": "Freshdesk trigger processed",
            "data": {
                "ticket_id": ticket_id,
                "ticket_status": ticket_status
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing Freshdesk webhook: {str(e)}"
        }
