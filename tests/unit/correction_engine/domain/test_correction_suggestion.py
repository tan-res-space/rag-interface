"""
Unit tests for CorrectionSuggestion domain entity.

Following TDD principles for real-time correction processing.
Tests focus on correction suggestion creation, validation, and business logic.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from src.correction_engine_service.domain.entities.correction_suggestion import (
    CorrectionSuggestion,
)
from src.correction_engine_service.domain.value_objects.confidence_score import (
    ConfidenceScore,
)
from src.correction_engine_service.domain.value_objects.correction_mode import (
    CorrectionMode,
)


class TestCorrectionSuggestionCreation:
    """Test correction suggestion entity creation and validation."""

    def test_create_valid_correction_suggestion(self):
        """Test creating a valid correction suggestion."""
        # Arrange
        suggestion_id = uuid4()
        original_text = "I are going to the store"
        corrected_text = "I am going to the store"
        confidence = ConfidenceScore(0.95)
        correction_type = "grammar"
        model_name = "grammar-corrector-v1"

        # Act
        suggestion = CorrectionSuggestion(
            id=suggestion_id,
            original_text=original_text,
            corrected_text=corrected_text,
            confidence_score=confidence,
            correction_type=correction_type,
            model_name=model_name,
        )

        # Assert
        assert suggestion.id == suggestion_id
        assert suggestion.original_text == original_text
        assert suggestion.corrected_text == corrected_text
        assert suggestion.confidence_score == confidence
        assert suggestion.correction_type == correction_type
        assert suggestion.model_name == model_name
        assert isinstance(suggestion.created_at, datetime)
        assert suggestion.metadata == {}

    def test_create_correction_suggestion_with_metadata(self):
        """Test creating correction suggestion with metadata."""
        # Arrange
        metadata = {
            "error_position": {"start": 2, "end": 5},
            "error_category": "subject_verb_agreement",
            "severity": "high",
        }

        # Act
        suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="They was happy",
            corrected_text="They were happy",
            confidence_score=ConfidenceScore(0.9),
            correction_type="grammar",
            model_name="test-model",
            metadata=metadata,
        )

        # Assert
        assert suggestion.metadata == metadata

    def test_create_correction_suggestion_with_empty_original_text_raises_error(self):
        """Test that empty original text raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="original_text cannot be empty"):
            CorrectionSuggestion(
                id=uuid4(),
                original_text="",
                corrected_text="corrected",
                confidence_score=ConfidenceScore(0.8),
                correction_type="grammar",
                model_name="test-model",
            )

    def test_create_correction_suggestion_with_empty_corrected_text_raises_error(self):
        """Test that empty corrected text raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="corrected_text cannot be empty"):
            CorrectionSuggestion(
                id=uuid4(),
                original_text="original",
                corrected_text="",
                confidence_score=ConfidenceScore(0.8),
                correction_type="grammar",
                model_name="test-model",
            )

    def test_create_correction_suggestion_with_same_texts_raises_error(self):
        """Test that identical original and corrected text raises error."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="original_text and corrected_text cannot be identical"
        ):
            CorrectionSuggestion(
                id=uuid4(),
                original_text="same text",
                corrected_text="same text",
                confidence_score=ConfidenceScore(0.8),
                correction_type="grammar",
                model_name="test-model",
            )

    def test_create_correction_suggestion_with_empty_correction_type_raises_error(self):
        """Test that empty correction type raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="correction_type cannot be empty"):
            CorrectionSuggestion(
                id=uuid4(),
                original_text="original",
                corrected_text="corrected",
                confidence_score=ConfidenceScore(0.8),
                correction_type="",
                model_name="test-model",
            )

    def test_create_correction_suggestion_with_empty_model_name_raises_error(self):
        """Test that empty model name raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="model_name cannot be empty"):
            CorrectionSuggestion(
                id=uuid4(),
                original_text="original",
                corrected_text="corrected",
                confidence_score=ConfidenceScore(0.8),
                correction_type="grammar",
                model_name="",
            )


