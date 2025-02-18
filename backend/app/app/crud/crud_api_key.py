import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from typing import Any, Optional, Union
from uuid import UUID, uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import GET_MULTI_MAX, MAX_API_KEY_GENERATION_ATTEMPTS, MAX_TOKEN_LENGTH
from app.crud.base import CRUDBase
from app.models import APIKey
from app.schemas import APIKeyCreate, APIKeyUpdate


class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, APIKeyUpdate]):
    """CRUD operations for API keys with secure key handling."""

    def _generate_api_key(self, attempts: int = MAX_API_KEY_GENERATION_ATTEMPTS) -> tuple[str, str]:
        """
        Generate a new API key and its hash.
        
        Returns:
            tuple: (original_key, key_hash)
        """
        for _ in range(attempts):
            key = f"{uuid4().hex}{secrets.token_urlsafe(MAX_TOKEN_LENGTH)}"
            key_hash = self._hash_key(key)
            return key, key_hash
        raise Exception("Failed to generate a valid API key")

    def _hash_key(self, key: str) -> str:
        """
        Create a secure hash of the API key.
        
        Args:
            key: Original API key
            
        Returns:
            str: Hashed key
        """
        return hmac.new(
            key=settings.HASH_SECRET_KEY.encode(),
            msg=key.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

    async def verify_key(self, db: AsyncSession, key: str) -> Optional[APIKey]:
        """
        Verify an API key against stored hash.
        
        Args:
            db: Database session
            key: API key to verify
            
        Returns:
            Optional[APIKey]: API key object if valid
        """
        key_hash = self._hash_key(key)
        result = await db.execute(
            select(APIKey)
            .where(APIKey.key_hash == key_hash)
            .where(APIKey.is_active == True)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        obj_in: APIKeyCreate
    ) -> tuple[APIKey, str]:
        """
        Create a new API key.
        
        Returns:
            tuple: (api_key_object, original_key)
        """
        key, key_hash = self._generate_api_key()
        db_obj = APIKey(
            key_hash=key_hash,
            user_id=user_id,
            name=obj_in.name,
            is_active=obj_in.is_active,
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj, key

    async def get_multi_by_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID,
        skip: int = 0,
        limit: int = GET_MULTI_MAX
    ) -> list[APIKey]:
        """Get multiple API keys for a user with pagination."""
        now = datetime.now(timezone.utc)
        query = (
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .where(
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > now
                )
            )
            .order_by(APIKey.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
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
            db_obj.is_active = update_data['is_active']
        
        if 'name' in update_data and update_data['name'] is not None:
            db_obj.name = update_data['name']
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj

    async def remove(self, db: AsyncSession, *, db_obj: APIKey) -> None:
        """Remove an API key."""
        await db.delete(db_obj)
        await db.commit()

    async def get_by_name(
        self, 
        db: AsyncSession, 
        *, 
        name: str,
        user_id: UUID,
        check_active: bool = False
    ) -> Optional[APIKey]:
        """Get API key by name for a specific user."""
        query = select(APIKey).where(
            and_(
                APIKey.name == name,
                APIKey.user_id == user_id
            )
        )
        
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
        return result.scalar_one_or_none()

    async def get_active_key_count(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> int:
        """Get count of active API keys for a user."""
        now = datetime.now(timezone.utc)
        query = select(func.count()).select_from(APIKey).where(
            and_(
                APIKey.user_id == user_id,
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > now
                )
            )
        )
        result = await db.execute(query)
        return result.scalar_one()

api_key = CRUDAPIKey(APIKey)
