"""
Speaker Error-Correction Pair Domain Entity

Represents error-correction pairs extracted from speaker historical data for RAG training.
Core domain entity for speaker-specific RAG processing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass
class SpeakerErrorCorrectionPair:
    """
    Domain entity representing an error-correction pair for speaker-specific RAG training.

    This entity encapsulates error patterns and their corrections extracted from
    historical ASR data for a specific speaker, used to train speaker-specific RAG models.
    """

    id: UUID
    speaker_id: UUID
    historical_data_id: UUID
    error_text: str
    correction_text: str
    error_type: Optional[str] = None
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    confidence_score: Optional[Decimal] = None
    embedding_id: Optional[UUID] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate the error-correction pair after initialization."""
        self._validate_required_fields()
        self._validate_text_content()
        self._validate_confidence_score()
        self._set_defaults()

    def _validate_required_fields(self) -> None:
        """Validate required fields."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")

        if not self.historical_data_id:
            raise ValueError("historical_data_id is required")

        if not self.error_text or not self.error_text.strip():
            raise ValueError("error_text cannot be empty")

        if not self.correction_text or not self.correction_text.strip():
            raise ValueError("correction_text cannot be empty")

    def _validate_text_content(self) -> None:
        """Validate text content fields."""
        # Check for reasonable text lengths
        if len(self.error_text) > 5000:
            raise ValueError("error_text exceeds maximum length")

        if len(self.correction_text) > 5000:
            raise ValueError("correction_text exceeds maximum length")

        # Ensure error and correction are different
        if self.error_text.strip() == self.correction_text.strip():
            raise ValueError("error_text and correction_text cannot be identical")

        # Validate context lengths if provided
        if self.context_before and len(self.context_before) > 1000:
            raise ValueError("context_before exceeds maximum length")

        if self.context_after and len(self.context_after) > 1000:
            raise ValueError("context_after exceeds maximum length")

    def _validate_confidence_score(self) -> None:
        """Validate confidence score field."""
        if self.confidence_score is not None:
            if self.confidence_score < 0 or self.confidence_score > 1:
                raise ValueError("confidence_score must be between 0 and 1")

    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def get_error_length(self) -> int:
        """
        Get length of error text in characters.

        Returns:
            Error text length
        """
        return len(self.error_text)

    def get_correction_length(self) -> int:
        """
        Get length of correction text in characters.

        Returns:
            Correction text length
        """
        return len(self.correction_text)

    def get_length_difference(self) -> int:
        """
        Get difference in length between correction and error.

        Returns:
            Length difference (positive = correction is longer)
        """
        return len(self.correction_text) - len(self.error_text)

    def get_length_ratio(self) -> float:
        """
        Get ratio of correction length to error length.

        Returns:
            Length ratio (1.0 = same length, >1.0 = correction longer)
        """
        if len(self.error_text) == 0:
            return float("inf") if len(self.correction_text) > 0 else 1.0

        return len(self.correction_text) / len(self.error_text)

    def has_context(self) -> bool:
        """
        Check if this pair has context information.

        Returns:
            True if context before or after is available
        """
        return bool(self.context_before or self.context_after)

    def get_full_context(self) -> str:
        """
        Get full context string combining before, error, and after.

        Returns:
            Full context string
        """
        parts = []

        if self.context_before:
            parts.append(self.context_before.strip())

        parts.append(f"[ERROR: {self.error_text}]")

        if self.context_after:
            parts.append(self.context_after.strip())

        return " ".join(parts)

    def get_correction_context(self) -> str:
        """
        Get full context string with correction instead of error.

        Returns:
            Context string with correction
        """
        parts = []

        if self.context_before:
            parts.append(self.context_before.strip())

        parts.append(self.correction_text)

        if self.context_after:
            parts.append(self.context_after.strip())

        return " ".join(parts)

    def is_high_confidence(self) -> bool:
        """
        Check if this is a high confidence error-correction pair.

        Returns:
            True if confidence >= 0.8
        """
        if self.confidence_score is None:
            return False

        return self.confidence_score >= Decimal("0.8")

    def is_suitable_for_training(self) -> bool:
        """
        Check if this pair is suitable for RAG training.

        Returns:
            True if suitable for training
        """
        # Must have meaningful content
        if len(self.error_text.strip()) < 3 or len(self.correction_text.strip()) < 3:
            return False

        # Should have reasonable confidence if available
        if self.confidence_score is not None and self.confidence_score < Decimal("0.3"):
            return False

        # Should not be too long (might be noisy)
        if len(self.error_text) > 500 or len(self.correction_text) > 500:
            return False

        return True

    def categorize_error_type(self) -> str:
        """
        Automatically categorize the error type based on text analysis.

        Returns:
            Error type category
        """
        if self.error_type:
            return self.error_type

        error_words = set(self.error_text.lower().split())
        correction_words = set(self.correction_text.lower().split())

        # Simple heuristics for error categorization
        if len(error_words - correction_words) > len(correction_words - error_words):
            return "deletion"
        elif len(correction_words - error_words) > len(error_words - correction_words):
            return "insertion"
        elif error_words != correction_words:
            return "substitution"
        else:
            return "formatting"

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the error-correction pair.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_training_example(self) -> Dict[str, str]:
        """
        Get training example format for RAG model.

        Returns:
            Dictionary with input and target for training
        """
        return {
            "input": self.get_full_context(),
            "target": self.get_correction_context(),
            "error_type": self.categorize_error_type(),
            "speaker_id": str(self.speaker_id),
        }

    def get_pair_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the error-correction pair.

        Returns:
            Dictionary containing pair summary
        """
        return {
            "id": str(self.id),
            "speaker_id": str(self.speaker_id),
            "historical_data_id": str(self.historical_data_id),
            "error_text": self.error_text,
            "correction_text": self.correction_text,
            "error_type": self.categorize_error_type(),
            "error_length": self.get_error_length(),
            "correction_length": self.get_correction_length(),
            "length_difference": self.get_length_difference(),
            "length_ratio": self.get_length_ratio(),
            "has_context": self.has_context(),
            "confidence_score": (
                float(self.confidence_score) if self.confidence_score else None
            ),
            "is_high_confidence": self.is_high_confidence(),
            "suitable_for_training": self.is_suitable_for_training(),
            "embedding_id": str(self.embedding_id) if self.embedding_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __eq__(self, other: "SpeakerErrorCorrectionPair") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, SpeakerErrorCorrectionPair):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)

    def __str__(self) -> str:
        """String representation of the error-correction pair."""
        return f"SpeakerErrorCorrectionPair(id={self.id}, speaker_id={self.speaker_id}, error_type={self.categorize_error_type()})"
