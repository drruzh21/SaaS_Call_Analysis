from typing import Any, Annotated
from fastapi import APIRouter, Depends

from app.worker.tests import test_celery
from app import models, schemas
from app.api import deps

router = APIRouter()


@router.post("/process-text", response_model=schemas.TaskResponse)
async def process_text(
    request: schemas.TextRequest,
    current_user: Annotated[models.User, Depends(deps.get_current_user_by_api_key)]
) -> Any:
    """
    Process text asynchronously using Celery task.
    Requires API key authentication via X-API-Key header.
    
    Args:
        request: TextRequest containing the text to process
        current_user: User authenticated via API key
        
    Returns:
        TaskResponse with task ID, status message and user information
    """
    task = test_celery.delay(request.text)
    return {
        "task_id": task.id,
        "message": "Task started successfully",
        "user_email": current_user.email,
        "user_full_name": current_user.full_name
    }
