"""
Vector Storage Secondary Port

Secondary port interface for vector database operations.
This is a driven port that defines the contract for vector storage adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.rag_integration_service.domain.entities.similarity_result import (
    SimilarityResult,
)
from src.rag_integration_service.domain.entities.vector_embedding import VectorEmbedding


class VectorStoragePort(ABC):
    """
    Secondary port for vector database operations.

    This port defines the contract that vector database adapters must implement
    to provide vector storage and retrieval functionality.
    """

    @abstractmethod
    async def store_embedding(self, embedding: VectorEmbedding) -> bool:
        """
        Store a vector embedding in the database.

        Args:
            embedding: Vector embedding to store

        Returns:
            True if storage was successful

        Raises:
            VectorStorageError: If storage operation fails
        """
        pass

    @abstractmethod
    async def store_batch_embeddings(self, embeddings: List[VectorEmbedding]) -> bool:
        """
        Store multiple vector embeddings in batch.

        Args:
            embeddings: List of vector embeddings to store

        Returns:
            True if batch storage was successful

        Raises:
            VectorStorageError: If batch storage operation fails
        """
        pass

    @abstractmethod
    async def find_embedding(self, embedding_id: UUID) -> Optional[VectorEmbedding]:
        """
        Find a vector embedding by ID.

        Args:
            embedding_id: Unique identifier of the embedding

        Returns:
            Vector embedding if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_similar(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """
        Find similar vectors using similarity search.

        Args:
            query_vector: Query vector for similarity search
            top_k: Number of top results to return
            filters: Optional metadata filters
            threshold: Minimum similarity threshold

        Returns:
            List of similarity results sorted by score (descending)

        Raises:
            VectorSearchError: If search operation fails
        """
        pass

    @abstractmethod
    async def find_similar_by_text(
        self,
        query_text: str,
        embedding_type: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """
        Find similar vectors by generating embedding for query text.

        Args:
            query_text: Text to generate query embedding from
            embedding_type: Type of embedding to generate
            top_k: Number of top results to return
            filters: Optional metadata filters
            threshold: Minimum similarity threshold

        Returns:
            List of similarity results sorted by score (descending)

        Raises:
            VectorSearchError: If search operation fails
        """
        pass

    @abstractmethod
    async def find_by_speaker(
        self,
        speaker_id: str,
        query_vector: List[float],
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """
        Find similar vectors for a specific speaker.

        Args:
            speaker_id: Speaker identifier
            query_vector: Query vector for similarity search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold

        Returns:
            List of similarity results for the speaker
        """
        pass

    @abstractmethod
    async def find_by_job(
        self,
        job_id: str,
        query_vector: List[float],
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """
        Find similar vectors for a specific job.

        Args:
            job_id: Job identifier
            query_vector: Query vector for similarity search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold

        Returns:
            List of similarity results for the job
        """
        pass

    @abstractmethod
    async def find_by_category(
        self,
        category: str,
        query_vector: List[float],
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """
        Find similar vectors for a specific error category.

        Args:
            category: Error category
            query_vector: Query vector for similarity search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold

        Returns:
            List of similarity results for the category
        """
        pass

    @abstractmethod
    async def delete_embedding(self, embedding_id: UUID) -> bool:
        """
        Delete a vector embedding from the database.

        Args:
            embedding_id: Unique identifier of the embedding

        Returns:
            True if deletion was successful

        Raises:
            VectorStorageError: If deletion operation fails
        """
        pass

    @abstractmethod
    async def delete_embeddings_by_job(self, job_id: str) -> int:
        """
        Delete all embeddings for a specific job.

        Args:
            job_id: Job identifier

        Returns:
            Number of embeddings deleted
        """
        pass

    @abstractmethod
    async def get_embedding_count(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Get count of embeddings matching filters.

        Args:
            filters: Optional metadata filters

        Returns:
            Number of embeddings matching filters
        """
        pass

    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get vector database statistics.

        Returns:
            Dictionary containing database statistics
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the vector database is healthy and responsive.

        Returns:
            True if database is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def create_index(self, index_config: Dict[str, Any]) -> bool:
        """
        Create or update vector index configuration.

        Args:
            index_config: Index configuration parameters

        Returns:
            True if index creation was successful

        Raises:
            VectorStorageError: If index creation fails
        """
        pass
