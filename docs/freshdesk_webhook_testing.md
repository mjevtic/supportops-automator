# Freshdesk Webhook Testing Guide

This guide explains how to test the Freshdesk webhook integration with SupportOps Automator.

## Using the Webhook Test Console

The easiest way to test the Freshdesk webhook integration is by using the built-in Webhook Test Console:

1. Navigate to the Webhook Console page in the SupportOps Automator UI
2. Select "Freshdesk" from the platform dropdown
3. The console will automatically load a sample Freshdesk payload
4. Click "Send Webhook" to send the test payload to the `/trigger/freshdesk` endpoint
5. View the response and logs in the console

## Sample Freshdesk Webhook Payload

The sample payload includes:

```json
{
  "freshdesk_webhook": {
    "ticket_id": 54321,
    "ticket_subject": "Cannot access my account",
    "ticket_description": "I'm getting an error when trying to login",
    "ticket_status": "Open",
    "ticket_priority": 2,
    "ticket_tags": ["urgent", "login", "account"]
  },
  "ticket": {
    "id": 54321,
    "tags": ["urgent", "login", "account"]
  },
  "timestamp": "2025-06-13T17:07:00.000Z"
}
```

## Setting Up a Real Freshdesk Webhook

To set up a real Freshdesk webhook:

1. Log in to your Freshdesk account
2. Navigate to Admin > Automations > Webhooks
3. Click "New Webhook"
4. Enter the following details:
   - Name: SupportOps Automator
   - URL: `https://your-backend-url.com/trigger/freshdesk`
   - Method: POST
   - Encoding: JSON
   - Authentication: None (or set up as needed)
5. Select the events that should trigger the webhook:
   - Ticket Created
   - Ticket Updated
   - Note Added
   - etc.
6. Save the webhook configuration

## Expected Rule Format

For a rule to be triggered by a Freshdesk webhook, it should have:

```json
{
  "trigger_platform": "freshdesk",
  "trigger_event": "ticket_tag_added",
  "trigger_data": "{\"tag\": \"urgent\"}"
}
```

## Testing with cURL

You can also test the webhook using cURL:

```bash
curl -X POST https://your-backend-url.com/trigger/freshdesk \
  -H "Content-Type: application/json" \
  -d '{
    "freshdesk_webhook": {
      "ticket_id": 54321,
      "ticket_subject": "Cannot access my account",
      "ticket_description": "I am getting an error when trying to login",
      "ticket_status": "Open",
      "ticket_priority": 2,
      "ticket_tags": ["urgent", "login", "account"]
    },
    "ticket": {
      "id": 54321,
      "tags": ["urgent", "login", "account"]
    },
    "timestamp": "2025-06-13T17:07:00.000Z"
  }'
```

## Troubleshooting

If your webhook is not triggering rules:

1. Check that the rule's `trigger_platform` is set to "freshdesk"
2. Verify that the `trigger_event` matches "ticket_tag_added"
3. Ensure the tag specified in the rule's `trigger_data` is included in the webhook payload
4. Check the server logs for any errors or debugging information
