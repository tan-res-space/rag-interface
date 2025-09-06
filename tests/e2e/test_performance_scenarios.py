"""
End-to-end performance and load testing scenarios.

These tests verify system performance under various load conditions,
response time requirements, and scalability characteristics.
Following TDD principles and testing real-world performance requirements.
"""

import asyncio
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.error_reporting_service.main import app
from tests.factories import SubmitErrorReportRequestFactory


@pytest.mark.e2e
@pytest.mark.performance
class TestPerformanceScenarios:
    """End-to-end performance testing scenarios"""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client"""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """Create async HTTP client"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers"""
        return {
            "Authorization": "Bearer performance.test.token",
            "Content-Type": "application/json",
        }

    def test_single_request_response_time(self, client, auth_headers):
        """Test single request response time meets requirements"""
        # Arrange
        error_data = SubmitErrorReportRequestFactory.create().__dict__

        # Act
        start_time = time.time()
        response = client.post("/api/v1/errors", json=error_data, headers=auth_headers)
        end_time = time.time()

        # Assert
        response_time = end_time - start_time
        assert response.status_code == 201
        assert response_time < 1.0  # Sub-second response requirement

        # Log performance metrics
        print(f"Single request response time: {response_time:.3f}s")

    def test_batch_submission_performance(self, client, auth_headers):
        """Test batch error submission performance"""
        # Arrange
        batch_size = 50
        error_reports = [
            SubmitErrorReportRequestFactory.create().__dict__ for _ in range(batch_size)
        ]

        # Act
        start_time = time.time()
        response_times = []

        for error_data in error_reports:
            request_start = time.time()
            response = client.post(
                "/api/v1/errors", json=error_data, headers=auth_headers
            )
            request_end = time.time()

            assert response.status_code == 201
            response_times.append(request_end - request_start)

        total_time = time.time() - start_time

        # Assert
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        throughput = batch_size / total_time

        assert avg_response_time < 0.5  # Average response time requirement
        assert max_response_time < 2.0  # Maximum response time requirement
        assert throughput > 10  # Minimum throughput requirement (requests/second)

        # Log performance metrics
        print(f"Batch submission metrics:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Max response time: {max_response_time:.3f}s")
        print(f"  Throughput: {throughput:.1f} requests/second")

    @pytest.mark.asyncio
    async def test_concurrent_request_performance(self, async_client, auth_headers):
        """Test concurrent request handling performance"""
        # Arrange
        concurrent_requests = 20
        error_reports = [
            SubmitErrorReportRequestFactory.create().__dict__
            for _ in range(concurrent_requests)
        ]

        # Act
        async def submit_error(error_data):
            start_time = time.time()
            response = await async_client.post(
                "/api/v1/errors", json=error_data, headers=auth_headers
            )
            end_time = time.time()
            return response.status_code, end_time - start_time

        start_time = time.time()
        results = await asyncio.gather(
            *[submit_error(error_data) for error_data in error_reports],
            return_exceptions=True,
        )
        total_time = time.time() - start_time

        # Assert
        successful_requests = [
            result
            for result in results
            if not isinstance(result, Exception) and result[0] == 201
        ]

        assert len(successful_requests) == concurrent_requests

        response_times = [result[1] for result in successful_requests]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        throughput = concurrent_requests / total_time

        assert avg_response_time < 1.0  # Concurrent average response time
        assert max_response_time < 3.0  # Concurrent maximum response time
        assert throughput > 5  # Minimum concurrent throughput

        # Log performance metrics
        print(f"Concurrent request metrics:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Max response time: {max_response_time:.3f}s")
        print(f"  Throughput: {throughput:.1f} requests/second")

    def test_search_performance_with_large_dataset(self, client, auth_headers):
        """Test search performance with large dataset"""
        # Arrange - Submit large number of error reports
        dataset_size = 100
        job_id = str(uuid4())
        speaker_id = str(uuid4())

        # Submit errors in batches for better performance
        batch_size = 10
        for batch_start in range(0, dataset_size, batch_size):
            batch_errors = []
            for i in range(batch_start, min(batch_start + batch_size, dataset_size)):
                error_data = SubmitErrorReportRequestFactory.create(
                    job_id=job_id if i % 2 == 0 else str(uuid4()),
                    speaker_id=speaker_id if i % 3 == 0 else str(uuid4()),
                    severity_level="high" if i % 5 == 0 else "medium",
                ).__dict__
                batch_errors.append(error_data)

            # Submit batch
            for error_data in batch_errors:
                response = client.post(
                    "/api/v1/errors", json=error_data, headers=auth_headers
                )
                assert response.status_code == 201

        # Act - Perform various search operations
        search_scenarios = [
            {"params": {"page": 1, "size": 20}, "description": "Basic pagination"},
            {
                "params": {"job_id": job_id, "page": 1, "size": 10},
                "description": "Job ID filter",
            },
            {
                "params": {"speaker_id": speaker_id, "page": 1, "size": 10},
                "description": "Speaker ID filter",
            },
            {
                "params": {"severity_level": "high", "page": 1, "size": 10},
                "description": "Severity filter",
            },
            {
                "params": {"categories": "medical_terminology", "page": 1, "size": 10},
                "description": "Category filter",
            },
        ]

        search_times = []
        for scenario in search_scenarios:
            start_time = time.time()
            response = client.get(
                "/api/v1/errors", headers=auth_headers, params=scenario["params"]
            )
            end_time = time.time()

            search_time = end_time - start_time
            search_times.append(search_time)

            # Assert
            assert response.status_code == 200
            assert search_time < 2.0  # Search response time requirement

            print(f"Search scenario '{scenario['description']}': {search_time:.3f}s")

        # Assert overall search performance
        avg_search_time = statistics.mean(search_times)
        max_search_time = max(search_times)

        assert avg_search_time < 1.0  # Average search time requirement
        assert max_search_time < 2.0  # Maximum search time requirement

        print(f"Search performance summary:")
        print(f"  Average search time: {avg_search_time:.3f}s")
        print(f"  Max search time: {max_search_time:.3f}s")

    def test_memory_usage_under_load(self, client, auth_headers):
        """Test memory usage under sustained load"""
        import os

        import psutil

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Arrange
        load_duration = 30  # seconds
        requests_per_second = 5
        total_requests = load_duration * requests_per_second

        # Act - Sustained load
        start_time = time.time()
        memory_samples = []

        for i in range(total_requests):
            error_data = SubmitErrorReportRequestFactory.create().__dict__

            response = client.post(
                "/api/v1/errors", json=error_data, headers=auth_headers
            )
            assert response.status_code == 201

            # Sample memory usage every 10 requests
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)

            # Control request rate
            elapsed = time.time() - start_time
            expected_time = (i + 1) / requests_per_second
            if elapsed < expected_time:
                time.sleep(expected_time - elapsed)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Assert
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_samples)

        # Memory usage should not increase excessively
        assert memory_increase < 100  # Less than 100MB increase
        assert max_memory < initial_memory + 150  # Peak memory limit

        print(f"Memory usage metrics:")
        print(f"  Initial memory: {initial_memory:.1f} MB")
        print(f"  Final memory: {final_memory:.1f} MB")
        print(f"  Memory increase: {memory_increase:.1f} MB")
        print(f"  Peak memory: {max_memory:.1f} MB")

    def test_database_connection_pool_performance(self, client, auth_headers):
        """Test database connection pool performance under load"""
        # Arrange
        concurrent_db_operations = 50

        def perform_db_operation():
            # Submit error (write operation)
            error_data = SubmitErrorReportRequestFactory.create().__dict__
            submit_response = client.post(
                "/api/v1/errors", json=error_data, headers=auth_headers
            )

            if submit_response.status_code == 201:
                error_id = submit_response.json()["error_id"]

                # Retrieve error (read operation)
                get_response = client.get(
                    f"/api/v1/errors/{error_id}", headers=auth_headers
                )

                return (
                    submit_response.status_code == 201
                    and get_response.status_code == 200
                )

            return False

        # Act - Concurrent database operations
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(perform_db_operation)
                for _ in range(concurrent_db_operations)
            ]

            results = [future.result() for future in futures]

        total_time = time.time() - start_time

        # Assert
        successful_operations = sum(results)
        success_rate = successful_operations / concurrent_db_operations
        throughput = successful_operations / total_time

        assert success_rate > 0.95  # 95% success rate requirement
        assert throughput > 10  # Minimum database throughput
        assert total_time < 30  # Maximum time for all operations

        print(f"Database performance metrics:")
        print(
            f"  Successful operations: {successful_operations}/{concurrent_db_operations}"
        )
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Throughput: {throughput:.1f} operations/second")
        print(f"  Total time: {total_time:.3f}s")

    @pytest.mark.asyncio
    async def test_api_rate_limiting_performance(self, async_client, auth_headers):
        """Test API rate limiting performance and behavior"""
        # Arrange
        rate_limit_requests = 100  # Exceed typical rate limits
        error_data = SubmitErrorReportRequestFactory.create().__dict__

        # Act
        async def make_request():
            try:
                response = await async_client.post(
                    "/api/v1/errors", json=error_data, headers=auth_headers
                )
                return response.status_code
            except Exception:
                return 500

        start_time = time.time()
        results = await asyncio.gather(
            *[make_request() for _ in range(rate_limit_requests)],
            return_exceptions=True,
        )
        total_time = time.time() - start_time

        # Analyze results
        status_codes = [
            result for result in results if not isinstance(result, Exception)
        ]

        successful_requests = status_codes.count(201)
        rate_limited_requests = status_codes.count(429)

        # Assert
        # Rate limiting should kick in
        assert rate_limited_requests > 0

        # System should remain responsive even under rate limiting
        assert total_time < 60  # Should complete within reasonable time

        # Some requests should still succeed
        assert successful_requests > 0

        print(f"Rate limiting performance:")
        print(f"  Total requests: {len(status_codes)}")
        print(f"  Successful: {successful_requests}")
        print(f"  Rate limited: {rate_limited_requests}")
        print(f"  Total time: {total_time:.3f}s")

    def test_large_payload_performance(self, client, auth_headers):
        """Test performance with large payloads"""
        # Arrange - Create error report with large text content
        large_text = "x" * 9000  # Near maximum text length
        large_metadata = {
            "large_field": "y" * 5000,
            "nested_data": {"items": [f"item_{i}" for i in range(1000)]},
            "description": "z" * 2000,
        }

        error_data = SubmitErrorReportRequestFactory.create(
            original_text=large_text,
            corrected_text=large_text.replace("x", "X", 1),
            metadata=large_metadata,
        ).__dict__

        # Act
        start_time = time.time()
        response = client.post("/api/v1/errors", json=error_data, headers=auth_headers)
        submit_time = time.time() - start_time

        # Assert submission
        assert response.status_code == 201
        assert submit_time < 3.0  # Large payload submission time limit

        error_id = response.json()["error_id"]

        # Test retrieval performance
        start_time = time.time()
        get_response = client.get(f"/api/v1/errors/{error_id}", headers=auth_headers)
        retrieval_time = time.time() - start_time

        # Assert retrieval
        assert get_response.status_code == 200
        assert retrieval_time < 2.0  # Large payload retrieval time limit

        # Verify data integrity
        retrieved_data = get_response.json()
        assert len(retrieved_data["original_text"]) == 9000
        assert len(retrieved_data["metadata"]["large_field"]) == 5000

        print(f"Large payload performance:")
        print(f"  Submission time: {submit_time:.3f}s")
        print(f"  Retrieval time: {retrieval_time:.3f}s")
        print(f"  Payload size: ~{len(str(error_data))} characters")
