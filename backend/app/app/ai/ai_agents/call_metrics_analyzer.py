"""AI agent for analyzing call metrics."""

import logging
from typing import Any

from app.ai.ai_agents.i_gpt_analyzer import IGptAnalyzer
from app.ai.prompts.metrics_analyzer_prompt import METRICS_ANALYZER_PROMPT
from app.ai.structured_output_models.call_metrics_model import CallAnalysisMetrics
from app.ai.openai_llm_service import OpenAILLMService


logger = logging.getLogger(__name__)


class CallMetricsAnalyzer(IGptAnalyzer[CallAnalysisMetrics]):
    """AI agent for analyzing detailed call metrics.
    
    This analyzer evaluates various aspects of the call, such as:
    - Contact establishment
    - Initiative holding
    - Dialog programming
    - Client qualification
    - Pain identification
    - Product presentation
    - Expertise demonstration
    - Objections handling
    - Next step setting
    - Client framing
    - Voice tone
    """
    
    def __init__(self, api_key: str):
        """
        Initialize analyzer
        
        Args:
            api_key: OpenAI API key
        """
        self.llm_service = OpenAILLMService(
            api_key=api_key,
            response_format=CallAnalysisMetrics,
            system_prompt=METRICS_ANALYZER_PROMPT
        )
    
    def analyze(self, call_text: str) -> CallAnalysisMetrics:
        """Analyze call text and produce detailed metrics.
        
        Args:
            call_text: The text of the call to analyze
            
        Returns:
            Detailed metrics analysis of the call
        """
        logger.info("Starting call metrics analysis")
        logger.debug(f"Analyzing call text of length: {len(call_text)}")
        
        try:
            # Get analysis from GPT
            logger.debug("Sending request to GPT")
            result = self.llm_service.get_completion(
                f"Проанализируйте следующую запись телефонного разговора и оцените все метрики:\n\n{call_text}"
            )
            logger.debug(f"Received GPT response with final grade: {result.final_grade:.2f}")
            
            # Validate metrics
            self._validate_metrics(result)
            
            logger.info("Call metrics analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during metrics analysis: {str(e)}", exc_info=True)
            raise
            
    def _validate_metrics(self, metrics: CallAnalysisMetrics):
        """Validate that all metrics are within expected ranges.
        
        Args:
            metrics: Metrics to validate
            
        Raises:
            ValueError: If any metric is outside the valid range [0, 1]
        """
        logger.debug("Validating metrics")
        numeric_fields = [
            'is_manager_established_contact',
            'is_manager_holding_initiative',
            'is_manager_using_dialog_programming',
            'is_manager_qualifying_client',
            'is_manager_identifying_pain',
            'is_manager_presenting_product',
            'is_manager_showing_expertise',
            'is_manager_handling_objections',
            'is_manager_setting_next_step',
            'is_manager_using_client_framing',
            'tone_of_voice'
        ]
        
        for field in numeric_fields:
            value = getattr(metrics, field)
            if value is not None and (value < 0 or value > 1):
                error_msg = f"Invalid {field} value: {value}. Must be between 0 and 1"
                logger.error(error_msg)
                raise ValueError(error_msg)
