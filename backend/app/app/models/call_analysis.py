from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

class CallObjection(Base):
    """Связующая таблица для many-to-many отношения между звонками и возражениями"""
    __tablename__ = "call_objections"
    
    call_id: Mapped[int] = mapped_column(ForeignKey("call_analysis_results.id"), primary_key=True)
    objection_id: Mapped[int] = mapped_column(ForeignKey("objections.id"), primary_key=True)

class Objection(Base):
    __tablename__ = "objections"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    # Relationship to calls
    calls: Mapped[List["CallAnalysisResult"]] = relationship(
        "CallAnalysisResult", 
        secondary="call_objections",
        back_populates="objections"
    )

class CallAnalysisResult(Base):
    __tablename__ = "call_analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("user.company_name_id"), 
        index=True,
        nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    manager_fio: Mapped[str] = mapped_column(String)

    # Metrics
    is_manager_established_contact: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_holding_initiative: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_using_dialog_programming: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_qualifying_client: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_identifying_pain: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_presenting_product: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_showing_expertise: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_handling_objections: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_setting_next_step: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    is_manager_using_client_framing: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)
    tone_of_voice: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0, nullable=True)
    final_grade: Mapped[float] = mapped_column(Float(precision=10, decimal_return_scale=5), default=0.0)

    # Comments
    is_manager_established_contact_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_holding_initiative_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_using_dialog_programming_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_qualifying_client_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_identifying_pain_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_presenting_product_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_showing_expertise_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_handling_objections_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_setting_next_step_comment: Mapped[str] = mapped_column(String, default="")
    is_manager_using_client_framing_comment: Mapped[str] = mapped_column(String, default="")
    tone_of_voice_comment: Mapped[str] = mapped_column(String, default="", nullable=True)

    # Additional fields
    call_text: Mapped[str] = mapped_column(String, default="")
    analysis_reason: Mapped[str] = mapped_column(String, default="")
    recommendations_how_to_work_with_client: Mapped[str] = mapped_column(String, default="")
    overall_analysis: Mapped[str] = mapped_column(String, default="")
    lead_url: Mapped[str] = mapped_column(String, default="")

    # Relationship to objections
    objections: Mapped[List[Objection]] = relationship(
        "Objection", 
        secondary="call_objections",
        back_populates="calls"
    )
