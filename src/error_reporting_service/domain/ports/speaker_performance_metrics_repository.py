"""
Speaker Performance Metrics Repository Port

Defines the interface for speaker performance metrics persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from error_reporting_service.domain.entities.speaker_performance_metrics import (
    SpeakerPerformanceMetrics,
)
from error_reporting_service.domain.entities.error_report import BucketType


class SpeakerPerformanceMetricsRepository(ABC):
    """Abstract repository for speaker performance metrics operations"""

    @abstractmethod
    async def save_metrics(self, metrics: SpeakerPerformanceMetrics) -> SpeakerPerformanceMetrics:
        """Save speaker performance metrics to the repository"""

    @abstractmethod
    async def get_metrics_by_speaker(self, speaker_id: UUID) -> Optional[SpeakerPerformanceMetrics]:
        """Get performance metrics for a specific speaker"""

    @abstractmethod
    async def get_metrics_by_bucket(self, bucket_type: BucketType) -> List[SpeakerPerformanceMetrics]:
        """Get all metrics for speakers in a specific bucket"""

    @abstractmethod
    async def get_speakers_needing_attention(self) -> List[SpeakerPerformanceMetrics]:
        """Get speakers that need attention based on performance"""

    @abstractmethod
    async def get_high_performers(self, minimum_errors: int = 10) -> List[SpeakerPerformanceMetrics]:
        """Get high-performing speakers"""

    @abstractmethod
    async def get_speakers_for_reassessment(self, days_threshold: int = 30) -> List[SpeakerPerformanceMetrics]:
        """Get speakers that should be reassessed"""

    @abstractmethod
    async def get_bucket_statistics(self) -> dict:
        """Get statistics for each bucket type"""

    @abstractmethod
    async def get_performance_trends(self, days: int = 90) -> dict:
        """Get performance trends over time"""
