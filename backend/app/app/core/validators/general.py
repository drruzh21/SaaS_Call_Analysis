import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.core.constants import EMAIL_REGEX, MAX_EMAIL_LENGTH, MAX_FULL_NAME_LENGTH, MIN_PASSWORD_LENGTH, SQL_PATTERNS

async def validate_gpt_filter_prompt(prompt: Optional[str]) -> Optional[str]:
    if prompt is None:
        return None

    sanitized_prompt = prompt.replace('\x00', '')
    sanitized_prompt = ' '.join(sanitized_prompt.split())
    sanitized_prompt = ''.join(char for char in sanitized_prompt if char.isprintable())
    
    combined_pattern = re.compile('|'.join(SQL_PATTERNS), re.IGNORECASE)
    matches = combined_pattern.finditer(sanitized_prompt)
    found_patterns = list(matches)
    
    if found_patterns:
        suspicious_patterns = [sanitized_prompt[m.start():m.end()] for m in found_patterns]
        raise ValueError(
            "Potentially dangerous SQL patterns detected: " + 
            ", ".join(f"'{pattern}'" for pattern in suspicious_patterns)
        )
        
    return sanitized_prompt

async def validate_email(email: str) -> str:
    if len(email) > MAX_EMAIL_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email cannot be longer than {MAX_EMAIL_LENGTH} characters"
        )
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    return email

async def validate_password(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    return password

async def validate_full_name(full_name: Optional[str]) -> Optional[str]:
    if full_name and len(full_name) > MAX_FULL_NAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Full name cannot be longer than {MAX_FULL_NAME_LENGTH} characters"
        )
    return full_name

async def validate_expiry(expires_at: Optional[datetime]) -> Optional[datetime]:
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at and expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expiration date cannot be in the past"
        )
    return expires_at
