"""First implementation of the call analysis orchestrator."""

import logging
from typing import Dict, Any

from app.ai.ai_agents.call_metrics_analyzer import CallMetricsAnalyzer
from app.ai.ai_agents.call_overall_analyzer import CallOverallAnalyzer
from app.ai.ai_agents.objections_analyzer import ObjectionsAnalyzer
from app.ai.structured_output_models.call_metrics_model import CallAnalysisMetrics
from app.models.call_analysis import CallAnalysisResult, Objection

logger = logging.getLogger(__name__)


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
        logger.info("Initializing V1Orchestrator with AI agents")
        self._metrics_analyzer = metrics_analyzer
        self._overall_analyzer = overall_analyzer
        self._objections_analyzer = objections_analyzer
    
    def _calculate_final_grade(self, metrics: CallAnalysisMetrics) -> float:
        """Calculate final grade as average of all metric scores.
        
        The final grade is calculated as the arithmetic mean of all numeric scores,
        excluding any textual analysis or comments.
        
        Args:
            metrics: Call analysis metrics containing all individual scores
            
        Returns:
            Final grade as a float between 0 and 1
        """
        logger.debug("Calculating final grade from metrics")
        scores = [
            metrics.is_manager_established_contact,
            metrics.is_manager_holding_initiative,
            metrics.is_manager_using_dialog_programming,
            metrics.is_manager_qualifying_client,
            metrics.is_manager_identifying_pain,
            metrics.is_manager_presenting_product,
            metrics.is_manager_showing_expertise,
            metrics.is_manager_handling_objections,
            metrics.is_manager_setting_next_step,
            metrics.is_manager_using_client_framing,
            metrics.tone_of_voice
        ]
        
        # Filter out None values if any
        valid_scores = [score for score in scores if score is not None]
        logger.debug(f"Found {len(valid_scores)} valid scores out of {len(scores)} total scores")
        
        if not valid_scores:
            logger.warning("No valid scores found, returning default grade 0.0")
            return 0.0
            
        final_grade = sum(valid_scores) / len(valid_scores)
        logger.info(f"Calculated final grade: {final_grade:.2f}")
        return final_grade
    
    def analyze_call(self, analysis_result: CallAnalysisResult) -> CallAnalysisResult:
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
        logger.info(f"Starting call analysis for manager: {analysis_result.manager_fio}")
        logger.debug(f"Call duration: {analysis_result.call_duration} seconds")
        
        call_text = analysis_result.call_text
        logger.debug(f"Call text length: {len(call_text)} characters")
        
        try:
            # Run all analyses
            logger.info("Running metrics analysis")
            metrics_analysis = self._metrics_analyzer.analyze(call_text)
            logger.debug(f"Metrics analysis completed with final grade: {metrics_analysis.final_grade:.2f}")
            
            logger.info("Running overall analysis")
            overall_analysis = self._overall_analyzer.analyze(call_text)
            logger.debug(f"Overall analysis completed with {len(overall_analysis.recommendations_how_to_work_with_client)} recommendations")
            
            logger.info("Running objections analysis")
            objections_analysis = self._objections_analyzer.analyze(call_text)
            logger.debug(f"Objections analysis found {len(objections_analysis.objections)} objections")
            
            # Map metrics analysis results
            logger.info("Mapping metrics analysis results")
            analysis_result.is_manager_established_contact = metrics_analysis.is_manager_established_contact
            analysis_result.is_manager_established_contact_comment = metrics_analysis.is_manager_established_contact_comment
            
            analysis_result.is_manager_holding_initiative = metrics_analysis.is_manager_holding_initiative
            analysis_result.is_manager_holding_initiative_comment = metrics_analysis.is_manager_holding_initiative_comment
            
            analysis_result.is_manager_using_dialog_programming = metrics_analysis.is_manager_using_dialog_programming
            analysis_result.is_manager_using_dialog_programming_comment = metrics_analysis.is_manager_using_dialog_programming_comment
            
            analysis_result.is_manager_qualifying_client = metrics_analysis.is_manager_qualifying_client
            analysis_result.is_manager_qualifying_client_comment = metrics_analysis.is_manager_qualifying_client_comment
            
            analysis_result.is_manager_identifying_pain = metrics_analysis.is_manager_identifying_pain
            analysis_result.is_manager_identifying_pain_comment = metrics_analysis.is_manager_identifying_pain_comment
            
            analysis_result.is_manager_presenting_product = metrics_analysis.is_manager_presenting_product
            analysis_result.is_manager_presenting_product_comment = metrics_analysis.is_manager_presenting_product_comment
            
            analysis_result.is_manager_showing_expertise = metrics_analysis.is_manager_showing_expertise
            analysis_result.is_manager_showing_expertise_comment = metrics_analysis.is_manager_showing_expertise_comment
            
            analysis_result.is_manager_handling_objections = metrics_analysis.is_manager_handling_objections
            analysis_result.is_manager_handling_objections_comment = metrics_analysis.is_manager_handling_objections_comment
            
            analysis_result.is_manager_setting_next_step = metrics_analysis.is_manager_setting_next_step
            analysis_result.is_manager_setting_next_step_comment = metrics_analysis.is_manager_setting_next_step_comment
            
            analysis_result.is_manager_using_client_framing = metrics_analysis.is_manager_using_client_framing
            analysis_result.is_manager_using_client_framing_comment = metrics_analysis.is_manager_using_client_framing_comment
            
            analysis_result.tone_of_voice = metrics_analysis.tone_of_voice
            analysis_result.tone_of_voice_comment = metrics_analysis.tone_of_voice_comment
            
            # Calculate and set final grade
            logger.info("Calculating final grade")
            analysis_result.final_grade = self._calculate_final_grade(metrics_analysis)
            
            # Map overall analysis results
            logger.info("Mapping overall analysis results")
            analysis_result.recommendations_how_to_work_with_client = overall_analysis.recommendations_how_to_work_with_client
            analysis_result.overall_analysis = overall_analysis.overall_analysis
            
            # Map objections analysis results
            logger.info("Mapping objections analysis results")
            # Create Objection objects for each objection type found
            objections = []
            for objection_type in objections_analysis.objections:
                objection = Objection(name=objection_type.value)
                objections.append(objection)
            
            analysis_result.objections = objections
            analysis_result.analysis_reason = objections_analysis.analysis
            
            logger.info("Call analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during call analysis: {str(e)}", exc_info=True)
            raise
