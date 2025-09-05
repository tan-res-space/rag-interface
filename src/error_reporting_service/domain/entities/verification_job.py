"""
Verification Job Domain Entity

Represents jobs pulled from InstaNote Database for error rectification verification.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID


class VerificationStatus(str, Enum):
    """Verification status for jobs"""

    PENDING = "pending"
    VERIFIED = "verified"
    NOT_RECTIFIED = "not_rectified"
    PARTIALLY_RECTIFIED = "partially_rectified"


class VerificationResult(str, Enum):
    """Result of verification process"""

    RECTIFIED = "rectified"
    NOT_RECTIFIED = "not_rectified"
    PARTIALLY_RECTIFIED = "partially_rectified"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class CorrectionApplied:
    """Represents a correction applied by RAG system"""

    correction_type: str
    original_text: str
    corrected_text: str
    confidence: float
    position_start: Optional[int] = None
    position_end: Optional[int] = None

    def __post_init__(self):
        """Validate correction data"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        if not self.original_text.strip():
            raise ValueError("original_text cannot be empty")

        if not self.corrected_text.strip():
            raise ValueError("corrected_text cannot be empty")


@dataclass(frozen=True)
class VerificationJob:
    """
    Verification Job Domain Entity

    Represents a job pulled from InstaNote Database for verification.
    Immutable entity with business rule validation.
    """

    # Required fields
    verification_id: UUID
    job_id: str  # InstaNote job ID
    speaker_id: UUID
    original_draft: str
    retrieval_timestamp: datetime

    # Optional fields
    error_report_id: Optional[UUID] = None
    rag_corrected_draft: Optional[str] = None
    corrections_applied: List[CorrectionApplied] = field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_result: Optional[VerificationResult] = None
    qa_comments: Optional[str] = None
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    job_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate business rules after initialization"""
        self._validate_text_fields()
        self._validate_verification_consistency()
        self._validate_qa_comments()

    def _validate_text_fields(self) -> None:
        """Validate text fields are not empty"""
        if not self.original_draft.strip():
            raise ValueError("original_draft cannot be empty")

        if not self.job_id.strip():
            raise ValueError("job_id cannot be empty")

    def _validate_verification_consistency(self) -> None:
        """Validate verification status and result consistency"""
        if self.verification_status == VerificationStatus.VERIFIED:
            if self.verification_result is None:
                raise ValueError("verification_result required when status is verified")
            if self.verified_by is None:
                raise ValueError("verified_by required when status is verified")
            if self.verified_at is None:
                raise ValueError("verified_at required when status is verified")

    def _validate_qa_comments(self) -> None:
        """Validate QA comments length"""
        if self.qa_comments and len(self.qa_comments) > 2000:
            raise ValueError("qa_comments cannot exceed 2000 characters")

    def __eq__(self, other) -> bool:
        """Equality based on verification_id (entity identity)"""
        if not isinstance(other, VerificationJob):
            return False
        return self.verification_id == other.verification_id

    def __hash__(self) -> int:
        """Hash based on verification_id (entity identity)"""
        return hash(self.verification_id)

    def __str__(self) -> str:
        """String representation of verification job"""
        return (
            f"VerificationJob(id={self.verification_id}, "
            f"job_id={self.job_id}, "
            f"speaker={self.speaker_id}, "
            f"status={self.verification_status.value})"
        )

    def is_pending(self) -> bool:
        """Check if verification is pending"""
        return self.verification_status == VerificationStatus.PENDING

    def is_verified(self) -> bool:
        """Check if verification is completed"""
        return self.verification_status == VerificationStatus.VERIFIED

    def has_corrections(self) -> bool:
        """Check if job has RAG corrections applied"""
        return len(self.corrections_applied) > 0

    def has_rag_corrected_draft(self) -> bool:
        """Check if job has RAG-corrected draft"""
        return self.rag_corrected_draft is not None and self.rag_corrected_draft.strip()

    def get_correction_count(self) -> int:
        """Get number of corrections applied"""
        return len(self.corrections_applied)

    def get_high_confidence_corrections(self, threshold: float = 0.8) -> List[CorrectionApplied]:
        """Get corrections with high confidence scores"""
        return [c for c in self.corrections_applied if c.confidence >= threshold]

    def get_corrections_by_type(self, correction_type: str) -> List[CorrectionApplied]:
        """Get corrections of specific type"""
        return [c for c in self.corrections_applied if c.correction_type == correction_type]

    def calculate_average_confidence(self) -> float:
        """Calculate average confidence of all corrections"""
        if not self.corrections_applied:
            return 0.0

        total_confidence = sum(c.confidence for c in self.corrections_applied)
        return total_confidence / len(self.corrections_applied)

    def is_rectified(self) -> bool:
        """Check if errors were rectified"""
        return self.verification_result == VerificationResult.RECTIFIED

    def is_not_rectified(self) -> bool:
        """Check if errors were not rectified"""
        return self.verification_result == VerificationResult.NOT_RECTIFIED

    def is_partially_rectified(self) -> bool:
        """Check if errors were partially rectified"""
        return self.verification_result == VerificationResult.PARTIALLY_RECTIFIED

    def needs_manual_review(self) -> bool:
        """Check if job needs manual review"""
        # Jobs with low confidence corrections need review
        if self.corrections_applied:
            avg_confidence = self.calculate_average_confidence()
            if avg_confidence < 0.7:
                return True

        # Jobs with many corrections need review
        if len(self.corrections_applied) > 5:
            return True

        # Jobs marked as not rectified need review
        if self.verification_result == VerificationResult.NOT_RECTIFIED:
            return True

        return False

    def get_verification_summary(self) -> dict:
        """Get comprehensive verification summary"""
        return {
            "verification_id": str(self.verification_id),
            "job_id": self.job_id,
            "speaker_id": str(self.speaker_id),
            "status": self.verification_status.value,
            "result": self.verification_result.value if self.verification_result else None,
            "corrections_count": self.get_correction_count(),
            "average_confidence": self.calculate_average_confidence(),
            "high_confidence_corrections": len(self.get_high_confidence_corrections()),
            "needs_manual_review": self.needs_manual_review(),
            "verified_by": str(self.verified_by) if self.verified_by else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "has_qa_comments": bool(self.qa_comments)
        }

    def with_rag_corrections(
        self,
        corrected_draft: str,
        corrections: List[CorrectionApplied]
    ) -> "VerificationJob":
        """Create new VerificationJob with RAG corrections applied"""
        return VerificationJob(
            verification_id=self.verification_id,
            job_id=self.job_id,
            speaker_id=self.speaker_id,
            original_draft=self.original_draft,
            retrieval_timestamp=self.retrieval_timestamp,
            error_report_id=self.error_report_id,
            rag_corrected_draft=corrected_draft,
            corrections_applied=corrections,
            verification_status=self.verification_status,
            verification_result=self.verification_result,
            qa_comments=self.qa_comments,
            verified_by=self.verified_by,
            verified_at=self.verified_at,
            job_metadata=self.job_metadata,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )

    def with_verification_result(
        self,
        result: VerificationResult,
        verified_by: UUID,
        qa_comments: Optional[str] = None
    ) -> "VerificationJob":
        """Create new VerificationJob with verification result"""
        return VerificationJob(
            verification_id=self.verification_id,
            job_id=self.job_id,
            speaker_id=self.speaker_id,
            original_draft=self.original_draft,
            retrieval_timestamp=self.retrieval_timestamp,
            error_report_id=self.error_report_id,
            rag_corrected_draft=self.rag_corrected_draft,
            corrections_applied=self.corrections_applied,
            verification_status=VerificationStatus.VERIFIED,
            verification_result=result,
            qa_comments=qa_comments,
            verified_by=verified_by,
            verified_at=datetime.utcnow(),
            job_metadata=self.job_metadata,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )
