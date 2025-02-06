"""API endpoints for task management."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app import models, schemas
from app.api import deps
from app.schemas.task import CallAnalysisRequest
from app.worker.analyze_call import analyze_call

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze-call/", response_model=schemas.TaskResponse)
async def create_call_analysis_task(
    request: CallAnalysisRequest,
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)]
) -> Any:
    """Create a new call analysis task.
    
    Args:
        request: Call analysis request containing call text and metadata
        current_user: Currently authenticated user
        
    Returns:
        Task ID and status
        
    Raises:
        HTTPException: If task creation fails
    """
    try:
        logger.info("Received call analysis request")
        logger.debug(f"Request details: manager={request.manager_name}, duration={request.call_duration}s")
        logger.debug(f"Call text length: {len(request.text)} characters")
        
        # Send task to Celery worker
        logger.info("Sending task to Celery worker")
        task = analyze_call.delay(request.dict())  # Convert Pydantic model to dict for Celery
        logger.debug(f"Task created with ID: {task.id}")
        
        return {
            "task_id": task.id,
            "message": "Call analysis task started successfully",
            "user_email": current_user.email,
            "user_full_name": current_user.full_name
        }
        
    except Exception as e:
        error_msg = f"Failed to create call analysis task: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)
