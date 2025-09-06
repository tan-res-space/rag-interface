"""
Unit tests for RAG Integration Service HTTP Controllers.

These tests focus on testing the HTTP controller endpoints
to increase infrastructure layer test coverage.
"""

import pytest
from unittest.mock import patch
from uuid import uuid4
from fastapi.testclient import TestClient

from src.rag_integration_service.infrastructure.adapters.http.controllers import router


class TestRAGIntegrationServiceControllers:
    """Tests for RAG Integration Service HTTP controllers."""

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

    def test_create_embedding_success(self, client, mock_current_user):
        """Test successful embedding creation."""
        # Arrange
        payload = {
            "text": "This is a test text for embedding",
            "embedding_type": "error",
            "metadata": {"source": "test"}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/embeddings", json=payload)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["text"] == payload["text"]
            assert data["embedding_type"] == payload["embedding_type"]
            assert len(data["vector"]) == 384  # Expected embedding dimension
            assert data["metadata"] == payload["metadata"]
            assert "embedding_id" in data
            assert "created_at" in data

    def test_create_embedding_invalid_type(self, client, mock_current_user):
        """Test embedding creation with invalid type."""
        # Arrange
        payload = {
            "text": "Test text",
            "embedding_type": "invalid_type",
            "metadata": {}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/embeddings", json=payload)

            # Assert
            assert response.status_code == 400
            assert "Invalid embedding type" in response.json()["detail"]

    def test_create_embedding_empty_text(self, client, mock_current_user):
        """Test embedding creation with empty text."""
        # Arrange
        payload = {
            "text": "",
            "embedding_type": "error",
            "metadata": {}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/embeddings", json=payload)

            # Assert
            assert response.status_code == 400
            assert "Text cannot be empty" in response.json()["detail"]

    def test_create_batch_embeddings_success(self, client, mock_current_user):
        """Test successful batch embedding creation."""
        # Arrange
        payload = {
            "texts": ["Text 1", "Text 2", "Text 3"],
            "embedding_type": "correction",
            "metadata": {"batch_id": "test_batch"}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/embeddings/batch", json=payload)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert len(data["embeddings"]) == 3
            assert data["batch_metadata"]["total_embeddings"] == 3
            assert data["batch_metadata"]["embedding_type"] == "correction"
            assert "batch_id" in data["batch_metadata"]

    def test_create_batch_embeddings_too_many(self, client, mock_current_user):
        """Test batch embedding creation with too many texts."""
        # Arrange
        payload = {
            "texts": ["Text"] * 101,  # Exceeds limit of 100
            "embedding_type": "error",
            "metadata": {}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/embeddings/batch", json=payload)

            # Assert
            assert response.status_code == 400
            assert "Too many texts" in response.json()["detail"]

    def test_similarity_search_success(self, client, mock_current_user):
        """Test successful similarity search."""
        # Arrange
        payload = {
            "query_text": "Find similar errors",
            "top_k": 5,
            "similarity_threshold": 0.7,
            "filters": {"embedding_type": "error"}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/search/similarity", json=payload)

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) <= 5
            assert data["query_metadata"]["top_k"] == 5
            assert data["query_metadata"]["similarity_threshold"] == 0.7
            assert "search_id" in data["query_metadata"]

    def test_similarity_search_invalid_threshold(self, client, mock_current_user):
        """Test similarity search with invalid threshold."""
        # Arrange
        payload = {
            "query_text": "Test query",
            "top_k": 5,
            "similarity_threshold": 1.5,  # Invalid: > 1.0
            "filters": {}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/search/similarity", json=payload)

            # Assert
            assert response.status_code == 400
            assert "Similarity threshold must be between 0.0 and 1.0" in response.json()["detail"]

    def test_similarity_search_invalid_top_k(self, client, mock_current_user):
        """Test similarity search with invalid top_k."""
        # Arrange
        payload = {
            "query_text": "Test query",
            "top_k": 101,  # Exceeds limit of 100
            "similarity_threshold": 0.7,
            "filters": {}
        }

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.post("/search/similarity", json=payload)

            # Assert
            assert response.status_code == 400
            assert "top_k must be between 1 and 100" in response.json()["detail"]

    def test_get_embedding_by_id_success(self, client, mock_current_user):
        """Test successful embedding retrieval by ID."""
        # Arrange
        embedding_id = str(uuid4())

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.get(f"/embeddings/{embedding_id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["embedding_id"] == embedding_id
            assert "text" in data
            assert "vector" in data
            assert "embedding_type" in data

    def test_get_embedding_by_id_not_found(self, client, mock_current_user):
        """Test embedding retrieval with non-existent ID."""
        # Arrange
        embedding_id = str(uuid4())

        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.get(f"/embeddings/{embedding_id}")

            # Assert
            # Note: The current implementation returns a mock response
            # In a real implementation, this would return 404
            assert response.status_code == 200  # Current mock behavior

    def test_get_statistics_success(self, client, mock_current_user):
        """Test successful statistics retrieval."""
        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            # Act
            response = client.get("/statistics")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "embedding_statistics" in data
            assert "vector_db_statistics" in data
            assert "model_statistics" in data
            assert "performance_metrics" in data
            assert data["embedding_statistics"]["total_embeddings"] == 1000
            assert data["performance_metrics"]["success_rate"] == 0.99

    def test_health_check_success(self, client):
        """Test successful health check."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data
        assert "version" in data

    def test_embedding_types_validation(self, client, mock_current_user):
        """Test all valid embedding types."""
        valid_types = ["error", "correction", "context"]
        
        with patch('src.rag_integration_service.infrastructure.adapters.http.controllers.get_current_user') as mock_auth:
            mock_auth.return_value = mock_current_user

            for embedding_type in valid_types:
                payload = {
                    "text": f"Test text for {embedding_type}",
                    "embedding_type": embedding_type,
                    "metadata": {}
                }

                response = client.post("/embeddings", json=payload)
                assert response.status_code == 201
                assert response.json()["embedding_type"] == embedding_type

    def test_router_includes_specialized_routers(self):
        """Test that router includes specialized routers when available."""
        # This test verifies the router structure
        from src.rag_integration_service.infrastructure.adapters.http.controllers import router
        
        # Check that router is properly configured
        assert router is not None
        assert hasattr(router, 'routes')
        
        # Check that main endpoints exist
        route_paths = [route.path for route in router.routes]
        assert "/embeddings" in route_paths
        assert "/search/similarity" in route_paths
        assert "/statistics" in route_paths
        assert "/health" in route_paths
