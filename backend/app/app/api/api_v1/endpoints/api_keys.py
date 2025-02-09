from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.validators import validate_api_key_exists, validate_api_key_is_active, validate_api_key_ownership

router = APIRouter()

@router.post("/", response_model=schemas.APIKey)
async def create_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    obj_in: schemas.APIKeyCreate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """Create a new API key for the current user.
    
    Args:
        db: Database session
        obj_in: API key creation data including name
        current_user: Current authenticated user
        
    Returns:
        Created API key object
    """
    return await crud.api_key.create(db=db, obj_in=obj_in, user_id=current_user.id)

@router.get("/", response_model=list[schemas.APIKey])
async def get_api_keys(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    page: int = 0,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    return await crud.api_key.get_multi_by_user(db=db, user_id=current_user.id, page=page)

@router.put("/{key}", response_model=schemas.APIKey)
async def update_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    key: str,
    obj_in: schemas.APIKeyUpdate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    api_key = await validate_api_key_exists(db, key)
    await validate_api_key_ownership(api_key, current_user)
    await validate_api_key_is_active(api_key)
    return await crud.api_key.update(db=db, db_obj=api_key, obj_in=obj_in, user_id=current_user.id)


@router.delete("/{key}", response_model=schemas.Msg)
async def delete_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    key: str,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    api_key = await validate_api_key_exists(db, key)
    await validate_api_key_ownership(api_key, current_user)
    await crud.api_key.remove(db=db, db_obj=api_key)
    return {"msg": "API key deleted"}
