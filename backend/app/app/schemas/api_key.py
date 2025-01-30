from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, constr, field_validator
from uuid import UUID

class APIKeyBase(BaseModel):
    expires_at: Optional[datetime] = Field(
        default=None,
        description="When this API key expires. If null, the key never expires"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this API key is active"
    )

class APIKeyUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    @field_validator("expires_at")
    def validate_expiry(cls, v):
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Expiry date cannot be in the past")
        return v

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
    """
    API Key model that represents an API key in the system.
    Contains all the fields necessary to identify and validate an API key.
    """
    pass