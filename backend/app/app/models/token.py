from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MAX_TOKEN_LENGTH
from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Token(Base):
    __table_args__ = (
        CheckConstraint(
            f'char_length(token) <= {MAX_TOKEN_LENGTH}',
            name='check_token_max_length'
        ),
    )

    token: Mapped[str] = mapped_column(String(MAX_TOKEN_LENGTH), primary_key=True, index=True)
    authenticates_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
    authenticates: Mapped["User"] = relationship(back_populates="refresh_tokens")
