"""First implementation of the call analysis orchestrator."""

from typing import Dict, Any

from app.ai.ai_agents.call_metrics_analyzer import CallMetricsAnalyzer
from app.ai.ai_agents.call_overall_analyzer import CallOverallAnalyzer
from app.ai.ai_agents.objections_analyzer import ObjectionsAnalyzer
from app.models.call_analysis import CallAnalysisResult


class V1Orchestrator:
    """First implementation of the call analysis orchestrator.
    
    This orchestrator coordinates three AI agents:
    1. CallMetricsAnalyzer - for detailed metrics analysis
    2. CallOverallAnalyzer - for overall call analysis and recommendations
    3. ObjectionsAnalyzer - for identifying and analyzing objections
    """
    
    def __init__(
        self,
        metrics_analyzer: CallMetricsAnalyzer,
        overall_analyzer: CallOverallAnalyzer,
        objections_analyzer: ObjectionsAnalyzer
    ):
        """Initialize the orchestrator with required AI agents.
        
        Args:
            metrics_analyzer: Agent for detailed metrics analysis
            overall_analyzer: Agent for overall call analysis
            objections_analyzer: Agent for objections analysis
        """
        self._metrics_analyzer = metrics_analyzer
        self._overall_analyzer = overall_analyzer
        self._objections_analyzer = objections_analyzer
    
    async def analyze_call(self, analysis_result: CallAnalysisResult) -> CallAnalysisResult:
        """Analyze a call using all available analyzers.
        
        This method enriches the provided CallAnalysisResult with:
        1. Detailed metrics analysis
        2. Overall analysis and recommendations
        3. Objections analysis
        
        Args:
            analysis_result: Object containing call text and other analysis data
            
        Returns:
            The same CallAnalysisResult object, enriched with analysis results
        """
        call_text = analysis_result.call_text
        
        # Run all analyses concurrently for better performance
        metrics_analysis = await self._metrics_analyzer.analyze(call_text)
        overall_analysis = await self._overall_analyzer.analyze(call_text)
        objections_analysis = await self._objections_analyzer.analyze(call_text)
        
        # Enrich the analysis result with all obtained data
        analysis_result.metrics_analysis = metrics_analysis
        analysis_result.overall_analysis = overall_analysis
        analysis_result.objections_analysis = objections_analysis
        
        return analysis_result
