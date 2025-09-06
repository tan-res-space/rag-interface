"""
Generate Embedding Use Case

This use case handles the generation of vector embeddings for text inputs.
It coordinates ML model operations, caching, and vector storage.
"""

import hashlib
import time
from datetime import datetime
from typing import Optional
from uuid import uuid4

from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding

from ..dto.requests import EmbeddingRequest
from ..dto.responses import EmbeddingResponse
from ..ports.secondary.cache_port import CachePort
from ..ports.secondary.ml_model_port import MLModelPort
from ..ports.secondary.vector_storage_port import VectorStoragePort


class GenerateEmbeddingUseCase:
    """
    Use case for generating vector embeddings.

    This use case coordinates the generation of vector embeddings by:
    1. Checking cache for existing embeddings
    2. Generating new embeddings using ML models
    3. Storing embeddings in vector database
    4. Caching results for future use
    """

    def __init__(
        self, ml_model: MLModelPort, vector_storage: VectorStoragePort, cache: CachePort
    ):
        """
        Initialize the use case with required dependencies.

        Args:
            ml_model: ML model port for embedding generation
            vector_storage: Vector storage port for persistence
            cache: Cache port for performance optimization
        """
        self._ml_model = ml_model
        self._vector_storage = vector_storage
        self._cache = cache

    async def execute(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Execute the generate embedding use case.

        Args:
            request: Embedding generation request

        Returns:
            Response containing the generated embedding

        Raises:
            ValueError: If request is invalid
            Exception: If embedding generation fails
        """
        start_time = time.time()

        # 1. Generate text hash for caching and deduplication
        text_hash = self._generate_text_hash(request.text, request.embedding_type)

        # 2. Check cache for existing embedding
        cached_embedding = await self._get_from_cache(text_hash)
        if cached_embedding:
            processing_time = time.time() - start_time
            return self._create_response(cached_embedding, processing_time)

        # 3. Generate new embedding using ML model
        vector = await self._ml_model.generate_embedding(
            request.text, request.embedding_type
        )

        # 4. Create domain entity
        embedding = self._create_embedding_entity(
            vector=vector,
            text=request.text,
            text_hash=text_hash,
            embedding_type=request.embedding_type,
            metadata=request.metadata or {},
            model_version=request.model_version,
        )

        # 5. Store in vector database
        await self._vector_storage.store_embedding(embedding)

        # 6. Cache the result
        await self._cache_embedding(text_hash, embedding)

        # 7. Calculate processing time and return response
        processing_time = time.time() - start_time
        return self._create_response(embedding, processing_time)

    def _generate_text_hash(self, text: str, embedding_type) -> str:
        """
        Generate a hash for the text and embedding type combination.

        Args:
            text: Input text
            embedding_type: Type of embedding

        Returns:
            SHA256 hash string
        """
        content = f"{text}:{embedding_type.value}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def _get_from_cache(self, text_hash: str) -> Optional[VectorEmbedding]:
        """
        Attempt to retrieve embedding from cache.

        Args:
            text_hash: Hash of the text

        Returns:
            VectorEmbedding if found in cache, None otherwise
        """
        try:
            return await self._cache.get_embedding(text_hash)
        except Exception:
            # Cache errors should not break the flow
            return None

    def _create_embedding_entity(
        self,
        vector: list,
        text: str,
        text_hash: str,
        embedding_type,
        metadata: dict,
        model_version: Optional[str],
    ) -> VectorEmbedding:
        """
        Create a VectorEmbedding domain entity.

        Args:
            vector: Generated vector embedding
            text: Original text
            text_hash: Hash of the text
            embedding_type: Type of embedding
            metadata: Additional metadata
            model_version: Model version (optional)

        Returns:
            VectorEmbedding entity
        """
        return VectorEmbedding(
            id=uuid4(),
            vector=vector,
            text=text,
            text_hash=text_hash,
            embedding_type=embedding_type,
            model_version=model_version or self._ml_model.get_model_version(),
            model_name=self._ml_model.get_model_name(),
            metadata=metadata,
            created_at=datetime.utcnow(),
        )

    async def _cache_embedding(
        self, text_hash: str, embedding: VectorEmbedding
    ) -> None:
        """
        Cache the embedding for future retrieval.

        Args:
            text_hash: Hash of the text
            embedding: The embedding to cache
        """
        try:
            # Cache for 1 hour by default
            await self._cache.set_embedding(text_hash, embedding, ttl=3600)
        except Exception:
            # Cache errors should not break the flow
            pass

    def _create_response(
        self, embedding: VectorEmbedding, processing_time: float
    ) -> EmbeddingResponse:
        """
        Create response DTO from embedding entity.

        Args:
            embedding: The embedding entity
            processing_time: Time taken to process the request

        Returns:
            EmbeddingResponse DTO
        """
        model_info = {
            "name": embedding.model_name,
            "version": embedding.model_version,
            "dimensions": len(embedding.vector),
        }

        return EmbeddingResponse(
            embedding=embedding,
            processing_time=processing_time,
            model_info=model_info,
            status="success",
        )
