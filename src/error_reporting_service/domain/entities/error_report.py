"""
Error Report Domain Entity

Core domain entity representing an error report in the ASR system.
Contains business rules and validation logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

# Import shared enums from shared components
from src.shared.domain.value_objects import BucketType, ErrorStatus, SeverityLevel


class AudioQuality(str, Enum):
    """Audio quality assessment levels"""

    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class SpeakerClarity(str, Enum):
    """Speaker clarity assessment levels"""

    CLEAR = "clear"
    SOMEWHAT_CLEAR = "somewhat_clear"
    UNCLEAR = "unclear"
    VERY_UNCLEAR = "very_unclear"


class BackgroundNoise(str, Enum):
    """Background noise levels"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NumberOfSpeakers(str, Enum):
    """Number of speakers in audio"""

    ONE = "one"
    TWO = "two"
    THREE = "three"
    FOUR = "four"
    FIVE = "five"


@dataclass(frozen=True)
class EnhancedMetadata:
    """Enhanced metadata for error reports"""

    # Core metadata
    audio_quality: AudioQuality
    speaker_clarity: SpeakerClarity
    background_noise: BackgroundNoise

    # Enhanced metadata fields
    number_of_speakers: NumberOfSpeakers
    overlapping_speech: bool
    requires_specialized_knowledge: bool
    additional_notes: Optional[str] = None

    def __post_init__(self):
        """Validate enhanced metadata"""
        if self.additional_notes and len(self.additional_notes) > 1000:
            raise ValueError("additional_notes cannot exceed 1000 characters")


