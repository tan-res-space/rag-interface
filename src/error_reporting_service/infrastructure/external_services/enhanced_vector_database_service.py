"""
Enhanced Vector Database Service

Provides integration with vector database for enhanced similarity search,
error pattern matching, and speaker profiling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VectorDatabaseConfig(BaseModel):
    """Configuration for vector database service"""
    
    host: str = Field(default="localhost", description="Qdrant host")
    port: int = Field(default=6333, description="Qdrant port")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    vector_size: int = Field(default=768, description="Vector embedding size")
    distance_metric: str = Field(default="cosine", description="Distance metric for similarity")


class ErrorEmbedding(BaseModel):
    """Error embedding model"""
    
    error_id: str = Field(..., description="Error report ID")
    speaker_id: str = Field(..., description="Speaker ID")
    client_id: str = Field(..., description="Client ID")
    bucket_type: str = Field(..., description="Quality-based bucket type")
    error_categories: List[str] = Field(..., description="Error categories")
    original_text: str = Field(..., description="Original text with error")
    corrected_text: str = Field(..., description="Corrected text")
    embedding_vector: List[float] = Field(..., description="Text embedding vector")
    
    # Enhanced metadata
    audio_quality: str = Field(..., description="Audio quality assessment")
    speaker_clarity: str = Field(..., description="Speaker clarity assessment")
    background_noise: str = Field(..., description="Background noise level")
    number_of_speakers: str = Field(..., description="Number of speakers")
    overlapping_speech: bool = Field(..., description="Overlapping speech flag")
    requires_specialized_knowledge: bool = Field(..., description="Specialized knowledge flag")
    complexity_score: float = Field(..., description="Error complexity score")
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SimilarityResult(BaseModel):
    """Similarity search result"""
    
    error_id: str = Field(..., description="Error report ID")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    original_text: str = Field(..., description="Original text")
    corrected_text: str = Field(..., description="Corrected text")
    error_categories: List[str] = Field(..., description="Error categories")
    bucket_type: str = Field(..., description="Bucket type")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class EnhancedVectorDatabaseService:
    """Service for enhanced vector database operations"""

    def __init__(self, config: VectorDatabaseConfig):
        self.config = config
        self.client: Optional[QdrantClient] = None
        self.collection_name = "error_embeddings"
        self.speaker_collection_name = "speaker_profiles"

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_client()

    async def _ensure_client(self):
        """Ensure Qdrant client is available"""
        if self.client is None:
            self.client = QdrantClient(
                host=self.config.host,
                port=self.config.port,
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            await self._ensure_collections()

    async def _close_client(self):
        """Close Qdrant client"""
        if self.client:
            self.client.close()
            self.client = None

    async def _ensure_collections(self):
        """Ensure required collections exist"""
        try:
            # Create error embeddings collection
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.config.vector_size,
                        distance=Distance.COSINE if self.config.distance_metric == "cosine" else Distance.EUCLIDEAN
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            
            # Create speaker profiles collection
            if self.speaker_collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.speaker_collection_name,
                    vectors_config=VectorParams(
                        size=self.config.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.speaker_collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to ensure collections: {e}")
            raise

    async def store_error_embedding(self, error_embedding: ErrorEmbedding) -> bool:
        """
        Store error embedding in vector database.
        
        Args:
            error_embedding: Error embedding to store
            
        Returns:
            True if storage was successful
        """
        await self._ensure_client()
        
        try:
            point = PointStruct(
                id=str(uuid4()),
                vector=error_embedding.embedding_vector,
                payload={
                    "error_id": error_embedding.error_id,
                    "speaker_id": error_embedding.speaker_id,
                    "client_id": error_embedding.client_id,
                    "bucket_type": error_embedding.bucket_type,
                    "error_categories": error_embedding.error_categories,
                    "original_text": error_embedding.original_text,
                    "corrected_text": error_embedding.corrected_text,
                    "audio_quality": error_embedding.audio_quality,
                    "speaker_clarity": error_embedding.speaker_clarity,
                    "background_noise": error_embedding.background_noise,
                    "number_of_speakers": error_embedding.number_of_speakers,
                    "overlapping_speech": error_embedding.overlapping_speech,
                    "requires_specialized_knowledge": error_embedding.requires_specialized_knowledge,
                    "complexity_score": error_embedding.complexity_score,
                    "created_at": error_embedding.created_at.isoformat(),
                    "updated_at": error_embedding.updated_at.isoformat(),
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Stored error embedding for error {error_embedding.error_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store error embedding: {e}")
            return False

    async def find_similar_errors(
        self,
        query_vector: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[SimilarityResult]:
        """
        Find similar errors using vector similarity search.
        
        Args:
            query_vector: Query embedding vector
            filters: Optional filters to apply
            limit: Maximum number of results
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of similar errors
        """
        await self._ensure_client()
        
        try:
            # Build filter conditions
            filter_conditions = []
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list values (e.g., error_categories)
                        for v in value:
                            filter_conditions.append(
                                FieldCondition(key=key, match=MatchValue(value=v))
                            )
                    else:
                        filter_conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=value))
                        )
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Perform similarity search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Convert results to SimilarityResult objects
            similar_errors = []
            for result in search_results:
                try:
                    similarity_result = SimilarityResult(
                        error_id=result.payload["error_id"],
                        similarity_score=result.score,
                        original_text=result.payload["original_text"],
                        corrected_text=result.payload["corrected_text"],
                        error_categories=result.payload["error_categories"],
                        bucket_type=result.payload["bucket_type"],
                        metadata={
                            "speaker_id": result.payload["speaker_id"],
                            "client_id": result.payload["client_id"],
                            "audio_quality": result.payload["audio_quality"],
                            "speaker_clarity": result.payload["speaker_clarity"],
                            "background_noise": result.payload["background_noise"],
                            "number_of_speakers": result.payload["number_of_speakers"],
                            "overlapping_speech": result.payload["overlapping_speech"],
                            "requires_specialized_knowledge": result.payload["requires_specialized_knowledge"],
                            "complexity_score": result.payload["complexity_score"],
                        }
                    )
                    similar_errors.append(similarity_result)
                except Exception as e:
                    logger.error(f"Failed to parse similarity result: {e}")
                    continue
            
            logger.info(f"Found {len(similar_errors)} similar errors")
            return similar_errors
            
        except Exception as e:
            logger.error(f"Failed to find similar errors: {e}")
            return []

    async def find_similar_errors_by_text(
        self,
        text: str,
        error_categories: Optional[List[str]] = None,
        bucket_type: Optional[str] = None,
        limit: int = 10
    ) -> List[SimilarityResult]:
        """
        Find similar errors by text (requires text embedding service).
        
        Args:
            text: Text to find similar errors for
            error_categories: Optional error categories filter
            bucket_type: Optional bucket type filter
            limit: Maximum number of results
            
        Returns:
            List of similar errors
        """
        # This would require integration with a text embedding service
        # For now, return empty list as placeholder
        logger.warning("Text embedding service not implemented")
        return []

    async def get_speaker_error_patterns(
        self,
        speaker_id: str,
        limit: int = 50
    ) -> List[SimilarityResult]:
        """
        Get error patterns for a specific speaker.
        
        Args:
            speaker_id: Speaker identifier
            limit: Maximum number of results
            
        Returns:
            List of speaker's error patterns
        """
        await self._ensure_client()
        
        try:
            # Search for errors by speaker
            filter_condition = Filter(
                must=[FieldCondition(key="speaker_id", match=MatchValue(value=speaker_id))]
            )
            
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=limit
            )
            
            # Convert to SimilarityResult objects
            error_patterns = []
            for result in search_results[0]:  # scroll returns (points, next_page_offset)
                try:
                    pattern = SimilarityResult(
                        error_id=result.payload["error_id"],
                        similarity_score=1.0,  # Not applicable for direct retrieval
                        original_text=result.payload["original_text"],
                        corrected_text=result.payload["corrected_text"],
                        error_categories=result.payload["error_categories"],
                        bucket_type=result.payload["bucket_type"],
                        metadata={
                            "speaker_id": result.payload["speaker_id"],
                            "complexity_score": result.payload["complexity_score"],
                            "created_at": result.payload["created_at"],
                        }
                    )
                    error_patterns.append(pattern)
                except Exception as e:
                    logger.error(f"Failed to parse error pattern: {e}")
                    continue
            
            logger.info(f"Retrieved {len(error_patterns)} error patterns for speaker {speaker_id}")
            return error_patterns
            
        except Exception as e:
            logger.error(f"Failed to get speaker error patterns: {e}")
            return []

    async def analyze_error_trends(
        self,
        filters: Optional[Dict[str, Any]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Analyze error trends using vector database data.
        
        Args:
            filters: Optional filters to apply
            time_range: Optional time range for analysis
            
        Returns:
            Dictionary containing trend analysis
        """
        await self._ensure_client()
        
        try:
            # Build filter conditions
            filter_conditions = []
            if filters:
                for key, value in filters.items():
                    filter_conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
            
            if time_range:
                start_time, end_time = time_range
                filter_conditions.extend([
                    FieldCondition(key="created_at", range=models.Range(gte=start_time.isoformat())),
                    FieldCondition(key="created_at", range=models.Range(lte=end_time.isoformat()))
                ])
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Get all matching points
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=10000  # Large limit to get all results
            )
            
            # Analyze trends
            trends = {
                "total_errors": len(search_results[0]),
                "bucket_distribution": {},
                "category_distribution": {},
                "complexity_distribution": {"low": 0, "medium": 0, "high": 0},
                "metadata_patterns": {
                    "audio_quality": {},
                    "speaker_clarity": {},
                    "overlapping_speech_frequency": 0,
                    "specialized_knowledge_frequency": 0,
                }
            }
            
            for point in search_results[0]:
                payload = point.payload
                
                # Bucket distribution
                bucket = payload.get("bucket_type", "unknown")
                trends["bucket_distribution"][bucket] = trends["bucket_distribution"].get(bucket, 0) + 1
                
                # Category distribution
                for category in payload.get("error_categories", []):
                    trends["category_distribution"][category] = trends["category_distribution"].get(category, 0) + 1
                
                # Complexity distribution
                complexity = payload.get("complexity_score", 0)
                if complexity <= 2.0:
                    trends["complexity_distribution"]["low"] += 1
                elif complexity <= 4.0:
                    trends["complexity_distribution"]["medium"] += 1
                else:
                    trends["complexity_distribution"]["high"] += 1
                
                # Metadata patterns
                audio_quality = payload.get("audio_quality", "unknown")
                trends["metadata_patterns"]["audio_quality"][audio_quality] = \
                    trends["metadata_patterns"]["audio_quality"].get(audio_quality, 0) + 1
                
                speaker_clarity = payload.get("speaker_clarity", "unknown")
                trends["metadata_patterns"]["speaker_clarity"][speaker_clarity] = \
                    trends["metadata_patterns"]["speaker_clarity"].get(speaker_clarity, 0) + 1
                
                if payload.get("overlapping_speech", False):
                    trends["metadata_patterns"]["overlapping_speech_frequency"] += 1
                
                if payload.get("requires_specialized_knowledge", False):
                    trends["metadata_patterns"]["specialized_knowledge_frequency"] += 1
            
            # Calculate percentages
            total = trends["total_errors"]
            if total > 0:
                trends["metadata_patterns"]["overlapping_speech_frequency"] = \
                    (trends["metadata_patterns"]["overlapping_speech_frequency"] / total) * 100
                trends["metadata_patterns"]["specialized_knowledge_frequency"] = \
                    (trends["metadata_patterns"]["specialized_knowledge_frequency"] / total) * 100
            
            logger.info(f"Analyzed trends for {total} errors")
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze error trends: {e}")
            return {}

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database collections.
        
        Returns:
            Dictionary containing collection statistics
        """
        await self._ensure_client()
        
        try:
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            
            stats = {
                "collection_name": self.collection_name,
                "total_points": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.name,
                "indexed": collection_info.status == models.CollectionStatus.GREEN,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retrieved collection stats: {stats['total_points']} points")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}

    async def health_check(self) -> bool:
        """
        Check if vector database is healthy.
        
        Returns:
            True if database is healthy
        """
        try:
            await self._ensure_client()
            collections = self.client.get_collections()
            return len(collections.collections) > 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
