import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.validators import validate_api_key_ownership, validate_api_key_for_operation

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "",
    response_model=schemas.APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New API Key",
    description="Creates a new API key for the authenticated user. The key name must be unique for the user.",
    responses={
        201: {"description": "API key created successfully"},
        400: {"description": "Invalid input"},
        409: {"description": "API key name already exists"}
    }
)
async def create_api_key(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    api_key_in: Annotated[schemas.APIKeyCreate, Body(...)],
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)]
) -> schemas.APIKeyResponse:
    """
    Create a new API key for the authenticated user.
    
    This endpoint generates a new API key with the specified name. The key name must
    be unique for the user. The actual API key value is only returned once upon creation
    and cannot be retrieved later for security reasons.
    
    Args:
        db: Async database session for database operations
        api_key_in: API key creation data containing name and optional active status
        current_user: Currently authenticated user requesting the key creation
        
    Returns:
        APIKeyResponse: Created API key data including the one-time visible key value
        
    Raises:
        HTTPException: 
            - 400: If the input data is invalid (e.g., name too short/long)
            - 409: If an API key with the same name already exists for this user
            - 401: If user is not authenticated
            - 403: If user is not active
    """
    logger.info(f"User {current_user.email} attempting to create API key named: {api_key_in.name}")
    
    existing_key = await crud.api_key.get_by_name(
        db=db,
        name=api_key_in.name,
        user_id=current_user.id
    )
    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="API key with this name already exists"
        )
    
    api_key, original_key = await crud.api_key.create(
        db=db,
        user_id=current_user.id,
        obj_in=api_key_in
    )
    
    response_data = {
        "id": api_key.id,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "is_active": api_key.is_active,
        "key": original_key
    }
    
    response = schemas.APIKeyResponse.model_validate(response_data)
    logger.info(f"API key created successfully for user {current_user.email}")
    return response

@router.put(
    "/{name}",
    response_model=schemas.APIKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update API Key",
    description="Updates an existing API key's name or active status. Only the key owner can perform this operation.",
    responses={
        200: {"description": "API key updated successfully"},
        404: {"description": "API key not found"},
        403: {"description": "Not enough permissions"}
    }
)
async def update_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    name: str,
    api_key_in: schemas.APIKeyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> schemas.APIKeyResponse:
    """
    Update an existing API key.
    """
    logger.info(f"User {current_user.email} attempting to update API key named: {name}")
    
    api_key = await validate_api_key_for_operation(
        db=db,
        name=name,
        user_id=current_user.id,
        operation="update"
    )
    
    await validate_api_key_ownership(api_key, current_user.id)
    
    updated_api_key = await crud.api_key.update(
        db=db,
        db_obj=api_key,
        obj_in=api_key_in,
        user_id=current_user.id
    )
    
    logger.info(f"API key {name} updated successfully by user {current_user.email}")
    return schemas.APIKeyResponse.model_validate(updated_api_key)

@router.get(
    "/me",
    response_model=schemas.PaginatedList[schemas.APIKeyResponse],
    status_code=status.HTTP_200_OK,
    summary="List User's API Keys",
    description="Retrieves all API keys belonging to the authenticated user with pagination support.",
    responses={
        200: {"description": "List of API keys retrieved successfully"}
    }
)
async def read_api_keys(
    pagination: Annotated[schemas.PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)]
) -> schemas.PaginatedList[schemas.APIKeyResponse]:
    """
    Retrieve all API keys belonging to the current user.
    
    This endpoint returns a paginated list of all API keys owned by the
    authenticated user. The keys are sorted by creation date in descending order.
    Sensitive information like key hashes is excluded from the response.
    
    Args:
        pagination: Pagination parameters (skip and limit)
        db: Async database session for database operations
        current_user: Currently authenticated user whose keys are being retrieved
        
    Returns:
        PaginatedList[APIKeyResponse]: Paginated list of API keys with total count
        
    Raises:
        HTTPException:
            - 401: If user is not authenticated
            - 403: If user is not active
    """
    logger.info(f"Fetching API keys for user {current_user.email} with skip {pagination.skip} and limit {pagination.limit}")
    total = await crud.api_key.get_active_key_count(
        db=db,
        user_id=current_user.id
    )
    items = await crud.api_key.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        skip=pagination.skip,
        limit=pagination.limit
    )

    page = (pagination.skip // pagination.limit) + 1
    pages = (total + pagination.limit - 1) // pagination.limit
    has_next = page < pages
    has_prev = page > 1
    
    return schemas.PaginatedList(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        page=page,
        pages=pages,
        per_page=pagination.limit,
        has_next=has_next,
        has_prev=has_prev
    )

@router.get(
    "/{name}",
    response_model=schemas.APIKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get API Key Details",
    description="Retrieves detailed information about a specific API key by its name.",
    responses={
        200: {"description": "API key details retrieved successfully"},
        404: {"description": "API key not found"}
    }
)
async def read_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    name: str,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> schemas.APIKeyResponse:
    api_key = await validate_api_key_for_operation(
        db=db,
        name=name,
        user_id=current_user.id,
        operation="access"
    )
    return schemas.APIKeyResponse.model_validate(api_key)

@router.delete(
    "/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete API Key",
    description="Deletes an existing API key. Only the key owner can perform this operation.",
    responses={
        204: {"description": "API key deleted successfully"},
        404: {"description": "API key not found"},
        403: {"description": "Not enough permissions"}
    }
)
async def delete_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    name: str,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> None:
    api_key = await validate_api_key_for_operation(
        db=db,
        name=name,
        user_id=current_user.id,
        operation="delete"
    )
    await crud.api_key.remove(db, db_obj=api_key)
    return None
