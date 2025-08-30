"""
Request DTOs for the Error Reporting Service application layer.

These DTOs define the structure of incoming requests to use cases.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SubmitErrorReportRequest:
    """
    Request DTO for submitting an error report.

    Contains all the information needed to create a new error report.
    """

    job_id: str
    speaker_id: str
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: str
    start_position: int
    end_position: int
    reported_by: str
    context_notes: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Set default metadata if None"""
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


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
    Filters for error report search.
    """

    severity_levels: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    speaker_id: Optional[str] = None
    job_id: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    text_search: Optional[str] = None


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
