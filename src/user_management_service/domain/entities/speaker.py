"""
Speaker Domain Entity

Represents a speaker with bucket categorization and quality metrics.
Core domain entity for speaker bucket management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from decimal import Decimal

from ..value_objects.speaker_bucket import SpeakerBucket


@dataclass
class Speaker:
    """
    Domain entity representing a speaker in the ASR system.
    
    This entity encapsulates speaker identification, bucket categorization,
    quality metrics, and processing history for the speaker bucket management system.
    """
    
    id: UUID
    speaker_identifier: str  # External speaker ID from InstaNote
    speaker_name: str
    current_bucket: SpeakerBucket
    total_notes_count: int = 0
    processed_notes_count: int = 0
    average_ser_score: Optional[Decimal] = None
    last_processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the speaker after initialization."""
        self._validate_speaker_identifier()
        self._validate_speaker_name()
        self._validate_counts()
        self._validate_ser_score()
        self._set_defaults()
    
    def _validate_speaker_identifier(self) -> None:
        """Validate speaker identifier field."""
        if not self.speaker_identifier or not self.speaker_identifier.strip():
            raise ValueError("speaker_identifier cannot be empty")
        
        if len(self.speaker_identifier) > 100:
            raise ValueError("speaker_identifier cannot exceed 100 characters")
    
    def _validate_speaker_name(self) -> None:
        """Validate speaker name field."""
        if not self.speaker_name or not self.speaker_name.strip():
            raise ValueError("speaker_name cannot be empty")
        
        if len(self.speaker_name) > 255:
            raise ValueError("speaker_name cannot exceed 255 characters")
    
    def _validate_counts(self) -> None:
        """Validate count fields."""
        if self.total_notes_count < 0:
            raise ValueError("total_notes_count cannot be negative")
        
        if self.processed_notes_count < 0:
            raise ValueError("processed_notes_count cannot be negative")
        
        if self.processed_notes_count > self.total_notes_count:
            raise ValueError("processed_notes_count cannot exceed total_notes_count")
    
    def _validate_ser_score(self) -> None:
        """Validate SER score field."""
        if self.average_ser_score is not None:
            if self.average_ser_score < 0:
                raise ValueError("average_ser_score cannot be negative")
            
            if self.average_ser_score > 100:
                raise ValueError("average_ser_score cannot exceed 100")
    
    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def get_processing_progress(self) -> float:
        """
        Get processing progress as a percentage.
        
        Returns:
            Processing progress (0.0 to 100.0)
        """
        if self.total_notes_count == 0:
            return 0.0
        
        return (self.processed_notes_count / self.total_notes_count) * 100.0
    
    def is_fully_processed(self) -> bool:
        """
        Check if all notes have been processed.
        
        Returns:
            True if all notes are processed
        """
        return self.processed_notes_count == self.total_notes_count and self.total_notes_count > 0
    
    def has_sufficient_data_for_analysis(self, min_notes: int = 10) -> bool:
        """
        Check if speaker has sufficient data for reliable analysis.
        
        Args:
            min_notes: Minimum number of processed notes required
            
        Returns:
            True if sufficient data is available
        """
        return self.processed_notes_count >= min_notes
    
    def get_recommended_bucket(self) -> SpeakerBucket:
        """
        Get recommended bucket based on current SER score.
        
        Returns:
            Recommended SpeakerBucket
        """
        if self.average_ser_score is None:
            return SpeakerBucket.HIGH_TOUCH  # Default for unprocessed speakers
        
        return SpeakerBucket.from_ser_score(float(self.average_ser_score))
    
    def should_transition_bucket(self) -> bool:
        """
        Check if speaker should transition to a different bucket.
        
        Returns:
            True if bucket transition is recommended
        """
        if not self.has_sufficient_data_for_analysis():
            return False
        
        recommended_bucket = self.get_recommended_bucket()
        return recommended_bucket != self.current_bucket
    
    def can_transition_to_bucket(self, target_bucket: SpeakerBucket) -> bool:
        """
        Check if speaker can transition to target bucket.
        
        Args:
            target_bucket: Target bucket for transition
            
        Returns:
            True if transition is valid
        """
        return self.current_bucket.can_transition_to(target_bucket)
    
    def get_quality_trend(self) -> str:
        """
        Get quality trend description based on bucket and SER score.
        
        Returns:
            Quality trend description
        """
        if self.average_ser_score is None:
            return "insufficient_data"
        
        recommended_bucket = self.get_recommended_bucket()
        
        if recommended_bucket.get_priority_level() > self.current_bucket.get_priority_level():
            return "improving"
        elif recommended_bucket.get_priority_level() < self.current_bucket.get_priority_level():
            return "declining"
        else:
            return "stable"
    
    def get_priority_score(self) -> int:
        """
        Get priority score for processing (lower = higher priority).
        
        Returns:
            Priority score
        """
        base_priority = self.current_bucket.get_priority_level()
        
        # Adjust priority based on data availability and trends
        if not self.has_sufficient_data_for_analysis():
            base_priority -= 1  # Higher priority for speakers needing more data
        
        if self.should_transition_bucket():
            base_priority -= 1  # Higher priority for speakers ready for transition
        
        return max(1, base_priority)  # Ensure minimum priority of 1
    
    def update_statistics(self, total_notes: int, processed_notes: int, avg_ser: Optional[Decimal]) -> None:
        """
        Update speaker statistics.
        
        Args:
            total_notes: Total number of notes
            processed_notes: Number of processed notes
            avg_ser: Average SER score
        """
        self.total_notes_count = total_notes
        self.processed_notes_count = processed_notes
        self.average_ser_score = avg_ser
        self.last_processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def transition_bucket(self, new_bucket: SpeakerBucket) -> None:
        """
        Transition speaker to new bucket.
        
        Args:
            new_bucket: New bucket to transition to
            
        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to_bucket(new_bucket):
            raise ValueError(f"Invalid bucket transition from {self.current_bucket} to {new_bucket}")
        
        self.current_bucket = new_bucket
        self.updated_at = datetime.utcnow()
    
    def get_speaker_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the speaker.
        
        Returns:
            Dictionary containing speaker summary
        """
        return {
            "id": str(self.id),
            "speaker_identifier": self.speaker_identifier,
            "speaker_name": self.speaker_name,
            "current_bucket": self.current_bucket.value,
            "bucket_description": self.current_bucket.get_description(),
            "total_notes_count": self.total_notes_count,
            "processed_notes_count": self.processed_notes_count,
            "processing_progress": self.get_processing_progress(),
            "average_ser_score": float(self.average_ser_score) if self.average_ser_score else None,
            "recommended_bucket": self.get_recommended_bucket().value,
            "should_transition": self.should_transition_bucket(),
            "quality_trend": self.get_quality_trend(),
            "priority_score": self.get_priority_score(),
            "has_sufficient_data": self.has_sufficient_data_for_analysis(),
            "last_processed_at": self.last_processed_at.isoformat() if self.last_processed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __eq__(self, other: "Speaker") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, Speaker):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation of the speaker."""
        return f"Speaker(id={self.id}, name={self.speaker_name}, bucket={self.current_bucket.value})"