class TestCorrectionSuggestionMethods:
    """Test correction suggestion methods and business logic."""

    def test_is_high_confidence(self):
        """Test high confidence detection."""
        # Arrange
        high_confidence_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.95),
            correction_type="grammar",
            model_name="test-model",
        )

        low_confidence_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.7),
            correction_type="grammar",
            model_name="test-model",
        )

        # Act & Assert
        assert high_confidence_suggestion.is_high_confidence()
        assert not low_confidence_suggestion.is_high_confidence()

    def test_should_apply_with_mode(self):
        """Test whether suggestion should be applied with different modes."""
        # Arrange
        high_confidence_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.95),
            correction_type="grammar",
            model_name="test-model",
        )

        medium_confidence_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.75),
            correction_type="grammar",
            model_name="test-model",
        )

        low_confidence_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.65),
            correction_type="grammar",
            model_name="test-model",
        )

        # Act & Assert
        # Conservative mode
        conservative = CorrectionMode.CONSERVATIVE
        assert high_confidence_suggestion.should_apply_with_mode(conservative)
        assert not medium_confidence_suggestion.should_apply_with_mode(conservative)
        assert not low_confidence_suggestion.should_apply_with_mode(conservative)

        # Balanced mode
        balanced = CorrectionMode.BALANCED
        assert high_confidence_suggestion.should_apply_with_mode(balanced)
        assert not medium_confidence_suggestion.should_apply_with_mode(balanced)
        assert not low_confidence_suggestion.should_apply_with_mode(balanced)

        # Aggressive mode
        aggressive = CorrectionMode.AGGRESSIVE
        assert high_confidence_suggestion.should_apply_with_mode(aggressive)
        assert medium_confidence_suggestion.should_apply_with_mode(aggressive)
        assert low_confidence_suggestion.should_apply_with_mode(aggressive)

    def test_get_correction_length(self):
        """Test getting correction length difference."""
        # Arrange
        suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="short",
            corrected_text="much longer text",
            confidence_score=ConfidenceScore(0.8),
            correction_type="expansion",
            model_name="test-model",
        )

        # Act
        length_diff = suggestion.get_correction_length_difference()

        # Assert
        assert length_diff == len("much longer text") - len("short")
        assert length_diff > 0  # Expansion

    def test_get_correction_ratio(self):
        """Test getting correction ratio."""
        # Arrange
        suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original text",
            corrected_text="corrected text",
            confidence_score=ConfidenceScore(0.8),
            correction_type="grammar",
            model_name="test-model",
        )

        # Act
        ratio = suggestion.get_correction_ratio()

        # Assert
        expected_ratio = len("corrected text") / len("original text")
        assert abs(ratio - expected_ratio) < 1e-9

    def test_is_expansion(self):
        """Test detecting text expansion."""
        # Arrange
        expansion_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="short",
            corrected_text="much longer text",
            confidence_score=ConfidenceScore(0.8),
            correction_type="expansion",
            model_name="test-model",
        )

        contraction_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="very long original text",
            corrected_text="short",
            confidence_score=ConfidenceScore(0.8),
            correction_type="contraction",
            model_name="test-model",
        )

        # Act & Assert
        assert expansion_suggestion.is_expansion()
        assert not contraction_suggestion.is_expansion()

    def test_is_contraction(self):
        """Test detecting text contraction."""
        # Arrange
        expansion_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="short",
            corrected_text="much longer text",
            confidence_score=ConfidenceScore(0.8),
            correction_type="expansion",
            model_name="test-model",
        )

        contraction_suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="very long original text",
            corrected_text="short",
            confidence_score=ConfidenceScore(0.8),
            correction_type="contraction",
            model_name="test-model",
        )

        # Act & Assert
        assert not expansion_suggestion.is_contraction()
        assert contraction_suggestion.is_contraction()

    def test_get_metadata_value(self):
        """Test getting metadata values."""
        # Arrange
        metadata = {"severity": "high", "category": "grammar"}
        suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.8),
            correction_type="grammar",
            model_name="test-model",
            metadata=metadata,
        )

        # Act & Assert
        assert suggestion.get_metadata_value("severity") == "high"
        assert suggestion.get_metadata_value("category") == "grammar"
        assert suggestion.get_metadata_value("missing") is None
        assert suggestion.get_metadata_value("missing", "default") == "default"

    def test_has_metadata_key(self):
        """Test checking for metadata keys."""
        # Arrange
        metadata = {"severity": "high", "category": "grammar"}
        suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.8),
            correction_type="grammar",
            model_name="test-model",
            metadata=metadata,
        )

        # Act & Assert
        assert suggestion.has_metadata_key("severity")
        assert suggestion.has_metadata_key("category")
        assert not suggestion.has_metadata_key("missing")


