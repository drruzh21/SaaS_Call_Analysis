"""Model for objections analysis output."""

from typing import List

from pydantic import BaseModel, Field

from app.ai.enums.objection_type import ObjectionType


class ObjectionsAnalysis(BaseModel):
    """Model for structured output of objections analysis."""
    
    analysis: str = Field(
        description="Подробный анализ возражений клиента в диалоге. Включает в себя: "
                   "1. Описание контекста, в котором возникло каждое возражение "
                   "2. Анализ причин возникновения возражений "
                   "3. Выявление явных и скрытых возражений клиента"
    )
    
    objections: List[ObjectionType] = Field(
        description="Список конкретных типов возражений, которые были выявлены в разговоре"
    )
