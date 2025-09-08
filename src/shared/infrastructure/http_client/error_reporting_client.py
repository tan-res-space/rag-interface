"""
Error Reporting Service Client

HTTP client for communicating with the Error Reporting Service.
Provides methods for error report management and analytics.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class ErrorReportingClient(BaseHTTPClient):
    """
    Client for Error Reporting Service.
    
    Provides methods for creating, retrieving, and managing error reports.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3,
        auth_token: Optional[str] = None
    ):
        """
        Initialize Error Reporting client.
        
        Args:
            base_url: Base URL of the Error Reporting Service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            auth_token: Authentication token
        """
        super().__init__(base_url, timeout, max_retries, auth_token)

    async def create_error_report(
        self,
        job_id: str,
        speaker_id: str,
        client_id: str,
        original_text: str,
        corrected_text: str,
        error_categories: List[str],
        severity_level: str,
        start_position: int,
        end_position: int,
        context_notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new error report.
        
        Args:
            job_id: ID of the job
            speaker_id: ID of the speaker
            client_id: ID of the client
            original_text: Original text with error
            corrected_text: Corrected text
            error_categories: List of error categories
            severity_level: Severity level of the error
            start_position: Start position of error in text
            end_position: End position of error in text
            context_notes: Optional context notes
            metadata: Optional additional metadata
            
        Returns:
            Created error report data
        """
        payload = {
            "job_id": job_id,
            "speaker_id": speaker_id,
            "client_id": client_id,
            "original_text": original_text,
            "corrected_text": corrected_text,
            "error_categories": error_categories,
            "severity_level": severity_level,
            "start_position": start_position,
            "end_position": end_position,
            "error_timestamp": datetime.utcnow().isoformat(),
        }
        
        if context_notes:
            payload["context_notes"] = context_notes
        
        if metadata:
            payload.update(metadata)
        
        try:
            response = await self.post_json("/api/v1/error-reports", json=payload)
            logger.debug(f"Created error report: {response.get('error_id')}")
            return response
        except Exception as e:
            logger.error(f"Failed to create error report: {e}")
            raise

    async def get_error_report(self, error_id: str) -> Dict[str, Any]:
        """
        Get an error report by ID.
        
        Args:
            error_id: ID of the error report
            
        Returns:
            Error report data
        """
        try:
            response = await self.get_json(f"/api/v1/error-reports/{error_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get error report {error_id}: {e}")
            raise

    async def list_error_reports(
        self,
        limit: int = 100,
        offset: int = 0,
        severity_level: Optional[str] = None,
        speaker_id: Optional[str] = None,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        List error reports with optional filtering.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            severity_level: Filter by severity level
            speaker_id: Filter by speaker ID
            client_id: Filter by client ID
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of error reports with pagination info
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if severity_level:
            params["severity_level"] = severity_level
        if speaker_id:
            params["speaker_id"] = speaker_id
        if client_id:
            params["client_id"] = client_id
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        try:
            response = await self.get_json("/api/v1/error-reports", params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to list error reports: {e}")
            raise

    async def update_error_report(
        self,
        error_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an error report.
        
        Args:
            error_id: ID of the error report
            updates: Fields to update
            
        Returns:
            Updated error report data
        """
        try:
            response = await self.put(f"/api/v1/error-reports/{error_id}", json=updates)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update error report {error_id}: {e}")
            raise

    async def delete_error_report(self, error_id: str) -> bool:
        """
        Delete an error report.
        
        Args:
            error_id: ID of the error report
            
        Returns:
            True if deletion was successful
        """
        try:
            response = await self.delete(f"/api/v1/error-reports/{error_id}")
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Failed to delete error report {error_id}: {e}")
            return False

    async def get_analytics_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics summary for error reports.
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            group_by: Group results by field (severity, speaker, client, etc.)
            
        Returns:
            Analytics summary data
        """
        params = {}
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        if group_by:
            params["group_by"] = group_by
        
        try:
            response = await self.get_json("/api/v1/analytics/summary", params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            raise

    async def get_speaker_performance(
        self,
        speaker_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a specific speaker.
        
        Args:
            speaker_id: ID of the speaker
            start_date: Start date for metrics
            end_date: End date for metrics
            
        Returns:
            Speaker performance data
        """
        params = {}
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        try:
            response = await self.get_json(f"/api/v1/analytics/speakers/{speaker_id}/performance", params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to get speaker performance for {speaker_id}: {e}")
            raise

    async def get_error_trends(
        self,
        period: str = "daily",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get error trends over time.
        
        Args:
            period: Time period for trends (daily, weekly, monthly)
            start_date: Start date for trends
            end_date: End date for trends
            
        Returns:
            Error trends data
        """
        params = {
            "period": period
        }
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        try:
            response = await self.get_json("/api/v1/analytics/trends", params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to get error trends: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if Error Reporting Service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error Reporting Service health check failed: {e}")
            return False


# Convenience function to create client from environment
def create_error_reporting_client_from_env() -> ErrorReportingClient:
    """
    Create Error Reporting client from environment variables.
    
    Environment variables:
    - ERROR_REPORTING_URL: Service URL (default: http://localhost:8000)
    - ERROR_REPORTING_TIMEOUT: Request timeout (default: 30)
    - ERROR_REPORTING_AUTH_TOKEN: Authentication token
    
    Returns:
        Configured Error Reporting client
    """
    import os
    
    base_url = os.getenv("ERROR_REPORTING_URL", "http://localhost:8000")
    timeout = int(os.getenv("ERROR_REPORTING_TIMEOUT", "30"))
    auth_token = os.getenv("ERROR_REPORTING_AUTH_TOKEN")
    
    return ErrorReportingClient(
        base_url=base_url,
        timeout=timeout,
        auth_token=auth_token
    )
