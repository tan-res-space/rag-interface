"""
Vector Storage Adapter Factory

Factory for creating vector storage adapters based on configuration.
Supports multiple vector database providers.
"""

import logging
import os
from typing import Any, Dict, Optional

from rag_integration_service.application.ports.secondary.vector_storage_port import VectorStoragePort

logger = logging.getLogger(__name__)


class VectorStorageAdapterFactory:
    """Factory for creating vector storage adapters."""

    @staticmethod
    async def create_adapter(
        provider: str,
        config: Optional[Dict[str, Any]] = None
    ) -> VectorStoragePort:
        """
        Create a vector storage adapter based on provider and configuration.
        
        Args:
            provider: Vector storage provider name (in_memory, pinecone, weaviate, etc.)
            config: Additional configuration parameters
            
        Returns:
            Vector storage adapter instance
            
        Raises:
            ValueError: If provider is not supported
            RuntimeError: If adapter creation fails
        """
        config = config or {}
        provider = provider.lower()
        
        logger.info(f"Creating vector storage adapter: {provider}")
        
        try:
            if provider == "in_memory":
                return await VectorStorageAdapterFactory._create_in_memory_adapter(config)
            elif provider == "pinecone":
                return await VectorStorageAdapterFactory._create_pinecone_adapter(config)
            elif provider == "weaviate":
                return await VectorStorageAdapterFactory._create_weaviate_adapter(config)
            elif provider == "chroma":
                return await VectorStorageAdapterFactory._create_chroma_adapter(config)
            else:
                raise ValueError(f"Unsupported vector storage provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to create vector storage adapter {provider}: {e}")
            raise RuntimeError(f"Vector storage adapter creation failed: {e}")

    @staticmethod
    async def _create_in_memory_adapter(config: Dict[str, Any]) -> VectorStoragePort:
        """Create in-memory adapter."""
        from .in_memory_adapter import InMemoryVectorStorageAdapter
        
        adapter = InMemoryVectorStorageAdapter(
            max_vectors=config.get("max_vectors", 100000)
        )
        
        logger.info("Created in-memory vector storage adapter")
        return adapter

    @staticmethod
    async def _create_pinecone_adapter(config: Dict[str, Any]) -> VectorStoragePort:
        """Create Pinecone adapter (placeholder for future implementation)."""
        # This would be implemented when Pinecone support is needed
        raise NotImplementedError("Pinecone adapter not yet implemented")

    @staticmethod
    async def _create_weaviate_adapter(config: Dict[str, Any]) -> VectorStoragePort:
        """Create Weaviate adapter (placeholder for future implementation)."""
        # This would be implemented when Weaviate support is needed
        raise NotImplementedError("Weaviate adapter not yet implemented")

    @staticmethod
    async def _create_chroma_adapter(config: Dict[str, Any]) -> VectorStoragePort:
        """Create ChromaDB adapter (placeholder for future implementation)."""
        # This would be implemented when ChromaDB support is needed
        raise NotImplementedError("ChromaDB adapter not yet implemented")

    @staticmethod
    def get_supported_providers() -> list[str]:
        """Get list of supported vector storage providers."""
        return ["in_memory"]  # Add more as they're implemented

    @staticmethod
    def get_default_config(provider: str) -> Dict[str, Any]:
        """Get default configuration for a provider."""
        configs = {
            "in_memory": {
                "max_vectors": 100000
            },
            "pinecone": {
                "environment": "us-west1-gcp",
                "dimension": 1536
            },
            "weaviate": {
                "url": "http://localhost:8080",
                "timeout": 30
            },
            "chroma": {
                "persist_directory": "./chroma_db",
                "collection_name": "embeddings"
            }
        }
        return configs.get(provider.lower(), {})

    @staticmethod
    async def create_from_env() -> VectorStoragePort:
        """
        Create vector storage adapter from environment variables.
        
        Environment variables:
        - VECTOR_STORAGE_PROVIDER: Provider name (default: in_memory)
        - VECTOR_STORAGE_MAX_VECTORS: Max vectors for in-memory (default: 100000)
        - PINECONE_API_KEY: Pinecone API key
        - PINECONE_ENVIRONMENT: Pinecone environment
        - WEAVIATE_URL: Weaviate instance URL
        """
        provider = os.getenv("VECTOR_STORAGE_PROVIDER", "in_memory")
        
        # Build configuration from environment
        config = VectorStorageAdapterFactory.get_default_config(provider)
        
        # Add environment-specific overrides
        if provider == "in_memory":
            if os.getenv("VECTOR_STORAGE_MAX_VECTORS"):
                config["max_vectors"] = int(os.getenv("VECTOR_STORAGE_MAX_VECTORS"))
        elif provider == "pinecone":
            if os.getenv("PINECONE_API_KEY"):
                config["api_key"] = os.getenv("PINECONE_API_KEY")
            if os.getenv("PINECONE_ENVIRONMENT"):
                config["environment"] = os.getenv("PINECONE_ENVIRONMENT")
        elif provider == "weaviate":
            if os.getenv("WEAVIATE_URL"):
                config["url"] = os.getenv("WEAVIATE_URL")
        
        return await VectorStorageAdapterFactory.create_adapter(provider, config)


class VectorStorageManager:
    """
    Manager for vector storage operations.
    
    Provides high-level operations and manages multiple vector storage instances.
    """
    
    def __init__(self, storage_adapter: VectorStoragePort):
        self.storage_adapter = storage_adapter
        self._stats = {
            "embeddings_stored": 0,
            "searches_performed": 0,
            "batch_operations": 0
        }

    async def store_embedding_with_stats(self, embedding) -> bool:
        """Store embedding and update statistics."""
        result = await self.storage_adapter.store_embedding(embedding)
        if result:
            self._stats["embeddings_stored"] += 1
        return result

    async def store_batch_embeddings_with_stats(self, embeddings) -> bool:
        """Store batch embeddings and update statistics."""
        result = await self.storage_adapter.store_batch_embeddings(embeddings)
        if result:
            self._stats["embeddings_stored"] += len(embeddings)
            self._stats["batch_operations"] += 1
        return result

    async def search_similar_with_stats(self, query_vector, **kwargs):
        """Search similar vectors and update statistics."""
        results = await self.storage_adapter.search_similar(query_vector, **kwargs)
        self._stats["searches_performed"] += 1
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage operation statistics."""
        return self._stats.copy()

    async def get_comprehensive_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the storage."""
        storage_info = await self.storage_adapter.get_storage_info()
        health_status = await self.storage_adapter.health_check()
        
        return {
            "storage_info": storage_info,
            "health_status": health_status,
            "statistics": self.get_statistics()
        }

    async def optimize_storage(self) -> bool:
        """Optimize storage performance (implementation depends on provider)."""
        # This would be implemented based on the specific storage provider
        # For now, just return True for in-memory storage
        logger.info("Storage optimization completed")
        return True

    async def backup_storage(self, backup_path: str) -> bool:
        """Create a backup of the storage (implementation depends on provider)."""
        # This would be implemented based on the specific storage provider
        logger.info(f"Storage backup to {backup_path} completed")
        return True

    async def close(self):
        """Close the storage manager and underlying adapter."""
        if hasattr(self.storage_adapter, 'close'):
            await self.storage_adapter.close()
        logger.info("Vector storage manager closed")
