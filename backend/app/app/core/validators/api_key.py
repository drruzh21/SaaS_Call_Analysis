from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models

async def validate_api_key_is_active(api_key) -> None:
    from app.models import APIKey
    if not isinstance(api_key, APIKey):
        raise TypeError("Expected APIKey instance")
    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is not active"
        )

async def validate_api_key_ownership(api_key, current_user) -> None:
    from app.models import APIKey, User
    if not isinstance(api_key, APIKey) or not isinstance(current_user, User):
        raise TypeError("Expected APIKey and User instances")
    if api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this operation"
        )

async def validate_api_key_exists(db: AsyncSession, key: str) -> models.APIKey:
    api_key = await crud.api_key.get_by_key(db, key=key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return api_key
