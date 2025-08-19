"""
Response DTOs for the Error Reporting Service application layer.

These DTOs define the structure of responses from use cases.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.error_reporting_service.domain.entities.error_report import ErrorReport


@dataclass(frozen=True)
class SubmitErrorReportResponse:
    """
    Response DTO for error report submission.
    
    Contains the result of submitting an error report.
    """
    
    error_id: str
    status: str
    message: str
    validation_warnings: List[str] = None
    
    def __post_init__(self):
        """Set default validation warnings if None"""
        if self.validation_warnings is None:
            object.__setattr__(self, 'validation_warnings', [])


@dataclass(frozen=True)
class ErrorReportResponse:
    """
    Response DTO for error report data.
    
    Contains error report information for API responses.
    """
    
    error_id: str
    job_id: str
    speaker_id: str
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
    status: str
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
            object.__setattr__(self, 'pages', calculated_pages)
        else:
            object.__setattr__(self, 'pages', 0)


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
