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
    """
    SQLAlchemy model for User.
    
    Represents a user in the system with authentication, authorization, and business logic properties.
    Each user can have multiple API keys and tokens, and has associated metadata like balance and company info.
    """
    
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

    # Core fields
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,  # Генерируем UUID на стороне Python
        nullable=False
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="Timestamp when the user was created"
    )
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the user was last modified"
    )

    # User metadata
    full_name: Mapped[Optional[str]] = mapped_column(
        index=True, 
        nullable=True,
        comment="User's full name"
    )
    email: Mapped[str] = mapped_column(
        unique=True, 
        index=True, 
        nullable=False,  # Email всегда должен быть
        comment="User's email address, used for authentication"
    )
    role: Mapped[Optional[str]] = mapped_column(
        nullable=True, 
        default="user",
        comment="User's role in the system (e.g., 'user', 'admin')"
    )
    
    # Authentication fields
    hashed_password: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="Hashed password for authentication"
    )
    totp_secret: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="Secret key for TOTP two-factor authentication"
    )
    totp_counter: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Counter for TOTP authentication"
    )
    
    # Account status
    email_validated: Mapped[bool] = mapped_column(
        default=False,
        nullable=True,
        comment="Whether the user's email has been validated"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=True,
        comment="Whether the user account is active"
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        nullable=True,
        comment="Whether the user has superuser privileges"
    )
    
    # Business logic fields
    balance_rub: Mapped[Optional[int]] = mapped_column(
        nullable=True, 
        default=0,
        comment="User's balance in rubles"
    )
    company_name_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        Sequence('user_company_name_id_seq'),
        server_default=text("nextval('user_company_name_id_seq')"),
        unique=True,
        index=True,
        nullable=True,
        comment="Unique identifier for the user's company"
    )
    gpt_filter_prompt: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="Custom GPT filter prompt for this user"
    )

    # Relationships
    refresh_tokens: Mapped[list["Token"]] = relationship(
        foreign_keys="[Token.authenticates_id]", 
        back_populates="authenticates", 
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["APIKey"]] = relationship(
        back_populates="user", 
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
