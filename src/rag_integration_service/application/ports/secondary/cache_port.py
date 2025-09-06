"""
Cache Secondary Port

Secondary port interface for caching operations.
This is a driven port that defines the contract for cache adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding


class CachePort(ABC):
    """
    Secondary port for cache operations.

    This port defines the contract that cache adapters must implement
    to provide caching functionality for the RAG Integration Service.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache by key.

        Args:
            key: The cache key

        Returns:
            The cached value if found, None otherwise
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in cache with optional TTL.

        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: The cache key to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.

        Args:
            key: The cache key to check

        Returns:
            True if key exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_embedding(self, text_hash: str) -> Optional[VectorEmbedding]:
        """
        Retrieve a vector embedding from cache by text hash.

        Args:
            text_hash: Hash of the text

        Returns:
            VectorEmbedding if found, None otherwise
        """
        pass

    @abstractmethod
    async def set_embedding(
        self, text_hash: str, embedding: VectorEmbedding, ttl: Optional[int] = None
    ) -> bool:
        """
        Store a vector embedding in cache.

        Args:
            text_hash: Hash of the text
            embedding: The vector embedding to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_search_results(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve search results from cache.

        Args:
            query_hash: Hash of the search query

        Returns:
            Search results if found, None otherwise
        """
        pass

    @abstractmethod
    async def set_search_results(
        self, query_hash: str, results: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """
        Store search results in cache.

        Args:
            query_hash: Hash of the search query
            results: The search results to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: The pattern to match (e.g., "embeddings:*")

        Returns:
            Number of keys invalidated
        """
        pass

    @abstractmethod
    async def get_batch(self, keys: List[str]) -> List[Optional[Any]]:
        """
        Retrieve multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            List of values (None for missing keys)
        """
        pass

    @abstractmethod
    async def set_batch(self, items: List[tuple], ttl: Optional[int] = None) -> bool:
        """
        Store multiple values in cache.

        Args:
            items: List of (key, value) tuples
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the cache is healthy and responsive.

        Returns:
            True if cache is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics and metrics.

        Returns:
            Dictionary containing cache statistics
        """
        pass

    @abstractmethod
    async def clear_all(self) -> bool:
        """
        Clear all cache entries (use with caution).

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get the time to live for a cache key.

        Args:
            key: The cache key

        Returns:
            TTL in seconds if key exists, None otherwise
        """
        pass

    @abstractmethod
    async def extend_ttl(self, key: str, ttl: int) -> bool:
        """
        Extend the time to live for a cache key.

        Args:
            key: The cache key
            ttl: New TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a numeric value in cache.

        Args:
            key: The cache key
            amount: Amount to increment by

        Returns:
            New value after increment
        """
        pass

    @abstractmethod
    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement a numeric value in cache.

        Args:
            key: The cache key
            amount: Amount to decrement by

        Returns:
            New value after decrement
        """
        pass
