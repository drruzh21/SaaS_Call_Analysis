import logging
import re
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.core.constants import (
    MAX_FULL_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_EMAIL_LENGTH,
    FULL_NAME_REGEX,
    PASSWORD_UPPERCASE_REGEX,
    PASSWORD_LOWERCASE_REGEX,
    PASSWORD_DIGIT_REGEX,
)

# Configure logging
logger = logging.getLogger(__name__)


async def validate_user_exists(db: AsyncSession, email: str) -> None:
    """
    Validate that a user with the given email already exists.
    
    Args:
        db: Database session
        email: Email to check
        
    Raises:
        HTTPException: If user with email already exists
    """
    user = await crud.user.get_by_email(db, email=email)
    if user:
        logger.warning(f"Attempted to create user with existing email: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )


async def validate_user_not_exists(db: AsyncSession, email: str) -> models.User:
    """
    Validate that a user with the given email exists.
    
    Args:
        db: Database session
        email: Email to check
        
    Returns:
        User object if found
        
    Raises:
        HTTPException: If user not found
    """
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        logger.warning(f"Attempted to access non-existent user: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


async def validate_email(email: EmailStr) -> None:
    """
    Validate email format and restrictions.
    
    Args:
        email: Email to validate
        
    Raises:
        HTTPException: If email is invalid
    """
    # Basic email validation (pydantic's EmailStr already does format validation)
    if not email or len(email) < MIN_EMAIL_LENGTH:
        logger.warning(f"Invalid email length: {email}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Email must be at least {MIN_EMAIL_LENGTH} characters long"
        )


async def validate_password(
    password: str,
    check_strength: bool = True
) -> None:
    """
    Validate password strength and format.
    
    Args:
        password: Password to validate
        check_strength: Whether to check password strength
        
    Raises:
        HTTPException: If password is invalid
    """
    if not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is required"
        )
        
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        )
        
    if len(password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at most {MAX_PASSWORD_LENGTH} characters long"
        )
    
    if check_strength:
        # Check for at least one uppercase letter
        if not re.search(PASSWORD_UPPERCASE_REGEX, password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one uppercase letter"
            )
            
        # Check for at least one lowercase letter
        if not re.search(PASSWORD_LOWERCASE_REGEX, password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one lowercase letter"
            )
            
        # Check for at least one digit
        if not re.search(PASSWORD_DIGIT_REGEX, password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one number"
            )


async def validate_full_name(full_name: Optional[str]) -> None:
    """
    Validate full name format and length.
    
    Args:
        full_name: Full name to validate
        
    Raises:
        HTTPException: If full name is invalid
    """
    if full_name is None:
        return
        
    if len(full_name) > MAX_FULL_NAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Full name must be at most {MAX_FULL_NAME_LENGTH} characters long"
        )
        
    if not re.match(FULL_NAME_REGEX, full_name):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name can only contain letters, spaces, hyphens, and apostrophes"
        )


async def validate_password_update(
    db: AsyncSession,
    current_user: models.User,
    original_password: Optional[str],
    new_password: str
) -> None:
    """
    Validate password update request.
    
    Args:
        db: Database session
        current_user: Current user object
        original_password: Original password for verification
        new_password: New password to set
        
    Raises:
        HTTPException: If validation fails
    """
    if not original_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original password is required to set new password"
        )
        
    if not await crud.user.authenticate(
        db, email=current_user.email, password=original_password
    ):
        logger.warning(f"Failed password update attempt for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original password is incorrect"
        )
        
    await validate_password(new_password)
