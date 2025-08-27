"""
Bucket Transition Request Domain Entity

Represents a request to transition a speaker from one bucket to another.
Core domain entity for speaker bucket management workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from decimal import Decimal

from ..value_objects.speaker_bucket import SpeakerBucket


@dataclass
class BucketTransitionRequest:
    """
    Domain entity representing a bucket transition request.
    
    This entity encapsulates the request to move a speaker from one bucket
    to another, including justification, approval workflow, and metrics.
    """
    
    id: UUID
    speaker_id: UUID
    from_bucket: SpeakerBucket
    to_bucket: SpeakerBucket
    transition_reason: str
    ser_improvement: Optional[Decimal] = None
    requested_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    status: str = "pending"  # pending, approved, rejected, cancelled
    approval_notes: Optional[str] = None
    transition_data: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the bucket transition request after initialization."""
        self._validate_required_fields()
        self._validate_bucket_transition()
        self._validate_status()
        self._validate_ser_improvement()
        self._set_defaults()
    
    def _validate_required_fields(self) -> None:
        """Validate required fields."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")
        
        if not self.transition_reason or not self.transition_reason.strip():
            raise ValueError("transition_reason cannot be empty")
        
        if len(self.transition_reason) > 1000:
            raise ValueError("transition_reason exceeds maximum length")
    
    def _validate_bucket_transition(self) -> None:
        """Validate bucket transition logic."""
        if self.from_bucket == self.to_bucket:
            raise ValueError("from_bucket and to_bucket cannot be the same")
        
        if not self.from_bucket.can_transition_to(self.to_bucket):
            raise ValueError(f"Invalid transition from {self.from_bucket} to {self.to_bucket}")
    
    def _validate_status(self) -> None:
        """Validate status field."""
        valid_statuses = ["pending", "approved", "rejected", "cancelled"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")
    
    def _validate_ser_improvement(self) -> None:
        """Validate SER improvement field."""
        if self.ser_improvement is not None:
            if self.ser_improvement < 0:
                raise ValueError("ser_improvement cannot be negative")
            
            if self.ser_improvement > 100:
                raise ValueError("ser_improvement cannot exceed 100")
    
    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_pending(self) -> bool:
        """Check if request is pending approval."""
        return self.status == "pending"
    
    def is_approved(self) -> bool:
        """Check if request is approved."""
        return self.status == "approved"
    
    def is_rejected(self) -> bool:
        """Check if request is rejected."""
        return self.status == "rejected"
    
    def is_cancelled(self) -> bool:
        """Check if request is cancelled."""
        return self.status == "cancelled"
    
    def is_improvement_transition(self) -> bool:
        """
        Check if this is an improvement transition (to better bucket).
        
        Returns:
            True if transitioning to a better bucket
        """
        return self.to_bucket.get_priority_level() > self.from_bucket.get_priority_level()
    
    def is_degradation_transition(self) -> bool:
        """
        Check if this is a degradation transition (to worse bucket).
        
        Returns:
            True if transitioning to a worse bucket
        """
        return self.to_bucket.get_priority_level() < self.from_bucket.get_priority_level()
    
    def get_transition_type(self) -> str:
        """
        Get the type of transition.
        
        Returns:
            Transition type string
        """
        if self.is_improvement_transition():
            return "improvement"
        elif self.is_degradation_transition():
            return "degradation"
        else:
            return "lateral"
    
    def requires_approval(self) -> bool:
        """
        Check if this transition requires approval.
        
        Returns:
            True if approval is required
        """
        # All bucket transitions require approval for audit trail
        return True
    
    def can_be_approved_by(self, user_id: UUID, user_roles: list) -> bool:
        """
        Check if user can approve this transition.
        
        Args:
            user_id: User ID attempting approval
            user_roles: List of user roles
            
        Returns:
            True if user can approve
        """
        # Cannot approve own request
        if self.requested_by == user_id:
            return False
        
        # Must have appropriate role
        approver_roles = ["admin", "qa_supervisor"]
        return any(role in approver_roles for role in user_roles)
    
    def approve(self, approved_by: UUID, approval_notes: Optional[str] = None) -> None:
        """
        Approve the transition request.
        
        Args:
            approved_by: User ID who approved the request
            approval_notes: Optional approval notes
            
        Raises:
            ValueError: If request cannot be approved
        """
        if not self.is_pending():
            raise ValueError("Only pending requests can be approved")
        
        self.status = "approved"
        self.approved_by = approved_by
        self.approval_notes = approval_notes
        self.approved_at = datetime.utcnow()
    
    def reject(self, rejected_by: UUID, rejection_reason: str) -> None:
        """
        Reject the transition request.
        
        Args:
            rejected_by: User ID who rejected the request
            rejection_reason: Reason for rejection
            
        Raises:
            ValueError: If request cannot be rejected
        """
        if not self.is_pending():
            raise ValueError("Only pending requests can be rejected")
        
        self.status = "rejected"
        self.approved_by = rejected_by  # Store who made the decision
        self.approval_notes = rejection_reason
        self.approved_at = datetime.utcnow()
    
    def cancel(self, cancelled_by: UUID, cancellation_reason: str) -> None:
        """
        Cancel the transition request.
        
        Args:
            cancelled_by: User ID who cancelled the request
            cancellation_reason: Reason for cancellation
            
        Raises:
            ValueError: If request cannot be cancelled
        """
        if not self.is_pending():
            raise ValueError("Only pending requests can be cancelled")
        
        self.status = "cancelled"
        self.approved_by = cancelled_by
        self.approval_notes = cancellation_reason
        self.approved_at = datetime.utcnow()
    
    def get_processing_time_hours(self) -> Optional[float]:
        """
        Get processing time in hours.
        
        Returns:
            Processing time in hours, or None if not processed
        """
        if self.approved_at is None:
            return None
        
        processing_time = self.approved_at - self.created_at
        return processing_time.total_seconds() / 3600
    
    def is_urgent(self) -> bool:
        """
        Check if this is an urgent transition request.
        
        Returns:
            True if urgent (degradation transitions are urgent)
        """
        return self.is_degradation_transition()
    
    def get_priority_score(self) -> int:
        """
        Get priority score for processing (lower = higher priority).
        
        Returns:
            Priority score
        """
        base_priority = 5
        
        # Higher priority for degradation transitions
        if self.is_degradation_transition():
            base_priority = 1
        elif self.is_improvement_transition():
            base_priority = 3
        
        # Adjust based on SER improvement
        if self.ser_improvement is not None:
            if self.ser_improvement >= 20:  # Significant improvement
                base_priority = max(1, base_priority - 2)
            elif self.ser_improvement >= 10:  # Moderate improvement
                base_priority = max(1, base_priority - 1)
        
        return base_priority
    
    def get_request_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the transition request.
        
        Returns:
            Dictionary containing request summary
        """
        return {
            "id": str(self.id),
            "speaker_id": str(self.speaker_id),
            "from_bucket": self.from_bucket.value,
            "to_bucket": self.to_bucket.value,
            "transition_type": self.get_transition_type(),
            "transition_reason": self.transition_reason,
            "ser_improvement": float(self.ser_improvement) if self.ser_improvement else None,
            "status": self.status,
            "requested_by": str(self.requested_by) if self.requested_by else None,
            "approved_by": str(self.approved_by) if self.approved_by else None,
            "approval_notes": self.approval_notes,
            "is_urgent": self.is_urgent(),
            "priority_score": self.get_priority_score(),
            "processing_time_hours": self.get_processing_time_hours(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None
        }
    
    def __eq__(self, other: "BucketTransitionRequest") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, BucketTransitionRequest):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation of the transition request."""
        return f"BucketTransitionRequest(id={self.id}, {self.from_bucket}->{self.to_bucket}, status={self.status})"
