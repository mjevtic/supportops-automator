from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from db import async_session
from models.integration import IntegrationCreate, IntegrationUpdate, IntegrationRead
from repositories.integration_repository import IntegrationRepository

router = APIRouter()

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/integrations", response_model=IntegrationRead, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new integration"""
    repository = IntegrationRepository(session)
    integration = await repository.create_integration(integration_data)
    return IntegrationRead.from_integration(integration)

@router.get("/integrations", response_model=List[IntegrationRead])
async def get_integrations(
    user_id: int = None,
    integration_type: str = None,
    session: AsyncSession = Depends(get_session)
):
    """Get all integrations for a user, optionally filtered by type"""
    repository = IntegrationRepository(session)
    
    # For now, if no user_id is provided, return all integrations
    # In a real production app, you'd use authentication to get the current user
    if user_id is None:
        integrations = await repository.get_all_integrations()
    elif integration_type:
        integrations = await repository.get_integrations_by_type(user_id, integration_type)
    else:
        integrations = await repository.get_integrations_by_user(user_id)
    
    return [IntegrationRead.from_integration(integration) for integration in integrations]

@router.get("/integrations/{integration_id}", response_model=IntegrationRead)
async def get_integration(
    integration_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific integration by ID"""
    repository = IntegrationRepository(session)
    integration = await repository.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with ID {integration_id} not found"
        )
    
    return IntegrationRead.from_integration(integration)

@router.put("/integrations/{integration_id}", response_model=IntegrationRead)
async def update_integration(
    integration_id: int,
    integration_data: IntegrationUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an integration"""
    repository = IntegrationRepository(session)
    integration = await repository.update_integration(integration_id, integration_data)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with ID {integration_id} not found"
        )
    
    return IntegrationRead.from_integration(integration)

@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete an integration"""
    repository = IntegrationRepository(session)
    success = await repository.delete_integration(integration_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with ID {integration_id} not found"
        )

@router.post("/integrations/{integration_id}/test", status_code=status.HTTP_200_OK)
async def test_integration(
    integration_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Test an existing integration's connectivity"""
    repository = IntegrationRepository(session)
    integration = await repository.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with ID {integration_id} not found"
        )
    
    # Get decrypted config
    config = repository.get_decrypted_config(integration)
    integration_type = integration.integration_type
    
    return await test_integration_connection(integration_type, config)


from pydantic import BaseModel

class TestConnectionRequest(BaseModel):
    integration_type: str
    config: dict

@router.post("/integrations/test", status_code=status.HTTP_200_OK)
async def test_integration_config(request: TestConnectionRequest):
    """Test an integration configuration without saving it"""
    return await test_integration_connection(request.integration_type, request.config)


async def test_integration_connection(integration_type: str, config: dict):
    """Helper function to test integration connection"""
    # Import the appropriate module based on integration type
    try:
        if integration_type == "zendesk":
            from modules.zendesk.actions import test_connection
        elif integration_type == "freshdesk":
            from modules.freshdesk.actions import test_connection
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported integration type: {integration_type}"
            )
        
        # Test the connection
        result = test_connection(config)
        
        if result.get("success"):
            return {"success": True, "message": "Connection successful"}
        else:
            return {
                "success": False, 
                "message": result.get("message", "Connection failed")
            }
    
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Integration module for {integration_type} not implemented"
        )
    except Exception as e:
        return {
            "success": False,
            "message": f"Error testing connection: {str(e)}"
        }
