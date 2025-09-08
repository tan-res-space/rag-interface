"""
Mock ML Model Adapter

Mock implementation of the MLModelPort for development and testing.
Provides deterministic embeddings for consistent testing.
"""

import asyncio
import hashlib
import logging
import random
import re
from typing import Any, Dict, List

from rag_integration_service.application.ports.secondary.ml_model_port import MLModelPort
from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType

logger = logging.getLogger(__name__)


class MockEmbeddingAdapter(MLModelPort):
    """
    Mock embedding model adapter for development and testing.
    
    Generates deterministic embeddings based on text content hash.
    Useful for development, testing, and when external ML services are unavailable.
    """

    def __init__(
        self,
        model_name: str = "mock-embedding-model",
        embedding_dimension: int = 1536,
        max_sequence_length: int = 8191,
        max_batch_size: int = 100,
        simulate_latency: bool = True,
    ):
        """
        Initialize the mock adapter.
        
        Args:
            model_name: Name of the mock model
            embedding_dimension: Dimension of generated embeddings
            max_sequence_length: Maximum sequence length in tokens
            max_batch_size: Maximum batch size for processing
            simulate_latency: Whether to simulate API latency
        """
        self.model_name = model_name
        self.embedding_dimension = embedding_dimension
        self.max_sequence_length = max_sequence_length
        self.max_batch_size = max_batch_size
        self.simulate_latency = simulate_latency
        self.model_version = "1.0.0-mock"
        
        # Initialize random seed for deterministic embeddings
        self._random = random.Random(42)

    async def generate_embedding(
        self, text: str, embedding_type: EmbeddingType = EmbeddingType.ERROR
    ) -> List[float]:
        """Generate a deterministic mock embedding for a single text."""
        if not await self.validate_text(text):
            raise ValueError(f"Text validation failed for input: {text[:100]}...")
        
        preprocessed_text = await self.preprocess_text(text)
        
        # Simulate API latency
        if self.simulate_latency:
            await asyncio.sleep(0.1 + self._random.uniform(0, 0.2))
        
        # Generate deterministic embedding based on text hash
        embedding = self._generate_deterministic_embedding(preprocessed_text)
        
        logger.debug(f"Generated mock embedding for text: {text[:50]}...")
        return embedding

    async def generate_batch_embeddings(
        self, texts: List[str], embedding_type: EmbeddingType = EmbeddingType.ERROR
    ) -> List[List[float]]:
        """Generate mock embeddings for multiple texts in batch."""
        if len(texts) > self.get_max_batch_size():
            raise ValueError(f"Batch size {len(texts)} exceeds maximum {self.get_max_batch_size()}")
        
        # Validate all texts first
        for text in texts:
            if not await self.validate_text(text):
                raise ValueError(f"Text validation failed for input: {text[:100]}...")
        
        # Simulate batch processing latency
        if self.simulate_latency:
            batch_latency = 0.05 * len(texts) + self._random.uniform(0, 0.1)
            await asyncio.sleep(min(batch_latency, 2.0))  # Cap at 2 seconds
        
        # Generate embeddings for all texts
        embeddings = []
        for text in texts:
            preprocessed_text = await self.preprocess_text(text)
            embedding = self._generate_deterministic_embedding(preprocessed_text)
            embeddings.append(embedding)
        
        logger.info(f"Generated {len(embeddings)} mock embeddings in batch")
        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.embedding_dimension

    def get_model_name(self) -> str:
        """Get the name of the current model."""
        return self.model_name

    def get_model_version(self) -> str:
        """Get the version of the current model."""
        return self.model_version

    def get_max_sequence_length(self) -> int:
        """Get the maximum sequence length supported by the model."""
        return self.max_sequence_length

    def get_max_batch_size(self) -> int:
        """Get the maximum batch size supported by the model."""
        return self.max_batch_size

    async def preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding generation."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Truncate if too long
        estimated_tokens = await self.estimate_tokens(text)
        if estimated_tokens > self.get_max_sequence_length():
            max_chars = int(self.get_max_sequence_length() * 3.5)
            text = text[:max_chars]
        
        return text

    async def validate_text(self, text: str) -> bool:
        """Validate if text is suitable for embedding generation."""
        if not text or not text.strip():
            return False
        
        if len(text) > 50000:
            return False
        
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            return False
        
        return True

    async def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    async def health_check(self) -> bool:
        """Check if the ML model is healthy and responsive."""
        try:
            test_embedding = await self.generate_embedding("health check test")
            return len(test_embedding) == self.get_embedding_dimension()
        except Exception as e:
            logger.error(f"Mock model health check failed: {e}")
            return False

    async def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the model."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "embedding_dimension": self.embedding_dimension,
            "max_sequence_length": self.max_sequence_length,
            "max_batch_size": self.max_batch_size,
            "provider": "Mock",
            "type": "development",
            "simulate_latency": self.simulate_latency,
            "deterministic": True
        }

    async def warm_up(self) -> bool:
        """Warm up the model for better performance."""
        try:
            # Generate a test embedding
            await self.generate_embedding("warmup test")
            logger.info("Mock model warm-up completed")
            return True
        except Exception as e:
            logger.error(f"Mock model warm-up failed: {e}")
            return False

    def _generate_deterministic_embedding(self, text: str) -> List[float]:
        """
        Generate a deterministic embedding based on text content.
        
        Uses text hash to create reproducible embeddings for testing.
        """
        # Create hash of the text
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        # Use hash to seed random number generator
        local_random = random.Random(text_hash)
        
        # Generate embedding with normal distribution
        embedding = []
        for i in range(self.embedding_dimension):
            # Generate values with mean 0 and std 0.1 for realistic embeddings
            value = local_random.gauss(0, 0.1)
            embedding.append(value)
        
        # Normalize the embedding to unit length (common practice)
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding

    def set_simulate_latency(self, simulate: bool):
        """Enable or disable latency simulation."""
        self.simulate_latency = simulate

    def get_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts based on their mock embeddings.
        Useful for testing similarity search functionality.
        """
        emb1 = self._generate_deterministic_embedding(text1)
        emb2 = self._generate_deterministic_embedding(text2)
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        magnitude1 = sum(x * x for x in emb1) ** 0.5
        magnitude2 = sum(x * x for x in emb2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
