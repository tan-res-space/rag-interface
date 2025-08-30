"""
Correction Suggestion Domain Entity

Represents a correction suggestion with confidence scoring and metadata.
Core domain entity for the correction engine service.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from ..value_objects.confidence_score import ConfidenceScore
from ..value_objects.correction_mode import CorrectionMode


@dataclass
class CorrectionSuggestion:
    """
    Domain entity representing a correction suggestion.

    This entity encapsulates correction logic, confidence scoring,
    and metadata for real-time text correction processing.
    """

    id: UUID
    original_text: str
    corrected_text: str
    confidence_score: ConfidenceScore
    correction_type: str
    model_name: str
    metadata: Dict[str, Any] = None
    created_at: datetime = None

    def __post_init__(self):
        """Validate the correction suggestion after initialization."""
        self._validate_texts()
        self._validate_correction_type()
        self._validate_model_name()
        self._set_defaults()

    def _validate_texts(self) -> None:
        """Validate original and corrected text fields."""
        if not self.original_text or not self.original_text.strip():
            raise ValueError("original_text cannot be empty")

        if not self.corrected_text or not self.corrected_text.strip():
            raise ValueError("corrected_text cannot be empty")

        if self.original_text.strip() == self.corrected_text.strip():
            raise ValueError("original_text and corrected_text cannot be identical")

    def _validate_correction_type(self) -> None:
        """Validate correction type field."""
        if not self.correction_type or not self.correction_type.strip():
            raise ValueError("correction_type cannot be empty")

    def _validate_model_name(self) -> None:
        """Validate model name field."""
        if not self.model_name or not self.model_name.strip():
            raise ValueError("model_name cannot be empty")

    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.metadata is None:
            self.metadata = {}

        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def is_high_confidence(self) -> bool:
        """
        Check if this is a high confidence suggestion.

        Returns:
            True if confidence score is high
        """
        return self.confidence_score.is_high_confidence()

    def should_apply_with_mode(self, mode: CorrectionMode) -> bool:
        """
        Determine if suggestion should be applied with given correction mode.

        Args:
            mode: Correction mode to check against

        Returns:
            True if suggestion should be applied
        """
        return mode.should_apply_correction(self.confidence_score.value)

    def get_correction_length_difference(self) -> int:
        """
        Get the length difference between original and corrected text.

        Returns:
            Positive for expansion, negative for contraction, zero for same length
        """
        return len(self.corrected_text) - len(self.original_text)

    def get_correction_ratio(self) -> float:
        """
        Get the ratio of corrected text length to original text length.

        Returns:
            Ratio as float (>1.0 for expansion, <1.0 for contraction)
        """
        if len(self.original_text) == 0:
            return float("inf") if len(self.corrected_text) > 0 else 1.0

        return len(self.corrected_text) / len(self.original_text)

    def is_expansion(self) -> bool:
        """
        Check if this correction expands the text.

        Returns:
            True if corrected text is longer than original
        """
        return len(self.corrected_text) > len(self.original_text)

    def is_contraction(self) -> bool:
        """
        Check if this correction contracts the text.

        Returns:
            True if corrected text is shorter than original
        """
        return len(self.corrected_text) < len(self.original_text)

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value by key.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def has_metadata_key(self, key: str) -> bool:
        """
        Check if metadata contains specific key.

        Args:
            key: Metadata key to check

        Returns:
            True if key exists, False otherwise
        """
        return key in self.metadata

    def get_error_position(self) -> Optional[Dict[str, int]]:
        """
        Get error position from metadata.

        Returns:
            Dictionary with 'start' and 'end' positions if available
        """
        return self.get_metadata_value("error_position")

    def get_severity_level(self) -> Optional[str]:
        """
        Get severity level from metadata.

        Returns:
            Severity level string if available
        """
        return self.get_metadata_value("severity")

    def get_alternatives(self) -> list:
        """
        Get alternative corrections from metadata.

        Returns:
            List of alternative corrections, empty list if not available
        """
        return self.get_metadata_value("alternatives", [])

    def is_grammar_correction(self) -> bool:
        """
        Check if this is a grammar correction.

        Returns:
            True if correction type is grammar-related
        """
        grammar_types = ["grammar", "subject_verb_agreement", "tense", "article"]
        return self.correction_type.lower() in grammar_types

    def is_spelling_correction(self) -> bool:
        """
        Check if this is a spelling correction.

        Returns:
            True if correction type is spelling-related
        """
        spelling_types = ["spelling", "typo", "misspelling"]
        return self.correction_type.lower() in spelling_types

    def is_style_correction(self) -> bool:
        """
        Check if this is a style correction.

        Returns:
            True if correction type is style-related
        """
        style_types = ["style", "clarity", "conciseness", "formality"]
        return self.correction_type.lower() in style_types

    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the correction suggestion.

        Returns:
            Dictionary containing suggestion summary
        """
        return {
            "id": str(self.id),
            "original_text": self.original_text,
            "corrected_text": self.corrected_text,
            "confidence_score": self.confidence_score.value,
            "confidence_level": self.confidence_score.get_confidence_level(),
            "correction_type": self.correction_type,
            "model_name": self.model_name,
            "length_difference": self.get_correction_length_difference(),
            "correction_ratio": self.get_correction_ratio(),
            "is_expansion": self.is_expansion(),
            "is_contraction": self.is_contraction(),
            "is_grammar": self.is_grammar_correction(),
            "is_spelling": self.is_spelling_correction(),
            "is_style": self.is_style_correction(),
            "metadata_keys": list(self.metadata.keys()),
            "created_at": self.created_at.isoformat(),
        }

    # Comparison methods for sorting and ranking
    def __lt__(self, other: "CorrectionSuggestion") -> bool:
        """Less than comparison based on confidence score."""
        if not isinstance(other, CorrectionSuggestion):
            return NotImplemented
        return self.confidence_score < other.confidence_score

    def __le__(self, other: "CorrectionSuggestion") -> bool:
        """Less than or equal comparison based on confidence score."""
        if not isinstance(other, CorrectionSuggestion):
            return NotImplemented
        return self.confidence_score <= other.confidence_score

    def __gt__(self, other: "CorrectionSuggestion") -> bool:
        """Greater than comparison based on confidence score."""
        if not isinstance(other, CorrectionSuggestion):
            return NotImplemented
        return self.confidence_score > other.confidence_score

    def __ge__(self, other: "CorrectionSuggestion") -> bool:
        """Greater than or equal comparison based on confidence score."""
        if not isinstance(other, CorrectionSuggestion):
            return NotImplemented
        return self.confidence_score >= other.confidence_score

    def __eq__(self, other: "CorrectionSuggestion") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, CorrectionSuggestion):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
