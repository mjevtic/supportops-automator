from backend.models.rule import Rule
from backend.services.rule_engine import process_rule
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    rule = Rule(
        id=1,
        user_id=1,
        trigger_platform="zendesk",
        trigger_event="ticket_tag_added",
        trigger_data='{"tag": "urgent"}',
        actions='[{"platform": "trello", "type": "create_card", "list_id": "684b6759815993af1bb15897", "name": "Test karta iz skripte", "desc": "Ova kartica je test iz dev_test.py"}]'
    )

    asyncio.run(process_rule(rule))
