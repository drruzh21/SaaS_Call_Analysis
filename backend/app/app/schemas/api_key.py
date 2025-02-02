from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID

class APIKeyBase(BaseModel):
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Когда этот API ключ истекает. Если null, ключ никогда не истекает"
    )
    is_active: bool = Field(
        default=True,
        description="Активен ли этот API ключ"
    )

    @field_validator("expires_at")
    def validate_expiry(cls, v):
        if v and v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)  # Делаем datetime "aware", если он "naive"
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Дата истечения не может быть в прошлом")
        return v

class APIKeyUpdate(APIKeyBase):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

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
    """Модель API ключа, представляющая API ключ в системе"""
    pass

class APIKeyCreate(APIKeyBase):
    """Схема для создания нового API ключа"""
    pass
