from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import MAX_API_NAME_LENGTH


class APIKeyBase(BaseModel):
    """
    Base API Key schema with common non-sensitive attributes.
    
    This schema serves as the foundation for all API key related schemas,
    containing only the most basic, non-sensitive fields that are common
    across all API key operations.
    
    Attributes:
        name: Human-readable identifier for the API key. Must be unique per user
              and follow length constraints.
    """
    name: str = Field(
        title="API Key Name",
        description="Human-readable identifier for the API key",
        min_length=1,
        max_length=MAX_API_NAME_LENGTH,
        example="Production API Key"
    )

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )


class APIKeyCreate(APIKeyBase):
    """
    Schema for API key creation requests.
    
    This schema defines the fields that can be set when creating a new API key.
    Inherits the name field from APIKeyBase and adds the is_active flag.
    
    Attributes:
        name: Inherited from APIKeyBase
        is_active: Flag indicating whether the key should be active upon creation
    """
    is_active: bool = Field(
        default=True,
        title="Initial Active Status",
        description="Whether the API key should be active upon creation"
    )


class APIKeyUpdate(APIKeyCreate):
    """
    Schema for API key update operations.
    
    This schema defines which fields can be modified after an API key has been created.
    All fields are optional to support partial updates. Inherits from APIKeyCreate
    but makes all fields optional.
    
    Attributes:
        name: Optional new name for the API key
        is_active: Optional flag to activate/deactivate the key
    """
    name: Optional[str] = Field(
        default=None,
        title="Updated API Key Name",
        description="New name for the API key. Leave empty to keep current name",
        example="Updated API Key Name"
    )
    is_active: Optional[bool] = Field(
        default=None,
        title="Updated Active Status",
        description="New active status for the API key. Leave empty to keep current status",
        example=True
    )


class APIKeyResponse(APIKeyCreate):
    """
    API Key response schema for external API communication.
    
    This schema represents the API key data that is returned to clients.
    It includes all public fields but excludes sensitive information like the key hash.
    The actual key value is only included in the response when a new key is created.
    
    Attributes:
        id: Unique identifier for the API key
        key: The actual API key value (only present in creation response)
        created_at: Timestamp when the key was created
        expires_at: Optional timestamp when the key will expire
        name: Inherited from APIKeyBase
        is_active: Inherited from APIKeyCreate
    """
    id: UUID
    key: Optional[str] = Field(
        default=None,
        description="API key value. Only shown once upon creation"
    )
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Production API Key",
                "created_at": "2024-01-30T12:00:00Z",
                "expires_at": "2025-01-30T12:00:00Z",
                "is_active": True
            }
        }
    )


class APIKeyInDB(APIKeyResponse):
    """
    Complete API key schema as stored in database.
    
    This schema represents the full API key record as stored in the database.
    It includes all fields from APIKeyResponse plus additional fields that are
    only used internally and should never be exposed through the API.
    
    Attributes:
        key_hash: Hashed version of the API key for secure storage
        user_id: ID of the user who owns this API key
        id: Inherited from APIKeyResponse
        created_at: Inherited from APIKeyResponse
        expires_at: Inherited from APIKeyResponse
        name: Inherited from APIKeyBase
        is_active: Inherited from APIKeyCreate
    """
    key_hash: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
