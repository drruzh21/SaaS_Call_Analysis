from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIKeyBase(BaseModel):
    """Base API Key schema with common attributes."""
    name: str = Field(
        default="",
        description="Name of the API key for identification purposes"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this API key is active"
    )


class APIKeyCreate(BaseModel):
    """Schema for creating a new API key. Only name can be set during creation."""
    name: str = Field(
        description="Name of the API key for identification purposes"
    )


class APIKeyUpdate(BaseModel):
    """Schema for updating an API key. Only name and is_active can be modified."""
    name: Optional[str] = Field(
        default=None,
        description="Name of the API key for identification purposes"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether this API key is active"
    )


class APIKeyInDBBase(APIKeyBase):
    """Base schema for API keys as stored in DB, including all fields."""
    id: UUID
    key: str
    user_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(
        default=None,
        description="When this API key expires. If null, the key never expires"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "key": "sk_test_abc123def456ghi789jkl",
                "name": "Production API Key",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2024-01-30T12:00:00Z",
                "expires_at": None,
                "is_active": True
            }
        }
    )


class APIKey(APIKeyInDBBase):
    """API Key model representing an API key in the system."""
    pass
