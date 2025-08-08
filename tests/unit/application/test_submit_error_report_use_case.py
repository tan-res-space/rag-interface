"""
Unit tests for SubmitErrorReportUseCase.

Following TDD principles - tests define the expected behavior.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from datetime import datetime

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport, SeverityLevel, ErrorStatus
)
from src.error_reporting_service.domain.services.validation_service import (
    ErrorValidationService
)
from src.error_reporting_service.domain.services.categorization_service import (
    ErrorCategorizationService
)
from src.error_reporting_service.application.use_cases.submit_error_report import (
    SubmitErrorReportUseCase
)
from src.error_reporting_service.application.dto.requests import (
    SubmitErrorReportRequest
)
from src.error_reporting_service.application.dto.responses import (
    SubmitErrorReportResponse
)
from src.error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository
)
from src.error_reporting_service.application.ports.secondary.event_publisher_port import (
    EventPublisher
)


class TestSubmitErrorReportUseCase:
    """Test suite for SubmitErrorReportUseCase"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_repository = AsyncMock(spec=ErrorReportRepository)
        self.mock_event_publisher = AsyncMock(spec=EventPublisher)
        self.mock_validation_service = Mock(spec=ErrorValidationService)
        self.mock_categorization_service = Mock(spec=ErrorCategorizationService)
        
        self.use_case = SubmitErrorReportUseCase(
            repository=self.mock_repository,
            event_publisher=self.mock_event_publisher,
            validation_service=self.mock_validation_service,
            categorization_service=self.mock_categorization_service
        )
    
    @pytest.mark.asyncio
    async def test_execute_valid_request_success(self):
        """Test successful execution with valid request"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="The patient has diabetis",
            corrected_text="The patient has diabetes",
            error_categories=["medical_terminology"],
            severity_level="high",
            start_position=16,
            end_position=24,
            context_notes="Common misspelling",
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={"audio_quality": "good"}
        )
        
        # Mock validation service responses
        self.mock_validation_service.validate_error_categories.return_value = True
        self.mock_validation_service.validate_context_integrity.return_value = True
        
        # Mock repository save
        saved_error = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            error_categories=request.error_categories,
            severity_level=SeverityLevel.HIGH,
            start_position=request.start_position,
            end_position=request.end_position,
            context_notes=request.context_notes,
            error_timestamp=datetime.now(),
            reported_at=datetime.now(),
            metadata=request.metadata
        )
        self.mock_repository.save.return_value = saved_error
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert isinstance(response, SubmitErrorReportResponse)
        assert response.status == "success"
        assert "successfully" in response.message
        assert response.error_id == str(saved_error.error_id)
        assert response.validation_warnings == []
        
        # Verify interactions
        self.mock_validation_service.validate_error_categories.assert_called_once()
        self.mock_validation_service.validate_context_integrity.assert_called_once()
        self.mock_repository.save.assert_called_once()
        self.mock_event_publisher.publish_error_reported.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_invalid_categories_raises_error(self):
        """Test that invalid categories raise ValueError"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="test",
            corrected_text="corrected",
            error_categories=["invalid_category"],
            severity_level="low",
            start_position=0,
            end_position=4,
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={}
        )
        
        # Mock validation service to return False for invalid categories
        self.mock_validation_service.validate_error_categories.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid error categories"):
            await self.use_case.execute(request)
        
        # Verify repository and event publisher were not called
        self.mock_repository.save.assert_not_called()
        self.mock_event_publisher.publish_error_reported.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_invalid_context_raises_error(self):
        """Test that invalid context raises ValueError"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="test",
            corrected_text="corrected",
            error_categories=["grammar"],
            severity_level="low",
            start_position=0,
            end_position=4,
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={}
        )
        
        # Mock validation service responses
        self.mock_validation_service.validate_error_categories.return_value = True
        self.mock_validation_service.validate_context_integrity.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid error context or position"):
            await self.use_case.execute(request)
        
        # Verify repository and event publisher were not called
        self.mock_repository.save.assert_not_called()
        self.mock_event_publisher.publish_error_reported.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_repository_error_propagates(self):
        """Test that repository errors are propagated"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="test",
            corrected_text="corrected",
            error_categories=["grammar"],
            severity_level="low",
            start_position=0,
            end_position=4,
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={}
        )
        
        # Mock validation service responses
        self.mock_validation_service.validate_error_categories.return_value = True
        self.mock_validation_service.validate_context_integrity.return_value = True
        
        # Mock repository to raise exception
        self.mock_repository.save.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await self.use_case.execute(request)
        
        # Verify event publisher was not called
        self.mock_event_publisher.publish_error_reported.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_creates_correct_domain_entity(self):
        """Test that the use case creates the correct domain entity"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="diabetis",
            corrected_text="diabetes",
            error_categories=["medical_terminology", "spelling"],
            severity_level="high",
            start_position=0,
            end_position=8,
            context_notes="Medical term misspelling",
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={"confidence": 0.95}
        )
        
        # Mock validation service responses
        self.mock_validation_service.validate_error_categories.return_value = True
        self.mock_validation_service.validate_context_integrity.return_value = True
        
        # Mock repository save to capture the entity
        saved_error = None
        async def capture_save(error_report):
            nonlocal saved_error
            saved_error = error_report
            return error_report
        
        self.mock_repository.save.side_effect = capture_save
        
        # Act
        await self.use_case.execute(request)
        
        # Assert
        assert saved_error is not None
        assert saved_error.original_text == request.original_text
        assert saved_error.corrected_text == request.corrected_text
        assert saved_error.error_categories == request.error_categories
        assert saved_error.severity_level == SeverityLevel.HIGH
        assert saved_error.start_position == request.start_position
        assert saved_error.end_position == request.end_position
        assert saved_error.context_notes == request.context_notes
        assert saved_error.metadata == request.metadata
        assert saved_error.status == ErrorStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_execute_publishes_correct_event(self):
        """Test that the use case publishes the correct domain event"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="test error",
            corrected_text="test correction",
            error_categories=["grammar"],
            severity_level="medium",
            start_position=0,
            end_position=10,
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={}
        )
        
        # Mock validation service responses
        self.mock_validation_service.validate_error_categories.return_value = True
        self.mock_validation_service.validate_context_integrity.return_value = True
        
        # Mock repository save
        saved_error = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            error_categories=request.error_categories,
            severity_level=SeverityLevel.MEDIUM,
            start_position=request.start_position,
            end_position=request.end_position,
            error_timestamp=datetime.now(),
            reported_at=datetime.now()
        )
        self.mock_repository.save.return_value = saved_error
        
        # Act
        await self.use_case.execute(request)
        
        # Assert
        self.mock_event_publisher.publish_error_reported.assert_called_once()
        
        # Get the event that was published
        call_args = self.mock_event_publisher.publish_error_reported.call_args
        published_event = call_args[0][0]
        
        assert published_event.error_id == str(saved_error.error_id)
        assert published_event.speaker_id == str(saved_error.speaker_id)
        assert published_event.job_id == str(saved_error.job_id)
        assert published_event.original_text == saved_error.original_text
        assert published_event.corrected_text == saved_error.corrected_text
        assert published_event.categories == saved_error.error_categories
        assert published_event.severity == saved_error.severity_level.value
