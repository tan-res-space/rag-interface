"""
Unit tests for VectorEmbedding domain entity.

Following TDD principles for ML/Vector processing components.
Tests focus on contracts and mathematical properties rather than exact values.
"""

from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID, uuid4

import pytest

from src.rag_integration_service.domain.entities.vector_embedding import VectorEmbedding
from src.rag_integration_service.domain.value_objects.embedding_type import (
    EmbeddingType,
)


class TestVectorEmbeddingCreation:
    """Test vector embedding entity creation and validation."""

    def test_create_valid_vector_embedding(self):
        """Test creating a valid vector embedding."""
        # Arrange
        embedding_id = uuid4()
        vector = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        text = "This is a test sentence"
        text_hash = "abc123"
        embedding_type = EmbeddingType.ERROR
        model_version = "v1.0"
        model_name = "test-model"
        metadata = {"speaker_id": "speaker1", "job_id": "job1"}
        created_at = datetime.utcnow()

        # Act
        embedding = VectorEmbedding(
            id=embedding_id,
            vector=vector,
            text=text,
            text_hash=text_hash,
            embedding_type=embedding_type,
            model_version=model_version,
            model_name=model_name,
            metadata=metadata,
            created_at=created_at,
        )

        # Assert
        assert embedding.id == embedding_id
        assert embedding.vector == vector
        assert embedding.text == text
        assert embedding.text_hash == text_hash
        assert embedding.embedding_type == embedding_type
        assert embedding.model_version == model_version
        assert embedding.model_name == model_name
        assert embedding.metadata == metadata
        assert embedding.created_at == created_at

    def test_vector_embedding_with_empty_text_raises_error(self):
        """Test that empty text raises validation error."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            VectorEmbedding(
                id=uuid4(),
                vector=[0.1] * 1536,
                text="",
                text_hash="abc123",
                embedding_type=EmbeddingType.ERROR,
                model_version="v1.0",
                model_name="test-model",
                metadata={},
                created_at=datetime.utcnow(),
            )

    def test_vector_embedding_with_whitespace_text_raises_error(self):
        """Test that whitespace-only text raises validation error."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            VectorEmbedding(
                id=uuid4(),
                vector=[0.1] * 1536,
                text="   \n\t  ",
                text_hash="abc123",
                embedding_type=EmbeddingType.ERROR,
                model_version="v1.0",
                model_name="test-model",
                metadata={},
                created_at=datetime.utcnow(),
            )

    def test_vector_embedding_with_invalid_dimensions_raises_error(self):
        """Test that invalid vector dimensions raise validation error."""
        with pytest.raises(ValueError, match="vector must be 1536-dimensional"):
            VectorEmbedding(
                id=uuid4(),
                vector=[0.1] * 100,  # Wrong dimensions
                text="test text",
                text_hash="abc123",
                embedding_type=EmbeddingType.ERROR,
                model_version="v1.0",
                model_name="test-model",
                metadata={},
                created_at=datetime.utcnow(),
            )

    def test_vector_embedding_with_empty_vector_raises_error(self):
        """Test that empty vector raises validation error."""
        with pytest.raises(ValueError, match="vector cannot be empty"):
            VectorEmbedding(
                id=uuid4(),
                vector=[],
                text="test text",
                text_hash="abc123",
                embedding_type=EmbeddingType.ERROR,
                model_version="v1.0",
                model_name="test-model",
                metadata={},
                created_at=datetime.utcnow(),
            )


