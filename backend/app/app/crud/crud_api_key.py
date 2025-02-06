import secrets
from datetime import datetime, timezone
from typing import Any, Optional, Union
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import MAX_API_KEY_GENERATION_ATTEMPTS, MAX_TOKEN_LENGTH
from app.crud.base import CRUDBase
from app.models import APIKey
from app.schemas import APIKeyCreate, APIKeyUpdate


class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, APIKeyUpdate]):
    """CRUD operations for API keys."""

    async def _generate_unique_key(self, db: AsyncSession, max_attempts=MAX_API_KEY_GENERATION_ATTEMPTS) -> str:
        """Generate a unique API key that doesn't exist in the database."""
        for _ in range(max_attempts):
            key = secrets.token_urlsafe(MAX_TOKEN_LENGTH)
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
        user_id: UUID
    ) -> APIKey:
        """Create a new API key for a user."""
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

        if 'is_active' in update_data:
            return await super().update(db, db_obj=db_obj, obj_in={'is_active': update_data['is_active']})
        
        return db_obj

    async def remove(self, db: AsyncSession, *, db_obj: APIKey) -> None:
        """Remove an API key."""
        await db.delete(db_obj)
        await db.commit()

api_key = CRUDAPIKey(APIKey)
