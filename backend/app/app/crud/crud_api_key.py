import secrets
from datetime import datetime, timezone
from typing import Any, Optional, Union
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import GET_MULTI_MAX, MAX_API_KEY_GENERATION_ATTEMPTS, MAX_TOKEN_LENGTH
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
        user_id: UUID,
        obj_in: APIKeyCreate
    ) -> APIKey:
        """
        Create a new API key for a user.
        Only the name can be set during creation.
        """
        key = await self._generate_unique_key(db)
        
        db_obj = APIKey(
            id=None,
            key=key,
            user_id=user_id,
            name=obj_in.name,
            is_active=True,
            expires_at=None,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: APIKey,
        obj_in: Union[APIKeyUpdate, dict[str, Any]]
    ) -> APIKey:
        """
        Update an API key.
        Only name and is_active can be modified.
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        
        allowed_fields = {"name", "is_active"}
        filtered_data = {
            k: v for k, v in update_data.items() 
            if k in allowed_fields and v is not None
        }
        
        return await super().update(db, db_obj=db_obj, obj_in=filtered_data)

    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        user_id: UUID,
        check_active: bool = True
    ) -> Optional[APIKey]:
        """Get an API key by its name and user_id."""
        conditions = [
            APIKey.name == name,
            APIKey.user_id == user_id
        ]
        
        if check_active:
            conditions.extend([
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > datetime.now(timezone.utc)
                )
            ])
            
        result = await db.execute(
            select(APIKey).where(and_(*conditions))
        )
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        id: UUID,
    ) -> Optional[APIKey]:
        """Get an API key by its id."""
        result = await db.execute(
            select(APIKey).where(APIKey.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = GET_MULTI_MAX
    ) -> list[APIKey]:
        """Get all API keys for a specific user."""
        result = await db.execute(
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .order_by(APIKey.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_key_count(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> int:
        """Get count of active API keys for a user."""
        result = await db.execute(
            select(func.count())
            .where(and_(
                APIKey.user_id == user_id,
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > datetime.now(timezone.utc)
                )
            ))
        )
        return result.scalar()


api_key = CRUDAPIKey(APIKey)
