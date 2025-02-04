from typing import Any, Annotated
from fastapi import APIRouter, Depends

from app.worker.tests import test_celery
from app import models, schemas
from app.api import deps

router = APIRouter(prefix="/celery")


@router.post("/analyze-call", response_model=schemas.TaskResponse)
async def analyze_call(
    request: schemas.CallAnalysisRequest,
    current_user: Annotated[models.User, Depends(deps.get_current_user_by_api_key)]
) -> Any:
    """
    Analyze call asynchronously using Celery task.
    Requires API key authentication via X-API-Key header.
    
    Args:
        request: CallAnalysisRequest containing the call details and text to analyze
        current_user: User authenticated via API key
        
    Returns:
        TaskResponse with task ID, status message and user information
    """
    # For now, we're using the test_celery task, but this should be replaced with the actual call analysis task
    task = test_celery.delay(request.text)
    return {
        "task_id": task.id,
        "message": "Call analysis task started successfully",
        "user_email": current_user.email,
        "user_full_name": current_user.full_name
    }
