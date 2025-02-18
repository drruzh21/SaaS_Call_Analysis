"""First implementation of the call analysis orchestrator."""

import logging
from datetime import datetime

from app.ai.ai_agents.call_metrics_analyzer import CallMetricsAnalyzer
from app.ai.ai_agents.call_overall_analyzer import CallOverallAnalyzer
from app.ai.ai_agents.objections_analyzer import ObjectionsAnalyzer
from app.ai.structured_output_models.call_metrics_model import CallAnalysisMetrics
from app.core.constants import METRIC_DEFAULT_VALUE
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
            metrics.speech_quality,
            metrics.is_manager_holding_initiative,
            metrics.problem_identification,
            metrics.product_presentation,
            metrics.expertise_demonstration,
            metrics.objection_handling,
            metrics.deal_closing,
            metrics.contact_verification,
            metrics.next_step_setting,
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
            logger.debug(f"Metrics analysis completed")
            
            logger.info("Running overall analysis")
            overall_analysis = self._overall_analyzer.analyze(call_text)

            logger.info("Running objections analysis")
            objections_analysis = self._objections_analyzer.analyze(call_text)

            # Map metrics analysis results
            logger.info("Mapping metrics analysis results")
            
            # Установление контакта
            analysis_result.is_manager_established_contact = metrics_analysis.is_manager_established_contact
            analysis_result.is_manager_established_contact_comment = metrics_analysis.is_manager_established_contact_comment
            
            # Качество речи -> Программирование диалога
            analysis_result.is_manager_using_dialog_programming = metrics_analysis.speech_quality
            analysis_result.is_manager_using_dialog_programming_comment = metrics_analysis.speech_quality_comment
            
            # Удержание инициативы
            analysis_result.is_manager_holding_initiative = metrics_analysis.is_manager_holding_initiative
            analysis_result.is_manager_holding_initiative_comment = metrics_analysis.is_manager_holding_initiative_comment
            
            # Квалификация клиента -> Идентификация проблемы
            analysis_result.is_manager_qualifying_client = metrics_analysis.problem_identification
            analysis_result.is_manager_qualifying_client_comment = metrics_analysis.problem_identification_comment
            
            # Идентификация боли -> Идентификация проблемы
            analysis_result.is_manager_identifying_pain = metrics_analysis.problem_identification
            analysis_result.is_manager_identifying_pain_comment = metrics_analysis.problem_identification_comment
            
            # Презентация продукта
            analysis_result.is_manager_presenting_product = metrics_analysis.product_presentation
            analysis_result.is_manager_presenting_product_comment = metrics_analysis.product_presentation_comment
            
            # Демонстрация экспертности
            analysis_result.is_manager_showing_expertise = metrics_analysis.expertise_demonstration
            analysis_result.is_manager_showing_expertise_comment = metrics_analysis.expertise_demonstration_comment
            
            # Работа с возражениями
            analysis_result.is_manager_handling_objections = metrics_analysis.objection_handling
            analysis_result.is_manager_handling_objections_comment = metrics_analysis.objection_handling_comment
            
            # Следующий шаг
            analysis_result.is_manager_setting_next_step = metrics_analysis.next_step_setting
            analysis_result.is_manager_setting_next_step_comment = metrics_analysis.next_step_setting_comment
            
            # Фрейминг клиента -> Верификация контакта
            analysis_result.is_manager_using_client_framing = metrics_analysis.contact_verification
            analysis_result.is_manager_using_client_framing_comment = metrics_analysis.contact_verification_comment
            
            # Тон голоса
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