@dataclass(frozen=True)
class ErrorReport:
    """
    Error Report Domain Entity

    Represents an error report submitted by QA personnel with enhanced metadata.
    Immutable entity with business rule validation.
    """

    # Required fields
    error_id: UUID
    job_id: UUID
    speaker_id: UUID
    client_id: UUID
    reported_by: UUID
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: SeverityLevel
    start_position: int
    end_position: int
    error_timestamp: datetime
    reported_at: datetime

    # Quality-based bucket management
    bucket_type: BucketType

    # Enhanced metadata
    enhanced_metadata: EnhancedMetadata

    # Optional fields with defaults
    context_notes: Optional[str] = None
    status: ErrorStatus = ErrorStatus.SUBMITTED
    vector_db_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate business rules after initialization"""
        self._validate_position_range()
        self._validate_text_difference()
        self._validate_error_categories()
        self._validate_text_fields()
        self._validate_bucket_type()
        self._validate_enhanced_metadata()

    def _validate_position_range(self) -> None:
        """Validate that end_position is greater than start_position"""
        if self.end_position <= self.start_position:
            raise ValueError("end_position must be greater than start_position")

        if self.start_position < 0:
            raise ValueError("start_position must be non-negative")

    def _validate_text_difference(self) -> None:
        """Validate that corrected_text differs from original_text"""
        if self.original_text == self.corrected_text:
            raise ValueError("corrected_text must differ from original_text")

    def _validate_error_categories(self) -> None:
        """Validate that error_categories is not empty"""
        if not self.error_categories:
            raise ValueError("error_categories cannot be empty")

    def _validate_text_fields(self) -> None:
        """Validate text field constraints"""
        if not self.original_text or not self.original_text.strip():
            raise ValueError("text cannot be empty or whitespace only")

        if not self.corrected_text or not self.corrected_text.strip():
            raise ValueError("text cannot be empty or whitespace only")

        if len(self.original_text) > 5000:
            raise ValueError("original_text cannot exceed 5000 characters")

        if len(self.corrected_text) > 5000:
            raise ValueError("corrected_text cannot exceed 5000 characters")

        # Validate position range against text length
        if self.end_position > len(self.original_text):
            raise ValueError("position range exceeds text length")

    def _validate_bucket_type(self) -> None:
        """Validate bucket type is a valid quality-based bucket"""
        if not isinstance(self.bucket_type, BucketType):
            raise ValueError("bucket_type must be a valid BucketType")

    def _validate_enhanced_metadata(self) -> None:
        """Validate enhanced metadata fields"""
        if not isinstance(self.enhanced_metadata, EnhancedMetadata):
            raise ValueError("enhanced_metadata must be an EnhancedMetadata instance")

        # Additional validation for context notes
        if self.context_notes and len(self.context_notes) > 2000:
            raise ValueError("context_notes cannot exceed 2000 characters")

    def __eq__(self, other) -> bool:
        """Equality based on error_id (entity identity)"""
        if not isinstance(other, ErrorReport):
            return False
        return self.error_id == other.error_id

    def __hash__(self) -> int:
        """Hash based on error_id (entity identity)"""
        return hash(self.error_id)

    def __str__(self) -> str:
        """String representation of error report"""
        return (
            f"ErrorReport(id={self.error_id}, "
            f"severity={self.severity_level.value}, "
            f"categories={self.error_categories}, "
            f"status={self.status.value})"
        )

    def is_critical(self) -> bool:
        """Check if error report is critical severity"""
        return self.severity_level == SeverityLevel.CRITICAL

    def is_medical_terminology_error(self) -> bool:
        """Check if error involves medical terminology"""
        return "medical_terminology" in self.error_categories

    def get_error_length(self) -> int:
        """Get the length of the error text"""
        return self.end_position - self.start_position

    def calculate_error_length(self) -> int:
        """Calculate the length of the error text (alias for get_error_length)"""
        return self.get_error_length()

    def get_error_text(self) -> str:
        """Extract the error portion from original text"""
        return self.original_text[self.start_position : self.end_position]

    def get_correction_text(self) -> str:
        """Extract the correction portion from corrected text"""
        return self.corrected_text[self.start_position : self.end_position]

    def requires_high_touch(self) -> bool:
        """Check if error is from a high touch bucket"""
        return self.bucket_type == BucketType.HIGH_TOUCH

    def is_multi_speaker(self) -> bool:
        """Check if error involves multiple speakers"""
        return self.enhanced_metadata.number_of_speakers != NumberOfSpeakers.ONE

    def has_overlapping_speech(self) -> bool:
        """Check if error has overlapping speech"""
        return self.enhanced_metadata.overlapping_speech

    def requires_specialized_knowledge(self) -> bool:
        """Check if error requires specialized knowledge"""
        return self.enhanced_metadata.requires_specialized_knowledge

    def has_poor_audio_quality(self) -> bool:
        """Check if error has poor audio quality"""
        return self.enhanced_metadata.audio_quality == AudioQuality.POOR

    def get_bucket_display_name(self) -> str:
        """Get human-readable bucket type name"""
        bucket_names = {
            BucketType.NO_TOUCH: "No Touch",
            BucketType.LOW_TOUCH: "Low Touch",
            BucketType.MEDIUM_TOUCH: "Medium Touch",
            BucketType.HIGH_TOUCH: "High Touch"
        }
        return bucket_names.get(self.bucket_type, self.bucket_type.value)

    def get_bucket_description(self) -> str:
        """Get bucket type description"""
        descriptions = {
            BucketType.NO_TOUCH: "ASR draft is of very high quality and no corrections are required",
            BucketType.LOW_TOUCH: "ASR draft is of high quality and minimal corrections are required by MTs",
            BucketType.MEDIUM_TOUCH: "ASR draft is of medium quality and some corrections are required",
            BucketType.HIGH_TOUCH: "ASR draft is of low quality and significant corrections are required"
        }
        return descriptions.get(self.bucket_type, "Unknown bucket type")

    def calculate_complexity_score(self) -> float:
        """Calculate error complexity score based on metadata"""
        score = 0.0

        # Base score from bucket type
        bucket_scores = {
            BucketType.NO_TOUCH: 1.0,
            BucketType.LOW_TOUCH: 2.0,
            BucketType.MEDIUM_TOUCH: 3.0,
            BucketType.HIGH_TOUCH: 4.0
        }
        score += bucket_scores.get(self.bucket_type, 2.0)

        # Audio quality impact
        if self.enhanced_metadata.audio_quality == AudioQuality.POOR:
            score += 1.0
        elif self.enhanced_metadata.audio_quality == AudioQuality.FAIR:
            score += 0.5

        # Multiple speakers complexity
        if self.is_multi_speaker():
            score += 0.5

        # Overlapping speech complexity
        if self.has_overlapping_speech():
            score += 0.5

        # Specialized knowledge requirement
        if self.requires_specialized_knowledge():
            score += 0.5

        return min(score, 5.0)  # Cap at 5.0

    def with_status(self, new_status: ErrorStatus) -> "ErrorReport":
        """Create a new ErrorReport with updated status (immutable update)"""
        return ErrorReport(
            error_id=self.error_id,
            job_id=self.job_id,
            speaker_id=self.speaker_id,
            client_id=self.client_id,
            reported_by=self.reported_by,
            original_text=self.original_text,
            corrected_text=self.corrected_text,
            error_categories=self.error_categories,
            severity_level=self.severity_level,
            start_position=self.start_position,
            end_position=self.end_position,
            context_notes=self.context_notes,
            error_timestamp=self.error_timestamp,
            reported_at=self.reported_at,
            bucket_type=self.bucket_type,
            enhanced_metadata=self.enhanced_metadata,
            status=new_status,
            vector_db_id=self.vector_db_id,
            metadata=self.metadata,
        )

    def with_vector_db_id(self, vector_db_id: str) -> "ErrorReport":
        """Create a new ErrorReport with vector database ID (immutable update)"""
        return ErrorReport(
            error_id=self.error_id,
            job_id=self.job_id,
            speaker_id=self.speaker_id,
            client_id=self.client_id,
            reported_by=self.reported_by,
            original_text=self.original_text,
            corrected_text=self.corrected_text,
            error_categories=self.error_categories,
            severity_level=self.severity_level,
            start_position=self.start_position,
            end_position=self.end_position,
            context_notes=self.context_notes,
            error_timestamp=self.error_timestamp,
            reported_at=self.reported_at,
            bucket_type=self.bucket_type,
            enhanced_metadata=self.enhanced_metadata,
            status=self.status,
            vector_db_id=vector_db_id,
            metadata=self.metadata,
        )
