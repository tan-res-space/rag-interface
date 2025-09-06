"""
Unit tests for SimilarityResult domain entity.

Tests focus on similarity scoring, ranking, and threshold validation.
"""

from uuid import uuid4

import pytest

from src.rag_integration_service.domain.entities.similarity_result import (
    SimilarityResult,
)


class TestSimilarityResultCreation:
    """Test similarity result entity creation and validation."""

    def test_create_valid_similarity_result(self):
        """Test creating a valid similarity result."""
        # Arrange
        embedding_id = uuid4()
        similarity_score = 0.85
        text = "This is a test sentence"
        metadata = {"speaker_id": "speaker1", "job_id": "job1"}
        distance_metric = "cosine"

        # Act
        result = SimilarityResult(
            embedding_id=embedding_id,
            similarity_score=similarity_score,
            text=text,
            metadata=metadata,
            distance_metric=distance_metric,
        )

        # Assert
        assert result.embedding_id == embedding_id
        assert result.similarity_score == similarity_score
        assert result.text == text
        assert result.metadata == metadata
        assert result.distance_metric == distance_metric

    def test_similarity_result_with_default_distance_metric(self):
        """Test similarity result with default distance metric."""
        # Arrange & Act
        result = SimilarityResult(
            embedding_id=uuid4(), similarity_score=0.75, text="test text", metadata={}
        )

        # Assert
        assert result.distance_metric == "cosine"  # Default value

    def test_similarity_result_with_invalid_score_raises_error(self):
        """Test that invalid similarity score raises error."""
        # Test score > 1.0
        with pytest.raises(
            ValueError, match="similarity_score must be between 0.0 and 1.0"
        ):
            SimilarityResult(
                embedding_id=uuid4(),
                similarity_score=1.5,
                text="test text",
                metadata={},
            )

        # Test score < 0.0
        with pytest.raises(
            ValueError, match="similarity_score must be between 0.0 and 1.0"
        ):
            SimilarityResult(
                embedding_id=uuid4(),
                similarity_score=-0.1,
                text="test text",
                metadata={},
            )

    def test_similarity_result_with_empty_text_raises_error(self):
        """Test that empty text raises validation error."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            SimilarityResult(
                embedding_id=uuid4(), similarity_score=0.8, text="", metadata={}
            )

    def test_similarity_result_with_whitespace_text_raises_error(self):
        """Test that whitespace-only text raises validation error."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            SimilarityResult(
                embedding_id=uuid4(),
                similarity_score=0.8,
                text="   \n\t  ",
                metadata={},
            )


class TestSimilarityResultMethods:
    """Test similarity result methods and business logic."""

    def test_is_above_threshold_with_score_above(self):
        """Test threshold check with score above threshold."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(), similarity_score=0.85, text="test text", metadata={}
        )

        # Act & Assert
        assert result.is_above_threshold(0.7) is True
        assert result.is_above_threshold(0.8) is True
        assert result.is_above_threshold(0.85) is True

    def test_is_above_threshold_with_score_below(self):
        """Test threshold check with score below threshold."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(), similarity_score=0.65, text="test text", metadata={}
        )

        # Act & Assert
        assert result.is_above_threshold(0.7) is False
        assert result.is_above_threshold(0.8) is False
        assert result.is_above_threshold(0.9) is False

    def test_is_above_threshold_with_equal_score(self):
        """Test threshold check with score equal to threshold."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(), similarity_score=0.75, text="test text", metadata={}
        )

        # Act & Assert
        assert result.is_above_threshold(0.75) is True  # Equal should return True

    def test_get_confidence_level_high(self):
        """Test confidence level calculation for high similarity."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(), similarity_score=0.95, text="test text", metadata={}
        )

        # Act & Assert
        assert result.get_confidence_level() == "high"

    def test_get_confidence_level_medium(self):
        """Test confidence level calculation for medium similarity."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(), similarity_score=0.75, text="test text", metadata={}
        )

        # Act & Assert
        assert result.get_confidence_level() == "medium"

    def test_get_confidence_level_low(self):
        """Test confidence level calculation for low similarity."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(), similarity_score=0.45, text="test text", metadata={}
        )

        # Act & Assert
        assert result.get_confidence_level() == "low"

    def test_get_metadata_value_existing_key(self):
        """Test getting metadata value for existing key."""
        # Arrange
        metadata = {"speaker_id": "speaker123", "category": "grammar"}
        result = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.8,
            text="test text",
            metadata=metadata,
        )

        # Act & Assert
        assert result.get_metadata_value("speaker_id") == "speaker123"
        assert result.get_metadata_value("category") == "grammar"

    def test_get_metadata_value_missing_key(self):
        """Test getting metadata value for missing key."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.8,
            text="test text",
            metadata={"speaker_id": "speaker123"},
        )

        # Act & Assert
        assert result.get_metadata_value("missing_key") is None
        assert result.get_metadata_value("missing_key", "default") == "default"

    def test_has_metadata_key_existing(self):
        """Test checking for existing metadata key."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.8,
            text="test text",
            metadata={"speaker_id": "speaker123", "category": "grammar"},
        )

        # Act & Assert
        assert result.has_metadata_key("speaker_id") is True
        assert result.has_metadata_key("category") is True

    def test_has_metadata_key_missing(self):
        """Test checking for missing metadata key."""
        # Arrange
        result = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.8,
            text="test text",
            metadata={"speaker_id": "speaker123"},
        )

        # Act & Assert
        assert result.has_metadata_key("missing_key") is False
        assert result.has_metadata_key("category") is False


