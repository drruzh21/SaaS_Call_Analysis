"""AI agent for overall call analysis."""

import logging
from typing import Any

from app.ai.ai_agents.i_gpt_analyzer import IGptAnalyzer
from app.ai.openai_llm_service import OpenAILLMService
from app.ai.prompts.overall_analyzer_prompt import OVERALL_ANALYZER_PROMPT
from app.ai.structured_output_models.call_overall_model import CallOverallAnalysis

logger = logging.getLogger(__name__)


class CallOverallAnalyzer(IGptAnalyzer[CallOverallAnalysis]):
    """GPT agent for providing overall call analysis and recommendations"""
    
    def __init__(self, api_key: str | None = None):
        # Get API key from settings if not provided
        if api_key is None:
            from app.core.config import settings
            api_key = settings.OPENAI_API_KEY
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
        logger.info("Starting overall call analysis")
        logger.debug(f"Analyzing call text of length: {len(call_text)}")
        
        try:
            # Get analysis from GPT
            logger.debug("Sending request to GPT")
            result = self.llm_service.get_completion(
                f"Проведите общий анализ следующего телефонного разговора и предоставьте рекомендации:\n\n{call_text}"
            )
            
            # Validate response
            self._validate_response(result)
            
            logger.info("Overall call analysis completed successfully")
            return CallOverallAnalysis.parse_obj(result)
            
        except Exception as e:
            logger.error(f"Error during overall analysis: {str(e)}", exc_info=True)
            raise
            
    def _validate_response(self, response: CallOverallAnalysis):
        """Validate that the response contains required fields.
        
        Args:
            response: Analysis response to validate
            
        Raises:
            ValueError: If required fields are missing or empty
        """
        logger.debug("Validating overall analysis response")
        
        if not response.overall_analysis:
            error_msg = "Overall analysis cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not response.recommendations_how_to_work_with_client:
            error_msg = "Recommendations cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