class TestCorrectionSuggestionComparison:
    """Test correction suggestion comparison and ranking."""

    def test_suggestions_are_comparable_by_confidence(self):
        """Test that suggestions can be compared by confidence score."""
        # Arrange
        high_confidence = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.95),
            correction_type="grammar",
            model_name="test-model",
        )

        low_confidence = CorrectionSuggestion(
            id=uuid4(),
            original_text="original",
            corrected_text="corrected",
            confidence_score=ConfidenceScore(0.7),
            correction_type="grammar",
            model_name="test-model",
        )

        # Act & Assert
        assert high_confidence > low_confidence
        assert low_confidence < high_confidence
        assert high_confidence >= low_confidence
        assert low_confidence <= high_confidence

    def test_sort_suggestions_by_confidence(self):
        """Test sorting suggestions by confidence score."""
        # Arrange
        suggestions = [
            CorrectionSuggestion(
                id=uuid4(),
                original_text="original",
                corrected_text="corrected",
                confidence_score=ConfidenceScore(0.7),
                correction_type="grammar",
                model_name="test-model",
            ),
            CorrectionSuggestion(
                id=uuid4(),
                original_text="original",
                corrected_text="corrected",
                confidence_score=ConfidenceScore(0.95),
                correction_type="grammar",
                model_name="test-model",
            ),
            CorrectionSuggestion(
                id=uuid4(),
                original_text="original",
                corrected_text="corrected",
                confidence_score=ConfidenceScore(0.8),
                correction_type="grammar",
                model_name="test-model",
            ),
        ]

        # Act
        sorted_suggestions = sorted(suggestions, reverse=True)

        # Assert
        confidence_scores = [s.confidence_score.value for s in sorted_suggestions]
        assert confidence_scores == [0.95, 0.8, 0.7]


class TestCorrectionSuggestionBusinessRules:
    """Test business rules and edge cases."""

    def test_suggestion_with_complex_metadata(self):
        """Test suggestion with complex metadata structure."""
        # Arrange
        complex_metadata = {
            "error_position": {"start": 5, "end": 10},
            "alternatives": ["option1", "option2"],
            "confidence_breakdown": {"grammar": 0.9, "context": 0.8, "style": 0.7},
        }

        # Act
        suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="original text",
            corrected_text="corrected text",
            confidence_score=ConfidenceScore(0.85),
            correction_type="grammar",
            model_name="test-model",
            metadata=complex_metadata,
        )

        # Assert
        assert suggestion.metadata == complex_metadata
        assert suggestion.get_metadata_value("error_position")["start"] == 5
        assert len(suggestion.get_metadata_value("alternatives")) == 2

    def test_suggestion_summary(self):
        """Test getting suggestion summary."""
        # Arrange
        suggestion = CorrectionSuggestion(
            id=uuid4(),
            original_text="I are going",
            corrected_text="I am going",
            confidence_score=ConfidenceScore(0.95),
            correction_type="grammar",
            model_name="grammar-model-v1",
        )

        # Act
        summary = suggestion.get_summary()

        # Assert
        assert "id" in summary
        assert summary["original_text"] == "I are going"
        assert summary["corrected_text"] == "I am going"
        assert summary["confidence_score"] == 0.95
        assert summary["confidence_level"] == "high"
        assert summary["correction_type"] == "grammar"
        assert summary["model_name"] == "grammar-model-v1"
        assert "created_at" in summary