class TestVectorEmbeddingMethods:
    """Test vector embedding mathematical operations."""

    def test_validate_dimensions_with_correct_size(self):
        """Test dimension validation with correct vector size."""
        # Arrange
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=[0.1] * 1536,
            text="test text",
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        # Act & Assert
        assert embedding.validate_dimensions() is True
        assert embedding.validate_dimensions(1536) is True

    def test_validate_dimensions_with_incorrect_size(self):
        """Test dimension validation with incorrect expected size."""
        # Arrange
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=[0.1] * 1536,
            text="test text",
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        # Act & Assert
        assert embedding.validate_dimensions(512) is False

    def test_calculate_magnitude_with_unit_vector(self):
        """Test magnitude calculation with unit vector."""
        # Arrange - Create a unit vector in 3D for easy verification
        vector = [1.0, 0.0, 0.0] + [0.0] * 1533  # Unit vector in first dimension
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=vector,
            text="test text",
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        # Act
        magnitude = embedding.calculate_magnitude()

        # Assert
        assert abs(magnitude - 1.0) < 0.001  # Should be approximately 1.0

    def test_calculate_magnitude_with_known_vector(self):
        """Test magnitude calculation with known vector."""
        # Arrange - Create vector [3, 4, 0, 0, ...] which has magnitude 5
        vector = [3.0, 4.0] + [0.0] * 1534
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=vector,
            text="test text",
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        # Act
        magnitude = embedding.calculate_magnitude()

        # Assert
        assert abs(magnitude - 5.0) < 0.001  # Should be approximately 5.0

    def test_normalize_vector(self):
        """Test vector normalization."""
        # Arrange
        vector = [3.0, 4.0] + [0.0] * 1534  # Magnitude = 5
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=vector,
            text="test text",
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        # Act
        normalized = embedding.normalize()

        # Assert
        assert len(normalized) == 1536
        assert abs(normalized[0] - 0.6) < 0.001  # 3/5 = 0.6
        assert abs(normalized[1] - 0.8) < 0.001  # 4/5 = 0.8

        # Normalized vector should have magnitude 1
        magnitude = sum(x**2 for x in normalized) ** 0.5
        assert abs(magnitude - 1.0) < 0.001

    def test_normalize_zero_vector_returns_original(self):
        """Test that normalizing zero vector returns original vector."""
        # Arrange
        vector = [0.0] * 1536
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=vector,
            text="test text",
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        # Act
        normalized = embedding.normalize()

        # Assert
        assert normalized == vector  # Should return original zero vector


class TestVectorEmbeddingBusinessRules:
    """Test business rules and edge cases."""

    def test_embedding_with_maximum_text_length(self):
        """Test embedding with maximum allowed text length."""
        # Arrange
        long_text = "x" * 10000  # Maximum allowed length

        # Act & Assert - Should not raise an error
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=[0.1] * 1536,
            text=long_text,
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        assert len(embedding.text) == 10000

    def test_embedding_with_text_exceeding_maximum_length_raises_error(self):
        """Test that text exceeding maximum length raises error."""
        # Arrange
        too_long_text = "x" * 10001  # Exceeds maximum

        # Act & Assert
        with pytest.raises(ValueError, match="text cannot exceed 10000 characters"):
            VectorEmbedding(
                id=uuid4(),
                vector=[0.1] * 1536,
                text=too_long_text,
                text_hash="abc123",
                embedding_type=EmbeddingType.ERROR,
                model_version="v1.0",
                model_name="test-model",
                metadata={},
                created_at=datetime.utcnow(),
            )

    def test_embedding_with_unicode_text(self):
        """Test embedding with Unicode text."""
        # Arrange
        unicode_text = "Hello 世界 🌍 café naïve résumé"

        # Act & Assert - Should handle Unicode properly
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=[0.1] * 1536,
            text=unicode_text,
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        assert embedding.text == unicode_text

    def test_embedding_with_complex_metadata(self):
        """Test embedding with complex metadata structure."""
        # Arrange
        complex_metadata = {
            "speaker_id": "speaker123",
            "job_id": "job456",
            "error_categories": ["grammar", "pronunciation"],
            "quality_metrics": {"wer": 0.15, "ser": 0.08, "edit_distance": 3},
            "audio_info": {"duration": 45.2, "sample_rate": 16000, "quality": "high"},
        }

        # Act & Assert
        embedding = VectorEmbedding(
            id=uuid4(),
            vector=[0.1] * 1536,
            text="test text",
            text_hash="abc123",
            embedding_type=EmbeddingType.ERROR,
            model_version="v1.0",
            model_name="test-model",
            metadata=complex_metadata,
            created_at=datetime.utcnow(),
        )

        assert embedding.metadata == complex_metadata
        assert embedding.metadata["quality_metrics"]["wer"] == 0.15
