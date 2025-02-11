from typing import Optional

from pydantic import BaseModel, Field

from app.core.constants import (
    MAX_GPT_FILTER_PROMPT_LENGTH,
    MIN_GPT_FILTER_PROMPT_LENGTH,
)


class UserGPTFilterPromptUpdate(BaseModel):
    """Schema for updating user's GPT filter prompt."""
    gpt_filter_prompt: Optional[str] = Field(
        default=None,
        description="User's custom GPT filter prompt",
        max_length=MAX_GPT_FILTER_PROMPT_LENGTH,
        min_length=MIN_GPT_FILTER_PROMPT_LENGTH,
    )


class UserGPTFilterPromptRead(UserGPTFilterPromptUpdate):
    """Schema for reading user's GPT filter prompt."""
    gpt_filter_prompt: str = Field(
        description="User's custom GPT filter prompt",
    )
