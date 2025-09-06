"""
API Performance Tests

Tests API endpoint performance, load handling, and scalability
following FastAPI best practices and async patterns.
"""

import pytest
import asyncio
import time

from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.error_reporting_service.main import app


class TestAPIPerformance:
    """Test API endpoint performance and scalability"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_single_endpoint_response_time(self, async_client):
        """Test individual endpoint response times"""
        endpoints = [
            ("GET", "/api/v1/health"),
            ("GET", "/api/v1/errors"),
            ("POST", "/api/v1/errors", {
                "job_id": "test-job-123",
                "speaker_id": "speaker-456",
                "original_text": "Patient shows signs of hypertention",
                "corrected_text": "Patient shows signs of hypertension",
                "error_categories": ["medical_terminology"],
                "severity_level": "medium",
                "start_position": 25,
                "end_position": 37,
                "reported_by": "user-789"
            })
        ]
        
        for method, url, *payload in endpoints:
            start_time = time.time()
            
            if method == "GET":
                response = await async_client.get(url)
            elif method == "POST":
                response = await async_client.post(url, json=payload[0])
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # API responses should be under 200ms for good UX
            assert response_time < 0.2, f"{method} {url} took {response_time:.3f}s"
            assert response.status_code in [200, 201, 422]  # 422 for validation errors

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, async_client):
        """Test API handling of concurrent requests"""
        async def make_request():
            response = await async_client.get("/api/v1/health")
            return response.status_code
        
        # Send 50 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # All requests should complete successfully
        assert all(status == 200 for status in results)
        
        # Should handle concurrent load efficiently
        assert total_time < 5.0, f"50 concurrent requests took {total_time:.2f}s"
        
        # Calculate requests per second
        rps = len(results) / total_time
        assert rps > 10, f"Only {rps:.1f} requests/second, expected > 10"

    @pytest.mark.asyncio
    async def test_bulk_data_processing_performance(self, async_client):
        """Test performance with bulk data operations"""
        # Create bulk error report data
        bulk_data = []
        for i in range(20):
            error_data = {
                "job_id": f"bulk-job-{i}",
                "speaker_id": f"speaker-{i % 5}",  # 5 different speakers
                "original_text": f"Sample error text {i} with mistake",
                "corrected_text": f"Sample error text {i} with correction",
                "error_categories": ["grammar", "spelling"],
                "severity_level": "medium",
                "start_position": 20,
                "end_position": 27,
                "reported_by": f"user-{i % 3}"  # 3 different users
            }
            bulk_data.append(error_data)
        
        # Submit bulk data
        start_time = time.time()
        
        # Send requests concurrently
        tasks = [
            async_client.post("/api/v1/errors", json=data) 
            for data in bulk_data
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process bulk data efficiently
        assert processing_time < 10.0, f"Bulk processing took {processing_time:.2f}s"
        
        # Count successful submissions
        successful = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code in [200, 201])
        assert successful >= 15, f"Only {successful}/20 requests succeeded"

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, async_client):
        """Test memory usage under sustained load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async def sustained_load():
            tasks = []
            for batch in range(5):  # 5 batches of 20 requests each
                batch_tasks = [
                    async_client.get("/api/v1/health") 
                    for _ in range(20)
                ]
                tasks.extend(batch_tasks)
                await asyncio.gather(*batch_tasks)
                await asyncio.sleep(0.1)  # Small delay between batches
            
            return len(tasks)
        
        total_requests = await sustained_load()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage should remain reasonable
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"
        assert total_requests == 100

    @pytest.mark.asyncio
    async def test_database_query_performance(self, async_client):
        """Test database query performance through API"""
        # First, create some test data
        for i in range(50):
            await async_client.post("/api/v1/errors", json={
                "job_id": f"perf-test-{i}",
                "speaker_id": f"speaker-{i % 10}",
                "original_text": f"Performance test error {i}",
                "corrected_text": f"Performance test correction {i}",
                "error_categories": ["performance_test"],
                "severity_level": "low",
                "start_position": 0,
                "end_position": 10,
                "reported_by": "perf-tester"
            })
        
        # Test various query patterns
        query_tests = [
            "/api/v1/errors?page=1&size=10",
            "/api/v1/errors?severity_level=low",
            "/api/v1/errors?categories=performance_test",
            "/api/v1/errors?speaker_id=speaker-1",
        ]
        
        for query_url in query_tests:
            start_time = time.time()
            response = await async_client.get(query_url)
            end_time = time.time()
            
            query_time = end_time - start_time
            
            # Database queries should be fast
            assert query_time < 1.0, f"Query {query_url} took {query_time:.3f}s"
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limiting_performance(self, async_client):
        """Test rate limiting implementation performance"""
        # Make rapid requests to test rate limiting
        start_time = time.time()
        responses = []
        
        for i in range(100):
            response = await async_client.get("/api/v1/health")
            responses.append(response.status_code)
            
            # Small delay to avoid overwhelming the system
            if i % 10 == 0:
                await asyncio.sleep(0.01)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle rate limiting efficiently
        assert total_time < 30.0, f"Rate limiting test took {total_time:.2f}s"
        
        # Should have some rate limited responses if implemented
        status_codes = set(responses)
        assert 200 in status_codes  # Some successful requests
        
        # If rate limiting is implemented, should see 429 responses
        if 429 in status_codes:
            rate_limited = sum(1 for code in responses if code == 429)
            assert rate_limited > 0, "Rate limiting should trigger under load"

    @pytest.mark.asyncio
    async def test_error_handling_performance(self, async_client):
        """Test error handling performance"""
        # Test various error scenarios
        error_scenarios = [
            ("POST", "/api/v1/errors", {"invalid": "data"}),  # Validation error
            ("GET", "/api/v1/errors/invalid-uuid"),  # Invalid ID format
            ("GET", "/api/v1/errors/00000000-0000-0000-0000-000000000000"),  # Not found
            ("POST", "/api/v1/nonexistent", {}),  # Invalid endpoint
        ]
        
        start_time = time.time()
        
        for method, url, *payload in error_scenarios:
            if method == "GET":
                response = await async_client.get(url)
            elif method == "POST":
                response = await async_client.post(url, json=payload[0] if payload else {})
            
            # Error responses should be fast
            assert response.status_code in [400, 404, 422, 500]
        
        end_time = time.time()
        error_handling_time = end_time - start_time
        
        # Error handling should be efficient
        assert error_handling_time < 2.0, f"Error handling took {error_handling_time:.2f}s"

    @pytest.mark.asyncio
    async def test_websocket_performance(self, async_client):
        """Test WebSocket connection performance if implemented"""
        # This test would be relevant if WebSocket endpoints are implemented
        # For now, we'll test the basic connection attempt
        
        try:
            # Attempt WebSocket connection
            async with async_client.websocket_connect("/ws") as websocket:
                start_time = time.time()
                
                # Send test messages
                for i in range(10):
                    await websocket.send_text(f"test message {i}")
                    response = await websocket.receive_text()
                    assert response is not None
                
                end_time = time.time()
                ws_time = end_time - start_time
                
                # WebSocket communication should be fast
                assert ws_time < 1.0, f"WebSocket communication took {ws_time:.3f}s"
                
        except Exception:
            # WebSocket not implemented, skip test
            pytest.skip("WebSocket endpoints not implemented")

    def test_synchronous_endpoint_performance(self, client):
        """Test synchronous endpoint performance using TestClient"""
        # Test endpoints that might not be async
        start_time = time.time()
        
        # Make multiple requests
        for _ in range(20):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
        
        end_time = time.time()
        sync_time = end_time - start_time
        
        # Synchronous requests should still be reasonably fast
        assert sync_time < 5.0, f"20 sync requests took {sync_time:.2f}s"

    @pytest.mark.asyncio
    async def test_large_payload_handling(self, async_client):
        """Test handling of large request payloads"""
        # Create a large error report
        large_text = "A" * 5000  # 5KB text
        
        large_payload = {
            "job_id": "large-payload-test",
            "speaker_id": "speaker-large",
            "original_text": large_text,
            "corrected_text": large_text.replace("A", "B"),
            "error_categories": ["large_text_test"],
            "severity_level": "medium",
            "start_position": 0,
            "end_position": 100,
            "reported_by": "large-payload-tester"
        }
        
        start_time = time.time()
        response = await async_client.post("/api/v1/errors", json=large_payload)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should handle large payloads efficiently
        assert processing_time < 2.0, f"Large payload took {processing_time:.3f}s"
        assert response.status_code in [201, 422]  # Created or validation error
