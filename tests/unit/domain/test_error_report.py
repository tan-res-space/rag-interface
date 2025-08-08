"""
Unit tests for ErrorReport domain entity.

Following TDD principles - tests are written first to define the expected behavior.
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Dict, Any

# Import will be available after we create the entity
from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport, 
    SeverityLevel, 
    ErrorStatus
)


class TestErrorReportEntity:
    """Test suite for ErrorReport domain entity"""
    
    def test_create_valid_error_report(self):
        """Test creating a valid error report with all required fields"""
        # Arrange
        error_id = uuid4()
        job_id = uuid4()
        speaker_id = uuid4()
        reported_by = uuid4()
        original_text = "The patient has diabetis"
        corrected_text = "The patient has diabetes"
        error_categories = ["medical_terminology"]
        severity_level = SeverityLevel.HIGH
        start_position = 16
        end_position = 24
        error_timestamp = datetime.utcnow()
        reported_at = datetime.utcnow()
        
        # Act
        error_report = ErrorReport(
            error_id=error_id,
            job_id=job_id,
            speaker_id=speaker_id,
            reported_by=reported_by,
            original_text=original_text,
            corrected_text=corrected_text,
            error_categories=error_categories,
            severity_level=severity_level,
            start_position=start_position,
            end_position=end_position,
            error_timestamp=error_timestamp,
            reported_at=reported_at
        )
        
        # Assert
        assert error_report.error_id == error_id
        assert error_report.job_id == job_id
        assert error_report.speaker_id == speaker_id
        assert error_report.reported_by == reported_by
        assert error_report.original_text == original_text
        assert error_report.corrected_text == corrected_text
        assert error_report.error_categories == error_categories
        assert error_report.severity_level == severity_level
        assert error_report.start_position == start_position
        assert error_report.end_position == end_position
        assert error_report.error_timestamp == error_timestamp
        assert error_report.reported_at == reported_at
        assert error_report.status == ErrorStatus.PENDING  # Default status
    
    def test_invalid_position_range_raises_error(self):
        """Test that invalid position range raises validation error"""
        with pytest.raises(ValueError, match="end_position must be greater than start_position"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="Test text",
                corrected_text="Corrected text",
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=10,
                end_position=5,  # Invalid: less than start_position
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )
    
    def test_same_original_and_corrected_text_raises_error(self):
        """Test that identical original and corrected text raises validation error"""
        with pytest.raises(ValueError, match="corrected_text must differ from original_text"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="Same text",
                corrected_text="Same text",  # Invalid: same as original
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=9,
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )
    
    def test_empty_error_categories_raises_error(self):
        """Test that empty error categories raises validation error"""
        with pytest.raises(ValueError, match="error_categories cannot be empty"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="Test text",
                corrected_text="Corrected text",
                error_categories=[],  # Invalid: empty list
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=9,
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )
    
    def test_error_report_with_optional_fields(self):
        """Test creating error report with optional fields"""
        # Arrange
        context_notes = "Common misspelling in medical terminology"
        metadata = {"audio_quality": "good", "confidence_score": 0.95}
        
        # Act
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="diabetis",
            corrected_text="diabetes",
            error_categories=["medical_terminology", "spelling"],
            severity_level=SeverityLevel.HIGH,
            start_position=0,
            end_position=8,
            context_notes=context_notes,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow(),
            metadata=metadata
        )
        
        # Assert
        assert error_report.context_notes == context_notes
        assert error_report.metadata == metadata
    
    def test_error_report_equality(self):
        """Test error report equality based on error_id"""
        # Arrange
        error_id = uuid4()
        
        error_report1 = ErrorReport(
            error_id=error_id,
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="test1",
            corrected_text="corrected1",
            error_categories=["grammar"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=5,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )
        
        error_report2 = ErrorReport(
            error_id=error_id,  # Same ID
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="test2",  # Different content
            corrected_text="corrected2",
            error_categories=["spelling"],
            severity_level=SeverityLevel.HIGH,
            start_position=0,
            end_position=5,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )
        
        # Act & Assert
        assert error_report1 == error_report2  # Should be equal based on ID
        assert hash(error_report1) == hash(error_report2)
    
    def test_error_report_string_representation(self):
        """Test error report string representation"""
        # Arrange
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="test",
            corrected_text="corrected",
            error_categories=["grammar"],
            severity_level=SeverityLevel.MEDIUM,
            start_position=0,
            end_position=4,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )
        
        # Act
        str_repr = str(error_report)
        
        # Assert
        assert "ErrorReport" in str_repr
        assert str(error_report.error_id) in str_repr
        assert error_report.severity_level.value in str_repr


class TestSeverityLevel:
    """Test suite for SeverityLevel enum"""
    
    def test_severity_level_values(self):
        """Test that all severity levels have correct values"""
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.CRITICAL.value == "critical"
    
    def test_severity_level_ordering(self):
        """Test severity level ordering for comparison"""
        # This will be implemented if we add ordering to the enum
        pass


class TestErrorStatus:
    """Test suite for ErrorStatus enum"""
    
    def test_error_status_values(self):
        """Test that all error statuses have correct values"""
        assert ErrorStatus.PENDING.value == "pending"
        assert ErrorStatus.PROCESSED.value == "processed"
        assert ErrorStatus.ARCHIVED.value == "archived"
