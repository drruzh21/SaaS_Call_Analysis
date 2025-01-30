import secrets
from typing import Any, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from uuid import UUID
from datetime import datetime, timezone

from app.crud.base import CRUDBase
from app.models import APIKey
from app.schemas import APIKeyCreate, APIKeyUpdate
from app.core.config import settings

class TooManyAPIKeysError(Exception):
    pass

class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, APIKeyUpdate]):
    """CRUD operations for API keys."""

    async def _generate_unique_key(self, db: AsyncSession, max_attempts=10) -> str:
        """Generate a unique API key that doesn't exist in the database."""
        for _ in range(max_attempts):
            key = secrets.token_urlsafe(32)
            result = await db.execute(
                select(func.count()).where(APIKey.key == key)
            )
            if result.scalar() == 0:
                return key
        raise RuntimeError("Failed to generate unique API key")

    async def create(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID,
        max_keys_per_user: int = settings.MAX_API_KEYS_PER_USER
    ) -> APIKey:
        """Create a new API key for a user."""
        # Check if user hasn't exceeded maximum number of keys
        result = await db.execute(
            select(func.count())
            .where(APIKey.user_id == user_id)
            .where(APIKey.is_active == True)
        )
        if result.scalar() >= max_keys_per_user:
            raise TooManyAPIKeysError(f"User cannot have more than {max_keys_per_user} active API keys")

        key = await self._generate_unique_key(db)
        db_obj = APIKey(key=key, user_id=user_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_key(
        self, 
        db: AsyncSession, 
        *, 
        key: str,
        check_active: bool = True
    ) -> Optional[APIKey]:
        """Get API key by its value, optionally checking if it's active."""
        query = select(APIKey).where(APIKey.key == key)
        
        if check_active:
            now = datetime.now(timezone.utc)
            query = query.where(
                and_(
                    APIKey.is_active == True,
                    or_(
                        APIKey.expires_at.is_(None),
                        APIKey.expires_at > now
                    )
                )
            )
            
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_by_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID, 
        page: int = 0,
        limit: int = settings.MULTI_MAX,
        include_expired: bool = False
    ) -> list[APIKey]:
        """Get multiple API keys for a user with pagination."""
        query = select(APIKey).where(APIKey.user_id == user_id)

        if not include_expired:
            now = datetime.now(timezone.utc)
            query = query.where(
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > now
                )
            )

        # Sort by creation date, newest first
        query = query.order_by(APIKey.created_at.desc())

        if page > 0:
            query = query.offset(page * limit)
        query = query.limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: APIKey, 
        obj_in: Union[APIKeyUpdate, dict[str, Any]],
        user_id: UUID
    ) -> APIKey:
        """Update an API key."""
        if db_obj.user_id != user_id:
            raise ValueError("Cannot update API key that doesn't belong to the user")

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if 'expires_at' in update_data:
            if update_data['expires_at'] and update_data['expires_at'] < datetime.now(timezone.utc):
                raise ValueError("Expiry date cannot be in the past")

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def remove(self, db: AsyncSession, *, db_obj: APIKey) -> None:
        """Remove an API key."""
        await db.delete(db_obj)
        await db.commit()

api_key = CRUDAPIKey(APIKey)
