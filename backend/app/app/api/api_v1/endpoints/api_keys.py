import logging
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.validators import (
    validate_api_key_exists,
    validate_api_key_is_active,
    validate_api_key_ownership
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=schemas.APIKey)
async def create_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    api_key_in: schemas.APIKeyCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create a new API key for the current user.
    Only the name can be set during creation.
    """
    # Log the creation attempt
    logger.info(f"User {current_user.email} attempting to create API key named: {api_key_in.name}")
    
    # Create the API key
    api_key = await crud.api_key.create(
        db=db,
        user_id=current_user.id,
        obj_in=api_key_in
    )
    
    logger.info(f"API key created successfully for user {current_user.email}")
    return api_key


@router.put("/{name}", response_model=schemas.APIKey)
async def update_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    name: str,
    api_key_in: schemas.APIKeyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an API key by name.
    Only name and is_active can be modified, and only by the key owner.
    """
    # Log the update attempt
    logger.info(f"User {current_user.email} attempting to update API key named: {name}")
    
    # Validate the API key exists and is owned by the current user
    api_key = await validate_api_key_exists(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    # Update the API key
    api_key = await crud.api_key.update(
        db=db,
        db_obj=api_key,
        obj_in=api_key_in
    )
    
    logger.info(f"API key {name} updated successfully by user {current_user.email}")
    return api_key


@router.get("/me", response_model=List[schemas.APIKey])
async def read_api_keys(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve all API keys for the current user.
    """
    api_keys = await crud.api_key.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return api_keys


@router.get("/{name}", response_model=schemas.APIKey)
async def read_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    name: str,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get a specific API key by its name.
    Only accessible by the key owner.
    """
    # Validate the API key exists and is owned by the current user
    api_key = await validate_api_key_exists(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    return api_key


@router.delete("/{name}", response_model=schemas.APIKey)
async def delete_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    name: str,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete an API key by name.
    Only accessible by the key owner.
    """
    # Log the deletion attempt
    logger.info(f"User {current_user.email} attempting to delete API key named: {name}")
    
    # Validate the API key exists and is owned by the current user
    api_key = await validate_api_key_exists(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    # Delete the API key
    api_key = await crud.api_key.remove(db=db, id=api_key.id)
    
    logger.info(f"API key {name} deleted successfully by user {current_user.email}")
    return api_key
