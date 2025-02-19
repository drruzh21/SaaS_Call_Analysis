from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    MAX_ANALYSIS_REASON_LENGTH,
    MAX_CALL_TEXT_LENGTH,
    MAX_COMMENT_LENGTH,
    MAX_LEAD_URL_LENGTH,
    MAX_MANAGER_NAME_LENGTH,
    MAX_OVERALL_ANALYSIS_LENGTH,
    MAX_RECOMMENDATIONS_LENGTH,
    METRIC_DECIMAL_SCALE,
    METRIC_DEFAULT_VALUE,
    METRIC_MAX_VALUE,
    METRIC_MIN_VALUE,
    METRIC_PRECISION,
)
from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User

class CallObjection(Base):
    """Join table for many-to-many relationship between calls and objections"""
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
    __table_args__ = (
        CheckConstraint(
            f'is_manager_established_contact >= {METRIC_MIN_VALUE} AND is_manager_established_contact <= {METRIC_MAX_VALUE}',
            name='check_established_contact_metric'
        ),
        CheckConstraint(
            f'is_manager_holding_initiative >= {METRIC_MIN_VALUE} AND is_manager_holding_initiative <= {METRIC_MAX_VALUE}',
            name='check_holding_initiative_metric'
        ),
        CheckConstraint(
            f'is_manager_using_dialog_programming >= {METRIC_MIN_VALUE} AND is_manager_using_dialog_programming <= {METRIC_MAX_VALUE}',
            name='check_using_dialog_programming_metric'
        ),
        CheckConstraint(
            f'is_manager_qualifying_client >= {METRIC_MIN_VALUE} AND is_manager_qualifying_client <= {METRIC_MAX_VALUE}',
            name='check_qualifying_client_metric'
        ),
        CheckConstraint(
            f'is_manager_identifying_pain >= {METRIC_MIN_VALUE} AND is_manager_identifying_pain <= {METRIC_MAX_VALUE}',
            name='check_identifying_pain_metric'
        ),
        CheckConstraint(
            f'is_manager_presenting_product >= {METRIC_MIN_VALUE} AND is_manager_presenting_product <= {METRIC_MAX_VALUE}',
            name='check_presenting_product_metric'
        ),
        CheckConstraint(
            f'is_manager_showing_expertise >= {METRIC_MIN_VALUE} AND is_manager_showing_expertise <= {METRIC_MAX_VALUE}',
            name='check_showing_expertise_metric'
        ),
        CheckConstraint(
            f'is_manager_handling_objections >= {METRIC_MIN_VALUE} AND is_manager_handling_objections <= {METRIC_MAX_VALUE}',
            name='check_handling_objections_metric'
        ),
        CheckConstraint(
            f'is_manager_setting_next_step >= {METRIC_MIN_VALUE} AND is_manager_setting_next_step <= {METRIC_MAX_VALUE}',
            name='check_setting_next_step_metric'
        ),
        CheckConstraint(
            f'is_manager_using_client_framing >= {METRIC_MIN_VALUE} AND is_manager_using_client_framing <= {METRIC_MAX_VALUE}',
            name='check_using_client_framing_metric'
        ),
        CheckConstraint(
            f'tone_of_voice >= {METRIC_MIN_VALUE} AND tone_of_voice <= {METRIC_MAX_VALUE}',
            name='check_tone_of_voice_metric'
        ),
        CheckConstraint(
            f'final_grade >= {METRIC_MIN_VALUE} AND final_grade <= {METRIC_MAX_VALUE}',
            name='check_final_grade_metric'
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("user.id"), 
        index=True,
        nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    manager_fio: Mapped[str] = mapped_column(String(MAX_MANAGER_NAME_LENGTH))
    call_duration: Mapped[float] = mapped_column(
        Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), nullable=True)

    # Metrics
    is_manager_established_contact: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_holding_initiative: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_using_dialog_programming: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_qualifying_client: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_identifying_pain: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_presenting_product: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_showing_expertise: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_handling_objections: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_setting_next_step: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    is_manager_using_client_framing: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)
    tone_of_voice: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE, nullable=True)
    final_grade: Mapped[float] = mapped_column(Float(precision=METRIC_PRECISION, decimal_return_scale=METRIC_DECIMAL_SCALE), default=METRIC_DEFAULT_VALUE)

    # Comments
    is_manager_established_contact_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_holding_initiative_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_using_dialog_programming_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_qualifying_client_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_identifying_pain_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_presenting_product_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_showing_expertise_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_handling_objections_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_setting_next_step_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    is_manager_using_client_framing_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="")
    tone_of_voice_comment: Mapped[str] = mapped_column(String(MAX_COMMENT_LENGTH), default="", nullable=True)

    # Additional fields
    call_text: Mapped[str] = mapped_column(String(MAX_CALL_TEXT_LENGTH), default="")
    analysis_reason: Mapped[str] = mapped_column(String(MAX_ANALYSIS_REASON_LENGTH), default="")
    recommendations_how_to_work_with_client: Mapped[str] = mapped_column(String(MAX_RECOMMENDATIONS_LENGTH), default="")
    overall_analysis: Mapped[str] = mapped_column(String(MAX_OVERALL_ANALYSIS_LENGTH), default="")
    lead_url: Mapped[str] = mapped_column(String(MAX_LEAD_URL_LENGTH), default="")

    # Relationship to objections
    objections: Mapped[List[Objection]] = relationship(
        "Objection", 
        secondary="call_objections",
        back_populates="calls"
    )

    user: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id],
        back_populates="call_analyses"
    )
