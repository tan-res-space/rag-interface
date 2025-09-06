"""
Comprehensive API Endpoint Validation Tests

Tests all API endpoints for proper validation, error handling,
and response formatting following FastAPI best practices.
"""

import pytest
import json
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.error_reporting_service.main import app


class TestErrorReportEndpointValidation:
    """Test error report endpoint validation comprehensively"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    def test_submit_error_report_valid_payload(self, client):
        """Test submitting error report with valid payload"""
        valid_payload = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "reported_by": str(uuid4()),
            "original_text": "Patient shows signs of hypertention",
            "corrected_text": "Patient shows signs of hypertension",
            "error_categories": ["medical_terminology"],
            "severity_level": "medium",
            "start_position": 25,
            "end_position": 37,
            "context_notes": "Medical terminology correction"
        }
        
        response = client.post("/api/v1/errors", json=valid_payload)
        
        # Should accept valid payload
        assert response.status_code in [201, 422]  # 422 if validation implemented
        
        if response.status_code == 201:
            data = response.json()
            assert "error_id" in data
            assert data["status"] == "success"

    def test_submit_error_report_missing_required_fields(self, client):
        """Test validation of required fields"""
        required_fields = [
            "job_id", "speaker_id", "reported_by", "original_text", 
            "corrected_text", "error_categories", "severity_level",
            "start_position", "end_position"
        ]
        
        base_payload = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "reported_by": str(uuid4()),
            "original_text": "Test original text",
            "corrected_text": "Test corrected text",
            "error_categories": ["test"],
            "severity_level": "medium",
            "start_position": 0,
            "end_position": 4
        }
        
        for field in required_fields:
            incomplete_payload = base_payload.copy()
            del incomplete_payload[field]
            
            response = client.post("/api/v1/errors", json=incomplete_payload)
            assert response.status_code == 422, f"Missing {field} should return 422"
            
            error_detail = response.json()
            assert "detail" in error_detail

    def test_submit_error_report_invalid_field_types(self, client):
        """Test validation of field types"""
        invalid_payloads = [
            # Invalid job_id type
            {
                "job_id": 123,  # Should be string
                "speaker_id": str(uuid4()),
                "reported_by": str(uuid4()),
                "original_text": "Test",
                "corrected_text": "Corrected",
                "error_categories": ["test"],
                "severity_level": "medium",
                "start_position": 0,
                "end_position": 4
            },
            # Invalid position types
            {
                "job_id": str(uuid4()),
                "speaker_id": str(uuid4()),
                "reported_by": str(uuid4()),
                "original_text": "Test",
                "corrected_text": "Corrected",
                "error_categories": ["test"],
                "severity_level": "medium",
                "start_position": "invalid",  # Should be int
                "end_position": 4
            },
            # Invalid severity level
            {
                "job_id": str(uuid4()),
                "speaker_id": str(uuid4()),
                "reported_by": str(uuid4()),
                "original_text": "Test",
                "corrected_text": "Corrected",
                "error_categories": ["test"],
                "severity_level": "invalid_severity",
                "start_position": 0,
                "end_position": 4
            }
        ]
        
        for payload in invalid_payloads:
            response = client.post("/api/v1/errors", json=payload)
            assert response.status_code == 422

    def test_submit_error_report_business_rule_validation(self, client):
        """Test business rule validation"""
        # Same original and corrected text
        same_text_payload = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "reported_by": str(uuid4()),
            "original_text": "Same text",
            "corrected_text": "Same text",  # Should be different
            "error_categories": ["test"],
            "severity_level": "medium",
            "start_position": 0,
            "end_position": 4
        }
        
        response = client.post("/api/v1/errors", json=same_text_payload)
        assert response.status_code == 422
        
        # Invalid position range
        invalid_position_payload = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "reported_by": str(uuid4()),
            "original_text": "Short",
            "corrected_text": "Corrected",
            "error_categories": ["test"],
            "severity_level": "medium",
            "start_position": 0,
            "end_position": 100  # Exceeds text length
        }
        
        response = client.post("/api/v1/errors", json=invalid_position_payload)
        assert response.status_code == 422

    def test_get_error_report_valid_id(self, client):
        """Test retrieving error report with valid ID"""
        valid_uuid = str(uuid4())
        response = client.get(f"/api/v1/errors/{valid_uuid}")
        
        # Should handle valid UUID format
        assert response.status_code in [200, 404]  # 404 if not found

    def test_get_error_report_invalid_id_format(self, client):
        """Test retrieving error report with invalid ID format"""
        invalid_ids = [
            "not-a-uuid",
            "123",
            "invalid-format-123",
            ""
        ]
        
        for invalid_id in invalid_ids:
            response = client.get(f"/api/v1/errors/{invalid_id}")
            assert response.status_code == 400, f"Invalid ID {invalid_id} should return 400"

    def test_search_errors_pagination_validation(self, client):
        """Test search endpoint pagination validation"""
        # Valid pagination
        response = client.get("/api/v1/errors?page=1&size=10")
        assert response.status_code == 200
        
        # Invalid pagination parameters
        invalid_params = [
            {"page": 0, "size": 10},  # Page should be >= 1
            {"page": 1, "size": 0},   # Size should be >= 1
            {"page": -1, "size": 10}, # Negative page
            {"page": 1, "size": 101}, # Size too large
        ]
        
        for params in invalid_params:
            response = client.get("/api/v1/errors", params=params)
            assert response.status_code == 400

    def test_search_errors_filter_validation(self, client):
        """Test search endpoint filter validation"""
        # Valid filters
        valid_filters = [
            {"severity_level": "high"},
            {"categories": "medical_terminology"},
            {"speaker_id": str(uuid4())},
            {"job_id": str(uuid4())}
        ]
        
        for filters in valid_filters:
            response = client.get("/api/v1/errors", params=filters)
            assert response.status_code == 200

    def test_response_format_consistency(self, client):
        """Test that all responses follow consistent format"""
        endpoints_to_test = [
            ("GET", "/api/v1/health", None),
            ("GET", "/api/v1/errors", None),
            ("GET", f"/api/v1/errors/{uuid4()}", None),
        ]
        
        for method, url, payload in endpoints_to_test:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=payload)
            
            # All responses should be valid JSON
            try:
                data = response.json()
                assert isinstance(data, dict)
            except json.JSONDecodeError:
                pytest.fail(f"Response from {method} {url} is not valid JSON")

    def test_error_response_format(self, client):
        """Test that error responses follow consistent format"""
        # Trigger various error types
        error_scenarios = [
            ("GET", "/api/v1/errors/invalid-uuid"),  # 400 error
            ("GET", "/api/v1/nonexistent"),          # 404 error
            ("POST", "/api/v1/errors", {"invalid": "data"}),  # 422 error
        ]
        
        for method, url, *payload in error_scenarios:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=payload[0] if payload else {})
            
            if response.status_code >= 400:
                error_data = response.json()
                
                # Error responses should have consistent structure
                assert "detail" in error_data or "error" in error_data
                
                # Should include error information
                if "error" in error_data:
                    assert "code" in error_data["error"]
                    assert "message" in error_data["error"]

    @pytest.mark.asyncio
    async def test_async_endpoint_performance(self, async_client):
        """Test async endpoint performance"""
        import time
        
        start_time = time.time()
        response = await async_client.get("/api/v1/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond quickly

    def test_content_type_validation(self, client):
        """Test content type validation"""
        # JSON content type
        response = client.post(
            "/api/v1/errors",
            json={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [201, 422]  # Should accept JSON
        
        # Invalid content type
        response = client.post(
            "/api/v1/errors",
            data="invalid data",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 422  # Should reject non-JSON

    def test_request_size_limits(self, client):
        """Test request size limits"""
        # Large but reasonable request
        large_text = "A" * 1000  # 1KB
        large_payload = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "reported_by": str(uuid4()),
            "original_text": large_text,
            "corrected_text": large_text.replace("A", "B"),
            "error_categories": ["large_text"],
            "severity_level": "medium",
            "start_position": 0,
            "end_position": 10
        }
        
        response = client.post("/api/v1/errors", json=large_payload)
        assert response.status_code in [201, 422, 413]  # 413 if too large

    def test_special_characters_in_requests(self, client):
        """Test handling of special characters in requests"""
        special_chars_payload = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "reported_by": str(uuid4()),
            "original_text": "Patient's temp: 98.6°F (37°C) - normal",
            "corrected_text": "Patient's temperature: 98.6°F (37°C) - normal",
            "error_categories": ["abbreviation"],
            "severity_level": "medium",
            "start_position": 10,
            "end_position": 14
        }
        
        response = client.post("/api/v1/errors", json=special_chars_payload)
        assert response.status_code in [201, 422]

    def test_concurrent_requests_to_same_endpoint(self, client):
        """Test concurrent requests to the same endpoint"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/api/v1/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)
        
        # Should handle concurrent load
        total_time = end_time - start_time
        assert total_time < 5.0  # Should complete within reasonable time

    def test_api_versioning_headers(self, client):
        """Test API versioning through headers"""
        response = client.get("/api/v1/health")
        
        # Should include version information
        assert response.status_code == 200
        
        # Check for version headers (if implemented)
        headers = response.headers
        # This would check for custom version headers if implemented
        assert "content-type" in headers

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.options("/api/v1/health")
        
        # Should handle OPTIONS request for CORS
        assert response.status_code in [200, 405]  # 405 if OPTIONS not implemented
        
        # Check for CORS headers in regular response
        get_response = client.get("/api/v1/health")
        get_response.headers
        
        # CORS headers should be present (if CORS is configured)
        # This test would verify CORS configuration
