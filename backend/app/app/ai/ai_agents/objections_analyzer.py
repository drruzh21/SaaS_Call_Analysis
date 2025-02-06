"""AI agent for analyzing objections in sales calls."""

import logging
from typing import Any

from app.ai.ai_agents.i_gpt_analyzer import IGptAnalyzer
from app.ai.openai_llm_service import OpenAILLMService
from app.ai.prompts.objections_analyzer_prompt import OBJECTIONS_ANALYZER_PROMPT
from app.ai.structured_output_models.objections_analysis_model import ObjectionsAnalysis

logger = logging.getLogger(__name__)


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
        logger.info("Starting objections analysis")
        logger.debug(f"Analyzing call text of length: {len(call_text)}")
        
        try:
            # Get analysis from GPT
            logger.debug("Sending request to GPT")
            response = await self._llm_service.get_structured_response(call_text)
            
            # Validate response
            self._validate_response(response)
            
            logger.info("Objections analysis completed successfully")
            logger.debug(f"Found {len(response.objections)} objections")
            return response
            
        except Exception as e:
            logger.error(f"Error during objections analysis: {str(e)}", exc_info=True)
            raise
            
    def _validate_response(self, response: ObjectionsAnalysis):
        """Validate that the response contains required fields.
        
        Args:
            response: Analysis response to validate
            
        Raises:
            ValueError: If required fields are missing or empty
        """
        logger.debug("Validating objections analysis response")
        
        if not response.analysis:
            error_msg = "Objections analysis cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not response.objections:
            logger.warning("No objections found in the call")
            # This is not an error, as some calls might not have objections
