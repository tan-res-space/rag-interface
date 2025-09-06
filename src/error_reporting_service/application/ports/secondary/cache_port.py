"""
Cache Port Interface

Secondary port for caching operations in the Error Reporting Service.
Defines the contract for cache adapters following Hexagonal Architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from error_reporting_service.domain.entities.error_report import ErrorReport


class CachePort(ABC):
    """
    Abstract interface for cache operations.

    This port defines the contract that cache adapters must implement
    to provide caching functionality for the Error Reporting Service.
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

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: The cache key to delete

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.

        Args:
            key: The cache key to check

        Returns:
            True if key exists, False otherwise
        """

    @abstractmethod
    async def get_error_report(self, key: str) -> Optional[ErrorReport]:
        """
        Retrieve an error report from cache.

        Args:
            key: The cache key

        Returns:
            ErrorReport if found, None otherwise
        """

    @abstractmethod
    async def set_error_report(
        self, key: str, error_report: ErrorReport, ttl: Optional[int] = None
    ) -> bool:
        """
        Store an error report in cache.

        Args:
            key: The cache key
            error_report: The error report to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def get_search_results(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve search results from cache.

        Args:
            key: The cache key

        Returns:
            Search results if found, None otherwise
        """

    @abstractmethod
    async def set_search_results(
        self, key: str, results: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """
        Store search results in cache.

        Args:
            key: The cache key
            results: The search results to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: The pattern to match (e.g., "search:job_123:*")

        Returns:
            Number of keys invalidated
        """

    @abstractmethod
    async def get_batch(self, keys: List[str]) -> List[Optional[Any]]:
        """
        Retrieve multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            List of values (None for missing keys)
        """

    @abstractmethod
    async def set_batch(
        self, items: List[Tuple[str, Any]], ttl: Optional[int] = None
    ) -> bool:
        """
        Store multiple values in cache.

        Args:
            items: List of (key, value) tuples
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the cache is healthy and responsive.

        Returns:
            True if cache is healthy, False otherwise
        """

    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics and metrics.

        Returns:
            Dictionary containing cache statistics
        """

    @abstractmethod
    async def clear_all(self) -> bool:
        """
        Clear all cache entries (use with caution).

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get the time to live for a cache key.

        Args:
            key: The cache key

        Returns:
            TTL in seconds if key exists, None otherwise
        """

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
