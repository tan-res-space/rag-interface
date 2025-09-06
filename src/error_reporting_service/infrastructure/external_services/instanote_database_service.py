"""
InstaNote Database Integration Service

Provides integration with InstaNote Database for pulling jobs and retrieving
transcription data for verification workflow.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class InstaNoteDatabaseConfig(BaseModel):
    """Configuration for InstaNote Database service"""
    
    base_url: str = Field(..., description="Base URL for InstaNote Database API")
    api_key: str = Field(..., description="API key for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")


class InstaNoteDatabaseJob(BaseModel):
    """InstaNote Database job model"""
    
    job_id: str = Field(..., description="Unique job identifier")
    speaker_id: str = Field(..., description="Speaker identifier")
    client_id: str = Field(..., description="Client identifier")
    original_draft: str = Field(..., description="Original transcription draft")
    audio_file_url: Optional[str] = Field(None, description="URL to audio file")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Job last update timestamp")
    status: str = Field(..., description="Job status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional job metadata")
    
    # Audio quality metadata
    audio_duration: Optional[float] = Field(None, description="Audio duration in seconds")
    audio_quality_score: Optional[float] = Field(None, description="Audio quality score (0-1)")
    speaker_count: Optional[int] = Field(None, description="Number of speakers detected")
    confidence_score: Optional[float] = Field(None, description="Overall transcription confidence")


class InstaNoteDatabaseService:
    """Service for integrating with InstaNote Database"""

    def __init__(self, config: InstaNoteDatabaseConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()

    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "RAG-Interface-ErrorReporting/2.0"
            }
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )

    async def _close_session(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        await self._ensure_session()
        
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.config.max_retries):
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Resource not found: {url}")
                        return {}
                    elif response.status >= 500:
                        # Server error, retry
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                            continue
                    
                    # Client error or final retry
                    response.raise_for_status()
                    
            except aiohttp.ClientError as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                raise
        
        raise Exception(f"Failed to complete request after {self.config.max_retries} attempts")

    async def get_jobs_for_speaker(
        self,
        speaker_id: str,
        start_date: datetime,
        end_date: datetime,
        error_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[InstaNoteDatabaseJob]:
        """
        Get jobs for a specific speaker within a date range.
        
        Args:
            speaker_id: Speaker identifier
            start_date: Start date for job search
            end_date: End date for job search
            error_types: Optional filter by error types
            limit: Maximum number of jobs to return
            
        Returns:
            List of InstaNote Database jobs
        """
        logger.info(f"Fetching jobs for speaker {speaker_id} from {start_date} to {end_date}")
        
        params = {
            "speaker_id": speaker_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "limit": limit,
            "status": "completed"  # Only get completed jobs
        }
        
        if error_types:
            params["error_types"] = ",".join(error_types)
        
        try:
            response = await self._make_request("GET", "/api/v1/jobs", params=params)
            
            jobs = []
            for job_data in response.get("jobs", []):
                try:
                    job = InstaNoteDatabaseJob(**job_data)
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Failed to parse job data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(jobs)} jobs for speaker {speaker_id}")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to fetch jobs for speaker {speaker_id}: {e}")
            raise

    async def get_job_by_id(self, job_id: str) -> Optional[InstaNoteDatabaseJob]:
        """
        Get a specific job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            InstaNote Database job or None if not found
        """
        logger.info(f"Fetching job {job_id}")
        
        try:
            response = await self._make_request("GET", f"/api/v1/jobs/{job_id}")
            
            if not response:
                return None
            
            job = InstaNoteDatabaseJob(**response)
            logger.info(f"Retrieved job {job_id}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to fetch job {job_id}: {e}")
            raise

    async def get_jobs_with_errors(
        self,
        start_date: datetime,
        end_date: datetime,
        error_categories: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[InstaNoteDatabaseJob]:
        """
        Get jobs that have reported errors within a date range.
        
        Args:
            start_date: Start date for job search
            end_date: End date for job search
            error_categories: Optional filter by error categories
            limit: Maximum number of jobs to return
            
        Returns:
            List of jobs with reported errors
        """
        logger.info(f"Fetching jobs with errors from {start_date} to {end_date}")
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "has_errors": "true",
            "limit": limit
        }
        
        if error_categories:
            params["error_categories"] = ",".join(error_categories)
        
        try:
            response = await self._make_request("GET", "/api/v1/jobs", params=params)
            
            jobs = []
            for job_data in response.get("jobs", []):
                try:
                    job = InstaNoteDatabaseJob(**job_data)
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Failed to parse job data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(jobs)} jobs with errors")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to fetch jobs with errors: {e}")
            raise

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update job status in InstaNote Database.
        
        Args:
            job_id: Job identifier
            status: New status
            metadata: Optional metadata to update
            
        Returns:
            True if update was successful
        """
        logger.info(f"Updating job {job_id} status to {status}")
        
        data = {"status": status}
        if metadata:
            data["metadata"] = metadata
        
        try:
            await self._make_request("PATCH", f"/api/v1/jobs/{job_id}", data=data)
            logger.info(f"Successfully updated job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False

    async def get_speaker_statistics(
        self,
        speaker_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get statistics for a speaker within a date range.
        
        Args:
            speaker_id: Speaker identifier
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary containing speaker statistics
        """
        logger.info(f"Fetching statistics for speaker {speaker_id}")
        
        params = {
            "speaker_id": speaker_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        try:
            response = await self._make_request("GET", "/api/v1/speakers/statistics", params=params)
            
            statistics = {
                "total_jobs": response.get("total_jobs", 0),
                "completed_jobs": response.get("completed_jobs", 0),
                "jobs_with_errors": response.get("jobs_with_errors", 0),
                "average_audio_quality": response.get("average_audio_quality", 0.0),
                "average_confidence": response.get("average_confidence", 0.0),
                "total_audio_duration": response.get("total_audio_duration", 0.0),
                "error_rate": response.get("error_rate", 0.0),
            }
            
            logger.info(f"Retrieved statistics for speaker {speaker_id}")
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to fetch statistics for speaker {speaker_id}: {e}")
            raise

    async def search_jobs(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[InstaNoteDatabaseJob]:
        """
        Search jobs using text query and filters.
        
        Args:
            query: Text search query
            filters: Optional filters to apply
            limit: Maximum number of results
            
        Returns:
            List of matching jobs
        """
        logger.info(f"Searching jobs with query: {query}")
        
        params = {
            "q": query,
            "limit": limit
        }
        
        if filters:
            params.update(filters)
        
        try:
            response = await self._make_request("GET", "/api/v1/jobs/search", params=params)
            
            jobs = []
            for job_data in response.get("jobs", []):
                try:
                    job = InstaNoteDatabaseJob(**job_data)
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Failed to parse job data: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} jobs matching query")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to search jobs: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if InstaNote Database service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self._make_request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
