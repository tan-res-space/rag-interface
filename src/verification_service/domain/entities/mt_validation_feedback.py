"""
MT Validation Feedback Domain Entity

Represents medical transcriptionist feedback on RAG corrections.
Core domain entity for the MT validation workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID


class ImprovementAssessment(str, Enum):
    """Enumeration for improvement assessment levels"""

    SIGNIFICANT = "significant"
    MODERATE = "moderate"
    MINIMAL = "minimal"
    NONE = "none"
    WORSE = "worse"


@dataclass
class MTValidationFeedback:
    """
    Domain entity representing MT validation feedback.

    This entity encapsulates feedback from medical transcriptionists on
    RAG-corrected ASR drafts compared to final corrected notes.
    """

    id: UUID
    session_id: UUID
    historical_data_id: UUID
    original_asr_text: str
    rag_corrected_text: str
    final_reference_text: str
    mt_feedback_rating: int  # 1-5 scale
    mt_comments: Optional[str] = None
    improvement_assessment: ImprovementAssessment = ImprovementAssessment.NONE
    recommended_for_bucket_change: bool = False
    feedback_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate the MT feedback after initialization."""
        self._validate_required_fields()
        self._validate_rating()
        self._validate_text_content()
        self._validate_improvement_assessment()
        self._set_defaults()

    def _validate_required_fields(self) -> None:
        """Validate required fields."""
        if not self.session_id:
            raise ValueError("session_id is required")

        if not self.historical_data_id:
            raise ValueError("historical_data_id is required")

        if not self.original_asr_text or not self.original_asr_text.strip():
            raise ValueError("original_asr_text cannot be empty")

        if not self.rag_corrected_text or not self.rag_corrected_text.strip():
            raise ValueError("rag_corrected_text cannot be empty")

        if not self.final_reference_text or not self.final_reference_text.strip():
            raise ValueError("final_reference_text cannot be empty")

    def _validate_rating(self) -> None:
        """Validate MT feedback rating."""
        if not isinstance(self.mt_feedback_rating, int):
            raise ValueError("mt_feedback_rating must be an integer")

        if not (1 <= self.mt_feedback_rating <= 5):
            raise ValueError("mt_feedback_rating must be between 1 and 5")

    def _validate_text_content(self) -> None:
        """Validate text content fields."""
        # Check for reasonable text lengths
        max_length = 50000  # 50KB limit

        if len(self.original_asr_text) > max_length:
            raise ValueError("original_asr_text exceeds maximum length")

        if len(self.rag_corrected_text) > max_length:
            raise ValueError("rag_corrected_text exceeds maximum length")

        if len(self.final_reference_text) > max_length:
            raise ValueError("final_reference_text exceeds maximum length")

        # Validate comments length if provided
        if self.mt_comments and len(self.mt_comments) > 5000:
            raise ValueError("mt_comments exceeds maximum length")

    def _validate_improvement_assessment(self) -> None:
        """Validate improvement assessment."""
        if not isinstance(self.improvement_assessment, ImprovementAssessment):
            raise ValueError(
                "improvement_assessment must be a valid ImprovementAssessment"
            )

    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def is_positive_feedback(self) -> bool:
        """
        Check if this is positive feedback (rating >= 4).

        Returns:
            True if feedback is positive
        """
        return self.mt_feedback_rating >= 4

    def is_negative_feedback(self) -> bool:
        """
        Check if this is negative feedback (rating <= 2).

        Returns:
            True if feedback is negative
        """
        return self.mt_feedback_rating <= 2

    def shows_significant_improvement(self) -> bool:
        """
        Check if feedback shows significant improvement.

        Returns:
            True if improvement is significant or moderate
        """
        return self.improvement_assessment in [
            ImprovementAssessment.SIGNIFICANT,
            ImprovementAssessment.MODERATE,
        ]

    def shows_degradation(self) -> bool:
        """
        Check if feedback shows quality degradation.

        Returns:
            True if RAG correction made things worse
        """
        return self.improvement_assessment == ImprovementAssessment.WORSE

    def get_quality_score(self) -> float:
        """
        Get normalized quality score (0.0 to 1.0).

        Returns:
            Quality score based on rating
        """
        return (self.mt_feedback_rating - 1) / 4.0

    def get_improvement_score(self) -> float:
        """
        Get improvement score based on assessment (0.0 to 1.0).

        Returns:
            Improvement score
        """
        score_map = {
            ImprovementAssessment.WORSE: 0.0,
            ImprovementAssessment.NONE: 0.2,
            ImprovementAssessment.MINIMAL: 0.4,
            ImprovementAssessment.MODERATE: 0.7,
            ImprovementAssessment.SIGNIFICANT: 1.0,
        }
        return score_map[self.improvement_assessment]

    def get_combined_score(self) -> float:
        """
        Get combined quality and improvement score.

        Returns:
            Combined score (0.0 to 1.0)
        """
        quality_weight = 0.6
        improvement_weight = 0.4

        return (
            self.get_quality_score() * quality_weight
            + self.get_improvement_score() * improvement_weight
        )

    def has_comments(self) -> bool:
        """
        Check if feedback has comments.

        Returns:
            True if comments are provided
        """
        return bool(self.mt_comments and self.mt_comments.strip())

    def get_text_length_comparison(self) -> Dict[str, int]:
        """
        Get text length comparison between versions.

        Returns:
            Dictionary with text lengths
        """
        return {
            "original_length": len(self.original_asr_text),
            "corrected_length": len(self.rag_corrected_text),
            "reference_length": len(self.final_reference_text),
            "correction_change": len(self.rag_corrected_text)
            - len(self.original_asr_text),
            "reference_change": len(self.final_reference_text)
            - len(self.rag_corrected_text),
        }

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the feedback.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.feedback_metadata[key] = value

    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the feedback.

        Returns:
            Dictionary containing feedback summary
        """
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "historical_data_id": str(self.historical_data_id),
            "mt_feedback_rating": self.mt_feedback_rating,
            "improvement_assessment": self.improvement_assessment.value,
            "recommended_for_bucket_change": self.recommended_for_bucket_change,
            "is_positive_feedback": self.is_positive_feedback(),
            "is_negative_feedback": self.is_negative_feedback(),
            "shows_significant_improvement": self.shows_significant_improvement(),
            "shows_degradation": self.shows_degradation(),
            "quality_score": self.get_quality_score(),
            "improvement_score": self.get_improvement_score(),
            "combined_score": self.get_combined_score(),
            "has_comments": self.has_comments(),
            "text_length_comparison": self.get_text_length_comparison(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __eq__(self, other: "MTValidationFeedback") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, MTValidationFeedback):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)

    def __str__(self) -> str:
        """String representation of the MT feedback."""
        return f"MTValidationFeedback(id={self.id}, session_id={self.session_id}, rating={self.mt_feedback_rating}, assessment={self.improvement_assessment.value})"
