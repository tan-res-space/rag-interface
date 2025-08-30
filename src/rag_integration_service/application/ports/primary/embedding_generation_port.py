"""
Embedding Generation Primary Port

Primary port interface for embedding generation operations.
This is a driving port that defines the contract for embedding generation use cases.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from ...dto.requests import (
    BatchEmbeddingRequest,
    EmbeddingRequest,
    SimilaritySearchRequest,
)
from ...dto.responses import (
    BatchEmbeddingResponse,
    EmbeddingResponse,
    SimilaritySearchResponse,
)


class EmbeddingGenerationPort(ABC):
    """
    Primary port for embedding generation operations.

    This port defines the contract that external systems (like REST controllers)
    use to interact with the embedding generation functionality.
    """

    @abstractmethod
    async def generate_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate a vector embedding for a single text.

        Args:
            request: Embedding generation request

        Returns:
            Response containing the generated embedding

        Raises:
            ValueError: If request is invalid
            EmbeddingGenerationError: If embedding generation fails
        """
        pass

    @abstractmethod
    async def generate_batch_embeddings(
        self, request: BatchEmbeddingRequest
    ) -> BatchEmbeddingResponse:
        """
        Generate vector embeddings for multiple texts in batch.

        Args:
            request: Batch embedding generation request

        Returns:
            Response containing the generated embeddings

        Raises:
            ValueError: If request is invalid
            EmbeddingGenerationError: If batch generation fails
        """
        pass

    @abstractmethod
    async def get_embedding(self, embedding_id: UUID) -> EmbeddingResponse:
        """
        Retrieve a specific embedding by ID.

        Args:
            embedding_id: Unique identifier of the embedding

        Returns:
            Response containing the embedding

        Raises:
            EmbeddingNotFoundError: If embedding doesn't exist
        """
        pass

    @abstractmethod
    async def search_similar_embeddings(
        self, request: SimilaritySearchRequest
    ) -> SimilaritySearchResponse:
        """
        Search for similar embeddings based on query.

        Args:
            request: Similarity search request

        Returns:
            Response containing similar embeddings

        Raises:
            ValueError: If request is invalid
            SimilaritySearchError: If search fails
        """
        pass

    @abstractmethod
    async def delete_embedding(self, embedding_id: UUID) -> bool:
        """
        Delete a specific embedding.

        Args:
            embedding_id: Unique identifier of the embedding

        Returns:
            True if deletion was successful

        Raises:
            EmbeddingNotFoundError: If embedding doesn't exist
        """
        pass

    @abstractmethod
    async def get_embedding_statistics(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about embeddings.

        Args:
            filters: Optional filters to apply

        Returns:
            Dictionary containing embedding statistics
        """
        pass
