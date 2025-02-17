from typing import Annotated, Any, Optional
import logging
from fastapi import APIRouter, Body, Depends, Path, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.constants import MAX_API_NAME_LENGTH, MIN_API_NAME_LENGTH
from app.core.validators import validate_api_key_exists_by_name, validate_api_key_ownership

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
    api_key, original_key = await crud.api_key.create(
        db=db,
        user_id=current_user.id,
        obj_in=api_key_in
    )
    response = schemas.APIKeyResponse.model_validate(api_key)
    response['key'] = original_key
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
    name: str = Path(..., min_length=MIN_API_NAME_LENGTH, max_length=MAX_API_NAME_LENGTH),
    api_key_in: schemas.APIKeyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Optional[schemas.APIKeyResponse]:
    """
    Update an existing API key's properties.
    
    This endpoint allows modifying an API key's name or active status.
    Only the key owner can perform this operation, and only certain fields
    can be modified for security reasons.
    
    Args:
        db: Async database session for database operations
        name: Current name of the API key to update
        api_key_in: Update data containing new name and/or active status
        current_user: Currently authenticated user requesting the update
        
    Returns:
        APIKeyResponse: Updated API key data
        
    Raises:
        HTTPException:
            - 404: If API key with given name doesn't exist
            - 403: If user doesn't own the API key
            - 401: If user is not authenticated
            - 400: If new name is invalid or already exists
    """
    logger.info(f"User {current_user.email} attempting to update API key named: {name}")
    
    # Validate the API key exists and is owned by the current user
    api_key = await validate_api_key_exists_by_name(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    # Check if the API key name is being changed and validate uniqueness
    if api_key_in.name and api_key_in.name != name:
        existing_key = await crud.api_key.get_by_name(
            db=db,
            name=api_key_in.name,
            user_id=current_user.id
        )
        if existing_key:
            logger.warning(f"API key with name {api_key_in.name} already exists for user {current_user.email}")
            raise HTTPException(
                status_code=400,
                detail="API key with this name already exists"
            )
    
    updated_api_key = await crud.api_key.update(
        db=db,
        db_obj=api_key,
        obj_in=api_key_in
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
    return schemas.PaginatedList(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
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
) -> Optional[schemas.APIKeyResponse]:
    """
    Retrieve detailed information about a specific API key.
    
    This endpoint returns detailed information about an API key identified by its name.
    Only the key owner can access this information. Sensitive data like the key hash
    is excluded from the response.
    
    Args:
        db: Async database session for database operations
        name: Name of the API key to retrieve
        current_user: Currently authenticated user requesting the key details
        
    Returns:
        APIKeyResponse: API key details excluding sensitive information
        
    Raises:
        HTTPException:
            - 404: If API key with given name doesn't exist
            - 403: If user doesn't own the API key
            - 401: If user is not authenticated
    """
    logger.info(f"User {current_user.email} requested details for API key: {name}")
    api_key = await validate_api_key_exists_by_name(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    return schemas.APIKeyResponse.model_validate(api_key)

@router.delete(
    "/{name}",
    response_model=schemas.APIKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete API Key",
    description="Permanently deletes an API key. This action cannot be undone.",
    responses={
        200: {"description": "API key deleted successfully"},
        404: {"description": "API key not found"},
        403: {"description": "Not enough permissions"}
    }
)
async def delete_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    name: str,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Optional[schemas.APIKeyResponse]:
    """
    Permanently delete an API key.
    
    This endpoint permanently deletes an API key identified by its name.
    Only the key owner can perform this operation. This action cannot be undone,
    and any services using this key will need to be updated.
    
    Args:
        db: Async database session for database operations
        name: Name of the API key to delete
        current_user: Currently authenticated user requesting the deletion
        
    Returns:
        APIKeyResponse: Deleted API key data
        
    Raises:
        HTTPException:
            - 404: If API key with given name doesn't exist
            - 403: If user doesn't own the API key
            - 401: If user is not authenticated
    """
    logger.info(f"User {current_user.email} attempting to delete API key named: {name}")
    api_key = await validate_api_key_exists_by_name(db, name, current_user.id)
    await validate_api_key_ownership(api_key, current_user.id)
    
    deleted_api_key = await crud.api_key.remove(db=db, db_obj=api_key)
    
    logger.info(f"API key {name} deleted successfully by user {current_user.email}")
    return schemas.APIKeyResponse.model_validate(deleted_api_key)