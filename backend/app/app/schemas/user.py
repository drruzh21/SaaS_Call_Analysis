from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing_extensions import Annotated

from app.core.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH


class UserLogin(BaseModel):
    """Schema for user login credentials."""
    username: EmailStr = Field(..., description="User's email address")
    password: Annotated[
        str, 
        StringConstraints(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    ] = Field(..., description="User's password")


# Shared properties
class UserBase(BaseModel):
    """Base user schema with shared properties."""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    email_validated: Optional[bool] = Field(False, description="Whether email is validated")
    is_active: Optional[bool] = Field(True, description="Whether user account is active")
    is_superuser: Optional[bool] = Field(False, description="Whether user has superuser privileges")
    full_name: Optional[str] = Field(None, description="User's full name")
    user_id: Optional[int] = Field(None, description="ID of user's company")
    gpt_filter_prompt: Optional[str] = Field(None, description="Custom GPT filter prompt")
    balance_rub: Optional[int] = Field(
        None, 
        description="User's balance in rubles",
        ge=0
    )
    role: Optional[str] = Field(
        "user",
        description="User's role in the system"
    )


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Schema for creating a new user."""
    email: EmailStr = Field(..., description="User's email address")
    password: Optional[Annotated[
        str, 
        StringConstraints(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    ]] = Field(None, description="User's password")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "full_name": "John Doe",
                "role": "user"
            }
        }
    )


# Properties to receive via API on update
class UserUpdate(UserBase):
    """Schema for updating an existing user."""
    original: Optional[Annotated[
        str, 
        StringConstraints(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    ]] = Field(None, description="Original password for verification")
    password: Optional[Annotated[
        str, 
        StringConstraints(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    ]] = Field(None, description="New password")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "full_name": "John Doe Updated",
                "original": "oldpassword123",
                "password": "newpassword123"
            }
        }
    )


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: Optional[UUID] = Field(None, description="User's unique identifier")
    hashed_password: Optional[str] = Field(None, description="Hashed password")
    totp_secret: Optional[str] = Field(None, description="TOTP secret key")
    created: Optional[datetime] = Field(None, description="Account creation timestamp")
    modified: Optional[datetime] = Field(None, description="Last modification timestamp")

    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """Schema for user responses via API."""
    hashed_password: Optional[str] = Field(default=None, alias="password")
    totp_secret: Optional[str] = Field(default=None, alias="totp")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "user",
                "balance_rub": 1000,
                "is_active": True,
                "email_validated": True
            }
        }
    )


class UserInDB(UserInDBBase):
    """Internal schema for user in database with sensitive fields."""
    hashed_password: Optional[str] = None
    totp_secret: Optional[str] = None
    totp_counter: Optional[int] = None
