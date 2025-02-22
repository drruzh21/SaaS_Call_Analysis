from typing import Optional

from pydantic import BaseModel, Field

from app.core.constants import MAX_GPT_FILTER_PROMPT_LENGTH, MIN_GPT_FILTER_PROMPT_LENGTH


class UserGPTFilterPromptUpdate(BaseModel):
    """
    Schema for updating user's GPT filter prompt.
    
    This schema is used when updating a user's custom GPT filter prompt.
    The prompt must meet length requirements and not contain malicious content.
    """
    gpt_filter_prompt: Optional[str] = Field(
        default=None,
        title="GPT Filter Prompt",
        description="Custom prompt for filtering GPT responses. Must be between MIN and MAX length and not contain SQL injections",
        max_length=MAX_GPT_FILTER_PROMPT_LENGTH,
        min_length=MIN_GPT_FILTER_PROMPT_LENGTH,
        example="Analyze this conversation and provide insights about..."
    )


class UserGPTFilterPromptRead(UserGPTFilterPromptUpdate):
    """
    Schema for reading user's GPT filter prompt.
    
    This schema represents the GPT filter prompt data that is returned
    to the client when reading the current prompt settings.
    """
    gpt_filter_prompt: str = Field(
        title="Current GPT Filter Prompt",
        description="The user's currently active GPT filter prompt",
        example="Analyze this conversation and provide insights about..."
    )


class UserBalanceUpdate(BaseModel):
    """
    Schema for updating user's balance.
    
    This schema is used when modifying a user's balance through payment
    operations. Balance cannot be negative.
    """
    balance_rub: Optional[int] = Field(
        title="Balance Amount",
        description="User's balance in Russian Rubles (RUB). Must be non-negative",
        ge=0,
        example=1000
    )


class UserBalanceRead(UserBalanceUpdate):
    """
    Schema for reading user's balance.
    
    This schema represents the balance data that is returned to the
    client when querying the current balance.
    """
    balance_rub: int = Field(
        title="Current Balance",
        description="User's current balance in Russian Rubles (RUB)",
        ge=0,
        example=1000
    )
