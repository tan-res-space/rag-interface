"""
Error Report Domain Entity

Core domain entity representing an error report in the ASR system.
Contains business rules and validation logic.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Enumeration for error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorStatus(str, Enum):
    """Enumeration for error report status"""
    PENDING = "pending"
    PROCESSED = "processed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ErrorReport:
    """
    Error Report Domain Entity
    
    Represents an error report submitted by QA personnel.
    Immutable entity with business rule validation.
    """
    
    # Required fields
    error_id: UUID
    job_id: UUID
    speaker_id: UUID
    reported_by: UUID
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: SeverityLevel
    start_position: int
    end_position: int
    error_timestamp: datetime
    reported_at: datetime
    
    # Optional fields with defaults
    context_notes: Optional[str] = None
    status: ErrorStatus = ErrorStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate business rules after initialization"""
        self._validate_position_range()
        self._validate_text_difference()
        self._validate_error_categories()
        self._validate_text_fields()
    
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
        return self.original_text[self.start_position:self.end_position]

    def get_correction_text(self) -> str:
        """Extract the correction portion from corrected text"""
        return self.corrected_text[self.start_position:self.end_position]
    
    def with_status(self, new_status: ErrorStatus) -> 'ErrorReport':
        """Create a new ErrorReport with updated status (immutable update)"""
        return ErrorReport(
            error_id=self.error_id,
            job_id=self.job_id,
            speaker_id=self.speaker_id,
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
            status=new_status,
            metadata=self.metadata
        )
