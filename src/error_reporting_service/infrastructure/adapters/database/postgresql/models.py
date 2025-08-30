"""
SQLAlchemy Models for PostgreSQL

This module contains SQLAlchemy ORM models for the PostgreSQL database.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ErrorReportModel(Base):
    """SQLAlchemy model for error reports"""

    __tablename__ = "error_reports"

    error_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    speaker_id = Column(UUID(as_uuid=True), nullable=False, index=True)
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
    status = Column(String(20), nullable=False, default="pending", index=True)
    error_metadata = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    audit_logs = relationship("ErrorAuditLogModel", back_populates="error_report")
    validations = relationship("ErrorValidationModel", back_populates="error_report")


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
