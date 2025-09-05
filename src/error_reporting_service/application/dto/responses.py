"""
Response DTOs for the Error Reporting Service application layer.

These DTOs define the structure of responses from use cases.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.error_reporting_service.domain.entities.error_report import ErrorReport


@dataclass(frozen=True)
class SubmitErrorReportResponse:
    """
    Response DTO for error report submission with enhanced metadata.

    Contains the result of submitting an error report.
    """

    error_id: str
    status: str
    message: str
    submission_timestamp: str
    vector_db_id: Optional[str] = None
    validation_warnings: List[str] = None

    def __post_init__(self):
        """Set default validation warnings if None"""
        if self.validation_warnings is None:
            object.__setattr__(self, "validation_warnings", [])


@dataclass(frozen=True)
class EnhancedMetadataResponse:
    """
    Response DTO for enhanced metadata fields.
    """

    audio_quality: str
    speaker_clarity: str
    background_noise: str
    number_of_speakers: str
    overlapping_speech: bool
    requires_specialized_knowledge: bool
    additional_notes: Optional[str] = None


@dataclass(frozen=True)
class ErrorReportResponse:
    """
    Response DTO for error report data with enhanced metadata.

    Contains error report information for API responses.
    """

    error_id: str
    job_id: str
    speaker_id: str
    client_id: str
    reported_by: str
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: str
    start_position: int
    end_position: int
    context_notes: Optional[str]
    error_timestamp: datetime
    reported_at: datetime

    # Quality-based bucket management
    bucket_type: str
    bucket_display_name: str
    bucket_description: str

    # Enhanced metadata
    enhanced_metadata: EnhancedMetadataResponse

    # System fields
    status: str
    vector_db_id: Optional[str]
    complexity_score: float
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class SearchErrorReportsResponse:
    """
    Response DTO for error report search results.
    """

    error_reports: List[ErrorReportResponse]
    total_count: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool


@dataclass(frozen=True)
class UpdateErrorReportResponse:
    """
    Response DTO for error report update operations.
    """

    error_id: str
    status: str
    message: str
    updated_fields: List[str]


@dataclass(frozen=True)
class GetErrorReportResponse:
    """
    Response DTO for error report retrieval.

    Contains the retrieved error report and status information.
    """

    error_report: ErrorReport
    status: str


@dataclass(frozen=True)
class PaginatedErrorReports:
    """
    Paginated collection of error reports.
    """

    items: List[ErrorReport]
    total: int
    page: int
    size: int
    pages: int

    def __post_init__(self):
        """Calculate total pages"""
        if self.size > 0:
            calculated_pages = (self.total + self.size - 1) // self.size
            object.__setattr__(self, "pages", calculated_pages)
        else:
            object.__setattr__(self, "pages", 0)


@dataclass(frozen=True)
class SearchErrorsResponse:
    """
    Response DTO for error report search.

    Contains search results and pagination information.
    """

    results: PaginatedErrorReports
    status: str


@dataclass(frozen=True)
class DeleteErrorReportResponse:
    """
    Response DTO for error report deletion.

    Contains the status of the deletion operation.
    """

    status: str
    message: str


@dataclass(frozen=True)
class SpeakerBucketHistoryResponse:
    """
    Response DTO for speaker bucket history.
    """

    history_id: str
    speaker_id: str
    bucket_type: str
    previous_bucket: Optional[str]
    assigned_date: datetime
    assigned_by: str
    assignment_reason: str
    assignment_type: str
    transition_description: str
    days_since_assignment: int
    confidence_score: Optional[float] = None


@dataclass(frozen=True)
class SpeakerPerformanceMetricsResponse:
    """
    Response DTO for speaker performance metrics.
    """

    speaker_id: str
    current_bucket: str
    performance_score: float
    rectification_rate: float
    total_errors_reported: int
    errors_rectified: int
    quality_trend: Optional[str]
    recommended_bucket: str
    needs_attention: bool
    should_reassess: bool
    days_in_current_bucket: int
    last_assessment_date: Optional[datetime]


@dataclass(frozen=True)
class VerificationJobResponse:
    """
    Response DTO for verification job data.
    """

    verification_id: str
    job_id: str
    speaker_id: str
    verification_status: str
    verification_result: Optional[str]
    corrections_count: int
    average_confidence: float
    needs_manual_review: bool
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    has_qa_comments: bool


@dataclass(frozen=True)
class DashboardMetricsResponse:
    """
    Response DTO for dashboard metrics.
    """

    metric_type: str
    time_period: str
    data: Dict[str, Any]
    generated_at: datetime


@dataclass(frozen=True)
class BucketDistributionResponse:
    """
    Response DTO for bucket distribution statistics.
    """

    bucket_type: str
    speaker_count: int
    percentage: float
    avg_rectification_rate: float
    avg_days_in_bucket: float


@dataclass(frozen=True)
class ErrorResponse:
    """
    Response DTO for error cases.

    Contains error information and details.
    """

    success: bool
    error: Dict[str, Any]
    timestamp: str
    request_id: str
    version: str
