"""
Verification Result Domain Entity

Represents a verification result with quality scoring and status tracking.
Core domain entity for the verification service.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from ..value_objects.quality_score import QualityScore
from ..value_objects.verification_status import VerificationStatus


@dataclass
class VerificationResult:
    """
    Domain entity representing a verification result.
    
    This entity encapsulates verification logic, quality scoring,
    and status tracking for correction verification processing.
    """
    
    id: UUID
    correction_id: UUID
    quality_score: QualityScore
    status: VerificationStatus
    verified_by: str
    verification_notes: Optional[str] = None
    metadata: Dict[str, Any] = None
    verified_at: datetime = None
    
    def __post_init__(self):
        """Validate the verification result after initialization."""
        self._validate_verified_by()
        self._set_defaults()
    
    def _validate_verified_by(self) -> None:
        """Validate verified_by field."""
        if not self.verified_by or not self.verified_by.strip():
            raise ValueError("verified_by cannot be empty")
    
    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.metadata is None:
            self.metadata = {}
        
        if self.verified_at is None:
            self.verified_at = datetime.utcnow()
    
    def is_verified(self) -> bool:
        """
        Check if this result is verified.
        
        Returns:
            True if status is verified
        """
        return self.status == VerificationStatus.VERIFIED
    
    def is_rejected(self) -> bool:
        """
        Check if this result is rejected.
        
        Returns:
            True if status is rejected
        """
        return self.status == VerificationStatus.REJECTED
    
    def is_pending(self) -> bool:
        """
        Check if this result is pending verification.
        
        Returns:
            True if status is pending or needs review
        """
        return self.status.is_pending()
    
    def is_high_quality(self) -> bool:
        """
        Check if this is a high quality result.
        
        Returns:
            True if quality score is high
        """
        return self.quality_score.is_high_quality()
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the verification result.
        
        Returns:
            Dictionary containing verification summary
        """
        return {
            "id": str(self.id),
            "correction_id": str(self.correction_id),
            "quality_score": self.quality_score.value,
            "quality_level": self.quality_score.get_quality_level(),
            "status": self.status.value,
            "verified_by": self.verified_by,
            "verification_notes": self.verification_notes,
            "is_verified": self.is_verified(),
            "is_rejected": self.is_rejected(),
            "is_pending": self.is_pending(),
            "is_high_quality": self.is_high_quality(),
            "verified_at": self.verified_at.isoformat(),
            "metadata_keys": list(self.metadata.keys())
        }
    
    def __eq__(self, other: "VerificationResult") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, VerificationResult):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
