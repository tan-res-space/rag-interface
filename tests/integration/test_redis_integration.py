"""
Integration tests for Redis cache operations.

These tests verify the integration between the application and Redis cache,
including caching strategies, TTL handling, and performance optimization.
Following TDD principles and Hexagonal Architecture patterns.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import fakeredis.aioredis
import pytest

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    ErrorStatus,
    SeverityLevel,
)
from src.error_reporting_service.infrastructure.adapters.cache.redis_adapter import (
    RedisErrorCacheAdapter,
)
from tests.factories import ErrorReportFactory


@pytest.mark.integration
@pytest.mark.redis
class TestRedisIntegration:
    """Integration tests for Redis cache operations"""

    @pytest.fixture
    async def redis_client(self):
        """Create fake Redis client for testing"""
        # Use fakeredis for integration tests to avoid external dependencies
        client = fakeredis.aioredis.FakeRedis()
        yield client
        await client.flushall()
        await client.close()

    @pytest.fixture
    def cache_adapter(self, redis_client):
        """Create Redis cache adapter with fake client"""
        return RedisErrorCacheAdapter(
            redis_client=redis_client, default_ttl=3600, key_prefix="test_ers"  # 1 hour
        )

    @pytest.mark.asyncio
    async def test_cache_error_report_success(self, cache_adapter):
        """Test successful caching of error report"""
        # Arrange
        error_report = ErrorReportFactory.create()
        cache_key = f"error_report:{error_report.error_id}"

        # Act
        await cache_adapter.set_error_report(cache_key, error_report)

        # Assert
        cached_data = await cache_adapter.get_error_report(cache_key)
        assert cached_data is not None
        assert cached_data.error_id == error_report.error_id
        assert cached_data.original_text == error_report.original_text
        assert cached_data.corrected_text == error_report.corrected_text

    @pytest.mark.asyncio
    async def test_cache_error_report_with_ttl(self, cache_adapter, redis_client):
        """Test caching error report with custom TTL"""
        # Arrange
        error_report = ErrorReportFactory.create()
        cache_key = f"error_report:{error_report.error_id}"
        custom_ttl = 300  # 5 minutes

        # Act
        await cache_adapter.set_error_report(cache_key, error_report, ttl=custom_ttl)

        # Assert
        # Verify data is cached
        cached_data = await cache_adapter.get_error_report(cache_key)
        assert cached_data is not None

        # Verify TTL is set correctly
        ttl = await redis_client.ttl(f"test_ers:{cache_key}")
        assert 290 <= ttl <= 300  # Allow for small timing differences

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self, cache_adapter):
        """Test cache miss returns None"""
        # Arrange
        nonexistent_key = f"error_report:{uuid4()}"

        # Act
        cached_data = await cache_adapter.get_error_report(nonexistent_key)

        # Assert
        assert cached_data is None

    @pytest.mark.asyncio
    async def test_cache_search_results(self, cache_adapter):
        """Test caching of search results"""
        # Arrange
        error_reports = ErrorReportFactory.create_batch(5)
        search_key = "search:job_123:severity_high"
        search_results = {
            "items": [
                {
                    "error_id": str(report.error_id),
                    "original_text": report.original_text,
                    "severity_level": report.severity_level.value,
                }
                for report in error_reports
            ],
            "total": 5,
            "page": 1,
            "size": 10,
        }

        # Act
        await cache_adapter.set_search_results(search_key, search_results)

        # Assert
        cached_results = await cache_adapter.get_search_results(search_key)
        assert cached_results is not None
        assert cached_results["total"] == 5
        assert len(cached_results["items"]) == 5
        assert cached_results["page"] == 1

    @pytest.mark.asyncio
    async def test_cache_invalidation_by_pattern(self, cache_adapter):
        """Test cache invalidation using key patterns"""
        # Arrange
        job_id = str(uuid4())
        error_reports = [ErrorReportFactory.create(job_id=uuid4()) for _ in range(3)]

        # Cache multiple search results for the same job
        for i, report in enumerate(error_reports):
            search_key = f"search:job_{job_id}:page_{i}"
            await cache_adapter.set_search_results(search_key, {"data": f"page_{i}"})

        # Cache unrelated data
        unrelated_key = f"search:job_{uuid4()}:page_1"
        await cache_adapter.set_search_results(unrelated_key, {"data": "unrelated"})

        # Act
        invalidated_count = await cache_adapter.invalidate_by_pattern(
            f"search:job_{job_id}:*"
        )

        # Assert
        assert invalidated_count == 3

        # Verify job-specific caches are invalidated
        for i in range(3):
            search_key = f"search:job_{job_id}:page_{i}"
            cached_data = await cache_adapter.get_search_results(search_key)
            assert cached_data is None

        # Verify unrelated cache is preserved
        unrelated_data = await cache_adapter.get_search_results(unrelated_key)
        assert unrelated_data is not None

    @pytest.mark.asyncio
    async def test_cache_error_report_with_complex_metadata(self, cache_adapter):
        """Test caching error report with complex metadata"""
        # Arrange
        complex_metadata = {
            "audio_quality": "excellent",
            "nested_data": {
                "recording_device": "microphone_a",
                "room_acoustics": "poor",
            },
            "technical_issues": ["static", "echo"],
            "timestamps": {
                "recording_start": "2023-01-01T10:00:00Z",
                "error_detected": "2023-01-01T10:05:30Z",
            },
        }

        error_report = ErrorReportFactory.create(metadata=complex_metadata)
        cache_key = f"error_report:{error_report.error_id}"

        # Act
        await cache_adapter.set_error_report(cache_key, error_report)

        # Assert
        cached_data = await cache_adapter.get_error_report(cache_key)
        assert cached_data.metadata["nested_data"]["recording_device"] == "microphone_a"
        assert len(cached_data.metadata["technical_issues"]) == 2
        assert "recording_start" in cached_data.metadata["timestamps"]

    @pytest.mark.asyncio
    async def test_cache_performance_with_large_data(self, cache_adapter):
        """Test cache performance with large data sets"""
        # Arrange
        large_text = "x" * 10000  # Large text content
        error_report = ErrorReportFactory.create(
            original_text=large_text, corrected_text=large_text.replace("x", "X", 1)
        )
        cache_key = f"error_report:{error_report.error_id}"

        # Act
        start_time = datetime.utcnow()
        await cache_adapter.set_error_report(cache_key, error_report)
        set_time = (datetime.utcnow() - start_time).total_seconds()

        start_time = datetime.utcnow()
        cached_data = await cache_adapter.get_error_report(cache_key)
        get_time = (datetime.utcnow() - start_time).total_seconds()

        # Assert
        assert cached_data is not None
        assert len(cached_data.original_text) == 10000
        assert set_time < 1.0  # Should cache within 1 second
        assert get_time < 0.5  # Should retrieve within 0.5 seconds

    @pytest.mark.asyncio
    async def test_cache_concurrent_access(self, cache_adapter):
        """Test cache behavior under concurrent access"""
        # Arrange
        error_report = ErrorReportFactory.create()
        cache_key = f"error_report:{error_report.error_id}"

        # Act - Concurrent cache operations
        async def cache_operation():
            await cache_adapter.set_error_report(cache_key, error_report)
            return await cache_adapter.get_error_report(cache_key)

        results = await asyncio.gather(
            cache_operation(),
            cache_operation(),
            cache_operation(),
            return_exceptions=True,
        )

        # Assert
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 3

        # All results should be consistent
        for result in successful_results:
            assert result.error_id == error_report.error_id

    @pytest.mark.asyncio
    async def test_cache_memory_usage_optimization(self, cache_adapter, redis_client):
        """Test cache memory usage optimization"""
        # Arrange
        error_reports = ErrorReportFactory.create_batch(100)

        # Act - Cache many error reports
        for report in error_reports:
            cache_key = f"error_report:{report.error_id}"
            await cache_adapter.set_error_report(cache_key, report)

        # Assert
        # Check memory usage (approximate)
        info = await redis_client.info("memory")
        used_memory = info.get("used_memory", 0)

        # Memory usage should be reasonable (less than 10MB for 100 reports)
        assert used_memory < 10 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_cache_expiration_handling(self, cache_adapter, redis_client):
        """Test cache expiration handling"""
        # Arrange
        error_report = ErrorReportFactory.create()
        cache_key = f"error_report:{error_report.error_id}"
        short_ttl = 1  # 1 second

        # Act
        await cache_adapter.set_error_report(cache_key, error_report, ttl=short_ttl)

        # Verify data is initially cached
        cached_data = await cache_adapter.get_error_report(cache_key)
        assert cached_data is not None

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Assert
        expired_data = await cache_adapter.get_error_report(cache_key)
        assert expired_data is None

    @pytest.mark.asyncio
    async def test_cache_serialization_error_handling(self, cache_adapter):
        """Test cache handling of serialization errors"""

        # Arrange
        # Create an object that can't be serialized
        class UnserializableObject:
            def __init__(self):
                self.func = lambda x: x  # Functions can't be JSON serialized

        error_report = ErrorReportFactory.create()
        error_report.metadata["unserializable"] = UnserializableObject()
        cache_key = f"error_report:{error_report.error_id}"

        # Act & Assert
        with pytest.raises(TypeError):
            await cache_adapter.set_error_report(cache_key, error_report)

    @pytest.mark.asyncio
    async def test_cache_connection_error_handling(self, cache_adapter):
        """Test cache behavior when Redis connection fails"""
        # Arrange
        error_report = ErrorReportFactory.create()
        cache_key = f"error_report:{error_report.error_id}"

        # Mock Redis client to raise connection error
        with patch.object(
            cache_adapter.redis_client,
            "set",
            side_effect=ConnectionError("Redis unavailable"),
        ):
            # Act & Assert
            with pytest.raises(ConnectionError):
                await cache_adapter.set_error_report(cache_key, error_report)

    @pytest.mark.asyncio
    async def test_cache_health_check(self, cache_adapter):
        """Test cache health check functionality"""
        # Act
        is_healthy = await cache_adapter.health_check()

        # Assert
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_cache_health_check_failure(self, cache_adapter):
        """Test cache health check failure"""
        # Arrange
        # Mock Redis client to raise error on ping
        with patch.object(
            cache_adapter.redis_client,
            "ping",
            side_effect=ConnectionError("Redis down"),
        ):
            # Act
            is_healthy = await cache_adapter.health_check()

            # Assert
            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_cache_statistics_collection(self, cache_adapter):
        """Test cache statistics collection"""
        # Arrange
        error_reports = ErrorReportFactory.create_batch(5)

        # Act - Perform various cache operations
        for report in error_reports:
            cache_key = f"error_report:{report.error_id}"
            await cache_adapter.set_error_report(cache_key, report)

        # Perform some cache hits
        for i in range(3):
            cache_key = f"error_report:{error_reports[i].error_id}"
            await cache_adapter.get_error_report(cache_key)

        # Perform some cache misses
        for i in range(2):
            cache_key = f"error_report:{uuid4()}"
            await cache_adapter.get_error_report(cache_key)

        # Assert
        stats = await cache_adapter.get_statistics()
        assert stats["cache_hits"] == 3
        assert stats["cache_misses"] == 2
        assert stats["cache_sets"] == 5
        assert stats["hit_rate"] == 0.6  # 3 hits out of 5 total gets

    @pytest.mark.asyncio
    async def test_cache_batch_operations(self, cache_adapter):
        """Test batch cache operations for performance"""
        # Arrange
        error_reports = ErrorReportFactory.create_batch(10)
        cache_keys = [f"error_report:{report.error_id}" for report in error_reports]

        # Act
        start_time = datetime.utcnow()
        await cache_adapter.set_batch(
            [(key, report) for key, report in zip(cache_keys, error_reports)]
        )
        batch_set_time = (datetime.utcnow() - start_time).total_seconds()

        start_time = datetime.utcnow()
        cached_reports = await cache_adapter.get_batch(cache_keys)
        batch_get_time = (datetime.utcnow() - start_time).total_seconds()

        # Assert
        assert len(cached_reports) == 10
        assert all(report is not None for report in cached_reports)
        assert batch_set_time < 2.0  # Batch operations should be fast
        assert batch_get_time < 1.0

    @pytest.mark.asyncio
    async def test_cache_compression_for_large_objects(self, cache_adapter):
        """Test cache compression for large objects"""
        # Arrange
        large_metadata = {
            "large_field": "x" * 50000,  # 50KB of data
            "nested_large": {"data": ["item_" + str(i) for i in range(1000)]},
        }

        error_report = ErrorReportFactory.create(metadata=large_metadata)
        cache_key = f"error_report:{error_report.error_id}"

        # Act
        await cache_adapter.set_error_report(cache_key, error_report, compress=True)

        # Assert
        cached_data = await cache_adapter.get_error_report(cache_key)
        assert cached_data is not None
        assert len(cached_data.metadata["large_field"]) == 50000
        assert len(cached_data.metadata["nested_large"]["data"]) == 1000
