"""
Semantic Clustering Adapter

Vector storage adapter with semantic clustering capabilities.
Organizes embeddings into clusters for improved search and organization.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass
from datetime import datetime
import json
import math

from rag_integration_service.application.ports.secondary.vector_storage_port import VectorStoragePort as BaseVectorStorageAdapter
from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding
from rag_integration_service.domain.value_objects.similarity_result import SimilarityResult

logger = logging.getLogger(__name__)


@dataclass
class Cluster:
    """Semantic cluster representation."""
    id: UUID
    centroid: List[float]
    embeddings: Set[UUID]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    quality_score: float = 0.0


class SemanticClusteringAdapter(BaseVectorStorageAdapter):
    """
    Semantic clustering adapter for organized vector storage.
    
    Automatically clusters embeddings based on semantic similarity
    and provides cluster-aware search capabilities.
    """

    def __init__(
        self,
        base_adapter: BaseVectorStorageAdapter,
        max_cluster_size: int = 100,
        min_cluster_size: int = 5,
        similarity_threshold: float = 0.8,
        auto_clustering: bool = True,
        clustering_interval: int = 1000  # Cluster every N embeddings
    ):
        """
        Initialize semantic clustering adapter.
        
        Args:
            base_adapter: Base vector storage adapter
            max_cluster_size: Maximum embeddings per cluster
            min_cluster_size: Minimum embeddings per cluster
            similarity_threshold: Threshold for cluster membership
            auto_clustering: Whether to automatically cluster new embeddings
            clustering_interval: How often to trigger clustering
        """
        self.base_adapter = base_adapter
        self.max_cluster_size = max_cluster_size
        self.min_cluster_size = min_cluster_size
        self.similarity_threshold = similarity_threshold
        self.auto_clustering = auto_clustering
        self.clustering_interval = clustering_interval
        
        # Cluster storage
        self.clusters: Dict[UUID, Cluster] = {}
        self.embedding_to_cluster: Dict[UUID, UUID] = {}
        self.unclustered_embeddings: Set[UUID] = set()
        
        # Clustering state
        self.embeddings_since_clustering = 0
        self.clustering_in_progress = False
        
        logger.info(f"Initialized clustering adapter with threshold={similarity_threshold}")

    async def store_embedding(self, embedding: VectorEmbedding) -> bool:
        """Store embedding and update clusters."""
        try:
            # Store in base adapter
            success = await self.base_adapter.store_embedding(embedding)
            
            if success:
                # Add to unclustered set
                self.unclustered_embeddings.add(embedding.id)
                self.embeddings_since_clustering += 1
                
                # Trigger clustering if needed
                if (self.auto_clustering and 
                    self.embeddings_since_clustering >= self.clustering_interval and
                    not self.clustering_in_progress):
                    asyncio.create_task(self._auto_cluster())
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store embedding in clustering adapter: {e}")
            return False

    async def store_batch_embeddings(self, embeddings: List[VectorEmbedding]) -> bool:
        """Store batch embeddings and update clusters."""
        try:
            # Store in base adapter
            success = await self.base_adapter.store_batch_embeddings(embeddings)
            
            if success:
                # Add all to unclustered set
                for embedding in embeddings:
                    self.unclustered_embeddings.add(embedding.id)
                
                self.embeddings_since_clustering += len(embeddings)
                
                # Trigger clustering if needed
                if (self.auto_clustering and 
                    self.embeddings_since_clustering >= self.clustering_interval and
                    not self.clustering_in_progress):
                    asyncio.create_task(self._auto_cluster())
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store batch embeddings in clustering adapter: {e}")
            return False

    async def find_similar(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        threshold: float = 0.7,
        use_clusters: bool = True
    ) -> List[SimilarityResult]:
        """
        Find similar vectors using cluster-aware search.
        
        Args:
            query_vector: Query vector
            top_k: Number of results
            filters: Optional filters
            threshold: Similarity threshold
            use_clusters: Whether to use cluster optimization
            
        Returns:
            Similar embeddings
        """
        try:
            if not use_clusters or not self.clusters:
                # Fallback to base adapter
                return await self.base_adapter.find_similar(query_vector, top_k, filters, threshold)
            
            # Find most relevant clusters
            relevant_clusters = await self._find_relevant_clusters(query_vector, top_k)
            
            # Search within relevant clusters
            cluster_results = []
            for cluster_id, cluster_score in relevant_clusters:
                cluster = self.clusters[cluster_id]
                
                # Get embeddings from this cluster
                cluster_embeddings = []
                for embedding_id in cluster.embeddings:
                    embedding = await self.base_adapter.get_embedding(embedding_id)
                    if embedding:
                        cluster_embeddings.append(embedding)
                
                # Search within cluster
                if cluster_embeddings:
                    for embedding in cluster_embeddings:
                        similarity = self._cosine_similarity(query_vector, embedding.vector)
                        if similarity >= threshold:
                            # Apply filters if provided
                            if not filters or self._matches_filters(embedding.metadata, filters):
                                result = SimilarityResult(
                                    embedding_id=embedding.id,
                                    similarity_score=similarity,
                                    embedding=embedding,
                                    metadata=embedding.metadata
                                )
                                cluster_results.append(result)
            
            # Sort and return top-k
            cluster_results.sort(key=lambda x: x.similarity_score, reverse=True)
            return cluster_results[:top_k]
            
        except Exception as e:
            logger.error(f"Cluster-aware search failed: {e}")
            # Fallback to base adapter
            return await self.base_adapter.find_similar(query_vector, top_k, filters, threshold)

    async def _find_relevant_clusters(
        self,
        query_vector: List[float],
        max_clusters: int = 5
    ) -> List[Tuple[UUID, float]]:
        """
        Find clusters most relevant to query vector.
        
        Args:
            query_vector: Query vector
            max_clusters: Maximum clusters to return
            
        Returns:
            List of (cluster_id, similarity_score) tuples
        """
        cluster_scores = []
        
        for cluster_id, cluster in self.clusters.items():
            # Calculate similarity to cluster centroid
            similarity = self._cosine_similarity(query_vector, cluster.centroid)
            cluster_scores.append((cluster_id, similarity))
        
        # Sort by similarity and return top clusters
        cluster_scores.sort(key=lambda x: x[1], reverse=True)
        return cluster_scores[:max_clusters]

    async def _auto_cluster(self):
        """Automatically cluster unclustered embeddings."""
        if self.clustering_in_progress:
            return
        
        try:
            self.clustering_in_progress = True
            logger.info(f"Starting auto-clustering of {len(self.unclustered_embeddings)} embeddings")
            
            # Get unclustered embeddings
            unclustered_list = list(self.unclustered_embeddings)
            embeddings_to_cluster = []
            
            for embedding_id in unclustered_list:
                embedding = await self.base_adapter.get_embedding(embedding_id)
                if embedding:
                    embeddings_to_cluster.append(embedding)
            
            # Perform clustering
            await self._cluster_embeddings(embeddings_to_cluster)
            
            # Clear unclustered set
            self.unclustered_embeddings.clear()
            self.embeddings_since_clustering = 0
            
            logger.info(f"Auto-clustering completed. Total clusters: {len(self.clusters)}")
            
        except Exception as e:
            logger.error(f"Auto-clustering failed: {e}")
        finally:
            self.clustering_in_progress = False

    async def _cluster_embeddings(self, embeddings: List[VectorEmbedding]):
        """
        Cluster embeddings using similarity-based clustering.
        
        Args:
            embeddings: List of embeddings to cluster
        """
        try:
            for embedding in embeddings:
                # Find best cluster for this embedding
                best_cluster_id = await self._find_best_cluster(embedding)
                
                if best_cluster_id:
                    # Add to existing cluster
                    await self._add_to_cluster(embedding, best_cluster_id)
                else:
                    # Create new cluster
                    await self._create_cluster(embedding)
            
            # Optimize clusters (merge small ones, split large ones)
            await self._optimize_clusters()
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")

    async def _find_best_cluster(self, embedding: VectorEmbedding) -> Optional[UUID]:
        """
        Find the best cluster for an embedding.
        
        Args:
            embedding: Embedding to cluster
            
        Returns:
            Best cluster ID or None if no suitable cluster
        """
        best_cluster_id = None
        best_similarity = 0.0
        
        for cluster_id, cluster in self.clusters.items():
            # Check if cluster has space
            if len(cluster.embeddings) >= self.max_cluster_size:
                continue
            
            # Calculate similarity to cluster centroid
            similarity = self._cosine_similarity(embedding.vector, cluster.centroid)
            
            if similarity >= self.similarity_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_cluster_id = cluster_id
        
        return best_cluster_id

    async def _add_to_cluster(self, embedding: VectorEmbedding, cluster_id: UUID):
        """Add embedding to existing cluster."""
        cluster = self.clusters[cluster_id]
        cluster.embeddings.add(embedding.id)
        self.embedding_to_cluster[embedding.id] = cluster_id
        
        # Update cluster centroid
        await self._update_cluster_centroid(cluster_id)
        
        cluster.updated_at = datetime.utcnow()

    async def _create_cluster(self, embedding: VectorEmbedding) -> UUID:
        """Create new cluster with embedding."""
        cluster_id = uuid4()
        
        cluster = Cluster(
            id=cluster_id,
            centroid=embedding.vector.copy(),
            embeddings={embedding.id},
            metadata={
                "created_by": "auto_clustering",
                "embedding_type": embedding.embedding_type.value if embedding.embedding_type else "unknown"
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.clusters[cluster_id] = cluster
        self.embedding_to_cluster[embedding.id] = cluster_id
        
        logger.debug(f"Created new cluster {cluster_id}")
        return cluster_id

    async def _update_cluster_centroid(self, cluster_id: UUID):
        """Update cluster centroid based on member embeddings."""
        cluster = self.clusters[cluster_id]
        
        if not cluster.embeddings:
            return
        
        # Get all embeddings in cluster
        vectors = []
        for embedding_id in cluster.embeddings:
            embedding = await self.base_adapter.get_embedding(embedding_id)
            if embedding:
                vectors.append(embedding.vector)
        
        if not vectors:
            return
        
        # Calculate centroid (mean of all vectors)
        centroid = [0.0] * len(vectors[0])
        for vector in vectors:
            for i, value in enumerate(vector):
                centroid[i] += value
        
        # Average
        for i in range(len(centroid)):
            centroid[i] /= len(vectors)
        
        cluster.centroid = centroid

    async def _optimize_clusters(self):
        """Optimize clusters by merging small ones and splitting large ones."""
        try:
            # Find clusters that are too small
            small_clusters = [
                cluster_id for cluster_id, cluster in self.clusters.items()
                if len(cluster.embeddings) < self.min_cluster_size
            ]
            
            # Merge small clusters
            for cluster_id in small_clusters:
                await self._merge_small_cluster(cluster_id)
            
            # Find clusters that are too large
            large_clusters = [
                cluster_id for cluster_id, cluster in self.clusters.items()
                if len(cluster.embeddings) > self.max_cluster_size
            ]
            
            # Split large clusters
            for cluster_id in large_clusters:
                await self._split_large_cluster(cluster_id)
            
        except Exception as e:
            logger.error(f"Cluster optimization failed: {e}")

    async def _merge_small_cluster(self, small_cluster_id: UUID):
        """Merge a small cluster with the most similar cluster."""
        small_cluster = self.clusters[small_cluster_id]
        
        # Find most similar cluster
        best_target_id = None
        best_similarity = 0.0
        
        for cluster_id, cluster in self.clusters.items():
            if cluster_id == small_cluster_id:
                continue
            
            if len(cluster.embeddings) + len(small_cluster.embeddings) > self.max_cluster_size:
                continue
            
            similarity = self._cosine_similarity(small_cluster.centroid, cluster.centroid)
            if similarity > best_similarity:
                best_similarity = similarity
                best_target_id = cluster_id
        
        # Merge if suitable target found
        if best_target_id and best_similarity >= self.similarity_threshold:
            target_cluster = self.clusters[best_target_id]
            
            # Move embeddings
            for embedding_id in small_cluster.embeddings:
                target_cluster.embeddings.add(embedding_id)
                self.embedding_to_cluster[embedding_id] = best_target_id
            
            # Update centroid
            await self._update_cluster_centroid(best_target_id)
            
            # Remove small cluster
            del self.clusters[small_cluster_id]
            
            logger.debug(f"Merged cluster {small_cluster_id} into {best_target_id}")

    async def _split_large_cluster(self, large_cluster_id: UUID):
        """Split a large cluster into smaller ones."""
        # For simplicity, we'll just create a new cluster with half the embeddings
        large_cluster = self.clusters[large_cluster_id]
        embeddings_list = list(large_cluster.embeddings)
        
        if len(embeddings_list) <= self.max_cluster_size:
            return
        
        # Split embeddings
        split_point = len(embeddings_list) // 2
        new_cluster_embeddings = embeddings_list[split_point:]
        
        # Create new cluster
        new_cluster_id = uuid4()
        new_cluster = Cluster(
            id=new_cluster_id,
            centroid=[0.0] * len(large_cluster.centroid),
            embeddings=set(new_cluster_embeddings),
            metadata=large_cluster.metadata.copy(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Update embedding mappings
        for embedding_id in new_cluster_embeddings:
            large_cluster.embeddings.remove(embedding_id)
            self.embedding_to_cluster[embedding_id] = new_cluster_id
        
        # Update centroids
        await self._update_cluster_centroid(large_cluster_id)
        await self._update_cluster_centroid(new_cluster_id)
        
        self.clusters[new_cluster_id] = new_cluster
        
        logger.debug(f"Split cluster {large_cluster_id} into {new_cluster_id}")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters."""
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    async def get_cluster_info(self, cluster_id: UUID) -> Optional[Dict[str, Any]]:
        """Get information about a specific cluster."""
        if cluster_id not in self.clusters:
            return None
        
        cluster = self.clusters[cluster_id]
        return {
            "id": str(cluster.id),
            "size": len(cluster.embeddings),
            "metadata": cluster.metadata,
            "created_at": cluster.created_at.isoformat(),
            "updated_at": cluster.updated_at.isoformat(),
            "quality_score": cluster.quality_score
        }

    async def get_clustering_stats(self) -> Dict[str, Any]:
        """Get clustering statistics."""
        total_embeddings = sum(len(cluster.embeddings) for cluster in self.clusters.values())
        
        return {
            "total_clusters": len(self.clusters),
            "total_clustered_embeddings": total_embeddings,
            "unclustered_embeddings": len(self.unclustered_embeddings),
            "average_cluster_size": total_embeddings / len(self.clusters) if self.clusters else 0,
            "clustering_threshold": self.similarity_threshold,
            "auto_clustering_enabled": self.auto_clustering
        }

    # Delegate other methods to base adapter
    async def get_embedding(self, embedding_id: UUID) -> Optional[VectorEmbedding]:
        return await self.base_adapter.get_embedding(embedding_id)

    async def delete_embedding(self, embedding_id: UUID) -> bool:
        success = await self.base_adapter.delete_embedding(embedding_id)
        if success:
            # Remove from cluster
            if embedding_id in self.embedding_to_cluster:
                cluster_id = self.embedding_to_cluster[embedding_id]
                if cluster_id in self.clusters:
                    self.clusters[cluster_id].embeddings.discard(embedding_id)
                del self.embedding_to_cluster[embedding_id]
            
            # Remove from unclustered set
            self.unclustered_embeddings.discard(embedding_id)
        
        return success

    async def health_check(self) -> bool:
        return await self.base_adapter.health_check()

    # Implement remaining abstract methods by delegating
    async def find_embedding(self, embedding_id: UUID) -> Optional[VectorEmbedding]:
        return await self.base_adapter.find_embedding(embedding_id)

    async def find_similar_by_text(self, query_text: str, embedding_type: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None, threshold: float = 0.7) -> List[SimilarityResult]:
        return await self.base_adapter.find_similar_by_text(query_text, embedding_type, top_k, filters, threshold)

    async def find_by_speaker(self, speaker_id: str, query_vector: List[float], top_k: int = 10, threshold: float = 0.7) -> List[SimilarityResult]:
        return await self.base_adapter.find_by_speaker(speaker_id, query_vector, top_k, threshold)

    async def find_by_job(self, job_id: str, query_vector: List[float], top_k: int = 10, threshold: float = 0.7) -> List[SimilarityResult]:
        return await self.base_adapter.find_by_job(job_id, query_vector, top_k, threshold)

    async def find_by_category(self, category: str, query_vector: List[float], top_k: int = 10, threshold: float = 0.7) -> List[SimilarityResult]:
        return await self.base_adapter.find_by_category(category, query_vector, top_k, threshold)

    async def delete_embeddings_by_job(self, job_id: str) -> int:
        return await self.base_adapter.delete_embeddings_by_job(job_id)

    async def get_embedding_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        return await self.base_adapter.get_embedding_count(filters)

    async def get_statistics(self) -> Dict[str, Any]:
        base_stats = await self.base_adapter.get_statistics()
        clustering_stats = await self.get_clustering_stats()
        return {**base_stats, "clustering": clustering_stats}

    async def create_index(self, index_config: Dict[str, Any]) -> bool:
        return await self.base_adapter.create_index(index_config)
