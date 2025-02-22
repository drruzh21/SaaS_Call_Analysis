"""Celery task for analyzing sales calls."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from celery import Task
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app import crud
from app.ai.ai_agents.call_metrics_analyzer import CallMetricsAnalyzer
from app.ai.ai_agents.call_overall_analyzer import CallOverallAnalyzer
from app.ai.ai_agents.objections_analyzer import ObjectionsAnalyzer
from app.ai.companies_orchestrators.v1_orchestrator import V1Orchestrator
from app.core.celery_app import celery_app
from app.db.session_async import async_session
from app.models.call_analysis import CallAnalysisResult, Objection
from app.schemas.task import CallAnalysisRequest

logger = logging.getLogger(__name__)

class DBTask(Task):
    """Base task that handles database session management."""
    
    _db: Optional[AsyncSession] = None
    
    @property
    async def db(self) -> AsyncSession:
        """Get database session."""
        if self._db is None:
            logger.warning("Creating new database session")
            self._db = async_session()
        return self._db
    
    async def after_return(self, *args, **kwargs):
        """Clean up after task execution."""
        if self._db is not None:
            logger.warning("Closing database session")
            await self._db.close()
            self._db = None

@celery_app.task(base=DBTask, bind=True)
def analyze_call(self, request_dict: Dict[str, Any]) -> dict:
    """Analyze a sales call using V1Orchestrator.
    
    This task:
    1. Creates a CallAnalysisResult object
    2. Enriches it with AI analysis using V1Orchestrator
    3. Saves the result to the database
    
    Args:
        request_dict: Dictionary containing call analysis request data
        
    Returns:
        Dictionary with analysis results
    """
    logger.warning(f"Starting call analysis task {self.request.id}")
    
    async def _analyze():
        try:
            # Convert dict to CallAnalysisRequest
            logger.warning("Converting request dictionary to CallAnalysisRequest")
            request = CallAnalysisRequest(**request_dict)
            logger.warning(f"Request details: manager={request.manager_name}, duration={request.call_duration}s")
            logger.warning(f"Call text length: {len(request.text)} characters")
            
            # Create orchestrator with required analyzers
            logger.warning("Initializing V1Orchestrator with analyzers")
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
            logger.warning("Creating initial analysis result object")
            analysis_result = CallAnalysisResult(
                id=1,
                user_id=1,
                lead_url="https://crm.example.com/lead/123",
                call_text=request.text,
                call_duration=request.call_duration,
                manager_fio=request.manager_name,
                # request.datetime is already a datetime object thanks to Pydantic
                date=request.datetime
            )
            
            # Enrich analysis result with AI analysis
            logger.warning("Starting call analysis with V1Orchestrator")
            analysis_result = orchestrator.analyze_call(analysis_result)
            logger.warning(f"Analysis completed with final grade: {analysis_result.final_grade:.2f}")
            
            # Set example values for missing fields
            logger.warning("Setting default values for missing fields")
            analysis_result.lead_url = f"https://crm.company.com/leads/{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if not analysis_result.analysis_reason:
                analysis_result.analysis_reason = "Call analysis performed as part of regular quality assessment"
                
            # Save to database with proper transaction handling
            logger.warning("Saving analysis results to database")
            db = await self.db
            
            try:
                # Start transaction
                async with db.begin():
                    logger.warning("Starting database transaction")
                    existing_objections = {
                        obj.name: obj 
                        for obj in (await db.execute(
                            db.query(Objection).filter(
                                Objection.name.in_([obj.name for obj in analysis_result.objections])
                            )
                        )).scalars().all()
                    }
                    logger.warning(f"Found {len(existing_objections)} existing objections")
                    
                    # Reuse existing objections or create new ones
                    for i, objection in enumerate(analysis_result.objections):
                        if objection.name in existing_objections:
                            logger.warning(f"Reusing existing objection: {objection.name}")
                            analysis_result.objections[i] = existing_objections[objection.name]
                        else:
                            logger.warning(f"Creating new objection: {objection.name}")
                    
                    # Add and commit
                    logger.warning("Adding analysis result to database")
                    db.add(analysis_result)
                    await db.commit()
                    logger.warning(f"Successfully saved analysis result with ID: {analysis_result.id}")
                
            except SQLAlchemyError as e:
                await db.rollback()
                error_msg = f"Database error while saving analysis result: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise
                
            # Return result as dictionary
            logger.warning("Call analysis task completed successfully")
            return {
                "id": analysis_result.id,
                "final_grade": analysis_result.final_grade,
                "overall_analysis": analysis_result.overall_analysis,
                "recommendations": analysis_result.recommendations_how_to_work_with_client
            }
            
        except Exception as e:
            error_msg = f"Error in analyze_call task: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
            
    # Run async function in event loop
    return asyncio.run(_analyze())
