"""
Historical ASR Data Domain Entity

Represents historical ASR drafts and final notes for speaker analysis.
Core domain entity for speaker bucket management data processing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID


@dataclass
class HistoricalASRData:
    """
    Domain entity representing historical ASR data for speaker analysis.
    
    This entity encapsulates ASR drafts, final corrected notes, and metadata
    used for speaker quality assessment and RAG training.
    """
    
    id: UUID
    speaker_id: UUID
    instanote_job_id: Optional[str]
    asr_draft: str
    final_note: str
    note_type: Optional[str] = None
    asr_engine: Optional[str] = None
    processing_date: Optional[datetime] = None
    is_test_data: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the historical ASR data after initialization."""
        self._validate_required_fields()
        self._validate_text_content()
        self._validate_identifiers()
        self._set_defaults()
    
    def _validate_required_fields(self) -> None:
        """Validate required fields."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")
        
        if not self.asr_draft or not self.asr_draft.strip():
            raise ValueError("asr_draft cannot be empty")
        
        if not self.final_note or not self.final_note.strip():
            raise ValueError("final_note cannot be empty")
    
    def _validate_text_content(self) -> None:
        """Validate text content fields."""
        # Check for reasonable text lengths
        if len(self.asr_draft) > 50000:  # 50KB limit
            raise ValueError("asr_draft exceeds maximum length")
        
        if len(self.final_note) > 50000:  # 50KB limit
            raise ValueError("final_note exceeds maximum length")
        
        # Ensure texts are different (otherwise no correction was made)
        if self.asr_draft.strip() == self.final_note.strip():
            raise ValueError("asr_draft and final_note cannot be identical")
    
    def _validate_identifiers(self) -> None:
        """Validate identifier fields."""
        if self.instanote_job_id is not None:
            if not self.instanote_job_id.strip():
                raise ValueError("instanote_job_id cannot be empty string")
            
            if len(self.instanote_job_id) > 255:
                raise ValueError("instanote_job_id exceeds maximum length")
    
    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def get_text_length_difference(self) -> int:
        """
        Get the difference in text length between ASR draft and final note.
        
        Returns:
            Length difference (positive = final note is longer)
        """
        return len(self.final_note) - len(self.asr_draft)
    
    def get_text_length_ratio(self) -> float:
        """
        Get the ratio of final note length to ASR draft length.
        
        Returns:
            Length ratio (1.0 = same length, >1.0 = final note longer)
        """
        if len(self.asr_draft) == 0:
            return float('inf') if len(self.final_note) > 0 else 1.0
        
        return len(self.final_note) / len(self.asr_draft)
    
    def has_significant_changes(self, threshold: float = 0.1) -> bool:
        """
        Check if there are significant changes between ASR draft and final note.
        
        Args:
            threshold: Minimum change ratio to consider significant
            
        Returns:
            True if changes are significant
        """
        length_ratio = self.get_text_length_ratio()
        return abs(length_ratio - 1.0) > threshold
    
    def is_suitable_for_training(self) -> bool:
        """
        Check if this data is suitable for RAG training.
        
        Returns:
            True if suitable for training
        """
        # Must have meaningful content
        if len(self.asr_draft.strip()) < 10 or len(self.final_note.strip()) < 10:
            return False
        
        # Must have actual corrections
        if not self.has_significant_changes():
            return False
        
        # Should not be test data
        if self.is_test_data:
            return False
        
        return True
    
    def is_suitable_for_testing(self) -> bool:
        """
        Check if this data is suitable for validation testing.
        
        Returns:
            True if suitable for testing
        """
        # Must have meaningful content
        if len(self.asr_draft.strip()) < 10 or len(self.final_note.strip()) < 10:
            return False
        
        # Must have actual corrections to validate
        if not self.has_significant_changes():
            return False
        
        return True
    
    def mark_as_test_data(self) -> None:
        """Mark this data as test data for validation."""
        self.is_test_data = True
    
    def unmark_as_test_data(self) -> None:
        """Unmark this data as test data."""
        self.is_test_data = False
    
    def get_word_count_asr(self) -> int:
        """
        Get word count of ASR draft.
        
        Returns:
            Word count
        """
        return len(self.asr_draft.split())
    
    def get_word_count_final(self) -> int:
        """
        Get word count of final note.
        
        Returns:
            Word count
        """
        return len(self.final_note.split())
    
    def get_processing_age_days(self) -> Optional[int]:
        """
        Get age of processing in days.
        
        Returns:
            Days since processing, or None if processing_date not set
        """
        if self.processing_date is None:
            return None
        
        age = datetime.utcnow() - self.processing_date
        return age.days
    
    def is_recent_data(self, days_threshold: int = 30) -> bool:
        """
        Check if this is recent data.
        
        Args:
            days_threshold: Maximum age in days to consider recent
            
        Returns:
            True if data is recent
        """
        age_days = self.get_processing_age_days()
        if age_days is None:
            return False
        
        return age_days <= days_threshold
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the historical data.
        
        Returns:
            Dictionary containing data summary
        """
        return {
            "id": str(self.id),
            "speaker_id": str(self.speaker_id),
            "instanote_job_id": self.instanote_job_id,
            "note_type": self.note_type,
            "asr_engine": self.asr_engine,
            "asr_word_count": self.get_word_count_asr(),
            "final_word_count": self.get_word_count_final(),
            "text_length_difference": self.get_text_length_difference(),
            "text_length_ratio": self.get_text_length_ratio(),
            "has_significant_changes": self.has_significant_changes(),
            "is_test_data": self.is_test_data,
            "suitable_for_training": self.is_suitable_for_training(),
            "suitable_for_testing": self.is_suitable_for_testing(),
            "processing_date": self.processing_date.isoformat() if self.processing_date else None,
            "processing_age_days": self.get_processing_age_days(),
            "is_recent_data": self.is_recent_data(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __eq__(self, other: "HistoricalASRData") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, HistoricalASRData):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation of the historical ASR data."""
        return f"HistoricalASRData(id={self.id}, speaker_id={self.speaker_id}, test_data={self.is_test_data})"
