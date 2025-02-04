"""AI agent for analyzing objections in sales calls."""

from app.ai.ai_agents.i_gpt_analyzer import IGptAnalyzer
from app.ai.prompts.objections_analyzer_prompt import OBJECTIONS_ANALYZER_PROMPT
from app.ai.structured_output_models.objections_analysis_model import ObjectionsAnalysis
from app.ai.openai_llm_service import OpenAILLMService


class ObjectionsAnalyzer(IGptAnalyzer[ObjectionsAnalysis]):
    """AI agent that analyzes objections in sales calls.
    
    This agent identifies specific types of objections that occurred during the call
    and provides detailed analysis of how they were handled.
    """
    
    def __init__(self, api_key: str):
        """Initialize the analyzer with OpenAI API key.
        
        Args:
            api_key: OpenAI API key for GPT access
        """
        self._llm_service = OpenAILLMService(
            api_key=api_key,
            response_format=ObjectionsAnalysis,
            system_prompt=OBJECTIONS_ANALYZER_PROMPT
        )
    
    async def analyze(self, call_text: str) -> ObjectionsAnalysis:
        """Analyze the call text to identify and classify objections.
        
        Args:
            call_text: The text transcript of the call to analyze
            
        Returns:
            ObjectionsAnalysis containing both detailed analysis and list of objection types
        """
        return await self._llm_service.get_structured_response(call_text)
