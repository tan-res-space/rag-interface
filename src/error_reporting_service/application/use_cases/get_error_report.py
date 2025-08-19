"""
Get Error Report Use Case

This use case handles the retrieval of error reports by ID.
It includes authorization checks, caching, and error handling.
"""

from uuid import UUID
from typing import Optional

from src.error_reporting_service.domain.entities.error_report import ErrorReport
from src.error_reporting_service.application.dto.requests import GetErrorReportRequest
from src.error_reporting_service.application.dto.responses import GetErrorReportResponse
from src.error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository
)
from src.error_reporting_service.application.ports.secondary.cache_port import CachePort
from src.error_reporting_service.application.ports.secondary.authorization_port import (
    AuthorizationPort
)


class GetErrorReportUseCase:
    """
    Use case for retrieving error reports by ID.
    
    This use case coordinates authorization checks, cache lookups,
    and repository access for error report retrieval.
    """
    
    def __init__(
        self,
        repository: ErrorReportRepository,
        cache: CachePort,
        authorization: AuthorizationPort
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
    
    async def execute(self, request: GetErrorReportRequest) -> GetErrorReportResponse:
        """
        Execute the get error report use case.
        
        Args:
            request: The error report retrieval request
            
        Returns:
            Response containing the error report or error information
            
        Raises:
            ValueError: If error ID format is invalid
            PermissionError: If user lacks access permissions
            ValueError: If error report is not found
        """
        
        # 1. Validate error ID format
        try:
            error_uuid = UUID(request.error_id)
        except ValueError:
            raise ValueError("Invalid error ID format")
        
        # 2. Check authorization
        if not await self._authorization.can_access_error_report(
            request.requested_by, request.error_id
        ):
            raise PermissionError("Access denied")
        
        # 3. Try cache first
        cached_error = await self._get_from_cache(request.error_id)
        if cached_error:
            return self._create_response(cached_error, request)
        
        # 4. Get from repository
        error_report = await self._repository.find_by_id(error_uuid)
        if not error_report:
            raise ValueError("Error report not found")
        
        # 5. Cache the result
        await self._cache_error_report(request.error_id, error_report)
        
        # 6. Return response
        return self._create_response(error_report, request)
    
    async def _get_from_cache(self, error_id: str) -> Optional[ErrorReport]:
        """
        Attempt to retrieve error report from cache.
        
        Args:
            error_id: The error report ID
            
        Returns:
            ErrorReport if found in cache, None otherwise
        """
        try:
            cache_key = f"error_report:{error_id}"
            cached_data = await self._cache.get(cache_key)
            
            if cached_data:
                # Convert cached data back to ErrorReport entity
                return self._deserialize_error_report(cached_data)
            
            return None
        except Exception:
            # Cache errors should not break the flow
            return None
    
    async def _cache_error_report(self, error_id: str, error_report: ErrorReport) -> None:
        """
        Cache the error report for future retrieval.
        
        Args:
            error_id: The error report ID
            error_report: The error report to cache
        """
        try:
            cache_key = f"error_report:{error_id}"
            serialized_data = self._serialize_error_report(error_report)
            await self._cache.set(cache_key, serialized_data, ttl=3600)  # 1 hour TTL
        except Exception:
            # Cache errors should not break the flow
            pass
    
    def _serialize_error_report(self, error_report: ErrorReport) -> dict:
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
            "metadata": error_report.metadata
        }
    
    def _deserialize_error_report(self, data: dict) -> ErrorReport:
        """
        Deserialize error report from cache data.
        
        Args:
            data: Dictionary representation of the error report
            
        Returns:
            ErrorReport entity
        """
        from datetime import datetime
        from src.error_reporting_service.domain.entities.error_report import (
            SeverityLevel, ErrorStatus
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
            metadata=data["metadata"]
        )
    
    def _create_response(
        self, 
        error_report: ErrorReport, 
        request: GetErrorReportRequest
    ) -> GetErrorReportResponse:
        """
        Create response DTO from error report entity.
        
        Args:
            error_report: The error report entity
            request: The original request
            
        Returns:
            GetErrorReportResponse DTO
        """
        # Filter metadata if requested
        metadata = error_report.metadata
        if hasattr(request, 'include_metadata') and not request.include_metadata:
            metadata = {}
        
        return GetErrorReportResponse(
            error_report=error_report,
            status="success"
        )
