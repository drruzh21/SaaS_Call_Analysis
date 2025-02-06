from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, Integer, Sequence, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func

from app.core.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FULL_NAME_LENGTH,
    MAX_GPT_FILTER_PROMPT_LENGTH,
)
from app.db.base_class import Base

if TYPE_CHECKING:
    from . import APIKey, Token  # noqa: F401


class User(Base):
    __table_args__ = (
        CheckConstraint(
            f'char_length(full_name) <= {MAX_FULL_NAME_LENGTH}',
            name='check_full_name_max_length'
        ),
        CheckConstraint(
            f'char_length(email) <= {MAX_EMAIL_LENGTH}',
            name='check_email_max_length'
        ),
        CheckConstraint(
            f'char_length(gpt_filter_prompt) <= {MAX_GPT_FILTER_PROMPT_LENGTH}',
            name='check_gpt_filter_prompt_max_length'
        ),
        CheckConstraint(
            'modified >= created',
            name='check_modified_after_created'
        ),
        CheckConstraint(
            'balance_rub >= 0',
            name='check_balance_non_negative'
        ),
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    # METADATA
    full_name: Mapped[str] = mapped_column(index=True, nullable=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)
    # AUTHENTICATION AND PERSISTENCE
    totp_secret: Mapped[Optional[str]] = mapped_column(nullable=True)
    totp_counter: Mapped[Optional[int]] = mapped_column(nullable=True)
    email_validated: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    refresh_tokens: Mapped[list["Token"]] = relationship(
        foreign_keys="[Token.authenticates_id]", back_populates="authenticates", lazy="dynamic"
    )
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="user", lazy="dynamic")
    role: Mapped[str] = mapped_column(nullable=True, default="user")
    balance_rub: Mapped[int] = mapped_column(nullable=True, default=0)
    company_name_id: Mapped[int] = mapped_column(
        Integer,
        Sequence('user_company_name_id_seq'),
        server_default=text("nextval('user_company_name_id_seq')"),
        unique=True,
        index=True,
        nullable=False
    )
    gpt_filter_prompt: Mapped[str] = mapped_column(nullable=True)

    @validates('email')
    def validate_email(self, key, email):
        from app.core.validators import validate_email
        return validate_email(email)

    @validates('gpt_filter_prompt')
    def validate_gpt_filter_prompt(self, key, gpt_filter_prompt):
        from app.core.validators import validate_gpt_filter_prompt
        return validate_gpt_filter_prompt(gpt_filter_prompt)
