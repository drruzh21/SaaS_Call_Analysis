from pydantic import BaseModel, Field
from app.ai.structured_output_models.score import Score


class CallAnalysisMetrics(BaseModel):
    """Model for detailed call analysis metrics"""

    # Contact establishment
    is_manager_established_contact_analysis: str = Field(
        description="Анализ приветствия, представления и обозначения цели звонка"
    )
    is_manager_established_contact: Score = Field(
        description="Оценка за установление контакта с клиентом (0-1)"
    )

    # Speech quality
    speech_quality_analysis: str = Field(
        description="Анализ четкости и разборчивости речи, отсутствия слов-паразитов"
    )
    speech_quality: Score = Field(
        description="Оценка за качество речи (0-1)"
    )

    # Initiative holding
    is_manager_holding_initiative_analysis: str = Field(
        description="Анализ управления диалогом и логики вопросов"
    )
    is_manager_holding_initiative: Score = Field(
        description="Оценка за удержание инициативы в разговоре (0-1)"
    )

    # Problem identification
    problem_identification_analysis: str = Field(
        description="Анализ выявления потребностей и болей клиента"
    )
    problem_identification: Score = Field(
        description="Оценка за выявление проблем клиента (0-1)"
    )

    # Product presentation
    product_presentation_analysis: str = Field(
        description="Анализ презентации решения с привязкой к болям клиента"
    )
    product_presentation: Score = Field(
        description="Оценка за презентацию продукта (0-1)"
    )

    # Expertise demonstration
    expertise_demonstration_analysis: str = Field(
        description="Анализ демонстрации экспертности в продукте и нише клиента"
    )
    expertise_demonstration: Score = Field(
        description="Оценка за демонстрацию экспертности (0-1)"
    )

    # Objection handling
    objection_handling_analysis: str = Field(
        description="Анализ работы с истинными и ложными возражениями"
    )
    objection_handling: Score = Field(
        description="Оценка за работу с возражениями (0-1)"
    )

    # Deal closing
    deal_closing_analysis: str = Field(
        description="Анализ подталкивания клиента к следующему шагу"
    )
    deal_closing: Score = Field(
        description="Оценка за закрытие сделки (0-1)"
    )

    # Contact verification
    contact_verification_analysis: str = Field(
        description="Анализ проверки контактных данных клиента"
    )
    contact_verification: Score = Field(
        description="Оценка за верификацию контактов (0-1)"
    )

    # Next step setting
    next_step_setting_analysis: str = Field(
        description="Анализ определения конкретного следующего шага и сроков"
    )
    next_step_setting: Score = Field(
        description="Оценка за определение следующего шага (0-1)"
    )

    # Tone of voice
    tone_of_voice_analysis: str = Field(
        description="Анализ тона голоса, эмоциональной вовлеченности и эмпатии менеджера"
    )
    tone_of_voice: Score = Field(
        description="Оценка за тон голоса и эмоциональную вовлеченность (0-1)"
    )

    # Final grade
    final_grade: Score = Field(
        description="Итоговая оценка за весь звонок (0-1)"
    )
