"""
In-Memory Vector Storage Adapter

In-memory implementation of the VectorStoragePort for development and testing.
Provides fast vector operations without external dependencies.
"""

import asyncio
import logging
import math
from typing import Any, Dict, List, Optional
from uuid import UUID

from rag_integration_service.application.ports.secondary.vector_storage_port import VectorStoragePort
from rag_integration_service.domain.entities.similarity_result import SimilarityResult
from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding

logger = logging.getLogger(__name__)


class InMemoryVectorStorageAdapter(VectorStoragePort):
    """
    In-memory vector storage adapter.
    
    Stores vectors in memory with efficient similarity search using cosine similarity.
    Suitable for development, testing, and small-scale deployments.
    """

    def __init__(self, max_vectors: int = 100000):
        """
        Initialize the in-memory vector storage.
        
        Args:
            max_vectors: Maximum number of vectors to store
        """
        self.max_vectors = max_vectors
        self._vectors: Dict[str, VectorEmbedding] = {}
        self._metadata_index: Dict[str, List[str]] = {}  # metadata_key -> list of vector_ids
        self._lock = asyncio.Lock()

    async def store_embedding(self, embedding: VectorEmbedding) -> bool:
        """Store a vector embedding."""
        async with self._lock:
            try:
                if len(self._vectors) >= self.max_vectors:
                    logger.warning(f"Vector storage at capacity ({self.max_vectors})")
                    return False
                
                vector_id = str(embedding.id)
                self._vectors[vector_id] = embedding
                
                # Update metadata index
                await self._update_metadata_index(vector_id, embedding.metadata)
                
                logger.debug(f"Stored embedding: {vector_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to store embedding {embedding.id}: {e}")
                return False

    async def store_batch_embeddings(self, embeddings: List[VectorEmbedding]) -> bool:
        """Store multiple vector embeddings in batch."""
        async with self._lock:
            try:
                if len(self._vectors) + len(embeddings) > self.max_vectors:
                    logger.warning(f"Batch would exceed capacity ({self.max_vectors})")
                    return False
                
                for embedding in embeddings:
                    vector_id = str(embedding.id)
                    self._vectors[vector_id] = embedding
                    await self._update_metadata_index(vector_id, embedding.metadata)
                
                logger.info(f"Stored {len(embeddings)} embeddings in batch")
                return True
                
            except Exception as e:
                logger.error(f"Failed to store batch embeddings: {e}")
                return False

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SimilarityResult]:
        """Search for similar vectors using cosine similarity."""
        async with self._lock:
            try:
                candidates = await self._filter_by_metadata(metadata_filter)
                
                # Calculate similarities
                similarities = []
                for vector_id in candidates:
                    embedding = self._vectors[vector_id]
                    similarity = self._cosine_similarity(query_vector, embedding.vector)
                    
                    if similarity >= threshold:
                        similarities.append((similarity, embedding))
                
                # Sort by similarity (descending) and limit results
                similarities.sort(key=lambda x: x[0], reverse=True)
                similarities = similarities[:limit]
                
                # Convert to SimilarityResult objects
                results = []
                for similarity, embedding in similarities:
                    result = SimilarityResult(
                        id=embedding.id,
                        similarity_score=similarity,
                        metadata=embedding.metadata,
                        vector=embedding.vector
                    )
                    results.append(result)
                
                logger.debug(f"Found {len(results)} similar vectors")
                return results
                
            except Exception as e:
                logger.error(f"Failed to search similar vectors: {e}")
                return []

    async def get_embedding(self, embedding_id: UUID) -> Optional[VectorEmbedding]:
        """Retrieve a specific embedding by ID."""
        async with self._lock:
            vector_id = str(embedding_id)
            return self._vectors.get(vector_id)

    async def delete_embedding(self, embedding_id: UUID) -> bool:
        """Delete an embedding by ID."""
        async with self._lock:
            try:
                vector_id = str(embedding_id)
                if vector_id not in self._vectors:
                    return False
                
                embedding = self._vectors[vector_id]
                del self._vectors[vector_id]
                
                # Update metadata index
                await self._remove_from_metadata_index(vector_id, embedding.metadata)
                
                logger.debug(f"Deleted embedding: {vector_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete embedding {embedding_id}: {e}")
                return False

    async def update_embedding(self, embedding: VectorEmbedding) -> bool:
        """Update an existing embedding."""
        async with self._lock:
            try:
                vector_id = str(embedding.id)
                if vector_id not in self._vectors:
                    return False
                
                old_embedding = self._vectors[vector_id]
                
                # Update metadata index
                await self._remove_from_metadata_index(vector_id, old_embedding.metadata)
                await self._update_metadata_index(vector_id, embedding.metadata)
                
                # Update the embedding
                self._vectors[vector_id] = embedding
                
                logger.debug(f"Updated embedding: {vector_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update embedding {embedding.id}: {e}")
                return False

    async def count_embeddings(self, metadata_filter: Optional[Dict[str, Any]] = None) -> int:
        """Count embeddings, optionally filtered by metadata."""
        async with self._lock:
            if metadata_filter is None:
                return len(self._vectors)
            
            candidates = await self._filter_by_metadata(metadata_filter)
            return len(candidates)

    async def list_embeddings(
        self,
        offset: int = 0,
        limit: int = 100,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[VectorEmbedding]:
        """List embeddings with pagination and optional filtering."""
        async with self._lock:
            candidates = await self._filter_by_metadata(metadata_filter)
            
            # Apply pagination
            paginated_ids = candidates[offset:offset + limit]
            
            return [self._vectors[vector_id] for vector_id in paginated_ids]

    async def health_check(self) -> bool:
        """Check if the vector storage is healthy."""
        try:
            # Simple health check - verify we can access the storage
            count = len(self._vectors)
            logger.debug(f"Vector storage health check: {count} vectors stored")
            return True
        except Exception as e:
            logger.error(f"Vector storage health check failed: {e}")
            return False

    async def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the storage."""
        async with self._lock:
            return {
                "type": "in_memory",
                "vector_count": len(self._vectors),
                "max_vectors": self.max_vectors,
                "capacity_used": len(self._vectors) / self.max_vectors,
                "metadata_indices": len(self._metadata_index)
            }

    async def clear_storage(self) -> bool:
        """Clear all stored vectors."""
        async with self._lock:
            try:
                self._vectors.clear()
                self._metadata_index.clear()
                logger.info("Cleared all vectors from storage")
                return True
            except Exception as e:
                logger.error(f"Failed to clear storage: {e}")
                return False

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    async def _filter_by_metadata(self, metadata_filter: Optional[Dict[str, Any]]) -> List[str]:
        """Filter vector IDs by metadata criteria."""
        if metadata_filter is None:
            return list(self._vectors.keys())
        
        candidates = set(self._vectors.keys())
        
        for key, value in metadata_filter.items():
            if key in self._metadata_index:
                # Get vectors that have this metadata key-value pair
                matching_vectors = set()
                for vector_id in self._metadata_index[key]:
                    if vector_id in self._vectors:
                        embedding = self._vectors[vector_id]
                        if embedding.metadata.get(key) == value:
                            matching_vectors.add(vector_id)
                
                candidates &= matching_vectors
            else:
                # No vectors have this metadata key
                candidates = set()
                break
        
        return list(candidates)

    async def _update_metadata_index(self, vector_id: str, metadata: Dict[str, Any]):
        """Update the metadata index for a vector."""
        for key in metadata.keys():
            if key not in self._metadata_index:
                self._metadata_index[key] = []
            
            if vector_id not in self._metadata_index[key]:
                self._metadata_index[key].append(vector_id)

    async def _remove_from_metadata_index(self, vector_id: str, metadata: Dict[str, Any]):
        """Remove a vector from the metadata index."""
        for key in metadata.keys():
            if key in self._metadata_index:
                if vector_id in self._metadata_index[key]:
                    self._metadata_index[key].remove(vector_id)
                
                # Clean up empty indices
                if not self._metadata_index[key]:
                    del self._metadata_index[key]

    async def find_embedding(self, embedding_id: UUID) -> Optional[VectorEmbedding]:
        """Find a vector embedding by ID."""
        return await self.get_embedding(embedding_id)

    async def find_similar(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """Find similar vectors using cosine similarity."""
        return await self.search_similar(query_vector, top_k, threshold, filters)

    async def find_similar_by_text(
        self,
        query_text: str,
        embedding_type: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """Find similar vectors by generating embedding for query text."""
        # For in-memory implementation, we'll generate a mock embedding
        # In a real implementation, this would use an ML model
        mock_vector = self._generate_deterministic_embedding(query_text)
        return await self.find_similar(mock_vector, top_k, filters, threshold)

    async def find_by_speaker(
        self,
        speaker_id: str,
        query_vector: List[float],
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """Find similar vectors for a specific speaker."""
        filters = {"speaker_id": speaker_id}
        return await self.find_similar(query_vector, top_k, filters, threshold)

    async def find_by_job(
        self,
        job_id: str,
        query_vector: List[float],
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """Find similar vectors for a specific job."""
        filters = {"job_id": job_id}
        return await self.find_similar(query_vector, top_k, filters, threshold)

    async def find_by_category(
        self,
        category: str,
        query_vector: List[float],
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """Find similar vectors for a specific category."""
        filters = {"category": category}
        return await self.find_similar(query_vector, top_k, filters, threshold)

    async def delete_embeddings_by_job(self, job_id: str) -> int:
        """Delete all embeddings for a specific job."""
        async with self._lock:
            try:
                deleted_count = 0
                to_delete = []

                for vector_id, embedding in self._vectors.items():
                    if embedding.metadata.get("job_id") == job_id:
                        to_delete.append(vector_id)

                for vector_id in to_delete:
                    embedding = self._vectors[vector_id]
                    del self._vectors[vector_id]
                    await self._remove_from_metadata_index(vector_id, embedding.metadata)
                    deleted_count += 1

                logger.debug(f"Deleted {deleted_count} embeddings for job: {job_id}")
                return deleted_count

            except Exception as e:
                logger.error(f"Failed to delete embeddings for job {job_id}: {e}")
                return 0

    async def get_embedding_count(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Get count of embeddings matching filters."""
        return await self.count_embeddings(filters)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        return await self.get_storage_info()

    async def create_index(self, index_config: Dict[str, Any]) -> bool:
        """Create or update vector index configuration."""
        # For in-memory implementation, this is a no-op
        logger.debug(f"Index creation requested: {index_config}")
        return True

    def _generate_deterministic_embedding(self, text: str) -> List[float]:
        """Generate a deterministic embedding based on text content."""
        import hashlib
        import random

        # Create hash of the text
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

        # Use hash to seed random number generator
        local_random = random.Random(text_hash)

        # Generate embedding with normal distribution
        embedding = []
        for i in range(1536):  # Default dimension
            # Generate values with mean 0 and std 0.1 for realistic embeddings
            value = local_random.gauss(0, 0.1)
            embedding.append(value)

        # Normalize the embedding to unit length (common practice)
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    async def close(self):
        """Close the storage and free resources."""
        async with self._lock:
            self._vectors.clear()
            self._metadata_index.clear()
            logger.info("In-memory vector storage closed")
