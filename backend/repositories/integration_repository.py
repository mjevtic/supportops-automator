from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
import json

from models.integration import Integration, IntegrationCreate, IntegrationUpdate
from utils.encryption import encrypt_config, decrypt_config

class IntegrationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_integration(self, integration_data: IntegrationCreate) -> Integration:
        """Create a new integration with encrypted sensitive data"""
        # Encrypt sensitive data in config
        encrypted_config = encrypt_config(integration_data.config)
        
        # Create integration with encrypted config
        integration = Integration(
            user_id=integration_data.user_id,
            name=integration_data.name,
            integration_type=integration_data.integration_type,
            config=json.dumps(encrypted_config)
        )
        
        self.session.add(integration)
        await self.session.commit()
        await self.session.refresh(integration)
        return integration
    
    async def get_integration(self, integration_id: int) -> Optional[Integration]:
        """Get integration by ID"""
        query = select(Integration).where(Integration.id == integration_id)
        result = await self.session.execute(query)
        integration = result.scalar_one_or_none()
        return integration
    
    async def get_integrations_by_user(self, user_id: int) -> List[Integration]:
        """Get all integrations for a user"""
        query = select(Integration).where(Integration.user_id == user_id)
        result = await self.session.execute(query)
        integrations = result.scalars().all()
        return list(integrations)
    
    async def get_integrations_by_type(self, user_id: int, integration_type: str) -> List[Integration]:
        """Get all integrations of a specific type for a user"""
        query = select(Integration).where(
            Integration.user_id == user_id,
            Integration.integration_type == integration_type
        )
        result = await self.session.execute(query)
        integrations = result.scalars().all()
        return list(integrations)
    
    async def update_integration(self, integration_id: int, integration_data: IntegrationUpdate) -> Optional[Integration]:
        """Update an integration"""
        query = select(Integration).where(Integration.id == integration_id)
        result = await self.session.execute(query)
        integration = result.scalar_one_or_none()
        
        if not integration:
            return None
        
        # Update fields if provided
        if integration_data.name is not None:
            integration.name = integration_data.name
        
        if integration_data.is_active is not None:
            integration.is_active = integration_data.is_active
        
        if integration_data.config is not None:
            # Get current config
            current_config = json.loads(integration.config)
            
            # Merge with new config
            for key, value in integration_data.config.items():
                current_config[key] = value
            
            # Encrypt and save
            encrypted_config = encrypt_config(current_config)
            integration.config = json.dumps(encrypted_config)
        
        await self.session.commit()
        await self.session.refresh(integration)
        return integration
    
    async def delete_integration(self, integration_id: int) -> bool:
        """Delete an integration"""
        query = select(Integration).where(Integration.id == integration_id)
        result = await self.session.execute(query)
        integration = result.scalar_one_or_none()
        
        if not integration:
            return False
        
        await self.session.delete(integration)
        await self.session.commit()
        return True
    
    def get_decrypted_config(self, integration: Integration) -> dict:
        """Get decrypted configuration for an integration"""
        config = json.loads(integration.config)
        return decrypt_config(config)
