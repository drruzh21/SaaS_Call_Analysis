from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import validate_expiry


class APIKeyBase(BaseModel):
    expires_at: Optional[datetime] = Field(
        default=None,
        description="When this API key expires. If null, the key never expires"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this API key is active"
    )

    @field_validator("expires_at")
    def validate_expiry(cls, v):
        return validate_expiry(v)

class APIKeyUpdate(BaseModel):
    is_active: bool = Field(
        default=True
    )

class APIKeyInDBBase(APIKeyBase):
    key: str
    user_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "key": "sk_test_abc123def456ghi789jkl",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2024-01-30T12:00:00Z",
                "expires_at": "2025-01-30T12:00:00Z",
                "is_active": True
            }
        }
    )

class APIKey(APIKeyInDBBase):
    """API Key model representing an API key in the system"""
    pass

class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key"""
    pass
