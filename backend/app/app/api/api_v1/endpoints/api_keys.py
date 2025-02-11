from typing import Annotated, Any
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.validators import validate_api_key_exists_by_name, validate_api_key_ownership

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=schemas.APIKey)
async def create_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    obj_in: schemas.APIKeyCreate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """Create a new API key for the current user."""
    logger.info(f"User {current_user.email} attempting to create new API key")
    
    # Проверяем, не существует ли уже ключ с таким именем у пользователя
    existing_key = await crud.api_key.get_by_name(
        db=db,
        name=obj_in.name,
        user_id=current_user.id
    )
    if existing_key:
        logger.warning(f"API key with name {obj_in.name} already exists for user {current_user.email}")
        raise HTTPException(
            status_code=400,
            detail="API key with this name already exists"
        )
    
    api_key = await crud.api_key.create(db=db, obj_in=obj_in, user_id=current_user.id)
    logger.info(f"API key {api_key.name} created successfully for user {current_user.email}")
    return api_key

@router.get("/", response_model=list[schemas.APIKey])
async def get_api_keys(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    page: int = 0,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """Get all API keys for the current user."""
    logger.info(f"Fetching API keys for user {current_user.email}, page {page}")
    return await crud.api_key.get_multi_by_user(db=db, user_id=current_user.id, page=page)

@router.put("/{name}", response_model=schemas.APIKey)
async def update_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    name: str,
    obj_in: schemas.APIKeyUpdate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """Update an API key by name."""
    logger.info(f"User {current_user.email} attempting to update API key named: {name}")
    
    api_key = await validate_api_key_exists_by_name(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    # Если меняется имя, проверяем уникальность нового имени
    if obj_in.name and obj_in.name != name:
        existing_key = await crud.api_key.get_by_name(
            db=db,
            name=obj_in.name,
            user_id=current_user.id
        )
        if existing_key:
            logger.warning(f"API key with name {obj_in.name} already exists for user {current_user.email}")
            raise HTTPException(
                status_code=400,
                detail="API key with this name already exists"
            )
    
    updated_key = await crud.api_key.update(
        db=db,
        db_obj=api_key,
        obj_in=obj_in,
        user_id=current_user.id
    )
    logger.info(f"API key {name} updated successfully by user {current_user.email}")
    return updated_key

@router.delete("/{name}", response_model=schemas.Msg)
async def delete_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    name: str,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """Delete an API key by name."""
    logger.info(f"User {current_user.email} attempting to delete API key named: {name}")
    
    api_key = await validate_api_key_exists_by_name(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    await crud.api_key.remove(db=db, db_obj=api_key)
    logger.info(f"API key {name} deleted successfully by user {current_user.email}")
    return {"msg": "API key deleted"}