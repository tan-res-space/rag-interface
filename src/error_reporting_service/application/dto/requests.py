"""
Request DTOs for the Error Reporting Service application layer.

These DTOs define the structure of incoming requests to use cases.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class EnhancedMetadataRequest:
    """
    Request DTO for enhanced metadata fields.
    """

    # Core metadata
    audio_quality: str  # good, fair, poor
    speaker_clarity: str  # clear, somewhat_clear, unclear, very_unclear
    background_noise: str  # none, low, medium, high

    # Enhanced metadata
    number_of_speakers: str  # one, two, three, four, five
    overlapping_speech: bool
    requires_specialized_knowledge: bool
    additional_notes: Optional[str] = None


@dataclass(frozen=True)
class SubmitErrorReportRequest:
    """
    Request DTO for submitting an error report with enhanced metadata.

    Contains all the information needed to create a new error report.
    """

    job_id: str
    speaker_id: str
    client_id: str
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: str
    start_position: int
    end_position: int
    reported_by: str

    # Quality-based bucket management
    bucket_type: str  # no_touch, low_touch, medium_touch, high_touch

    # Enhanced metadata
    enhanced_metadata: EnhancedMetadataRequest

    # Optional fields
    context_notes: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Set default metadata if None and validate enhanced metadata"""
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

        # Validate additional_notes length
        if (self.enhanced_metadata.additional_notes and
            len(self.enhanced_metadata.additional_notes) > 1000):
            raise ValueError("additional_notes cannot exceed 1000 characters")


@dataclass(frozen=True)
class GetErrorReportRequest:
    """
    Request DTO for retrieving an error report by ID.
    """

    error_id: str
    requested_by: str
    include_metadata: bool = True


@dataclass(frozen=True)
class ErrorFilters:
    """
    Filters for error report search with enhanced metadata support.
    """

    severity_levels: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    speaker_id: Optional[str] = None
    client_id: Optional[str] = None
    job_id: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    text_search: Optional[str] = None

    # Quality-based bucket filters
    bucket_types: Optional[List[str]] = None

    # Enhanced metadata filters
    audio_quality: Optional[List[str]] = None
    speaker_clarity: Optional[List[str]] = None
    background_noise: Optional[List[str]] = None
    number_of_speakers: Optional[List[str]] = None
    overlapping_speech: Optional[bool] = None
    requires_specialized_knowledge: Optional[bool] = None


@dataclass(frozen=True)
class PaginationParams:
    """
    Pagination parameters for search requests.
    """

    page: int = 1
    size: int = 10

    def __post_init__(self):
        """Validate pagination parameters"""
        if self.page <= 0 or self.size <= 0:
            raise ValueError("Invalid pagination parameters")


@dataclass(frozen=True)
class SortParams:
    """
    Sorting parameters for search requests.
    """

    field: str = "created_at"
    direction: str = "desc"  # "asc" or "desc"


@dataclass(frozen=True)
class SearchErrorsRequest:
    """
    Request DTO for searching error reports.
    """

    requested_by: str
    filters: ErrorFilters
    pagination: PaginationParams
    sort: SortParams


@dataclass(frozen=True)
class GetErrorReportRequest:
    """
    Request DTO for retrieving an error report by ID.
    """

    error_id: str
    requested_by: str


@dataclass(frozen=True)
class UpdateErrorReportRequest:
    """
    Request DTO for updating an error report.
    """

    error_id: str
    updated_by: str
    updates: Dict[str, Any]


@dataclass(frozen=True)
class SearchErrorReportsRequest:
    """
    Request DTO for searching error reports.
    """

    speaker_id: Optional[str] = None
    job_id: Optional[str] = None
    error_categories: Optional[List[str]] = None
    severity_level: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = 1
    limit: int = 20
    requested_by: str = ""


@dataclass(frozen=True)
class AssignSpeakerBucketRequest:
    """
    Request DTO for assigning a speaker to a bucket.
    """

    speaker_id: str
    bucket_type: str  # no_touch, low_touch, medium_touch, high_touch
    assignment_reason: str
    assigned_by: str
    assignment_type: str = "manual"  # manual, automatic, system


@dataclass(frozen=True)
class GetSpeakerHistoryRequest:
    """
    Request DTO for retrieving speaker bucket history.
    """

    speaker_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = None
    requested_by: str = ""


@dataclass(frozen=True)
class GetSpeakerPerformanceRequest:
    """
    Request DTO for retrieving speaker performance metrics.
    """

    speaker_id: str
    requested_by: str = ""


@dataclass(frozen=True)
class PullVerificationJobsRequest:
    """
    Request DTO for pulling jobs from InstaNote Database for verification.
    """

    speaker_id: str
    date_range: Dict[str, str]  # {"start_date": "ISO date", "end_date": "ISO date"}
    error_types: Optional[List[str]] = None
    max_jobs: int = 10
    requested_by: str = ""


@dataclass(frozen=True)
class VerifyCorrectionRequest:
    """
    Request DTO for verifying correction results.
    """

    verification_id: str
    job_id: str
    error_id: str
    verification_result: str  # rectified, not_rectified, partially_rectified, not_applicable
    qa_comments: Optional[str] = None
    verified_by: str = ""


@dataclass(frozen=True)
class GetDashboardMetricsRequest:
    """
    Request DTO for retrieving dashboard metrics.
    """

    metric_type: str  # bucket_overview, performance_metrics, metadata_insights
    time_period: Optional[str] = None  # last_7_days, last_30_days, last_90_days
    requested_by: str = ""
