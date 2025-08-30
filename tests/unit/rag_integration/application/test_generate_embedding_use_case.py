"""
Unit tests for Generate Embedding Use Case.

Following TDD principles for ML/Vector processing components.
Tests focus on use case orchestration with mocked dependencies.
"""

import asyncio
import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.rag_integration_service.application.dto.requests import EmbeddingRequest
from src.rag_integration_service.application.dto.responses import EmbeddingResponse
from src.rag_integration_service.application.ports.secondary.cache_port import CachePort
from src.rag_integration_service.application.ports.secondary.ml_model_port import (
    MLModelPort,
)
from src.rag_integration_service.application.ports.secondary.vector_storage_port import (
    VectorStoragePort,
)
from src.rag_integration_service.application.use_cases.generate_embedding import (
    GenerateEmbeddingUseCase,
)
from src.rag_integration_service.domain.entities.vector_embedding import VectorEmbedding
from src.rag_integration_service.domain.value_objects.embedding_type import (
    EmbeddingType,
)


class TestGenerateEmbeddingUseCase:
    """Test generate embedding use case orchestration."""

    @pytest.fixture
    def mock_ml_model(self):
        """Create mock ML model port."""
        mock = Mock(spec=MLModelPort)
        mock.generate_embedding = AsyncMock(return_value=[0.1] * 1536)
        mock.get_model_name.return_value = "test-model"
        mock.get_model_version.return_value = "v1.0"
        mock.get_embedding_dimension.return_value = 1536
        return mock

    @pytest.fixture
    def mock_vector_storage(self):
        """Create mock vector storage port."""
        mock = Mock(spec=VectorStoragePort)
        mock.store_embedding = AsyncMock(return_value=True)
        return mock

    @pytest.fixture
    def mock_cache(self):
        """Create mock cache port."""
        mock = Mock(spec=CachePort)
        mock.get_embedding = AsyncMock(return_value=None)  # Cache miss by default
        mock.set_embedding = AsyncMock(return_value=True)
        return mock

    @pytest.fixture
    def use_case(self, mock_ml_model, mock_vector_storage, mock_cache):
        """Create use case with mocked dependencies."""
        return GenerateEmbeddingUseCase(
            ml_model=mock_ml_model, vector_storage=mock_vector_storage, cache=mock_cache
        )

    @pytest.mark.asyncio
    async def test_generate_embedding_success(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test successful embedding generation."""
        # Arrange
        request = EmbeddingRequest(
            text="This is a test sentence",
            embedding_type=EmbeddingType.ERROR,
            metadata={"speaker_id": "speaker1"},
            requested_by="user1",
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert isinstance(response, EmbeddingResponse)
        assert response.status == "success"
        assert response.embedding.text == request.text
        assert response.embedding.embedding_type == request.embedding_type
        assert response.embedding.metadata == request.metadata
        assert len(response.embedding.vector) == 1536
        assert response.processing_time > 0

        # Verify interactions
        mock_ml_model.generate_embedding.assert_called_once_with(
            request.text, request.embedding_type
        )
        mock_vector_storage.store_embedding.assert_called_once()
        mock_cache.set_embedding.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embedding_with_cache_hit(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test embedding generation with cache hit."""
        # Arrange
        request = EmbeddingRequest(
            text="Cached text", embedding_type=EmbeddingType.ERROR
        )

        cached_embedding = VectorEmbedding(
            id=uuid4(),
            vector=[0.2] * 1536,
            text=request.text,
            text_hash="cached_hash",
            embedding_type=request.embedding_type,
            model_version="v1.0",
            model_name="test-model",
            metadata={},
            created_at=datetime.utcnow(),
        )

        mock_cache.get_embedding.return_value = cached_embedding

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.embedding == cached_embedding
        assert response.status == "success"

        # Verify ML model was not called due to cache hit
        mock_ml_model.generate_embedding.assert_not_called()
        mock_vector_storage.store_embedding.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_embedding_ml_model_failure(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test handling of ML model failure."""
        # Arrange
        request = EmbeddingRequest(text="Test text", embedding_type=EmbeddingType.ERROR)

        mock_ml_model.generate_embedding.side_effect = Exception("ML model error")

        # Act & Assert
        with pytest.raises(Exception, match="ML model error"):
            await use_case.execute(request)

        # Verify storage was not called due to ML failure
        mock_vector_storage.store_embedding.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_embedding_storage_failure(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test handling of vector storage failure."""
        # Arrange
        request = EmbeddingRequest(text="Test text", embedding_type=EmbeddingType.ERROR)

        mock_vector_storage.store_embedding.side_effect = Exception("Storage error")

        # Act & Assert
        with pytest.raises(Exception, match="Storage error"):
            await use_case.execute(request)

        # Verify ML model was called but storage failed
        mock_ml_model.generate_embedding.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embedding_with_different_types(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test embedding generation with different embedding types."""
        # Test ERROR type
        request_error = EmbeddingRequest(
            text="Error text", embedding_type=EmbeddingType.ERROR
        )

        response_error = await use_case.execute(request_error)
        assert response_error.embedding.embedding_type == EmbeddingType.ERROR

        # Test CORRECTION type
        request_correction = EmbeddingRequest(
            text="Correction text", embedding_type=EmbeddingType.CORRECTION
        )

        response_correction = await use_case.execute(request_correction)
        assert response_correction.embedding.embedding_type == EmbeddingType.CORRECTION

        # Test CONTEXT type
        request_context = EmbeddingRequest(
            text="Context text", embedding_type=EmbeddingType.CONTEXT
        )

        response_context = await use_case.execute(request_context)
        assert response_context.embedding.embedding_type == EmbeddingType.CONTEXT

    @pytest.mark.asyncio
    async def test_generate_embedding_with_custom_model_version(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test embedding generation with custom model version."""
        # Arrange
        request = EmbeddingRequest(
            text="Test text",
            embedding_type=EmbeddingType.ERROR,
            model_version="custom-v2.0",
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.embedding.model_version == "custom-v2.0"

    @pytest.mark.asyncio
    async def test_generate_embedding_with_complex_metadata(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test embedding generation with complex metadata."""
        # Arrange
        complex_metadata = {
            "speaker_id": "speaker123",
            "job_id": "job456",
            "error_categories": ["grammar", "pronunciation"],
            "quality_metrics": {"wer": 0.15, "ser": 0.08},
        }

        request = EmbeddingRequest(
            text="Complex metadata test",
            embedding_type=EmbeddingType.ERROR,
            metadata=complex_metadata,
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.embedding.metadata == complex_metadata

    @pytest.mark.asyncio
    async def test_generate_embedding_performance_tracking(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test that processing time is tracked correctly."""
        # Arrange
        request = EmbeddingRequest(
            text="Performance test", embedding_type=EmbeddingType.ERROR
        )

        # Simulate some processing time
        async def slow_generate_embedding(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return [0.1] * 1536

        mock_ml_model.generate_embedding = slow_generate_embedding

        # Act
        start_time = time.time()
        response = await use_case.execute(request)
        end_time = time.time()

        # Assert
        assert response.processing_time > 0
        assert response.processing_time <= (end_time - start_time)

    @pytest.mark.asyncio
    async def test_generate_embedding_text_hash_generation(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test that text hash is generated correctly."""
        # Arrange
        request = EmbeddingRequest(
            text="Hash test text", embedding_type=EmbeddingType.ERROR
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.embedding.text_hash is not None
        assert len(response.embedding.text_hash) > 0

        # Same text should produce same hash
        response2 = await use_case.execute(request)
        assert response.embedding.text_hash == response2.embedding.text_hash

    @pytest.mark.asyncio
    async def test_generate_embedding_model_info_in_response(
        self, use_case, mock_ml_model, mock_vector_storage, mock_cache
    ):
        """Test that model information is included in response."""
        # Arrange
        request = EmbeddingRequest(
            text="Model info test", embedding_type=EmbeddingType.ERROR
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert "name" in response.model_info
        assert "version" in response.model_info
        assert "dimensions" in response.model_info
        assert response.model_info["name"] == "test-model"
        assert response.model_info["version"] == "v1.0"
        assert response.model_info["dimensions"] == 1536
