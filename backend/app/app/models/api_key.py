from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.constants import MAX_API_NAME_LENGTH
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
        Index('ix_api_key_name', 'name'),
        CheckConstraint(
            'expires_at IS NULL OR expires_at > created_at',
            name='check_expiry_after_creation'
        ),
        CheckConstraint(
            f'char_length(name) <= {MAX_API_NAME_LENGTH}',
            name='check_name_max_length'
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    key_hash: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    name: Mapped[str] = mapped_column(
        String(MAX_API_NAME_LENGTH),
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, key={self.key_hash[:8]}..., user_id={self.user_id}, name={self.name})>"
