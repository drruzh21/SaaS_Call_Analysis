from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models import User, Token
from app.schemas import RefreshTokenCreate, RefreshTokenUpdate
from app.core.config import settings


class CRUDToken(CRUDBase[Token, RefreshTokenCreate, RefreshTokenUpdate]):
    # Everything is user-dependent
    async def create(self, db: AsyncSession, *, obj_in: str, user_obj: User) -> Token:
        result = await db.execute(
            select(self.model).where(self.model.token == obj_in)
        )
        db_obj = result.scalars().first()
        if db_obj and db_obj.authenticates != user_obj:
            raise ValueError("Token mismatch between key and user.")
        obj_in = RefreshTokenCreate(**{"token": obj_in, "authenticates_id": user_obj.id})
        return await super().create(db=db, obj_in=obj_in)

    async def get(self, db: AsyncSession, *, user: User, token: str) -> Token:
        result = await db.execute(
            select(self.model)
            .where(self.model.token == token)
            .where(self.model.authenticates_id == user.id)
        )
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, user: User, page: int = 0, page_break: bool = False) -> list[Token]:
        query = select(self.model).where(self.model.authenticates_id == user.id)
        if not page_break:
            if page > 0:
                query = query.offset(page * settings.MULTI_MAX)
            query = query.limit(settings.MULTI_MAX)
        result = await db.execute(query)
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, db_obj: Token) -> None:
        await db.delete(db_obj)
        await db.commit()
        return None

token = CRUDToken(Token)
