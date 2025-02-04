from app.ai.ai_agents.i_gpt_analyzer import IGptAnalyzer
from app.ai.structured_output_models.call_overall_model import CallOverallAnalysis
from app.ai.prompts.overall_analyzer_prompt import OVERALL_ANALYZER_PROMPT
from app.ai.openai_llm_service import OpenAILLMService


class CallOverallAnalyzer(IGptAnalyzer[CallOverallAnalysis]):
    """GPT agent for providing overall call analysis and recommendations"""
    
    def __init__(self, api_key: str):
        """
        Initialize analyzer
        
        Args:
            api_key: OpenAI API key
        """
        self.llm_service = OpenAILLMService(
            api_key=api_key,
            response_format=CallOverallAnalysis,
            system_prompt=OVERALL_ANALYZER_PROMPT
        )
    
    def analyze(self, call_text: str) -> CallOverallAnalysis:
        """
        Analyze call text to provide overall analysis and recommendations
        
        Args:
            call_text: The transcribed call text
            
        Returns:
            CallOverallAnalysis containing analysis and recommendations
        """
        result = self.llm_service.get_completion(
            f"Проведите общий анализ следующего телефонного разговора и предоставьте рекомендации:\n\n{call_text}"
        )
        return CallOverallAnalysis.parse_obj(result)
