from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import validator
import json

class Integration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    name: str
    integration_type: str  # zendesk, freshdesk, etc.
    config: str  # JSON stringified config (encrypted sensitive data)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("config")
    def validate_config(cls, v):
        try:
            json.loads(v)
            return v
        except:
            raise ValueError("Config must be valid JSON")

class IntegrationCreate(SQLModel):
    user_id: int
    name: str
    integration_type: str
    config: dict
    
    def to_integration(self):
        return Integration(
            user_id=self.user_id,
            name=self.name,
            integration_type=self.integration_type,
            config=json.dumps(self.config)
        )

class IntegrationRead(SQLModel):
    id: int
    user_id: int
    name: str
    integration_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_integration(cls, integration: Integration):
        return cls(
            id=integration.id,
            user_id=integration.user_id,
            name=integration.name,
            integration_type=integration.integration_type,
            is_active=integration.is_active,
            created_at=integration.created_at,
            updated_at=integration.updated_at
        )

class IntegrationUpdate(SQLModel):
    name: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None
