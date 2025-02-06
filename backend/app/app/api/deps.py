from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core.config import settings
from app.db.session import async_session

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/oauth")


async def get_db() -> AsyncGenerator:
    async with async_session() as db:
        try:
            yield db
        finally:
            await db.close()


async def get_token_payload(token: str) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)], token: Annotated[str, Depends(reusable_oauth2)]
) -> models.User:
    token_data = await get_token_payload(token)
    if token_data.refresh or token_data.totp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_totp_user(
    db: Annotated[AsyncSession, Depends(get_db)], token: Annotated[str, Depends(reusable_oauth2)]
) -> models.User:
    token_data = await get_token_payload(token)
    if token_data.refresh or not token_data.totp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_magic_token(token: Annotated[str, Depends(reusable_oauth2)]) -> schemas.MagicTokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.MagicTokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data


async def get_refresh_user(
    db: Annotated[AsyncSession, Depends(get_db)], token: Annotated[str, Depends(reusable_oauth2)]
) -> models.User:
    token_data = await get_token_payload(token)
    if not token_data.refresh:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not await crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    token_obj = await crud.token.get(db=db, token=token, user=user)
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    await crud.token.remove(db, db_obj=token_obj)
    return user


async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    if not await crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    if not await crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user


async def get_active_websocket_user(*, db: AsyncSession, token: str) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise ValidationError("Could not validate credentials")
    if token_data.refresh:
        raise ValidationError("Could not validate credentials")
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise ValidationError("User not found")
    if not await crud.user.is_active(user):
        raise ValidationError("Inactive user")
    return user


async def get_current_user_by_api_key(
    db: Annotated[AsyncSession, Depends(get_db)],
    api_key: str = Header(None, alias="X-API-Key"),
) -> models.User:
    """
    Get current user by API key from header.
    Validates the API key and returns the associated user.
    
    Checks:
    1. API key is provided
    2. API key exists and is active
    3. API key is not expired
    4. Associated user exists and is active
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
        )
    
    api_key_obj = await crud.api_key.get_by_key(db, key=api_key, check_active=True)
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )
    
    if not api_key_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive",
        )
    
    user = await crud.user.get(db, id=api_key_obj.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or deleted",
        )
    
    return user
