"""
RAG Integration Service Client

HTTP client for communicating with the RAG Integration Service.
Provides methods for embedding generation and similarity search.
"""

import logging
from typing import Any, Dict, List, Optional

from .base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class RAGIntegrationClient(BaseHTTPClient):
    """
    Client for RAG Integration Service.
    
    Provides methods for embedding generation, similarity search, and vector operations.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8003",
        timeout: int = 60,  # Longer timeout for ML operations
        max_retries: int = 3,
        auth_token: Optional[str] = None
    ):
        """
        Initialize RAG Integration client.
        
        Args:
            base_url: Base URL of the RAG Integration Service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            auth_token: Authentication token
        """
        super().__init__(base_url, timeout, max_retries, auth_token)

    async def generate_embedding(
        self,
        text: str,
        embedding_type: str = "ERROR"
    ) -> Dict[str, Any]:
        """
        Generate vector embedding for text.
        
        Args:
            text: Text to generate embedding for
            embedding_type: Type of embedding (ERROR, CORRECTION, etc.)
            
        Returns:
            Embedding response with vector and metadata
        """
        payload = {
            "text": text,
            "embedding_type": embedding_type
        }
        
        try:
            response = await self.post_json("/api/v1/embeddings", json=payload)
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def generate_batch_embeddings(
        self,
        texts: List[str],
        embedding_type: str = "ERROR"
    ) -> Dict[str, Any]:
        """
        Generate vector embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            embedding_type: Type of embedding
            
        Returns:
            Batch embedding response
        """
        payload = {
            "texts": texts,
            "embedding_type": embedding_type
        }
        
        try:
            response = await self.post_json("/api/v1/embeddings/batch", json=payload)
            logger.debug(f"Generated {len(texts)} embeddings in batch")
            return response
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    async def search_similar(
        self,
        query_text: str,
        limit: int = 10,
        threshold: float = 0.7,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar texts using vector similarity.
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            threshold: Similarity threshold (0.0 to 1.0)
            metadata_filter: Optional metadata filters
            
        Returns:
            Similarity search results
        """
        payload = {
            "query_text": query_text,
            "limit": limit,
            "threshold": threshold
        }
        
        if metadata_filter:
            payload["metadata_filter"] = metadata_filter
        
        try:
            response = await self.post_json("/api/v1/similarity/search", json=payload)
            logger.debug(f"Found {len(response.get('results', []))} similar texts")
            return response
        except Exception as e:
            logger.error(f"Failed to search similar texts: {e}")
            raise

    async def search_similar_by_vector(
        self,
        query_vector: List[float],
        limit: int = 10,
        threshold: float = 0.7,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar vectors using vector similarity.
        
        Args:
            query_vector: Vector to search for
            limit: Maximum number of results
            threshold: Similarity threshold (0.0 to 1.0)
            metadata_filter: Optional metadata filters
            
        Returns:
            Similarity search results
        """
        payload = {
            "query_vector": query_vector,
            "limit": limit,
            "threshold": threshold
        }
        
        if metadata_filter:
            payload["metadata_filter"] = metadata_filter
        
        try:
            response = await self.post_json("/api/v1/similarity/search-by-vector", json=payload)
            logger.debug(f"Found {len(response.get('results', []))} similar vectors")
            return response
        except Exception as e:
            logger.error(f"Failed to search similar vectors: {e}")
            raise

    async def get_embedding(self, embedding_id: str) -> Dict[str, Any]:
        """
        Get a specific embedding by ID.
        
        Args:
            embedding_id: ID of the embedding
            
        Returns:
            Embedding data
        """
        try:
            response = await self.get_json(f"/api/v1/embeddings/{embedding_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get embedding {embedding_id}: {e}")
            raise

    async def delete_embedding(self, embedding_id: str) -> bool:
        """
        Delete an embedding by ID.
        
        Args:
            embedding_id: ID of the embedding to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            response = await self.delete(f"/api/v1/embeddings/{embedding_id}")
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Failed to delete embedding {embedding_id}: {e}")
            return False

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the ML model.
        
        Returns:
            Model information
        """
        try:
            response = await self.get_json("/api/v1/model/info")
            return response
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            raise

    async def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about vector storage.
        
        Returns:
            Storage information
        """
        try:
            response = await self.get_json("/api/v1/storage/info")
            return response
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if RAG Integration Service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"RAG Integration Service health check failed: {e}")
            return False


# Convenience function to create client from environment
def create_rag_client_from_env() -> RAGIntegrationClient:
    """
    Create RAG Integration client from environment variables.
    
    Environment variables:
    - RAG_INTEGRATION_URL: Service URL (default: http://localhost:8003)
    - RAG_INTEGRATION_TIMEOUT: Request timeout (default: 60)
    - RAG_INTEGRATION_AUTH_TOKEN: Authentication token
    
    Returns:
        Configured RAG Integration client
    """
    import os
    
    base_url = os.getenv("RAG_INTEGRATION_URL", "http://localhost:8003")
    timeout = int(os.getenv("RAG_INTEGRATION_TIMEOUT", "60"))
    auth_token = os.getenv("RAG_INTEGRATION_AUTH_TOKEN")
    
    return RAGIntegrationClient(
        base_url=base_url,
        timeout=timeout,
        auth_token=auth_token
    )
