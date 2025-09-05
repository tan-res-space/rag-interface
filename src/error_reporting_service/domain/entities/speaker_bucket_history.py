"""
Speaker Bucket History Domain Entity

Tracks the history of bucket assignments for speakers in the quality-based system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from .error_report import BucketType


class AssignmentType(str, Enum):
    """Type of bucket assignment"""

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SYSTEM = "system"


@dataclass(frozen=True)
class SpeakerBucketHistory:
    """
    Speaker Bucket History Domain Entity

    Represents a bucket assignment event for a speaker.
    Immutable entity tracking bucket transitions.
    """

    # Required fields
    history_id: UUID
    speaker_id: UUID
    bucket_type: BucketType
    assigned_date: datetime
    assigned_by: UUID
    assignment_reason: str
    assignment_type: AssignmentType

    # Optional fields
    previous_bucket: Optional[BucketType] = None
    error_count_at_assignment: Optional[int] = None
    rectification_rate_at_assignment: Optional[float] = None
    quality_score_at_assignment: Optional[float] = None
    confidence_score: Optional[float] = None

    def __post_init__(self):
        """Validate business rules after initialization"""
        self._validate_assignment_reason()
        self._validate_confidence_score()
        self._validate_rectification_rate()

    def _validate_assignment_reason(self) -> None:
        """Validate assignment reason is not empty"""
        if not self.assignment_reason or not self.assignment_reason.strip():
            raise ValueError("assignment_reason cannot be empty")

        if len(self.assignment_reason) > 500:
            raise ValueError("assignment_reason cannot exceed 500 characters")

    def _validate_confidence_score(self) -> None:
        """Validate confidence score is within valid range"""
        if self.confidence_score is not None:
            if not 0.0 <= self.confidence_score <= 1.0:
                raise ValueError("confidence_score must be between 0.0 and 1.0")

    def _validate_rectification_rate(self) -> None:
        """Validate rectification rate is within valid range"""
        if self.rectification_rate_at_assignment is not None:
            if not 0.0 <= self.rectification_rate_at_assignment <= 1.0:
                raise ValueError("rectification_rate_at_assignment must be between 0.0 and 1.0")

    def __eq__(self, other) -> bool:
        """Equality based on history_id (entity identity)"""
        if not isinstance(other, SpeakerBucketHistory):
            return False
        return self.history_id == other.history_id

    def __hash__(self) -> int:
        """Hash based on history_id (entity identity)"""
        return hash(self.history_id)

    def __str__(self) -> str:
        """String representation of bucket history"""
        return (
            f"SpeakerBucketHistory(id={self.history_id}, "
            f"speaker={self.speaker_id}, "
            f"bucket={self.bucket_type.value}, "
            f"date={self.assigned_date.isoformat()})"
        )

    def is_bucket_upgrade(self) -> bool:
        """Check if this assignment represents a bucket upgrade (quality improvement)"""
        if self.previous_bucket is None:
            return False

        # Define bucket quality order (higher index = better quality)
        bucket_order = [
            BucketType.HIGH_TOUCH,
            BucketType.MEDIUM_TOUCH,
            BucketType.LOW_TOUCH,
            BucketType.NO_TOUCH
        ]

        try:
            previous_index = bucket_order.index(self.previous_bucket)
            current_index = bucket_order.index(self.bucket_type)
            return current_index > previous_index
        except ValueError:
            return False

    def is_bucket_downgrade(self) -> bool:
        """Check if this assignment represents a bucket downgrade (quality decline)"""
        if self.previous_bucket is None:
            return False

        # Define bucket quality order (higher index = better quality)
        bucket_order = [
            BucketType.HIGH_TOUCH,
            BucketType.MEDIUM_TOUCH,
            BucketType.LOW_TOUCH,
            BucketType.NO_TOUCH
        ]

        try:
            previous_index = bucket_order.index(self.previous_bucket)
            current_index = bucket_order.index(self.bucket_type)
            return current_index < previous_index
        except ValueError:
            return False

    def is_initial_assignment(self) -> bool:
        """Check if this is the initial bucket assignment"""
        return self.previous_bucket is None

    def is_automatic_assignment(self) -> bool:
        """Check if this was an automatic assignment"""
        return self.assignment_type == AssignmentType.AUTOMATIC

    def is_manual_assignment(self) -> bool:
        """Check if this was a manual assignment"""
        return self.assignment_type == AssignmentType.MANUAL

    def get_bucket_transition_description(self) -> str:
        """Get human-readable description of bucket transition"""
        if self.is_initial_assignment():
            return f"Initial assignment to {self.bucket_type.value}"

        if self.is_bucket_upgrade():
            return f"Upgraded from {self.previous_bucket.value} to {self.bucket_type.value}"

        if self.is_bucket_downgrade():
            return f"Downgraded from {self.previous_bucket.value} to {self.bucket_type.value}"

        return f"Reassigned from {self.previous_bucket.value} to {self.bucket_type.value}"

    def get_assignment_type_description(self) -> str:
        """Get human-readable description of assignment type"""
        descriptions = {
            AssignmentType.MANUAL: "Manual assignment by QA personnel",
            AssignmentType.AUTOMATIC: "Automatic assignment by system",
            AssignmentType.SYSTEM: "System-initiated assignment"
        }
        return descriptions.get(self.assignment_type, "Unknown assignment type")

    def calculate_days_since_assignment(self, current_date: datetime = None) -> int:
        """Calculate number of days since this assignment"""
        if current_date is None:
            current_date = datetime.utcnow()

        delta = current_date - self.assigned_date
        return delta.days

    def has_high_confidence(self) -> bool:
        """Check if assignment has high confidence score"""
        return self.confidence_score is not None and self.confidence_score >= 0.8

    def has_performance_metrics(self) -> bool:
        """Check if assignment includes performance metrics"""
        return (
            self.error_count_at_assignment is not None or
            self.rectification_rate_at_assignment is not None or
            self.quality_score_at_assignment is not None
        )
