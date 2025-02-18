from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.core.validators import validate_balance, validate_gpt_filter_prompt, validate_user_exists_by_id
from app.models.user import User
from app.schemas.users_servises import (
    UserBalanceRead,
    UserBalanceUpdate,
    UserGPTFilterPromptRead,
    UserGPTFilterPromptUpdate,
)

router = APIRouter()


@router.get(
    "/me/gpt-filter-prompt",
    response_model=UserGPTFilterPromptRead,
    status_code=status.HTTP_200_OK,
    summary="Get GPT Filter Prompt",
    description="Retrieves the current user's custom GPT filter prompt settings. This prompt is used to customize how GPT processes and filters responses.",
    responses={
        200: {"description": "Successfully retrieved GPT filter prompt"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this resource"}
    }
)
async def read_user_gpt_filter_prompt(
    current_user: User = Depends(deps.get_current_active_user),
) -> UserGPTFilterPromptRead:
    """
    Get current user's GPT filter prompt.
    
    This endpoint returns the custom GPT filter prompt configured for the authenticated user.
    The prompt is used to customize how GPT processes and analyzes responses.
    
    Returns:
        dict: Contains the current GPT filter prompt
    """
    return {"gpt_filter_prompt": current_user.gpt_filter_prompt}


@router.patch(
    "/me/gpt-filter-prompt",
    response_model=UserGPTFilterPromptRead,
    status_code=status.HTTP_200_OK,
    summary="Update GPT Filter Prompt",
    description="Updates the current user's GPT filter prompt. The new prompt must meet length requirements and security validations.",
    responses={
        200: {"description": "Successfully updated GPT filter prompt"},
        400: {"description": "Invalid prompt format or content"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to modify this resource"},
        422: {"description": "Validation error in prompt content"}
    }
)
async def update_user_gpt_filter_prompt(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    prompt_in: UserGPTFilterPromptUpdate,
) -> UserGPTFilterPromptRead:
    """
    Update current user's GPT filter prompt.
    
    This endpoint allows updating the custom GPT filter prompt for the authenticated user.
    The new prompt undergoes security validation and length checks before being saved.
    
    Args:
        db: Database session
        current_user: Currently authenticated user
        prompt_in: New prompt data
        
    Returns:
        dict: Contains the updated GPT filter prompt
    
    Raises:
        HTTPException: If prompt validation fails or user not found
    """
    validated_prompt = await validate_gpt_filter_prompt(prompt_in.gpt_filter_prompt)
    await validate_user_exists_by_id(db, current_user.id)
    
    updated_user = await crud.user.update_gpt_filter_prompt(
        db=db,
        user_id=current_user.id,
        gpt_filter_prompt=validated_prompt
    )
    return {"gpt_filter_prompt": updated_user.gpt_filter_prompt}


@router.get(
    "/me/balance",
    response_model=UserBalanceRead,
    status_code=status.HTTP_200_OK,
    summary="Get Current Balance",
    description="Retrieves the current user's balance in Russian Rubles (RUB).",
    responses={
        200: {"description": "Successfully retrieved balance"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this resource"}
    }
)
async def read_user_balance(
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
) -> UserBalanceRead:
    """
    Get current user's balance.
    
    This endpoint returns the current balance in Russian Rubles (RUB)
    for the authenticated user.
    
    Returns:
        dict: Contains the current balance in RUB
    """
    return {"balance_rub": current_user.balance_rub}


@router.patch(
    "/me/balance",
    response_model=UserBalanceRead,
    status_code=status.HTTP_200_OK,
    summary="Update Balance",
    description="Updates the current user's balance. The new balance must be non-negative.",
    responses={
        200: {"description": "Successfully updated balance"},
        400: {"description": "Invalid balance value"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to modify this resource"},
        422: {"description": "Validation error in balance value"}
    }
)
async def update_user_balance(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
    balance_in: Annotated[UserBalanceUpdate, Body(...)],
) -> UserBalanceRead:
    """
    Update current user's balance.
    
    This endpoint allows updating the balance for the authenticated user.
    The new balance must be non-negative and passes validation checks.
    
    Args:
        db: Database session
        current_user: Currently authenticated user
        balance_in: New balance data
        
    Returns:
        dict: Contains the updated balance
        
    Raises:
        HTTPException: If balance validation fails or user not found
    """
    await validate_balance(balance_in.balance_rub)
    await validate_user_exists_by_id(db, current_user.id)
    
    updated_user = await crud.user.update_balance(
        db=db,
        user_id=current_user.id,
        balance_rub=balance_in.balance_rub
    )
    return {"balance_rub": updated_user.balance_rub}
