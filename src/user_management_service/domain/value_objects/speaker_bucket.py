"""
Speaker Bucket Value Object

Defines speaker quality buckets with associated thresholds and characteristics.
Immutable value object following domain-driven design principles.
"""

from enum import Enum
from typing import Any, Dict, List


class SpeakerBucket(Enum):
    """
    Enumeration of speaker quality buckets.

    Each bucket represents different levels of ASR quality and required intervention:
    - NO_TOUCH: Highest quality, no corrections needed
    - LOW_TOUCH: High quality, minimal corrections needed
    - MEDIUM_TOUCH: Medium quality, some corrections needed
    - HIGH_TOUCH: Low quality, significant corrections needed
    """

    NO_TOUCH = "no_touch"
    LOW_TOUCH = "low_touch"
    MEDIUM_TOUCH = "medium_touch"
    HIGH_TOUCH = "high_touch"

    def get_ser_threshold_range(self) -> tuple[float, float]:
        """
        Get SER (Sentence Edit Rate) threshold range for this bucket.

        Returns:
            Tuple of (min_ser, max_ser) for this bucket
        """
        threshold_map = {
            SpeakerBucket.NO_TOUCH: (0.0, 5.0),
            SpeakerBucket.LOW_TOUCH: (5.0, 15.0),
            SpeakerBucket.MEDIUM_TOUCH: (15.0, 30.0),
            SpeakerBucket.HIGH_TOUCH: (30.0, float("inf")),
        }
        return threshold_map[self]

    def get_description(self) -> str:
        """
        Get human-readable description of this bucket.

        Returns:
            Description string
        """
        description_map = {
            SpeakerBucket.NO_TOUCH: "Speakers with excellent ASR quality requiring no corrections",
            SpeakerBucket.LOW_TOUCH: "Speakers with high ASR quality requiring minimal corrections",
            SpeakerBucket.MEDIUM_TOUCH: "Speakers with medium ASR quality requiring some corrections",
            SpeakerBucket.HIGH_TOUCH: "Speakers with low ASR quality requiring significant corrections",
        }
        return description_map[self]

    def get_priority_level(self) -> int:
        """
        Get priority level for processing (1 = highest priority).

        Returns:
            Priority level (1-4)
        """
        priority_map = {
            SpeakerBucket.HIGH_TOUCH: 1,  # Highest priority for improvement
            SpeakerBucket.MEDIUM_TOUCH: 2,
            SpeakerBucket.LOW_TOUCH: 3,
            SpeakerBucket.NO_TOUCH: 4,  # Lowest priority (already good)
        }
        return priority_map[self]

    def get_recommended_rag_intensity(self) -> str:
        """
        Get recommended RAG processing intensity for this bucket.

        Returns:
            RAG intensity level
        """
        intensity_map = {
            SpeakerBucket.NO_TOUCH: "minimal",
            SpeakerBucket.LOW_TOUCH: "light",
            SpeakerBucket.MEDIUM_TOUCH: "moderate",
            SpeakerBucket.HIGH_TOUCH: "intensive",
        }
        return intensity_map[self]

    def can_transition_to(self, target_bucket: "SpeakerBucket") -> bool:
        """
        Check if transition to target bucket is valid.

        Args:
            target_bucket: Target bucket for transition

        Returns:
            True if transition is valid
        """
        # Generally, speakers should only move to better buckets (lower touch)
        # or stay in the same bucket
        current_priority = self.get_priority_level()
        target_priority = target_bucket.get_priority_level()

        # Allow transitions to better buckets (higher priority number = better quality)
        return target_priority >= current_priority

    def get_next_better_bucket(self) -> "SpeakerBucket":
        """
        Get the next better bucket in the quality hierarchy.

        Returns:
            Next better bucket, or same bucket if already at the top
        """
        improvement_map = {
            SpeakerBucket.HIGH_TOUCH: SpeakerBucket.MEDIUM_TOUCH,
            SpeakerBucket.MEDIUM_TOUCH: SpeakerBucket.LOW_TOUCH,
            SpeakerBucket.LOW_TOUCH: SpeakerBucket.NO_TOUCH,
            SpeakerBucket.NO_TOUCH: SpeakerBucket.NO_TOUCH,  # Already at the top
        }
        return improvement_map[self]

    def requires_mt_validation(self) -> bool:
        """
        Check if this bucket requires MT validation for transitions.

        Returns:
            True if MT validation is required
        """
        # All buckets except NO_TOUCH require MT validation for transitions
        return self != SpeakerBucket.NO_TOUCH

    @classmethod
    def from_ser_score(cls, ser_score: float) -> "SpeakerBucket":
        """
        Determine bucket from SER score.

        Args:
            ser_score: SER score to classify

        Returns:
            Appropriate SpeakerBucket
        """
        if ser_score <= 5.0:
            return cls.NO_TOUCH
        elif ser_score <= 15.0:
            return cls.LOW_TOUCH
        elif ser_score <= 30.0:
            return cls.MEDIUM_TOUCH
        else:
            return cls.HIGH_TOUCH

    @classmethod
    def from_string(cls, bucket_str: str) -> "SpeakerBucket":
        """
        Create speaker bucket from string value.

        Args:
            bucket_str: String representation of the bucket

        Returns:
            SpeakerBucket instance

        Raises:
            ValueError: If bucket string is invalid
        """
        if not bucket_str or not bucket_str.strip():
            raise ValueError("Invalid speaker bucket: empty string")

        bucket_str = bucket_str.strip().lower()

        for bucket in cls:
            if bucket.value == bucket_str:
                return bucket

        raise ValueError(f"Invalid speaker bucket: {bucket_str}")

    @classmethod
    def get_all_buckets_info(cls) -> List[Dict[str, Any]]:
        """
        Get information about all buckets.

        Returns:
            List of dictionaries with bucket information
        """
        return [
            {
                "bucket": bucket.value,
                "description": bucket.get_description(),
                "ser_range": bucket.get_ser_threshold_range(),
                "priority": bucket.get_priority_level(),
                "rag_intensity": bucket.get_recommended_rag_intensity(),
                "requires_mt_validation": bucket.requires_mt_validation(),
            }
            for bucket in cls
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert bucket to dictionary representation.

        Returns:
            Dictionary with bucket information
        """
        return {
            "value": self.value,
            "description": self.get_description(),
            "ser_range": self.get_ser_threshold_range(),
            "priority": self.get_priority_level(),
            "rag_intensity": self.get_recommended_rag_intensity(),
            "requires_mt_validation": self.requires_mt_validation(),
        }

    def __str__(self) -> str:
        """String representation of the speaker bucket."""
        return self.value

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"SpeakerBucket.{self.name}"
