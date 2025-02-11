"""AI agent for analyzing call metrics."""

import logging

from app.ai.ai_agents.i_gpt_analyzer import IGptAnalyzer
from app.ai.openai_llm_service import OpenAILLMService
from app.ai.prompts.metrics_analyzer_prompt import METRICS_ANALYZER_PROMPT
from app.ai.structured_output_models.call_metrics_model import CallAnalysisMetrics
from app.ai.structured_output_models.score import Score

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
            logger.debug(f"Received GPT response")
            
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
            metrics: Metrics to validate. Can be either a CallAnalysisMetrics instance or a dict.
            
        Raises:
            ValueError: If any metric is outside the valid range [0, 1]
        """
        logger.debug("Validating metrics")

        # These are the actual field names from the Pydantic model
        numeric_fields = [
            'is_manager_established_contact',
            'speech_quality',
            'is_manager_holding_initiative',
            'problem_identification',
            'product_presentation',
            'expertise_demonstration',
            'objection_handling',
            'next_step_setting',
            'tone_of_voice'
        ]
        
        for field in numeric_fields:
            try:
                value = getattr(metrics, field)
                if isinstance(value, float) or isinstance(value, int):
                    if value is not None and (value < 0 or value > 1):
                        error_msg = f"Invalid {field} value: {value}. Must be between 0 and 1"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
            except AttributeError:
                logger.warning(f"Field {field} not found in metrics")
                continue  # Skip fields that don't exist
