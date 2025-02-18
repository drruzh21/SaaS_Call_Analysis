import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models

logger = logging.getLogger(__name__)


async def validate_api_key_for_operation(
    db: AsyncSession,
    name: str,
    user_id: UUID,
    operation: str = "access"
) -> models.APIKey:
    """
    Unified validator for API key operations.
    
    Args:
        db: Database session
        name: Name of the API key
        user_id: ID of the user performing the operation
        operation: Type of operation (access, update, delete)
        
    Returns:
        APIKey: The validated API key
        
    Raises:
        HTTPException:
            - 404: If the API key doesn't exist
            - 403: If the user doesn't own the key
    """
    api_key = await crud.api_key.get_by_name(
        db, 
        name=name, 
        user_id=user_id
    )
    
    if not api_key:
        logger.warning(f"Attempt to {operation} non-existent API key with name: {name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
        
    if api_key.user_id != user_id:
        logger.warning(
            f"User {user_id} attempted to {operation} API key {api_key.id} "
            f"belonging to user {api_key.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    return api_key


async def validate_api_key_ownership(api_key: models.APIKey, user_id: UUID) -> None:
    """
    Validate that an API key belongs to a specific user.
    
    Args:
        api_key: API key to validate
        user_id: User ID to check ownership against
        
    Raises:
        HTTPException: If the API key doesn't belong to the user
    """
    if api_key.user_id != user_id:
        logger.warning(
            f"User {user_id} attempted to access API key {api_key.id} "
            f"belonging to user {api_key.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
