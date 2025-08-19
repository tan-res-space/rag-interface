"""
Unit tests for ErrorReport domain entity.

Following TDD principles - tests are written first to define the expected behavior.
This test suite covers all business rules, validation logic, and edge cases
as specified in the design document.
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import will be available after we create the entity
from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    SeverityLevel,
    ErrorStatus
)
from tests.factories import ErrorReportFactory, create_medical_error_report


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


class TestErrorReportBusinessRules:
    """Test suite for ErrorReport business rules and validation logic"""

    def test_negative_start_position_raises_error(self):
        """Test that negative start position raises validation error"""
        with pytest.raises(ValueError, match="start_position must be non-negative"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="Test text",
                corrected_text="Corrected text",
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=-1,  # Invalid: negative position
                end_position=5,
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )

    def test_empty_original_text_raises_error(self):
        """Test that empty original text raises validation error"""
        with pytest.raises(ValueError, match="text cannot be empty or whitespace only"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="",  # Invalid: empty text
                corrected_text="Corrected text",
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=5,
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )

    def test_empty_corrected_text_raises_error(self):
        """Test that empty corrected text raises validation error"""
        with pytest.raises(ValueError, match="text cannot be empty or whitespace only"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="Test text",
                corrected_text="",  # Invalid: empty text
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=5,
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )

    def test_whitespace_only_text_raises_error(self):
        """Test that whitespace-only text raises validation error"""
        with pytest.raises(ValueError, match="text cannot be empty or whitespace only"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="   ",  # Invalid: whitespace only
                corrected_text="Corrected text",
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=3,
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )

    def test_position_range_exceeds_text_length_raises_error(self):
        """Test that position range exceeding text length raises validation error"""
        with pytest.raises(ValueError, match="position range exceeds text length"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="Short",  # 5 characters
                corrected_text="Corrected",
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=10,  # Invalid: exceeds text length
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )

    def test_is_critical_method(self):
        """Test the is_critical method for severity checking"""
        # Test critical error
        critical_error = ErrorReportFactory.create(severity_level=SeverityLevel.CRITICAL)
        assert critical_error.is_critical() is True

        # Test non-critical errors
        for severity in [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH]:
            error = ErrorReportFactory.create(severity_level=severity)
            assert error.is_critical() is False

    def test_calculate_error_length_method(self):
        """Test the calculate_error_length method"""
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="The patient has diabetis",
            corrected_text="The patient has diabetes",
            error_categories=["medical_terminology"],
            severity_level=SeverityLevel.HIGH,
            start_position=16,  # "diabetis" starts at position 16
            end_position=24,    # "diabetis" ends at position 24
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert error_report.calculate_error_length() == 8  # "diabetis" is 8 characters

    def test_get_error_text_method(self):
        """Test the get_error_text method to extract the error portion"""
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="The patient has diabetis",
            corrected_text="The patient has diabetes",
            error_categories=["medical_terminology"],
            severity_level=SeverityLevel.HIGH,
            start_position=16,
            end_position=24,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert error_report.get_error_text() == "diabetis"

    def test_get_correction_text_method(self):
        """Test the get_correction_text method to extract the correction portion"""
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="The patient has diabetis",
            corrected_text="The patient has diabetes",
            error_categories=["medical_terminology"],
            severity_level=SeverityLevel.HIGH,
            start_position=16,
            end_position=24,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert error_report.get_correction_text() == "diabetes"


class TestErrorReportFactoryIntegration:
    """Test suite for ErrorReport using factory-generated data"""

    def test_factory_creates_valid_error_reports(self):
        """Test that factory creates valid error reports"""
        error_report = ErrorReportFactory.create()

        # Verify all required fields are present
        assert error_report.error_id is not None
        assert error_report.job_id is not None
        assert error_report.speaker_id is not None
        assert error_report.reported_by is not None
        assert error_report.original_text
        assert error_report.corrected_text
        assert error_report.error_categories
        assert error_report.severity_level in SeverityLevel
        assert error_report.start_position >= 0
        assert error_report.end_position > error_report.start_position
        assert error_report.error_timestamp is not None
        assert error_report.reported_at is not None
        assert error_report.status in ErrorStatus

    def test_factory_creates_medical_error_reports(self):
        """Test that factory creates realistic medical error reports"""
        error_report = create_medical_error_report()

        assert "medical_terminology" in error_report.error_categories
        assert error_report.severity_level == SeverityLevel.HIGH
        assert "pnemonia" in error_report.original_text
        assert "pneumonia" in error_report.corrected_text

    def test_factory_batch_creation(self):
        """Test creating multiple error reports in batch"""
        error_reports = ErrorReportFactory.create_batch(5)

        assert len(error_reports) == 5

        # Verify all reports are unique
        error_ids = [report.error_id for report in error_reports]
        assert len(set(error_ids)) == 5

        # Verify all reports are valid
        for report in error_reports:
            assert report.end_position > report.start_position
            assert report.original_text != report.corrected_text
            assert len(report.error_categories) > 0


class TestErrorReportEdgeCases:
    """Test suite for ErrorReport edge cases and boundary conditions"""

    def test_single_character_error(self):
        """Test error report with single character error"""
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="a",
            corrected_text="A",
            error_categories=["capitalization"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=1,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert error_report.calculate_error_length() == 1
        assert error_report.get_error_text() == "a"
        assert error_report.get_correction_text() == "A"

    def test_maximum_text_length(self):
        """Test error report with maximum allowed text length"""
        long_text = "x" * 5000  # Maximum allowed length
        corrected_text = "X" * 5000

        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text=long_text,
            corrected_text=corrected_text,
            error_categories=["capitalization"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=5000,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert len(error_report.original_text) == 5000
        assert len(error_report.corrected_text) == 5000

    def test_unicode_text_handling(self):
        """Test error report with Unicode characters"""
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="Café résumé naïve",
            corrected_text="Cafe resume naive",
            error_categories=["diacritics"],
            severity_level=SeverityLevel.MEDIUM,
            start_position=0,
            end_position=17,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert "é" in error_report.original_text
        assert "e" in error_report.corrected_text

    def test_multiple_error_categories(self):
        """Test error report with multiple error categories"""
        categories = ["medical_terminology", "spelling", "grammar", "pronunciation"]

        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="The patient has diabetis and hypertention",
            corrected_text="The patient has diabetes and hypertension",
            error_categories=categories,
            severity_level=SeverityLevel.HIGH,
            start_position=16,
            end_position=41,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert len(error_report.error_categories) == 4
        assert all(cat in error_report.error_categories for cat in categories)

    def test_complex_metadata_handling(self):
        """Test error report with complex metadata"""
        complex_metadata = {
            "audio_quality": "good",
            "background_noise": True,
            "confidence_score": 0.95,
            "speaker_accent": "british",
            "technical_issues": ["static", "echo"],
            "nested_data": {
                "recording_device": "microphone_a",
                "room_acoustics": "poor"
            },
            "timestamps": {
                "recording_start": "2023-01-01T10:00:00Z",
                "error_detected": "2023-01-01T10:05:30Z"
            }
        }

        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="Test text",
            corrected_text="Corrected text",
            error_categories=["grammar"],
            severity_level=SeverityLevel.MEDIUM,
            start_position=0,
            end_position=9,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow(),
            metadata=complex_metadata
        )

        assert error_report.metadata["audio_quality"] == "good"
        assert error_report.metadata["nested_data"]["recording_device"] == "microphone_a"
        assert len(error_report.metadata["technical_issues"]) == 2
