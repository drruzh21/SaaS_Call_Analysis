from app.ai.ai_agents.i_gpt_analyzer import IGptAnalyzer
from app.ai.structured_output_models.call_metrics_model import CallAnalysisMetrics
from app.ai.prompts.metrics_analyzer_prompt import METRICS_ANALYZER_PROMPT
from app.ai.openai_llm_service import OpenAILLMService


class CallMetricsAnalyzer(IGptAnalyzer[CallAnalysisMetrics]):
    """GPT agent for analyzing call metrics"""
    
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
        """
        Analyze call text to evaluate detailed metrics
        
        Args:
            call_text: The transcribed call text
            
        Returns:
            CallAnalysisMetrics containing detailed performance metrics
        """
        result = self.llm_service.get_completion(
            f"Проанализируйте следующую запись телефонного разговора и оцените все метрики:\n\n{call_text}"
        )
        return CallAnalysisMetrics.parse_obj(result)
