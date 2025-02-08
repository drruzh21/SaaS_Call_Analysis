"""Validation functions for API keys."""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models

logger = logging.getLogger(__name__)


async def validate_api_key_exists_by_name(
    db: AsyncSession,
    name: str,
    user_id: UUID,
    check_active: bool = False
) -> models.APIKey:
    """
    Validate that an API key exists for a given name and user.
    
    Args:
        db: Database session
        name: Name of the API key to validate
        user_id: ID of the user who owns the key
        check_active: Whether to check if the key is active
        
    Returns:
        APIKey: The API key if it exists
        
    Raises:
        HTTPException: If the API key doesn't exist or is inactive
    """
    api_key = await crud.api_key.get_by_name(
        db, 
        name=name, 
        user_id=user_id,
        check_active=check_active
    )
    if not api_key:
        logger.warning(f"Attempt to access non-existent API key with name: {name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return api_key


async def validate_api_key_is_active(api_key: models.APIKey) -> None:
    """
    Validate that an API key is active and not expired.
    
    Args:
        api_key: API key to validate
        
    Raises:
        HTTPException: If the API key is inactive or expired
    """
    if not api_key.is_active:
        logger.warning(f"Attempt to use inactive API key: {api_key.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key is inactive"
        )

    if api_key.expires_at and api_key.expires_at <= datetime.now(timezone.utc):
        logger.warning(f"Attempt to use expired API key: {api_key.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key has expired"
        )


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
