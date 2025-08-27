"""
Validation Test Session Domain Entity

Represents an MT validation session for speaker bucket evaluation.
Core domain entity for the medical transcriptionist validation workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID
from enum import Enum


class SessionStatus(str, Enum):
    """Enumeration for validation session status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ValidationTestSession:
    """
    Domain entity representing an MT validation test session.
    
    This entity encapsulates the validation workflow where medical transcriptionists
    review RAG-corrected ASR drafts against final notes to assess quality improvements.
    """
    
    id: UUID
    speaker_id: UUID
    session_name: str
    test_data_count: int
    status: SessionStatus = SessionStatus.PENDING
    mt_user_id: Optional[UUID] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the validation test session after initialization."""
        self._validate_required_fields()
        self._validate_test_data_count()
        self._validate_session_name()
        self._validate_status_consistency()
        self._set_defaults()
    
    def _validate_required_fields(self) -> None:
        """Validate required fields."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")
        
        if not self.session_name or not self.session_name.strip():
            raise ValueError("session_name cannot be empty")
    
    def _validate_test_data_count(self) -> None:
        """Validate test data count."""
        if self.test_data_count <= 0:
            raise ValueError("test_data_count must be positive")
        
        if self.test_data_count > 1000:  # Reasonable upper limit
            raise ValueError("test_data_count exceeds maximum allowed")
    
    def _validate_session_name(self) -> None:
        """Validate session name."""
        if len(self.session_name) > 255:
            raise ValueError("session_name exceeds maximum length")
    
    def _validate_status_consistency(self) -> None:
        """Validate status consistency with timestamps."""
        if self.status == SessionStatus.IN_PROGRESS and self.started_at is None:
            # Auto-set started_at if status is in_progress but not set
            self.started_at = datetime.utcnow()
        
        if self.status == SessionStatus.COMPLETED and self.completed_at is None:
            # Auto-set completed_at if status is completed but not set
            self.completed_at = datetime.utcnow()
    
    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_pending(self) -> bool:
        """Check if session is pending."""
        return self.status == SessionStatus.PENDING
    
    def is_in_progress(self) -> bool:
        """Check if session is in progress."""
        return self.status == SessionStatus.IN_PROGRESS
    
    def is_completed(self) -> bool:
        """Check if session is completed."""
        return self.status == SessionStatus.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if session is cancelled."""
        return self.status == SessionStatus.CANCELLED
    
    def can_be_started(self) -> bool:
        """Check if session can be started."""
        return self.status == SessionStatus.PENDING
    
    def can_be_completed(self) -> bool:
        """Check if session can be completed."""
        return self.status == SessionStatus.IN_PROGRESS
    
    def can_be_cancelled(self) -> bool:
        """Check if session can be cancelled."""
        return self.status in [SessionStatus.PENDING, SessionStatus.IN_PROGRESS]
    
    def start_session(self, mt_user_id: UUID) -> None:
        """
        Start the validation session.
        
        Args:
            mt_user_id: Medical transcriptionist user ID
            
        Raises:
            ValueError: If session cannot be started
        """
        if not self.can_be_started():
            raise ValueError(f"Session cannot be started from status: {self.status}")
        
        self.status = SessionStatus.IN_PROGRESS
        self.mt_user_id = mt_user_id
        self.started_at = datetime.utcnow()
    
    def complete_session(self) -> None:
        """
        Complete the validation session.
        
        Raises:
            ValueError: If session cannot be completed
        """
        if not self.can_be_completed():
            raise ValueError(f"Session cannot be completed from status: {self.status}")
        
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def cancel_session(self, reason: str) -> None:
        """
        Cancel the validation session.
        
        Args:
            reason: Reason for cancellation
            
        Raises:
            ValueError: If session cannot be cancelled
        """
        if not self.can_be_cancelled():
            raise ValueError(f"Session cannot be cancelled from status: {self.status}")
        
        self.status = SessionStatus.CANCELLED
        self.session_metadata["cancellation_reason"] = reason
        self.session_metadata["cancelled_at"] = datetime.utcnow().isoformat()
    
    def get_duration_minutes(self) -> Optional[float]:
        """
        Get session duration in minutes.
        
        Returns:
            Duration in minutes, or None if not applicable
        """
        if self.started_at is None:
            return None
        
        end_time = self.completed_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds() / 60
    
    def get_progress_percentage(self, completed_items: int) -> float:
        """
        Get session progress percentage.
        
        Args:
            completed_items: Number of completed validation items
            
        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if self.test_data_count == 0:
            return 100.0
        
        progress = min(completed_items / self.test_data_count, 1.0) * 100
        return round(progress, 2)
    
    def is_overdue(self, max_duration_hours: int = 8) -> bool:
        """
        Check if session is overdue.
        
        Args:
            max_duration_hours: Maximum expected duration in hours
            
        Returns:
            True if session is overdue
        """
        if not self.is_in_progress() or self.started_at is None:
            return False
        
        duration_hours = (datetime.utcnow() - self.started_at).total_seconds() / 3600
        return duration_hours > max_duration_hours
    
    def get_estimated_completion_time(self, completed_items: int, avg_time_per_item_minutes: float = 2.0) -> Optional[datetime]:
        """
        Get estimated completion time based on progress.
        
        Args:
            completed_items: Number of completed items
            avg_time_per_item_minutes: Average time per item in minutes
            
        Returns:
            Estimated completion time, or None if not applicable
        """
        if not self.is_in_progress() or self.started_at is None:
            return None
        
        remaining_items = max(0, self.test_data_count - completed_items)
        if remaining_items == 0:
            return datetime.utcnow()
        
        estimated_minutes = remaining_items * avg_time_per_item_minutes
        return datetime.utcnow() + datetime.timedelta(minutes=estimated_minutes)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the session.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.session_metadata[key] = value
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the validation session.
        
        Returns:
            Dictionary containing session summary
        """
        return {
            "id": str(self.id),
            "speaker_id": str(self.speaker_id),
            "session_name": self.session_name,
            "test_data_count": self.test_data_count,
            "status": self.status.value,
            "mt_user_id": str(self.mt_user_id) if self.mt_user_id else None,
            "duration_minutes": self.get_duration_minutes(),
            "is_overdue": self.is_overdue(),
            "can_be_started": self.can_be_started(),
            "can_be_completed": self.can_be_completed(),
            "can_be_cancelled": self.can_be_cancelled(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.session_metadata
        }
    
    def __eq__(self, other: "ValidationTestSession") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, ValidationTestSession):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation of the validation session."""
        return f"ValidationTestSession(id={self.id}, speaker_id={self.speaker_id}, status={self.status.value})"
