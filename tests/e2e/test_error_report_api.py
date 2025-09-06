"""
End-to-end tests for Error Report API endpoints.

These tests verify complete workflows from HTTP request to response,
including authentication, validation, business logic, and data persistence.
Following TDD principles and testing real API behavior.
"""

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.error_reporting_service.main import app
from tests.factories import SubmitErrorReportRequestFactory


@pytest.mark.e2e
@pytest.mark.api
class TestErrorReportAPIEndpoints:
    """End-to-end tests for Error Report API endpoints"""

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
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token",
            "Content-Type": "application/json",
        }

    @pytest.fixture
    def valid_error_report_data(self):
        """Create valid error report request data"""
        return {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "original_text": "The patient has diabetis",
            "corrected_text": "The patient has diabetes",
            "error_categories": ["medical_terminology"],
            "severity_level": "high",
            "start_position": 16,
            "end_position": 24,
            "context_notes": "Common misspelling in medical terminology",
            "metadata": {"audio_quality": "good", "confidence_score": 0.95},
        }

    def test_submit_error_report_success(
        self, client, auth_headers, valid_error_report_data
    ):
        """Test successful error report submission"""
        # Act
        response = client.post(
            "/api/v1/errors", json=valid_error_report_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == 201

        response_data = response.json()
        assert response_data["status"] == "success"
        assert "error_id" in response_data
        assert response_data["message"] == "Error report submitted successfully"
        assert response_data["validation_warnings"] == []

        # Verify response structure
        assert "error_id" in response_data
        assert len(response_data["error_id"]) > 0

    def test_submit_error_report_invalid_data(self, client, auth_headers):
        """Test error report submission with invalid data"""
        # Arrange
        invalid_data = {
            "job_id": "invalid-uuid",
            "speaker_id": "",
            "original_text": "",
            "corrected_text": "",
            "error_categories": [],
            "severity_level": "invalid",
            "start_position": -1,
            "end_position": 0,
            "context_notes": "x" * 1001,  # Exceeds max length
            "metadata": {},
        }

        # Act
        response = client.post(
            "/api/v1/errors", json=invalid_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == 400

        response_data = response.json()
        assert response_data["success"] is False
        assert "error" in response_data
        assert response_data["error"]["code"] in ["VALIDATION_ERROR", "INVALID_REQUEST"]
        assert len(response_data["error"]["details"]) > 0

    def test_submit_error_report_unauthorized(self, client, valid_error_report_data):
        """Test error report submission without authentication"""
        # Act
        response = client.post("/api/v1/errors", json=valid_error_report_data)

        # Assert
        assert response.status_code == 401

        response_data = response.json()
        assert response_data["success"] is False
        assert response_data["error"]["code"] == "UNAUTHORIZED"

    def test_submit_error_report_invalid_token(self, client, valid_error_report_data):
        """Test error report submission with invalid token"""
        # Arrange
        invalid_headers = {
            "Authorization": "Bearer invalid.jwt.token",
            "Content-Type": "application/json",
        }

        # Act
        response = client.post(
            "/api/v1/errors", json=valid_error_report_data, headers=invalid_headers
        )

        # Assert
        assert response.status_code == 401

        response_data = response.json()
        assert response_data["error"]["code"] == "INVALID_TOKEN"

    def test_get_error_report_success(self, client, auth_headers):
        """Test successful error report retrieval"""
        # Arrange - First submit an error report
        error_data = SubmitErrorReportRequestFactory.create().__dict__
        submit_response = client.post(
            "/api/v1/errors", json=error_data, headers=auth_headers
        )
        error_id = submit_response.json()["error_id"]

        # Act
        response = client.get(f"/api/v1/errors/{error_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["id"] == error_id
        assert response_data["original_text"] == error_data["original_text"]
        assert response_data["corrected_text"] == error_data["corrected_text"]
        assert response_data["severity_level"] == error_data["severity_level"]
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_get_error_report_not_found(self, client, auth_headers):
        """Test error report retrieval for non-existent ID"""
        # Arrange
        nonexistent_id = str(uuid4())

        # Act
        response = client.get(f"/api/v1/errors/{nonexistent_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 404

        response_data = response.json()
        assert response_data["error"]["code"] == "ERROR_REPORT_NOT_FOUND"

    def test_get_error_report_invalid_id_format(self, client, auth_headers):
        """Test error report retrieval with invalid ID format"""
        # Arrange
        invalid_id = "invalid-uuid-format"

        # Act
        response = client.get(f"/api/v1/errors/{invalid_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 400

        response_data = response.json()
        assert response_data["error"]["code"] == "INVALID_REQUEST"

    def test_update_error_report_success(self, client, auth_headers):
        """Test successful error report update"""
        # Arrange - First submit an error report
        error_data = SubmitErrorReportRequestFactory.create().__dict__
        submit_response = client.post(
            "/api/v1/errors", json=error_data, headers=auth_headers
        )
        error_id = submit_response.json()["error_id"]

        # Prepare update data
        update_data = {
            "context_notes": "Updated context notes",
            "status": "processed",
            "metadata": {"review_status": "approved", "reviewer_id": str(uuid4())},
        }

        # Act
        response = client.put(
            f"/api/v1/errors/{error_id}", json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["id"] == error_id
        assert response_data["context_notes"] == "Updated context notes"
        assert response_data["status"] == "processed"
        assert response_data["metadata"]["review_status"] == "approved"

    def test_update_error_report_not_found(self, client, auth_headers):
        """Test error report update for non-existent ID"""
        # Arrange
        nonexistent_id = str(uuid4())
        update_data = {"context_notes": "Updated notes"}

        # Act
        response = client.put(
            f"/api/v1/errors/{nonexistent_id}", json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == 404

        response_data = response.json()
        assert response_data["error"]["code"] == "ERROR_REPORT_NOT_FOUND"

    def test_delete_error_report_success(self, client, auth_headers):
        """Test successful error report deletion"""
        # Arrange - First submit an error report
        error_data = SubmitErrorReportRequestFactory.create().__dict__
        submit_response = client.post(
            "/api/v1/errors", json=error_data, headers=auth_headers
        )
        error_id = submit_response.json()["error_id"]

        # Act
        response = client.delete(f"/api/v1/errors/{error_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 204

        # Verify error report is deleted
        get_response = client.get(f"/api/v1/errors/{error_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_error_report_not_found(self, client, auth_headers):
        """Test error report deletion for non-existent ID"""
        # Arrange
        nonexistent_id = str(uuid4())

        # Act
        response = client.delete(
            f"/api/v1/errors/{nonexistent_id}", headers=auth_headers
        )

        # Assert
        assert response.status_code == 404

        response_data = response.json()
        assert response_data["error"]["code"] == "ERROR_REPORT_NOT_FOUND"

    def test_search_errors_basic_success(self, client, auth_headers):
        """Test basic error search functionality"""
        # Arrange - Submit multiple error reports
        error_reports = []
        for _ in range(3):
            error_data = SubmitErrorReportRequestFactory.create().__dict__
            response = client.post(
                "/api/v1/errors", json=error_data, headers=auth_headers
            )
            error_reports.append(response.json()["error_id"])

        # Act
        response = client.get(
            "/api/v1/errors", headers=auth_headers, params={"page": 1, "size": 10}
        )

        # Assert
        assert response.status_code == 200

        response_data = response.json()
        assert "items" in response_data
        assert "total" in response_data
        assert "page" in response_data
        assert "size" in response_data
        assert "pages" in response_data

        assert len(response_data["items"]) >= 3
        assert response_data["total"] >= 3
        assert response_data["page"] == 1
        assert response_data["size"] == 10

    def test_search_errors_with_filters(self, client, auth_headers):
        """Test error search with filters"""
        # Arrange - Submit error reports with specific characteristics
        high_severity_data = SubmitErrorReportRequestFactory.create(
            severity_level="high", error_categories=["medical_terminology"]
        ).__dict__

        client.post("/api/v1/errors", json=high_severity_data, headers=auth_headers)

        # Act
        response = client.get(
            "/api/v1/errors",
            headers=auth_headers,
            params={
                "severity_level": "high",
                "categories": "medical_terminology",
                "page": 1,
                "size": 10,
            },
        )

        # Assert
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data["items"]) >= 1

        # Verify all returned items match the filter
        for item in response_data["items"]:
            assert item["severity_level"] == "high"
            assert "medical_terminology" in item["error_categories"]

    def test_search_errors_pagination(self, client, auth_headers):
        """Test error search pagination"""
        # Arrange - Submit multiple error reports
        for _ in range(15):
            error_data = SubmitErrorReportRequestFactory.create().__dict__
            client.post("/api/v1/errors", json=error_data, headers=auth_headers)

        # Act - Get first page
        page_1_response = client.get(
            "/api/v1/errors", headers=auth_headers, params={"page": 1, "size": 5}
        )

        # Act - Get second page
        page_2_response = client.get(
            "/api/v1/errors", headers=auth_headers, params={"page": 2, "size": 5}
        )

        # Assert
        assert page_1_response.status_code == 200
        assert page_2_response.status_code == 200

        page_1_data = page_1_response.json()
        page_2_data = page_2_response.json()

        assert len(page_1_data["items"]) == 5
        assert len(page_2_data["items"]) == 5
        assert page_1_data["page"] == 1
        assert page_2_data["page"] == 2

        # Verify no overlap between pages
        page_1_ids = {item["id"] for item in page_1_data["items"]}
        page_2_ids = {item["id"] for item in page_2_data["items"]}
        assert page_1_ids.isdisjoint(page_2_ids)

    def test_api_rate_limiting(self, client, auth_headers, valid_error_report_data):
        """Test API rate limiting functionality"""
        # Act - Make multiple rapid requests
        responses = []
        for _ in range(100):  # Exceed rate limit
            response = client.post(
                "/api/v1/errors", json=valid_error_report_data, headers=auth_headers
            )
            responses.append(response.status_code)

            # Stop if we hit rate limit
            if response.status_code == 429:
                break

        # Assert
        assert 429 in responses  # Rate limit should be triggered

    def test_api_cors_headers(self, client, auth_headers):
        """Test CORS headers are properly set"""
        # Act
        response = client.options("/api/v1/errors", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers

    @pytest.mark.asyncio
    async def test_api_performance_requirements(
        self, async_client, auth_headers, valid_error_report_data
    ):
        """Test API performance requirements"""
        # Act
        start_time = datetime.utcnow()
        response = await async_client.post(
            "/api/v1/errors", json=valid_error_report_data, headers=auth_headers
        )
        end_time = datetime.utcnow()

        # Assert
        response_time = (end_time - start_time).total_seconds()
        assert response.status_code == 201
        assert response_time < 1.0  # Should respond within 1 second

    def test_api_error_response_format(self, client, auth_headers):
        """Test consistent error response format"""
        # Arrange
        invalid_data = {"invalid": "data"}

        # Act
        response = client.post(
            "/api/v1/errors", json=invalid_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == 400

        response_data = response.json()

        # Verify error response structure
        assert "success" in response_data
        assert response_data["success"] is False
        assert "error" in response_data
        assert "code" in response_data["error"]
        assert "message" in response_data["error"]
        assert "timestamp" in response_data
        assert "request_id" in response_data
        assert "version" in response_data
