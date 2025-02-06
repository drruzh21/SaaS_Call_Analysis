from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator
from typing_extensions import Annotated

from app.core.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from app.core.validators import validate_email, validate_full_name, validate_password


class UserLogin(BaseModel):
    username: str
    password: str


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    email_validated: Optional[bool] = False
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: Optional[Annotated[str, StringConstraints(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)]] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return validate_email(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password(v)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if v:
            return validate_full_name(v)
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    original: Optional[Annotated[str, StringConstraints(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)]] = None
    password: Optional[Annotated[str, StringConstraints(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)]] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v:
            return validate_email(v)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v:
            return validate_password(v)
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if v:
            return validate_full_name(v)
        return v


class UserInDBBase(UserBase):
    id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


# Additional properties to return via API
class User(UserInDBBase):
    hashed_password: bool = Field(default=False, alias="password")
    totp_secret: bool = Field(default=False, alias="totp")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("hashed_password", mode="before")
    @classmethod
    def evaluate_hashed_password(cls, hashed_password):
        if hashed_password:
            return True
        return False

    @field_validator("totp_secret", mode="before")
    @classmethod
    def evaluate_totp_secret(cls, totp_secret):
        if totp_secret:
            return True
        return False


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: Optional[str] = None
    totp_secret: Optional[str] = None
    totp_counter: Optional[int] = None
