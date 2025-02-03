from pydantic import BaseModel


class TextRequest(BaseModel):
    """
    Request model for text processing.
    """
    text: str


class TaskResponse(BaseModel):
    """
    Response model for task creation.
    """
    task_id: str
    message: str
    user_email: str
    user_full_name: str | None
