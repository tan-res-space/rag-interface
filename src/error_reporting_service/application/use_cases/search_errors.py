"""
Search Errors Use Case

This use case handles searching and filtering error reports.
It includes authorization checks, caching, pagination, and sorting.
"""

import hashlib
import json
from typing import Any, Dict, List

from src.error_reporting_service.application.dto.requests import SearchErrorsRequest
from src.error_reporting_service.application.dto.responses import (
    PaginatedErrorReports,
    SearchErrorsResponse,
)
from src.error_reporting_service.application.ports.secondary.authorization_port import (
    AuthorizationPort,
)
from src.error_reporting_service.application.ports.secondary.cache_port import CachePort
from src.error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository,
)
from src.error_reporting_service.domain.entities.error_report import ErrorReport


class SearchErrorsUseCase:
    """
    Use case for searching error reports.

    This use case coordinates authorization checks, cache lookups,
    filtering, pagination, and sorting for error report searches.
    """

    def __init__(
        self,
        repository: ErrorReportRepository,
        cache: CachePort,
        authorization: AuthorizationPort,
    ):
        """
        Initialize the use case with required dependencies.

        Args:
            repository: Repository for error report persistence
            cache: Cache for performance optimization
            authorization: Authorization service for access control
        """
        self._repository = repository
        self._cache = cache
        self._authorization = authorization

    async def execute(self, request: SearchErrorsRequest) -> SearchErrorsResponse:
        """
        Execute the search errors use case.

        Args:
            request: The search request with filters and pagination

        Returns:
            Response containing search results and pagination info

        Raises:
            PermissionError: If user lacks search permissions
            ValueError: If search parameters are invalid
        """

        # 1. Check authorization
        if not await self._authorization.can_search_errors(request.requested_by):
            raise PermissionError("Search access denied")

        # 2. Validate pagination parameters
        self._validate_pagination(request.pagination)

        # 3. Try cache first
        cache_key = self._generate_cache_key(request)
        cached_results = await self._get_from_cache(cache_key)
        if cached_results:
            return self._create_response_from_cache(cached_results)

        # 4. Build search filters
        search_filters = self._build_search_filters(request)

        # 5. Execute search
        error_reports = await self._repository.search(search_filters)
        total_count = await self._repository.count_by_filters(search_filters)

        # 6. Apply pagination
        paginated_results = self._paginate_results(
            error_reports, total_count, request.pagination
        )

        # 7. Cache the results
        await self._cache_results(cache_key, paginated_results)

        # 8. Return response
        return SearchErrorsResponse(results=paginated_results, status="success")

    def _validate_pagination(self, pagination) -> None:
        """
        Validate pagination parameters.

        Args:
            pagination: Pagination parameters

        Raises:
            ValueError: If pagination parameters are invalid
        """
        if pagination.page <= 0 or pagination.size <= 0:
            raise ValueError("Invalid pagination parameters")

        if pagination.size > 100:  # Maximum page size limit
            raise ValueError("Page size cannot exceed 100")

    def _generate_cache_key(self, request: SearchErrorsRequest) -> str:
        """
        Generate a cache key for the search request.

        Args:
            request: The search request

        Returns:
            Cache key string
        """
        # Create a deterministic hash of the search parameters
        search_params = {
            "filters": {
                "severity_levels": request.filters.severity_levels,
                "categories": request.filters.categories,
                "speaker_id": request.filters.speaker_id,
                "job_id": request.filters.job_id,
                "status": request.filters.status,
                "date_from": (
                    request.filters.date_from.isoformat()
                    if request.filters.date_from
                    else None
                ),
                "date_to": (
                    request.filters.date_to.isoformat()
                    if request.filters.date_to
                    else None
                ),
                "text_search": request.filters.text_search,
            },
            "pagination": {
                "page": request.pagination.page,
                "size": request.pagination.size,
            },
            "sort": {"field": request.sort.field, "direction": request.sort.direction},
        }

        params_json = json.dumps(search_params, sort_keys=True)
        params_hash = hashlib.md5(params_json.encode()).hexdigest()

        return f"search_errors:{params_hash}"

    async def _get_from_cache(self, cache_key: str) -> Dict[str, Any]:
        """
        Attempt to retrieve search results from cache.

        Args:
            cache_key: The cache key

        Returns:
            Cached search results if found, None otherwise
        """
        try:
            return await self._cache.get_search_results(cache_key)
        except Exception:
            # Cache errors should not break the flow
            return None

    def _build_search_filters(self, request: SearchErrorsRequest) -> Dict[str, Any]:
        """
        Build search filters for the repository query.

        Args:
            request: The search request

        Returns:
            Dictionary of search filters
        """
        filters = {}

        if request.filters.severity_levels:
            filters["severity_levels"] = request.filters.severity_levels

        if request.filters.categories:
            filters["categories"] = request.filters.categories

        if request.filters.speaker_id:
            filters["speaker_id"] = request.filters.speaker_id

        if request.filters.job_id:
            filters["job_id"] = request.filters.job_id

        if request.filters.status:
            filters["status"] = request.filters.status

        if request.filters.date_from:
            filters["date_from"] = request.filters.date_from

        if request.filters.date_to:
            filters["date_to"] = request.filters.date_to

        if request.filters.text_search:
            filters["text_search"] = request.filters.text_search

        # Add pagination and sorting
        filters["limit"] = request.pagination.size
        filters["offset"] = (request.pagination.page - 1) * request.pagination.size
        filters["sort_field"] = request.sort.field
        filters["sort_direction"] = request.sort.direction

        return filters

    def _paginate_results(
        self, error_reports: List[ErrorReport], total_count: int, pagination
    ) -> PaginatedErrorReports:
        """
        Create paginated results from error reports.

        Args:
            error_reports: List of error reports
            total_count: Total number of matching records
            pagination: Pagination parameters

        Returns:
            PaginatedErrorReports object
        """
        return PaginatedErrorReports(
            items=error_reports,
            total=total_count,
            page=pagination.page,
            size=pagination.size,
            pages=0,  # Will be calculated in __post_init__
        )

    async def _cache_results(
        self, cache_key: str, results: PaginatedErrorReports
    ) -> None:
        """
        Cache the search results for future requests.

        Args:
            cache_key: The cache key
            results: The search results to cache
        """
        try:
            # Serialize results for caching
            cache_data = {
                "items": [self._serialize_error_report(item) for item in results.items],
                "total": results.total,
                "page": results.page,
                "size": results.size,
                "pages": results.pages,
            }

            # Cache for 5 minutes (search results change frequently)
            await self._cache.set_search_results(cache_key, cache_data, ttl=300)
        except Exception:
            # Cache errors should not break the flow
            pass

    def _serialize_error_report(self, error_report: ErrorReport) -> Dict[str, Any]:
        """
        Serialize error report for caching.

        Args:
            error_report: The error report to serialize

        Returns:
            Dictionary representation of the error report
        """
        return {
            "error_id": str(error_report.error_id),
            "job_id": str(error_report.job_id),
            "speaker_id": str(error_report.speaker_id),
            "reported_by": str(error_report.reported_by),
            "original_text": error_report.original_text,
            "corrected_text": error_report.corrected_text,
            "error_categories": error_report.error_categories,
            "severity_level": error_report.severity_level.value,
            "start_position": error_report.start_position,
            "end_position": error_report.end_position,
            "context_notes": error_report.context_notes,
            "error_timestamp": error_report.error_timestamp.isoformat(),
            "reported_at": error_report.reported_at.isoformat(),
            "status": error_report.status.value,
            "metadata": error_report.metadata,
        }

    def _create_response_from_cache(
        self, cached_data: Dict[str, Any]
    ) -> SearchErrorsResponse:
        """
        Create response from cached search results.

        Args:
            cached_data: Cached search results

        Returns:
            SearchErrorsResponse object
        """
        # Deserialize error reports from cache
        error_reports = [
            self._deserialize_error_report(item_data)
            for item_data in cached_data["items"]
        ]

        paginated_results = PaginatedErrorReports(
            items=error_reports,
            total=cached_data["total"],
            page=cached_data["page"],
            size=cached_data["size"],
            pages=cached_data["pages"],
        )

        return SearchErrorsResponse(results=paginated_results, status="success")

    def _deserialize_error_report(self, data: Dict[str, Any]) -> ErrorReport:
        """
        Deserialize error report from cache data.

        Args:
            data: Dictionary representation of the error report

        Returns:
            ErrorReport entity
        """
        from datetime import datetime
        from uuid import UUID

        from src.error_reporting_service.domain.entities.error_report import (
            ErrorStatus,
            SeverityLevel,
        )

        return ErrorReport(
            error_id=UUID(data["error_id"]),
            job_id=UUID(data["job_id"]),
            speaker_id=UUID(data["speaker_id"]),
            reported_by=UUID(data["reported_by"]),
            original_text=data["original_text"],
            corrected_text=data["corrected_text"],
            error_categories=data["error_categories"],
            severity_level=SeverityLevel(data["severity_level"]),
            start_position=data["start_position"],
            end_position=data["end_position"],
            context_notes=data["context_notes"],
            error_timestamp=datetime.fromisoformat(data["error_timestamp"]),
            reported_at=datetime.fromisoformat(data["reported_at"]),
            status=ErrorStatus(data["status"]),
            metadata=data["metadata"],
        )
