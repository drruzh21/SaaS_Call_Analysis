from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TextRequest(BaseModel):
    """
    Request model for text processing.
    """
    text: str


class CallAnalysisRequest(BaseModel):
    """
    Request model for call analysis.
    """
    text: str
    call_duration: float
    manager_name: str
    datetime: datetime

    # Optional CRM fields
    deal_source: Optional[str] = Field(None, description="Source of the deal from CRM")
    sales_funnel_stage: Optional[str] = Field(None, description="Current stage in the sales funnel")
    call_direction: Optional[str] = Field(None, description="Direction of the call (incoming/outgoing)")
    is_repeat_call: Optional[bool] = Field(None, description="Whether this is a repeat call with the client")
    manager_phone: Optional[str] = Field(None, description="Manager's phone number")
    client_phone: Optional[str] = Field(None, description="Client's phone number")


class TaskResponse(BaseModel):
    """
    Response model for task creation.
    """
    task_id: str
    message: str
    user_email: str
    user_full_name: str | None