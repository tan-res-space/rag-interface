"""
Verification Job Repository Port

Defines the interface for verification job persistence operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from error_reporting_service.domain.entities.verification_job import (
    VerificationJob,
    VerificationStatus,
    VerificationResult,
)


class VerificationJobRepository(ABC):
    """Abstract repository for verification job operations"""

    @abstractmethod
    async def save_verification_job(self, verification_job: VerificationJob) -> VerificationJob:
        """Save a verification job to the repository"""
        pass

    @abstractmethod
    async def get_by_id(self, verification_id: UUID) -> Optional[VerificationJob]:
        """Get a verification job by ID"""
        pass

    @abstractmethod
    async def get_by_job_id(self, job_id: str) -> Optional[VerificationJob]:
        """Get a verification job by InstaNote job ID"""
        pass

    @abstractmethod
    async def get_jobs_by_speaker(
        self, 
        speaker_id: UUID,
        status: Optional[VerificationStatus] = None
    ) -> List[VerificationJob]:
        """Get verification jobs for a specific speaker"""
        pass

    @abstractmethod
    async def get_jobs_needing_review(
        self, 
        speaker_id: Optional[UUID] = None
    ) -> List[VerificationJob]:
        """Get verification jobs that need manual review"""
        pass

    @abstractmethod
    async def get_pending_jobs(self, limit: Optional[int] = None) -> List[VerificationJob]:
        """Get pending verification jobs"""
        pass

    @abstractmethod
    async def get_jobs_by_status(
        self, 
        status: VerificationStatus,
        limit: Optional[int] = None
    ) -> List[VerificationJob]:
        """Get verification jobs by status"""
        pass

    @abstractmethod
    async def get_verification_statistics(self, days: int = 30) -> dict:
        """Get verification workflow statistics"""
        pass

    @abstractmethod
    async def get_jobs_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        speaker_id: Optional[UUID] = None
    ) -> List[VerificationJob]:
        """Get verification jobs within a date range"""
        pass
