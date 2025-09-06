"""
Submit Error Report Use Case

This use case handles the submission of new error reports.
It orchestrates domain validation, persistence, and event publishing.
"""

from datetime import datetime
from uuid import UUID, uuid4

from error_reporting_service.application.dto.requests import (
    SubmitErrorReportRequest,
)
from error_reporting_service.application.dto.responses import (
    SubmitErrorReportResponse,
)
from error_reporting_service.application.ports.secondary.event_publisher_port import (
    EventPublisher,
)
from error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository,
)
from error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    AudioQuality,
    SpeakerClarity,
    BackgroundNoise,
    NumberOfSpeakers,
    EnhancedMetadata,
)
from src.shared.domain.value_objects import BucketType, ErrorStatus, SeverityLevel
from error_reporting_service.domain.events.domain_events import ErrorReportedEvent
from error_reporting_service.domain.services.categorization_service import (
    ErrorCategorizationService,
)
from error_reporting_service.domain.services.validation_service import (
    ErrorValidationService,
)


class SubmitErrorReportUseCase:
    """
    Use case for submitting error reports.

    This use case coordinates the process of validating, saving, and publishing
    events for new error reports.
    """

    def __init__(
        self,
        repository: ErrorReportRepository,
        event_publisher: EventPublisher,
        validation_service: ErrorValidationService,
        categorization_service: ErrorCategorizationService,
    ):
        """
        Initialize the use case with its dependencies.

        Args:
            repository: Repository for error report persistence
            event_publisher: Publisher for domain events
            validation_service: Service for error validation
            categorization_service: Service for error categorization
        """
        self._repository = repository
        self._event_publisher = event_publisher
        self._validation_service = validation_service
        self._categorization_service = categorization_service

    async def execute(
        self, request: SubmitErrorReportRequest
    ) -> SubmitErrorReportResponse:
        """
        Execute the submit error report use case.

        Args:
            request: The error report submission request

        Returns:
            Response containing the result of the submission

        Raises:
            ValueError: If validation fails
            RepositoryError: If persistence fails
            EventPublishingError: If event publishing fails
        """

        # 1. Create domain entity from request
        error_report = self._create_error_report_from_request(request)

        # 2. Validate business rules
        self._validate_error_report(error_report)

        # 3. Persist error report
        saved_error = await self._repository.save(error_report)

        # 4. Publish domain event
        await self._publish_error_reported_event(saved_error)

        # 5. Return success response
        return SubmitErrorReportResponse(
            error_id=str(saved_error.error_id),
            status="success",
            message="Error report with enhanced metadata submitted successfully",
            submission_timestamp=saved_error.reported_at.isoformat(),
            vector_db_id=saved_error.vector_db_id,
            validation_warnings=[],
        )

    def _create_error_report_from_request(
        self, request: SubmitErrorReportRequest
    ) -> ErrorReport:
        """
        Create a domain entity from the request DTO with enhanced metadata.

        Args:
            request: The error report submission request

        Returns:
            ErrorReport domain entity
        """
        # Create enhanced metadata object
        enhanced_metadata = EnhancedMetadata(
            audio_quality=AudioQuality(request.enhanced_metadata.audio_quality),
            speaker_clarity=SpeakerClarity(request.enhanced_metadata.speaker_clarity),
            background_noise=BackgroundNoise(request.enhanced_metadata.background_noise),
            number_of_speakers=NumberOfSpeakers(request.enhanced_metadata.number_of_speakers),
            overlapping_speech=request.enhanced_metadata.overlapping_speech,
            requires_specialized_knowledge=request.enhanced_metadata.requires_specialized_knowledge,
            additional_notes=request.enhanced_metadata.additional_notes,
        )

        return ErrorReport(
            error_id=uuid4(),
            job_id=UUID(request.job_id),
            speaker_id=UUID(request.speaker_id),
            client_id=UUID(request.client_id),
            reported_by=UUID(request.reported_by),
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            error_categories=request.error_categories,
            severity_level=SeverityLevel(request.severity_level),
            start_position=request.start_position,
            end_position=request.end_position,
            context_notes=request.context_notes,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow(),
            bucket_type=BucketType(request.bucket_type),
            enhanced_metadata=enhanced_metadata,
            status=ErrorStatus.SUBMITTED,
            metadata=request.metadata or {},
        )

    def _validate_error_report(self, error_report: ErrorReport) -> None:
        """
        Validate the error report using domain services.

        Args:
            error_report: The error report to validate

        Raises:
            ValueError: If validation fails
        """
        # Validate error categories
        if not self._validation_service.validate_error_categories(
            error_report.error_categories
        ):
            raise ValueError("Invalid error categories")

        # Validate context integrity
        if not self._validation_service.validate_context_integrity(error_report):
            raise ValueError("Invalid error context or position")

    async def _publish_error_reported_event(self, error_report: ErrorReport) -> None:
        """
        Publish the error reported domain event.

        Args:
            error_report: The error report that was saved
        """
        event = ErrorReportedEvent(
            event_id=str(uuid4()),
            correlation_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            error_id=str(error_report.error_id),
            speaker_id=str(error_report.speaker_id),
            job_id=str(error_report.job_id),
            original_text=error_report.original_text,
            corrected_text=error_report.corrected_text,
            categories=error_report.error_categories,
            severity=error_report.severity_level.value,
            reported_by=str(error_report.reported_by),
            metadata=error_report.metadata,
        )

        await self._event_publisher.publish_error_reported(event)
