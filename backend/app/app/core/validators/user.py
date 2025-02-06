from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models

async def validate_user_exists(db: AsyncSession, email: str) -> None:
    user = await crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

async def validate_user_not_exists(db: AsyncSession, email: str) -> models.User:
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
