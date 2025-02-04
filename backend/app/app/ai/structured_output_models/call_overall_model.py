from pydantic import BaseModel, Field


class CallOverallAnalysis(BaseModel):
    """Model for overall call analysis and recommendations"""
    
    overall_analysis: str = Field(
        description="Общий анализ звонка, включая основные выводы и наблюдения"
    )
    recommendations_how_to_work_with_client: str = Field(
        description="Подробные рекомендации по улучшению работы с данным клиентом"
    )
