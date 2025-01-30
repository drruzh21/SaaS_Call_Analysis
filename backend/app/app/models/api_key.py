from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import Optional, TYPE_CHECKING

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User

class APIKey(Base):
    """
    SQLAlchemy model for API keys.
    
    Represents an API key in the system that can be used for authentication.
    Each key is associated with a user and can have an optional expiration date.
    """
   
    __table_args__ = (
        Index('ix_api_key_user_id_created_at', 'user_id', 'created_at'),
        CheckConstraint(
            'expires_at IS NULL OR expires_at > created_at',
            name='check_expiry_after_creation'
        ),
    )

    key: Mapped[str] = mapped_column(
        primary_key=True,
        index=True,
        comment="Unique API key string"
    )
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        comment="ID of the user who owns this API key"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the API key was created"
    )
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Optional timestamp when the API key expires"
    )
    
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Whether this API key is currently active"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="api_keys",
        comment="Reference to the user who owns this API key"
    )

    def __repr__(self) -> str:
        return f"<APIKey(key={self.key[:8]}..., user_id={self.user_id})>"
