"""
OpenAI ML Model Adapter

Concrete implementation of the MLModelPort using OpenAI's embedding models.
Provides production-ready embedding generation using OpenAI's API.
"""

import asyncio
import logging
import os
import re
from typing import Any, Dict, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from rag_integration_service.application.ports.secondary.ml_model_port import MLModelPort
from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType

logger = logging.getLogger(__name__)


class OpenAIEmbeddingAdapter(MLModelPort):
    """
    OpenAI embedding model adapter.
    
    Implements the MLModelPort interface using OpenAI's embedding API.
    Supports text-embedding-ada-002 and text-embedding-3-small models.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "text-embedding-3-small",
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """
        Initialize the OpenAI adapter.
        
        Args:
            api_key: OpenAI API key
            model_name: Name of the embedding model to use
            max_retries: Maximum number of retries for API calls
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model_name = model_name
        self.max_retries = max_retries
        self.timeout = timeout
        self.base_url = "https://api.openai.com/v1"
        
        # Model specifications
        self._model_specs = {
            "text-embedding-ada-002": {
                "dimension": 1536,
                "max_tokens": 8191,
                "max_batch_size": 2048,
                "version": "v2"
            },
            "text-embedding-3-small": {
                "dimension": 1536,
                "max_tokens": 8191,
                "max_batch_size": 2048,
                "version": "v3"
            },
            "text-embedding-3-large": {
                "dimension": 3072,
                "max_tokens": 8191,
                "max_batch_size": 2048,
                "version": "v3"
            }
        }
        
        if model_name not in self._model_specs:
            raise ValueError(f"Unsupported model: {model_name}")
        
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_embedding(
        self, text: str, embedding_type: EmbeddingType = EmbeddingType.ERROR
    ) -> List[float]:
        """Generate vector embedding for a single text."""
        if not await self.validate_text(text):
            raise ValueError(f"Text validation failed for input: {text[:100]}...")
        
        preprocessed_text = await self.preprocess_text(text)
        
        try:
            response = await self._client.post(
                f"{self.base_url}/embeddings",
                json={
                    "input": preprocessed_text,
                    "model": self.model_name,
                    "encoding_format": "float"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            embedding = data["data"][0]["embedding"]
            
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return embedding
            
        except httpx.HTTPError as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}")

    async def generate_batch_embeddings(
        self, texts: List[str], embedding_type: EmbeddingType = EmbeddingType.ERROR
    ) -> List[List[float]]:
        """Generate vector embeddings for multiple texts in batch."""
        if len(texts) > self.get_max_batch_size():
            raise ValueError(f"Batch size {len(texts)} exceeds maximum {self.get_max_batch_size()}")
        
        # Validate and preprocess all texts
        processed_texts = []
        for text in texts:
            if not await self.validate_text(text):
                raise ValueError(f"Text validation failed for input: {text[:100]}...")
            processed_texts.append(await self.preprocess_text(text))
        
        try:
            response = await self._client.post(
                f"{self.base_url}/embeddings",
                json={
                    "input": processed_texts,
                    "model": self.model_name,
                    "encoding_format": "float"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]
            
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings
            
        except httpx.HTTPError as e:
            logger.error(f"OpenAI API batch error: {e}")
            raise RuntimeError(f"Failed to generate batch embeddings: {e}")

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self._model_specs[self.model_name]["dimension"]

    def get_model_name(self) -> str:
        """Get the name of the current model."""
        return self.model_name

    def get_model_version(self) -> str:
        """Get the version of the current model."""
        return self._model_specs[self.model_name]["version"]

    def get_max_sequence_length(self) -> int:
        """Get the maximum sequence length supported by the model."""
        return self._model_specs[self.model_name]["max_tokens"]

    def get_max_batch_size(self) -> int:
        """Get the maximum batch size supported by the model."""
        return self._model_specs[self.model_name]["max_batch_size"]

    async def preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding generation."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Truncate if too long (rough estimate)
        estimated_tokens = await self.estimate_tokens(text)
        if estimated_tokens > self.get_max_sequence_length():
            # Rough truncation - in production, use proper tokenizer
            max_chars = int(self.get_max_sequence_length() * 3.5)  # ~3.5 chars per token
            text = text[:max_chars]
        
        return text

    async def validate_text(self, text: str) -> bool:
        """Validate if text is suitable for embedding generation."""
        if not text or not text.strip():
            return False
        
        if len(text) > 50000:  # Rough character limit
            return False
        
        # Check for valid UTF-8
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            return False
        
        return True

    async def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the text."""
        # Rough estimation: ~4 characters per token for English text
        # In production, use tiktoken library for accurate counting
        return len(text) // 4

    async def health_check(self) -> bool:
        """Check if the ML model is healthy and responsive."""
        try:
            test_embedding = await self.generate_embedding("health check test")
            return len(test_embedding) == self.get_embedding_dimension()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the model."""
        return {
            "model_name": self.model_name,
            "model_version": self.get_model_version(),
            "embedding_dimension": self.get_embedding_dimension(),
            "max_sequence_length": self.get_max_sequence_length(),
            "max_batch_size": self.get_max_batch_size(),
            "provider": "OpenAI",
            "api_base": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }

    async def warm_up(self) -> bool:
        """Warm up the model for better performance."""
        try:
            # Generate a small test embedding to warm up the connection
            await self.generate_embedding("warmup test")
            logger.info("Model warm-up completed successfully")
            return True
        except Exception as e:
            logger.error(f"Model warm-up failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
