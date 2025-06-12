from sqlmodel import SQLModel, Field
from typing import Optional

class Rule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    trigger_platform: str
    trigger_event: str
    trigger_data: str  # JSON stringified
    actions: str       # JSON stringified list
