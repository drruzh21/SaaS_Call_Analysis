from typing import Any, Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import settings

T = TypeVar('T', bound=BaseModel)

class OpenAILLMService:
    """Service for interacting with OpenAI's LLM using beta.chat.completions.parse"""

    def __init__(
        self,
        api_key: str,
        response_format: Type[T],
        system_prompt: str
    ):
        """Initialize service with API key and response format.
        
        Args:
            api_key: OpenAI API key
            response_format: Expected response format (Pydantic model)
            system_prompt: System prompt for GPT
        """
        self.client = OpenAI(api_key=api_key)
        self.response_format = response_format
        self.system_prompt = system_prompt

    def get_completion(self, user_text: str) -> T:
        """Get completion from OpenAI using .parse()
        
        Args:
            user_text: User's input text
            
        Returns:
            Pydantic model of type T
            
        Raises:
            ValueError: If GPT refuses or fails to return the expected format
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_text},
        ]

        # Вызываем beta.chat.completions.parse и передаём
        # именно self.response_format как тип, а не type(self.response_format).
        completion = self.client.beta.chat.completions.parse(
            model=settings.GPT_MODEL,
            messages=messages,
            response_format=self.response_format,
            temperature=0
        )

        # См. официальную документацию: результат модели (структурированный)
        # будет в completion.choices[0].message.parsed
        message = completion.choices[0].message
        if message.parsed:
            # Возвращаем Pydantic модель напрямую
            return message.parsed
        else:
            # Если GPT отказался или не смог вернуть нужный формат,
            # библиотека OpenAI положит причину в поле `refusal`.
            raise ValueError(f"GPT refused to provide response in expected format: {message.refusal}")

