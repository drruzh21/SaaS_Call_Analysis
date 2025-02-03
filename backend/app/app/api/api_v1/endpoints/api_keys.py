from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.APIKey)
async def create_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    return await crud.api_key.create(db=db, user_id=current_user.id)

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
    db_obj = await crud.api_key.get_by_key(db=db, key=key, check_active=False)
    if not db_obj or db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")
    return await crud.api_key.update(db=db, db_obj=db_obj, obj_in=obj_in, user_id=current_user.id)

@router.delete("/{key}", response_model=schemas.Msg)
async def delete_api_key(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    key: str,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    db_obj = await crud.api_key.get_by_key(db=db, key=key)
    if not db_obj or db_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")
    await crud.api_key.remove(db=db, db_obj=db_obj)
    return {"msg": "API key deleted"}
