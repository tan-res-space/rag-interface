"""
Speaker Bucket History Repository Port

Defines the interface for speaker bucket history persistence operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.error_reporting_service.domain.entities.speaker_bucket_history import (
    SpeakerBucketHistory,
    AssignmentType,
)
from src.error_reporting_service.domain.entities.error_report import BucketType


class SpeakerBucketHistoryRepository(ABC):
    """Abstract repository for speaker bucket history operations"""

    @abstractmethod
    async def save_bucket_assignment(self, bucket_history: SpeakerBucketHistory) -> SpeakerBucketHistory:
        """Save a bucket assignment to the repository"""
        pass

    @abstractmethod
    async def get_speaker_bucket_history(
        self, 
        speaker_id: UUID, 
        limit: Optional[int] = None
    ) -> List[SpeakerBucketHistory]:
        """Get bucket history for a specific speaker"""
        pass

    @abstractmethod
    async def get_current_bucket(self, speaker_id: UUID) -> Optional[BucketType]:
        """Get the current bucket assignment for a speaker"""
        pass

    @abstractmethod
    async def get_bucket_transitions(
        self, 
        speaker_id: UUID, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SpeakerBucketHistory]:
        """Get bucket transitions for a speaker within a date range"""
        pass

    @abstractmethod
    async def get_recent_assignments(
        self, 
        assignment_type: Optional[AssignmentType] = None,
        days: int = 7
    ) -> List[SpeakerBucketHistory]:
        """Get recent bucket assignments"""
        pass

    @abstractmethod
    async def count_bucket_assignments(
        self, 
        bucket_type: BucketType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count bucket assignments by type and date range"""
        pass

    @abstractmethod
    async def get_bucket_distribution(self) -> dict:
        """Get current bucket distribution statistics"""
        pass

    @abstractmethod
    async def get_assignment_trends(self, days: int = 30) -> dict:
        """Get bucket assignment trends over time"""
        pass