if __name__ == "__main__":
    # Load environment variables before any other imports
    import os
    import sys
    from pathlib import Path

    from dotenv import load_dotenv

    # Get the absolute path to the app directory (2 levels up from this file)
    app_dir = Path(__file__).resolve().parent.parent.parent
    
    # Add the app directory to Python path to make imports work
    sys.path.insert(0, str(app_dir))
    
    # Look for .env file in app directory
    env_file = app_dir / ".env"
    if not env_file.exists():
        # If not found in app dir, try one level up (backend/app/.env)
        env_file = app_dir.parent / ".env"
    
    if not env_file.exists():
        print(f"Error: .env file not found in {app_dir} or {app_dir.parent}")
        sys.exit(1)
    
    # Load environment variables from the found .env file
    load_dotenv(env_file)
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG for more detailed logging
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Log the environment setup
    logger = logging.getLogger(__name__)
    logger.info(f"Using .env file from: {env_file}")
    
    # Sample call text for testing
    sample_call = '''
    Менеджер: Добрый день! Меня зовут Иван, компания "Инновации". Как я могу к вам обращаться?
    Клиент: Здравствуйте, я Андрей.
    Менеджер: Андрей, я звоню вам, чтобы рассказать о нашем новом решении для автоматизации продаж. Скажите, как сейчас у вас организован процесс работы с клиентами?
    Клиент: Ну, в основном все в Excel ведем, иногда забываем перезвонить клиентам вовремя.
    Менеджер: А как это влияет на продажи, много ли клиентов "теряется"?
    Клиент: Да, бывает, что забываем перезвонить, клиенты уходят к конкурентам.
    Менеджер: Понятно. Наше решение как раз помогает автоматизировать эти процессы. Система сама напоминает о необходимости связаться с клиентом, ведет историю взаимодействий. Как вы считаете, это могло бы помочь в решении проблемы?
    Клиент: Звучит интересно, но наверное это дорого стоит?
    Менеджер: Давайте я расскажу про наши тарифы. У нас есть гибкая система оплаты, зависящая от количества пользователей. При этом окупаемость обычно наступает уже через 2-3 месяца за счет повышения конверсии и среднего чека. Могу провести для вас демонстрацию системы, чтобы вы увидели все возможности?
    Клиент: Да, давайте посмотрим.
    Менеджер: Отлично! Давайте сверим ваш email для отправки приглашения на демонстрацию. Это test@test.com?
    Клиент: Да, верно.
    Менеджер: Хорошо, тогда я отправлю вам приглашение на завтра на 14:00, вам удобно будет?
    Клиент: Да, завтра в 14:00 подойдет.
    Менеджер: Замечательно! Тогда до встречи завтра, хорошего дня!
    '''
    # Initialize real analyzers with OpenAI API key from settings
    from app.core.config import settings

    # Create real analyzers
    metrics_analyzer = CallMetricsAnalyzer(api_key=settings.OPENAI_API_KEY)
    overall_analyzer = CallOverallAnalyzer(api_key=settings.OPENAI_API_KEY)
    objections_analyzer = ObjectionsAnalyzer(api_key=settings.OPENAI_API_KEY)
    
    # Initialize orchestrator with real analyzers
    orchestrator = V1Orchestrator(
        metrics_analyzer=metrics_analyzer,
        overall_analyzer=overall_analyzer,
        objections_analyzer=objections_analyzer
    )
    
    # Create a sample CallAnalysisResult with all required fields initialized
    analysis_result = CallAnalysisResult(
        # Required fields from database schema
        id=1,
        company_name_id=1,  # This should be a valid company ID from your database
        date=datetime.utcnow(),
        
        # Basic call information
        call_text=sample_call,
        manager_fio="Иван Петров",
        call_duration=180,  # 3 minutes
        lead_url="https://crm.example.com/lead/123",  # Example lead URL
        
        # Initialize metrics with default values (will be updated by analyzers)
        is_manager_established_contact=METRIC_DEFAULT_VALUE,
        is_manager_holding_initiative=METRIC_DEFAULT_VALUE,
        is_manager_using_dialog_programming=METRIC_DEFAULT_VALUE,
        is_manager_qualifying_client=METRIC_DEFAULT_VALUE,
        is_manager_identifying_pain=METRIC_DEFAULT_VALUE,
        is_manager_presenting_product=METRIC_DEFAULT_VALUE,
        is_manager_showing_expertise=METRIC_DEFAULT_VALUE,
        is_manager_handling_objections=METRIC_DEFAULT_VALUE,
        is_manager_setting_next_step=METRIC_DEFAULT_VALUE,
        is_manager_using_client_framing=METRIC_DEFAULT_VALUE,
        tone_of_voice=METRIC_DEFAULT_VALUE,
        final_grade=METRIC_DEFAULT_VALUE,
        
        # Initialize metric comments with empty strings (will be updated by analyzers)
        is_manager_established_contact_comment="",
        is_manager_holding_initiative_comment="",
        is_manager_using_dialog_programming_comment="",
        is_manager_qualifying_client_comment="",
        is_manager_identifying_pain_comment="",
        is_manager_presenting_product_comment="",
        is_manager_showing_expertise_comment="",
        is_manager_handling_objections_comment="",
        is_manager_setting_next_step_comment="",
        is_manager_using_client_framing_comment="",
        tone_of_voice_comment="",
        
        # Initialize analysis fields with empty strings (will be updated by analyzers)
        analysis_reason="",
        recommendations_how_to_work_with_client="",
        overall_analysis="",
        
        # Initialize empty objections list (will be updated by analyzers)
        objections=[]
    )
    
    # Run analysis
    try:
        result = orchestrator.analyze_call(analysis_result)
        
        # Print results
        print("\n=== Call Analysis Results ===")
        print(f"Final Grade: {result.final_grade:.2f}")
        print("\nMetrics Analysis:")
        print(f"Contact Established: {result.is_manager_established_contact:.2f} - {result.is_manager_established_contact_comment}")
        print(f"Initiative: {result.is_manager_holding_initiative:.2f} - {result.is_manager_holding_initiative_comment}")
        
        print("\nOverall Analysis:")
        print(result.overall_analysis)
        print("\nRecommendations:")
        print(result.recommendations_how_to_work_with_client)

        
        print("\nObjections:")
        for obj in result.objections:
            print(f"- {obj.name}")
        print(f"\nObjections Analysis: {result.analysis_reason}")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

