"""
Speaker Performance Metrics Domain Entity

Tracks performance metrics for speakers in the quality-based bucket system.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from .error_report import BucketType


class QualityTrend(str, Enum):
    """Quality trend indicators"""

    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


@dataclass(frozen=True)
class SpeakerPerformanceMetrics:
    """
    Speaker Performance Metrics Domain Entity

    Represents calculated performance metrics for a speaker.
    Immutable entity with business rule validation.
    """

    # Required fields
    metrics_id: UUID
    speaker_id: UUID
    current_bucket: BucketType
    calculated_at: datetime

    # Error metrics
    total_errors_reported: int = 0
    errors_rectified: int = 0
    errors_pending: int = 0
    rectification_rate: float = 0.0

    # Quality metrics
    average_audio_quality: Optional[float] = None
    average_clarity_score: Optional[float] = None
    specialized_knowledge_frequency: Optional[float] = None
    overlapping_speech_frequency: Optional[float] = None

    # Performance trends
    quality_trend: Optional[QualityTrend] = None
    last_assessment_date: Optional[datetime] = None
    next_assessment_date: Optional[datetime] = None

    # Time metrics
    average_time_to_rectification: Optional[timedelta] = None
    time_in_current_bucket: Optional[timedelta] = None

    # System fields
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate business rules after initialization"""
        self._validate_error_counts()
        self._validate_rates()
        self._validate_quality_scores()
        self._validate_frequencies()

    def _validate_error_counts(self) -> None:
        """Validate error count consistency"""
        if self.total_errors_reported < 0:
            raise ValueError("total_errors_reported cannot be negative")

        if self.errors_rectified < 0:
            raise ValueError("errors_rectified cannot be negative")

        if self.errors_pending < 0:
            raise ValueError("errors_pending cannot be negative")

        if self.errors_rectified > self.total_errors_reported:
            raise ValueError("errors_rectified cannot exceed total_errors_reported")

        # Check if pending + rectified equals total (allowing for other statuses)
        if self.errors_rectified + self.errors_pending > self.total_errors_reported:
            raise ValueError("rectified + pending cannot exceed total errors")

    def _validate_rates(self) -> None:
        """Validate rate values are within valid ranges"""
        if not 0.0 <= self.rectification_rate <= 1.0:
            raise ValueError("rectification_rate must be between 0.0 and 1.0")

    def _validate_quality_scores(self) -> None:
        """Validate quality score ranges"""
        if self.average_audio_quality is not None:
            if not 1.0 <= self.average_audio_quality <= 3.0:
                raise ValueError("average_audio_quality must be between 1.0 and 3.0")

        if self.average_clarity_score is not None:
            if not 1.0 <= self.average_clarity_score <= 4.0:
                raise ValueError("average_clarity_score must be between 1.0 and 4.0")

    def _validate_frequencies(self) -> None:
        """Validate frequency values are within valid ranges"""
        if self.specialized_knowledge_frequency is not None:
            if not 0.0 <= self.specialized_knowledge_frequency <= 1.0:
                raise ValueError("specialized_knowledge_frequency must be between 0.0 and 1.0")

        if self.overlapping_speech_frequency is not None:
            if not 0.0 <= self.overlapping_speech_frequency <= 1.0:
                raise ValueError("overlapping_speech_frequency must be between 0.0 and 1.0")

    def __eq__(self, other) -> bool:
        """Equality based on metrics_id (entity identity)"""
        if not isinstance(other, SpeakerPerformanceMetrics):
            return False
        return self.metrics_id == other.metrics_id

    def __hash__(self) -> int:
        """Hash based on metrics_id (entity identity)"""
        return hash(self.metrics_id)

    def __str__(self) -> str:
        """String representation of performance metrics"""
        return (
            f"SpeakerPerformanceMetrics(id={self.metrics_id}, "
            f"speaker={self.speaker_id}, "
            f"bucket={self.current_bucket.value}, "
            f"rectification_rate={self.rectification_rate:.2f})"
        )

    def has_sufficient_data(self, minimum_errors: int = 5) -> bool:
        """Check if there's sufficient data for reliable metrics"""
        return self.total_errors_reported >= minimum_errors

    def is_high_performer(self) -> bool:
        """Check if speaker is a high performer"""
        return (
            self.rectification_rate >= 0.8 and
            self.total_errors_reported >= 10 and
            self.quality_trend in [QualityTrend.IMPROVING, QualityTrend.STABLE]
        )

    def is_improving(self) -> bool:
        """Check if speaker performance is improving"""
        return self.quality_trend == QualityTrend.IMPROVING

    def is_declining(self) -> bool:
        """Check if speaker performance is declining"""
        return self.quality_trend == QualityTrend.DECLINING

    def needs_attention(self) -> bool:
        """Check if speaker needs attention based on performance"""
        return (
            self.rectification_rate < 0.5 or
            self.quality_trend == QualityTrend.DECLINING or
            (self.total_errors_reported >= 20 and self.rectification_rate < 0.7)
        )

    def calculate_performance_score(self) -> float:
        """Calculate overall performance score (0.0 to 10.0)"""
        if not self.has_sufficient_data():
            return 5.0  # Neutral score for insufficient data

        score = 0.0

        # Rectification rate (40% weight)
        score += self.rectification_rate * 4.0

        # Quality trend (30% weight)
        trend_scores = {
            QualityTrend.IMPROVING: 3.0,
            QualityTrend.STABLE: 2.0,
            QualityTrend.DECLINING: 1.0
        }
        if self.quality_trend:
            score += trend_scores.get(self.quality_trend, 2.0)

        # Audio quality (20% weight)
        if self.average_audio_quality:
            # Convert 1-3 scale to 0-2 scale
            normalized_audio = (self.average_audio_quality - 1.0) / 2.0
            score += normalized_audio * 2.0

        # Consistency bonus (10% weight)
        if self.total_errors_reported >= 20:
            consistency_bonus = min(self.total_errors_reported / 100.0, 1.0)
            score += consistency_bonus * 1.0

        return min(score, 10.0)

    def get_bucket_recommendation(self) -> BucketType:
        """Get recommended bucket based on performance metrics"""
        performance_score = self.calculate_performance_score()

        if performance_score >= 8.5:
            return BucketType.NO_TOUCH
        elif performance_score >= 7.0:
            return BucketType.LOW_TOUCH
        elif performance_score >= 5.0:
            return BucketType.MEDIUM_TOUCH
        else:
            return BucketType.HIGH_TOUCH

    def should_reassess_bucket(self, days_threshold: int = 30) -> bool:
        """Check if bucket should be reassessed based on time and performance"""
        if self.last_assessment_date is None:
            return True

        days_since_assessment = (datetime.utcnow() - self.last_assessment_date).days

        # Time-based reassessment
        if days_since_assessment >= days_threshold:
            return True

        # Performance-based reassessment
        recommended_bucket = self.get_bucket_recommendation()
        if recommended_bucket != self.current_bucket:
            return True

        # Declining performance requires immediate attention
        if self.quality_trend == QualityTrend.DECLINING:
            return True

        return False

    def calculate_days_in_current_bucket(self, current_date: datetime = None) -> int:
        """Calculate number of days in current bucket"""
        if self.time_in_current_bucket is None:
            return 0

        if current_date is None:
            current_date = datetime.utcnow()

        return self.time_in_current_bucket.days

    def get_quality_trend_description(self) -> str:
        """Get human-readable quality trend description"""
        descriptions = {
            QualityTrend.IMPROVING: "Performance is improving over time",
            QualityTrend.STABLE: "Performance is stable and consistent",
            QualityTrend.DECLINING: "Performance is declining and needs attention"
        }
        return descriptions.get(self.quality_trend, "Quality trend not determined")

    def get_performance_summary(self) -> dict:
        """Get comprehensive performance summary"""
        return {
            "speaker_id": str(self.speaker_id),
            "current_bucket": self.current_bucket.value,
            "performance_score": self.calculate_performance_score(),
            "rectification_rate": self.rectification_rate,
            "total_errors": self.total_errors_reported,
            "quality_trend": self.quality_trend.value if self.quality_trend else None,
            "recommended_bucket": self.get_bucket_recommendation().value,
            "needs_attention": self.needs_attention(),
            "should_reassess": self.should_reassess_bucket(),
            "days_in_bucket": self.calculate_days_in_current_bucket()
        }
