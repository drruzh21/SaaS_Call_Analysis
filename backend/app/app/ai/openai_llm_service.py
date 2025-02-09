from typing import Any, Type

from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import settings


class OpenAILLMService():
    """Service for interacting with OpenAI's LLM using beta.chat.completions.parse"""

    def __init__(
        self,
        response_format: Type[BaseModel],  # <--- Класс (тип) вашей Pydantic модели
        system_prompt: str,
        api_key: str = settings.OPENAI_API_KEY,
    ):
        """
        Initialize OpenAI LLM service

        Args:
            api_key: OpenAI API key
            response_format: Класс Pydantic-модели, в которую надо распарсить ответ
            system_prompt: Системный промпт для LLM
        """
        self.client = OpenAI(api_key=api_key)
        self.response_format = response_format
        self.system_prompt = system_prompt

    def get_completion(self, user_text: str) -> Any:
        """
        Get completion from OpenAI using .parse()
        Возвращаем Pydantic-модель (или отказ, если GPT не смог вернуть структуру).
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
            # Если модель успешно вернула JSON, который подходит под Pydantic-модель,
            # то message.parsed уже будет вашим объектом (экземпляром Pydantic).
            # Можно сразу вернуть в виде dict, если нужно:
            return message.parsed.model_dump()
        else:
            # Если GPT отказался или не смог вернуть нужный формат,
            # библиотека OpenAI положит причину в поле `refusal`.
            return message.refusal

