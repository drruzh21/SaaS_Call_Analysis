from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.user_gpt_filter_prompt import (
    UserGPTFilterPromptRead,
    UserGPTFilterPromptUpdate,
)
from app.core.validators import validate_gpt_filter_prompt, validate_user_exists_by_id

router = APIRouter()


@router.get(
    "/me/gpt-filter-prompt",
    response_model=UserGPTFilterPromptRead,
    status_code=status.HTTP_200_OK,
)
async def read_user_gpt_filter_prompt(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's GPT filter prompt.
    """
    return {"gpt_filter_prompt": current_user.gpt_filter_prompt}


@router.patch(
    "/me/gpt-filter-prompt",
    response_model=UserGPTFilterPromptRead,
    status_code=status.HTTP_200_OK,
)
async def update_user_gpt_filter_prompt(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    prompt_in: UserGPTFilterPromptUpdate,
) -> Any:
    """
    Update current user's GPT filter prompt.
    """
    await validate_gpt_filter_prompt(prompt_in.gpt_filter_prompt)
    
    await validate_user_exists_by_id(db, current_user.id)
    
    updated_user = await crud.user.update_gpt_filter_prompt(
        db=db,
        user_id=current_user.id,
        gpt_filter_prompt=prompt_in.gpt_filter_prompt
    )
    return {"gpt_filter_prompt": updated_user.gpt_filter_prompt}
