from typing import Annotated, Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.validators import (
    validate_email, 
    validate_full_name, 
    validate_password, 
    validate_password_update, 
    validate_user_exists
)
from app.utilities import (
    send_new_account_email,
)

router = APIRouter()


@router.post("/", response_model=schemas.User)
async def create_user_profile(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    password: str = Body(..., description="User's password"),
    email: EmailStr = Body(..., description="User's email address"),
    full_name: str = Body(None, description="User's full name"),
) -> Any:
    """
    Create new user without the need to be logged in.
    
    Args:
        password: User's password
        email: User's email address
        full_name: Optional user's full name
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Validate input data
    await validate_email(email)
    await validate_password(password)
    await validate_full_name(full_name)
    await validate_user_exists(db, email)

    user_in = schemas.UserCreate(
        password=password,
        email=email,
        full_name=full_name,
        email_validated=False,
        is_active=True
    )
    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.put("/", response_model=schemas.User)
async def update_user(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    obj_in: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """
    Update current user's profile.
    
    Args:
        obj_in: User update data
        current_user: Current authenticated user
        
    Returns:
        Updated user object
        
    Raises:
        HTTPException: If validation fails
    """
    # Validate password update if requested
    if obj_in.password is not None:
        await validate_password_update(
            db, 
            current_user, 
            obj_in.original, 
            obj_in.password
        )

    # Validate other fields if provided
    if obj_in.email is not None:
        await validate_email(obj_in.email)
        
    if obj_in.full_name is not None:
        await validate_full_name(obj_in.full_name)

    user = await crud.user.update(db, db_obj=current_user, obj_in=obj_in)
    return user


@router.get("/me", response_model=schemas.User)
async def read_user(
    *,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """
    Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user object
    """
    return current_user


@router.get("/all", response_model=List[schemas.User])
async def read_all_users(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    page: int = 0,
    current_user: Annotated[models.User, Depends(deps.get_current_active_superuser)],
) -> Any:
    """
    Retrieve all users (superuser only).
    
    Args:
        page: Page number for pagination
        current_user: Current authenticated superuser
        
    Returns:
        List of user objects
    """
    users = await crud.user.get_multi(db, page=page)
    return users


@router.post("/totp/new", response_model=schemas.NewTOTP)
async def request_new_totp(
    *,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> Any:
    """
    Request new TOTP keys for two-factor authentication.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        New TOTP configuration
    """
    return security.generate_totp()


@router.put("/toggle", response_model=schemas.User)
async def toggle_state(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    user_in: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_superuser)],
) -> Any:
    """
    Toggle user state (superuser only).
    
    Args:
        user_in: User update data with email and new state
        current_user: Current authenticated superuser
        
    Returns:
        Updated user object
        
    Raises:
        HTTPException: If user not found
    """
    user = await crud.user.toggle_user_state(db=db, obj_in=user_in)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system",
        )
    return user


@router.post("/create", response_model=schemas.User)
async def create_user(
    *,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    user_in: schemas.UserCreate,
    current_user: Annotated[models.User, Depends(deps.get_current_active_superuser)],
) -> Any:
    """
    Create new user (superuser only).
    
    Args:
        user_in: User creation data
        current_user: Current authenticated superuser
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If user already exists
    """
    await validate_user_exists(db, user_in.email)
    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.get("/data", response_model=schemas.Msg)
async def data_endpoint() -> Any:
    """
    Test current endpoint.
    """
    return {"msg": "data was sent successfully."}

@router.get("/tester", response_model=schemas.Msg)
async def test_endpoint() -> Any:
    """
    Test current endpoint.
    """
    return ({"msg": "Message returned ok. Definitely ok."})
