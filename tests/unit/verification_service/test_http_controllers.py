"""
Unit tests for Verification Service HTTP Controllers.

These tests focus on testing the HTTP controller endpoints
to increase infrastructure layer test coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.verification_service.infrastructure.adapters.http.controllers import router


class TestVerificationServiceControllers:
    """Tests for Verification Service HTTP controllers."""

    @pytest.fixture
    def client(self):
        """Create test client for the router."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user for authentication."""
        return {
            "user_id": str(uuid4()),
            "username": "test_user",
            "email": "test@example.com"
        }

    def test_create_verification_success(self, client, mock_current_user):
        """Test successful verification creation."""
        # Arrange
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.85,
            "verification_status": "verified",
            "notes": "Good correction"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["correction_id"] == correction_id
            assert data["quality_score"] == 0.85
            assert data["status"] == "verified"
            assert data["verified_by"] == mock_current_user["username"]
            assert data["verification_notes"] == "Good correction"
            assert data["is_verified"] is True
            assert data["is_high_quality"] is True

    def test_create_verification_invalid_correction_id(self, client, mock_current_user):
        """Test verification creation with invalid correction ID."""
        # Arrange
        payload = {
            "correction_id": "invalid-uuid",
            "quality_score": 0.85,
            "verification_status": "verified"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 400
            assert "Invalid correction ID format" in response.json()["detail"]

    def test_create_verification_invalid_quality_score(self, client, mock_current_user):
        """Test verification creation with invalid quality score."""
        # Arrange
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 1.5,  # Invalid: > 1.0
            "verification_status": "verified"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 400
            assert "Quality score must be between 0.0 and 1.0" in response.json()["detail"]

    def test_create_verification_invalid_status(self, client, mock_current_user):
        """Test verification creation with invalid status."""
        # Arrange
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.85,
            "verification_status": "invalid_status"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 400
            assert "Invalid status" in response.json()["detail"]

    def test_create_verification_low_quality_score(self, client, mock_current_user):
        """Test verification creation with low quality score."""
        # Arrange
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.5,  # Low quality
            "verification_status": "needs_review"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["quality_score"] == 0.5
            assert data["status"] == "needs_review"
            assert data["is_verified"] is False
            assert data["is_high_quality"] is False

    def test_create_verification_rejected_status(self, client, mock_current_user):
        """Test verification creation with rejected status."""
        # Arrange
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.3,
            "verification_status": "rejected",
            "notes": "Poor quality correction"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "rejected"
            assert data["is_verified"] is False
            assert data["verification_notes"] == "Poor quality correction"

    def test_create_verification_pending_status(self, client, mock_current_user):
        """Test verification creation with pending status."""
        # Arrange
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.75,
            "verification_status": "pending"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "pending"
            assert data["is_verified"] is False

    def test_create_verification_boundary_quality_scores(self, client, mock_current_user):
        """Test verification creation with boundary quality scores."""
        # Test minimum valid score
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.0,
            "verification_status": "rejected"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            response = client.post("/verifications", json=payload)
            assert response.status_code == 201
            assert response.json()["quality_score"] == 0.0

        # Test maximum valid score
        payload["quality_score"] = 1.0
        payload["verification_status"] = "verified"
        response = client.post("/verifications", json=payload)
        assert response.status_code == 201
        assert response.json()["quality_score"] == 1.0

    def test_create_verification_without_notes(self, client, mock_current_user):
        """Test verification creation without optional notes."""
        # Arrange
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.85,
            "verification_status": "verified"
            # No notes provided
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/verifications", json=payload)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["verification_notes"] is None

    def test_create_verification_high_quality_threshold(self, client, mock_current_user):
        """Test verification creation around high quality threshold."""
        # Test just below threshold
        correction_id = str(uuid4())
        payload = {
            "correction_id": correction_id,
            "quality_score": 0.79,
            "verification_status": "verified"
        }

        with patch('src.verification_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            response = client.post("/verifications", json=payload)
            assert response.status_code == 201
            assert response.json()["is_high_quality"] is False

        # Test at threshold
        payload["quality_score"] = 0.8
        response = client.post("/verifications", json=payload)
        assert response.status_code == 201
        assert response.json()["is_high_quality"] is True

    def test_router_includes_specialized_routers(self):
        """Test that router includes specialized routers when available."""
        # This test verifies the router structure
        from src.verification_service.infrastructure.adapters.http.controllers import router
        
        # Check that router is properly configured
        assert router is not None
        assert hasattr(router, 'routes')
        
        # Check that the main verification endpoint exists
        route_paths = [route.path for route in router.routes]
        assert "/verifications" in route_paths
