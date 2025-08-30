"""
Unit tests for ConfidenceScore value object.

Following TDD principles for confidence scoring in real-time correction processing.
Tests focus on confidence validation, comparison, and business rules.
"""

import pytest

from src.correction_engine_service.domain.value_objects.confidence_score import (
    ConfidenceScore,
)


class TestConfidenceScoreCreation:
    """Test confidence score value object creation and validation."""

    def test_create_valid_confidence_score(self):
        """Test creating valid confidence scores."""
        # Arrange & Act
        low_confidence = ConfidenceScore(0.3)
        medium_confidence = ConfidenceScore(0.7)
        high_confidence = ConfidenceScore(0.95)

        # Assert
        assert low_confidence.value == 0.3
        assert medium_confidence.value == 0.7
        assert high_confidence.value == 0.95

    def test_create_boundary_confidence_scores(self):
        """Test creating confidence scores at boundaries."""
        # Arrange & Act
        min_confidence = ConfidenceScore(0.0)
        max_confidence = ConfidenceScore(1.0)

        # Assert
        assert min_confidence.value == 0.0
        assert max_confidence.value == 1.0

    def test_create_confidence_score_below_minimum_raises_error(self):
        """Test that confidence score below 0.0 raises error."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="Confidence score must be between 0.0 and 1.0"
        ):
            ConfidenceScore(-0.1)

        with pytest.raises(
            ValueError, match="Confidence score must be between 0.0 and 1.0"
        ):
            ConfidenceScore(-1.0)

    def test_create_confidence_score_above_maximum_raises_error(self):
        """Test that confidence score above 1.0 raises error."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="Confidence score must be between 0.0 and 1.0"
        ):
            ConfidenceScore(1.1)

        with pytest.raises(
            ValueError, match="Confidence score must be between 0.0 and 1.0"
        ):
            ConfidenceScore(2.0)

    def test_confidence_score_precision(self):
        """Test confidence score precision handling."""
        # Arrange & Act
        precise_score = ConfidenceScore(0.123456789)

        # Assert
        assert abs(precise_score.value - 0.123456789) < 1e-9

    def test_confidence_score_from_percentage(self):
        """Test creating confidence score from percentage."""
        # Act
        score_from_percentage = ConfidenceScore.from_percentage(85.5)

        # Assert
        assert abs(score_from_percentage.value - 0.855) < 1e-9

    def test_confidence_score_from_invalid_percentage_raises_error(self):
        """Test that invalid percentage raises error."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="Percentage must be between 0.0 and 100.0"
        ):
            ConfidenceScore.from_percentage(-5.0)

        with pytest.raises(
            ValueError, match="Percentage must be between 0.0 and 100.0"
        ):
            ConfidenceScore.from_percentage(105.0)


class TestConfidenceScoreComparison:
    """Test confidence score comparison operations."""

    def test_confidence_scores_are_comparable(self):
        """Test that confidence scores can be compared."""
        # Arrange
        low = ConfidenceScore(0.3)
        medium = ConfidenceScore(0.7)
        high = ConfidenceScore(0.9)

        # Act & Assert
        assert low < medium < high
        assert high > medium > low
        assert low <= medium <= high
        assert high >= medium >= low

    def test_confidence_scores_equality(self):
        """Test confidence score equality."""
        # Arrange
        score1 = ConfidenceScore(0.75)
        score2 = ConfidenceScore(0.75)
        score3 = ConfidenceScore(0.76)

        # Act & Assert
        assert score1 == score2
        assert score1 != score3
        assert hash(score1) == hash(score2)
        assert hash(score1) != hash(score3)

    def test_confidence_score_sorting(self):
        """Test sorting confidence scores."""
        # Arrange
        scores = [
            ConfidenceScore(0.8),
            ConfidenceScore(0.3),
            ConfidenceScore(0.95),
            ConfidenceScore(0.6),
        ]

        # Act
        sorted_scores = sorted(scores)

        # Assert
        expected_values = [0.3, 0.6, 0.8, 0.95]
        actual_values = [score.value for score in sorted_scores]
        assert actual_values == expected_values


class TestConfidenceScoreClassification:
    """Test confidence score classification methods."""

    def test_is_high_confidence(self):
        """Test high confidence classification."""
        # Arrange
        high_scores = [
            ConfidenceScore(0.9),
            ConfidenceScore(0.95),
            ConfidenceScore(1.0),
        ]
        medium_scores = [
            ConfidenceScore(0.7),
            ConfidenceScore(0.8),
            ConfidenceScore(0.85),
        ]
        low_scores = [ConfidenceScore(0.3), ConfidenceScore(0.5), ConfidenceScore(0.65)]

        # Act & Assert
        for score in high_scores:
            assert score.is_high_confidence()

        for score in medium_scores:
            assert not score.is_high_confidence()

        for score in low_scores:
            assert not score.is_high_confidence()

    def test_is_medium_confidence(self):
        """Test medium confidence classification."""
        # Arrange
        high_scores = [ConfidenceScore(0.9), ConfidenceScore(0.95)]
        medium_scores = [
            ConfidenceScore(0.6),
            ConfidenceScore(0.7),
            ConfidenceScore(0.85),
        ]
        low_scores = [ConfidenceScore(0.3), ConfidenceScore(0.55)]

        # Act & Assert
        for score in medium_scores:
            assert score.is_medium_confidence()

        for score in high_scores:
            assert not score.is_medium_confidence()

        for score in low_scores:
            assert not score.is_medium_confidence()

    def test_is_low_confidence(self):
        """Test low confidence classification."""
        # Arrange
        high_scores = [ConfidenceScore(0.9), ConfidenceScore(0.95)]
        medium_scores = [ConfidenceScore(0.7), ConfidenceScore(0.8)]
        low_scores = [ConfidenceScore(0.0), ConfidenceScore(0.3), ConfidenceScore(0.55)]

        # Act & Assert
        for score in low_scores:
            assert score.is_low_confidence()

        for score in medium_scores:
            assert not score.is_low_confidence()

        for score in high_scores:
            assert not score.is_low_confidence()

    def test_get_confidence_level(self):
        """Test getting confidence level as string."""
        # Arrange & Act & Assert
        assert ConfidenceScore(0.95).get_confidence_level() == "high"
        assert ConfidenceScore(0.9).get_confidence_level() == "high"
        assert ConfidenceScore(0.85).get_confidence_level() == "medium"
        assert ConfidenceScore(0.7).get_confidence_level() == "medium"
        assert ConfidenceScore(0.6).get_confidence_level() == "medium"
        assert ConfidenceScore(0.55).get_confidence_level() == "low"
        assert ConfidenceScore(0.3).get_confidence_level() == "low"
        assert ConfidenceScore(0.0).get_confidence_level() == "low"


class TestConfidenceScoreBusinessRules:
    """Test business rules and utility methods."""

    def test_meets_threshold(self):
        """Test threshold checking."""
        # Arrange
        score = ConfidenceScore(0.75)

        # Act & Assert
        assert score.meets_threshold(0.7)
        assert score.meets_threshold(0.75)
        assert not score.meets_threshold(0.8)
        assert not score.meets_threshold(0.9)

    def test_to_percentage(self):
        """Test converting to percentage."""
        # Arrange
        score = ConfidenceScore(0.755)

        # Act
        percentage = score.to_percentage()

        # Assert
        assert abs(percentage - 75.5) < 1e-9

    def test_to_percentage_rounded(self):
        """Test converting to rounded percentage."""
        # Arrange
        score = ConfidenceScore(0.7567)

        # Act
        percentage_1dp = score.to_percentage(decimal_places=1)
        percentage_0dp = score.to_percentage(decimal_places=0)

        # Assert
        assert percentage_1dp == 75.7
        assert percentage_0dp == 76.0

    def test_combine_scores_average(self):
        """Test combining multiple confidence scores."""
        # Arrange
        scores = [ConfidenceScore(0.8), ConfidenceScore(0.9), ConfidenceScore(0.7)]

        # Act
        combined = ConfidenceScore.combine_average(scores)

        # Assert
        expected_average = (0.8 + 0.9 + 0.7) / 3
        assert abs(combined.value - expected_average) < 1e-9

    def test_combine_scores_weighted(self):
        """Test combining confidence scores with weights."""
        # Arrange
        scores = [ConfidenceScore(0.8), ConfidenceScore(0.9), ConfidenceScore(0.6)]
        weights = [0.5, 0.3, 0.2]

        # Act
        combined = ConfidenceScore.combine_weighted(scores, weights)

        # Assert
        expected_weighted = 0.8 * 0.5 + 0.9 * 0.3 + 0.6 * 0.2
        assert abs(combined.value - expected_weighted) < 1e-9

    def test_combine_empty_scores_raises_error(self):
        """Test that combining empty scores raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot combine empty list of scores"):
            ConfidenceScore.combine_average([])

    def test_combine_mismatched_weights_raises_error(self):
        """Test that mismatched weights raise error."""
        # Arrange
        scores = [ConfidenceScore(0.8), ConfidenceScore(0.9)]
        weights = [0.5, 0.3, 0.2]  # Wrong number of weights

        # Act & Assert
        with pytest.raises(
            ValueError, match="Number of weights must match number of scores"
        ):
            ConfidenceScore.combine_weighted(scores, weights)

    def test_confidence_score_immutability(self):
        """Test that confidence score is immutable."""
        # Arrange
        score = ConfidenceScore(0.8)

        # Act & Assert - should not be able to modify value
        with pytest.raises(AttributeError):
            score.value = 0.9

    def test_string_representation(self):
        """Test string representation of confidence score."""
        # Arrange
        score = ConfidenceScore(0.856)

        # Act & Assert
        assert str(score) == "0.856"
        assert repr(score) == "ConfidenceScore(0.856)"