class TestSimilarityResultComparison:
    """Test similarity result comparison and ranking."""

    def test_similarity_results_are_comparable(self):
        """Test that similarity results can be compared by score."""
        # Arrange
        result1 = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.9,
            text="high similarity",
            metadata={},
        )
        result2 = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.7,
            text="medium similarity",
            metadata={},
        )
        result3 = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.9,
            text="equal similarity",
            metadata={},
        )

        # Act & Assert
        assert result1 > result2
        assert result2 < result1
        assert result1 == result3
        assert result1 >= result3
        assert result2 <= result1

    def test_sort_similarity_results_descending(self):
        """Test sorting similarity results in descending order."""
        # Arrange
        results = [
            SimilarityResult(uuid4(), 0.6, "low", {}),
            SimilarityResult(uuid4(), 0.9, "high", {}),
            SimilarityResult(uuid4(), 0.75, "medium", {}),
            SimilarityResult(uuid4(), 0.95, "highest", {}),
        ]

        # Act
        sorted_results = sorted(results, reverse=True)

        # Assert
        scores = [r.similarity_score for r in sorted_results]
        assert scores == [0.95, 0.9, 0.75, 0.6]
        assert sorted_results[0].text == "highest"
        assert sorted_results[-1].text == "low"


class TestSimilarityResultBusinessRules:
    """Test business rules and edge cases."""

    def test_similarity_result_with_complex_metadata(self):
        """Test similarity result with complex metadata structure."""
        # Arrange
        complex_metadata = {
            "speaker_id": "speaker123",
            "job_id": "job456",
            "error_categories": ["grammar", "pronunciation"],
            "quality_metrics": {"wer": 0.15, "ser": 0.08, "edit_distance": 3},
            "context": {"audio_duration": 45.2, "background_noise": "low"},
        }

        # Act & Assert
        result = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.85,
            text="complex metadata test",
            metadata=complex_metadata,
        )

        assert result.metadata == complex_metadata
        assert result.get_metadata_value("speaker_id") == "speaker123"
        assert result.get_metadata_value("quality_metrics")["wer"] == 0.15

    def test_similarity_result_with_perfect_score(self):
        """Test similarity result with perfect similarity score."""
        # Arrange & Act
        result = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=1.0,
            text="perfect match",
            metadata={},
        )

        # Assert
        assert result.similarity_score == 1.0
        assert result.get_confidence_level() == "high"
        assert result.is_above_threshold(0.99) is True

    def test_similarity_result_with_zero_score(self):
        """Test similarity result with zero similarity score."""
        # Arrange & Act
        result = SimilarityResult(
            embedding_id=uuid4(),
            similarity_score=0.0,
            text="no similarity",
            metadata={},
        )

        # Assert
        assert result.similarity_score == 0.0
        assert result.get_confidence_level() == "low"
        assert result.is_above_threshold(0.1) is False
