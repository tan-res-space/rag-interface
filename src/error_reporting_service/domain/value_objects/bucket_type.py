"""
Bucket Type Value Object

Defines the types of buckets used for categorizing speaker performance metrics.
"""

from enum import Enum


class BucketType(Enum):
    """
    Enumeration of bucket types for speaker performance categorization.
    
    These buckets are used to group speakers based on their performance metrics
    and error patterns for analysis and reporting purposes.
    """
    
    # Performance-based buckets
    HIGH_PERFORMER = "high_performer"
    AVERAGE_PERFORMER = "average_performer"
    LOW_PERFORMER = "low_performer"
    
    # Error frequency buckets
    LOW_ERROR_RATE = "low_error_rate"
    MEDIUM_ERROR_RATE = "medium_error_rate"
    HIGH_ERROR_RATE = "high_error_rate"
    
    # Experience level buckets
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    
    # Language proficiency buckets
    NATIVE_SPEAKER = "native_speaker"
    FLUENT_SPEAKER = "fluent_speaker"
    INTERMEDIATE_SPEAKER = "intermediate_speaker"
    BEGINNER_SPEAKER = "beginner_speaker"
    
    # Audio quality buckets
    EXCELLENT_AUDIO = "excellent_audio"
    GOOD_AUDIO = "good_audio"
    FAIR_AUDIO = "fair_audio"
    POOR_AUDIO = "poor_audio"
    
    # Default/uncategorized
    UNCATEGORIZED = "uncategorized"
    
    def __str__(self) -> str:
        """Return the string representation of the bucket type."""
        return self.value
    
    @classmethod
    def get_performance_buckets(cls) -> list["BucketType"]:
        """Get all performance-related bucket types."""
        return [cls.HIGH_PERFORMER, cls.AVERAGE_PERFORMER, cls.LOW_PERFORMER]
    
    @classmethod
    def get_error_rate_buckets(cls) -> list["BucketType"]:
        """Get all error rate bucket types."""
        return [cls.LOW_ERROR_RATE, cls.MEDIUM_ERROR_RATE, cls.HIGH_ERROR_RATE]
    
    @classmethod
    def get_experience_buckets(cls) -> list["BucketType"]:
        """Get all experience level bucket types."""
        return [cls.BEGINNER, cls.INTERMEDIATE, cls.ADVANCED, cls.EXPERT]
    
    @classmethod
    def get_language_buckets(cls) -> list["BucketType"]:
        """Get all language proficiency bucket types."""
        return [
            cls.NATIVE_SPEAKER,
            cls.FLUENT_SPEAKER,
            cls.INTERMEDIATE_SPEAKER,
            cls.BEGINNER_SPEAKER
        ]
    
    @classmethod
    def get_audio_quality_buckets(cls) -> list["BucketType"]:
        """Get all audio quality bucket types."""
        return [cls.EXCELLENT_AUDIO, cls.GOOD_AUDIO, cls.FAIR_AUDIO, cls.POOR_AUDIO]
