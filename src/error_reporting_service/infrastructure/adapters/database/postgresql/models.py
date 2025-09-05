"""
SQLAlchemy Models for PostgreSQL

This module contains SQLAlchemy ORM models for the PostgreSQL database.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ErrorReportModel(Base):
    """SQLAlchemy model for error reports with enhanced metadata"""

    __tablename__ = "error_reports"

    error_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    speaker_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    reported_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    error_categories = Column(JSON, nullable=False)
    severity_level = Column(String(20), nullable=False, index=True)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    context_notes = Column(Text)
    error_timestamp = Column(DateTime, nullable=False)
    reported_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Quality-based bucket management
    bucket_type = Column(String(20), nullable=False, index=True)

    # Core metadata fields
    audio_quality = Column(String(20), nullable=False)
    speaker_clarity = Column(String(30), nullable=False)
    background_noise = Column(String(20), nullable=False)

    # Enhanced metadata fields
    number_of_speakers = Column(String(10), nullable=False)
    overlapping_speech = Column(Boolean, nullable=False, default=False)
    requires_specialized_knowledge = Column(Boolean, nullable=False, default=False)
    additional_notes = Column(Text)

    # System fields
    status = Column(String(20), nullable=False, default="submitted", index=True)
    vector_db_id = Column(String(255))
    error_metadata = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    audit_logs = relationship("ErrorAuditLogModel", back_populates="error_report")
    validations = relationship("ErrorValidationModel", back_populates="error_report")


class SpeakerBucketHistoryModel(Base):
    """SQLAlchemy model for speaker bucket history"""

    __tablename__ = "speaker_bucket_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    speaker_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    bucket_type = Column(String(20), nullable=False, index=True)
    previous_bucket = Column(String(20))
    assigned_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    assigned_by = Column(UUID(as_uuid=True), nullable=False)
    assignment_reason = Column(Text, nullable=False)
    assignment_type = Column(String(20), nullable=False, default="manual")

    # Performance metrics at time of assignment
    error_count_at_assignment = Column(Integer, default=0)
    rectification_rate_at_assignment = Column(String(10))  # Decimal as string for compatibility
    quality_score_at_assignment = Column(String(10))  # Decimal as string for compatibility
    confidence_score = Column(String(10))  # Decimal as string for compatibility

    created_at = Column(DateTime, default=datetime.utcnow)


class SpeakerPerformanceMetricsModel(Base):
    """SQLAlchemy model for speaker performance metrics"""

    __tablename__ = "speaker_performance_metrics"

    metrics_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    speaker_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    current_bucket = Column(String(20), nullable=False, index=True)

    # Error metrics
    total_errors_reported = Column(Integer, default=0)
    errors_rectified = Column(Integer, default=0)
    errors_pending = Column(Integer, default=0)
    rectification_rate = Column(String(10), default="0.0000")  # Decimal as string

    # Quality metrics
    average_audio_quality = Column(String(10))  # Decimal as string
    average_clarity_score = Column(String(10))  # Decimal as string
    specialized_knowledge_frequency = Column(String(10))  # Decimal as string
    overlapping_speech_frequency = Column(String(10))  # Decimal as string

    # Performance trends
    quality_trend = Column(String(20))
    last_assessment_date = Column(DateTime)
    next_assessment_date = Column(DateTime)

    # Time metrics (stored as total seconds)
    average_time_to_rectification_seconds = Column(Integer)
    time_in_current_bucket_seconds = Column(Integer)

    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VerificationJobModel(Base):
    """SQLAlchemy model for verification jobs"""

    __tablename__ = "verification_jobs"

    verification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(255), nullable=False, index=True)  # InstaNote job ID
    speaker_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    error_report_id = Column(UUID(as_uuid=True), ForeignKey("error_reports.error_id"))

    # Job content
    original_draft = Column(Text, nullable=False)
    rag_corrected_draft = Column(Text)
    corrections_applied = Column(JSON, default=[])

    # Verification details
    verification_status = Column(String(30), nullable=False, default="pending", index=True)
    verification_result = Column(String(30))
    qa_comments = Column(Text)
    verified_by = Column(UUID(as_uuid=True))
    verified_at = Column(DateTime)

    # Job metadata from InstaNote
    job_metadata = Column(JSON, default={})
    retrieval_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    error_report = relationship("ErrorReportModel")


class ErrorAuditLogModel(Base):
    """SQLAlchemy model for error audit logs"""

    __tablename__ = "error_audit_logs"

    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    error_id = Column(
        UUID(as_uuid=True), ForeignKey("error_reports.error_id"), nullable=False
    )
    action_type = Column(String(50), nullable=False, index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    performed_by = Column(UUID(as_uuid=True), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    reason = Column(Text)

    # Relationships
    error_report = relationship("ErrorReportModel", back_populates="audit_logs")


class ErrorValidationModel(Base):
    """SQLAlchemy model for error validations"""

    __tablename__ = "error_validations"

    validation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    error_id = Column(
        UUID(as_uuid=True), ForeignKey("error_reports.error_id"), nullable=False
    )
    validation_type = Column(String(50), nullable=False, index=True)
    is_valid = Column(
        String(10), nullable=False
    )  # Using string for boolean compatibility
    validation_details = Column(JSON)
    validated_at = Column(DateTime, default=datetime.utcnow)
    validated_by = Column(UUID(as_uuid=True), nullable=False)

    # Relationships
    error_report = relationship("ErrorReportModel", back_populates="validations")


class ErrorCategoryModel(Base):
    """SQLAlchemy model for error categories"""

    __tablename__ = "error_categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    is_active = Column(
        String(10), nullable=False, default="true"
    )  # Using string for boolean compatibility
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
