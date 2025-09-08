"""
Contextual Embedding Adapter

Advanced embedding adapter that considers surrounding context when generating embeddings.
Implements sophisticated contextual understanding for better semantic representation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json

from rag_integration_service.application.ports.secondary.ml_model_port import MLModelPort as BaseEmbeddingAdapter
from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType

logger = logging.getLogger(__name__)


class ContextualEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    Contextual embedding adapter that enhances embeddings with surrounding context.
    
    This adapter analyzes the context around text to generate more accurate embeddings
    that capture semantic relationships and contextual meaning.
    """

    def __init__(
        self,
        base_adapter: BaseEmbeddingAdapter,
        context_window: int = 512,
        context_weight: float = 0.3,
        enable_caching: bool = True
    ):
        """
        Initialize contextual embedding adapter.
        
        Args:
            base_adapter: Base embedding adapter to wrap
            context_window: Size of context window in characters
            context_weight: Weight for context influence (0.0 to 1.0)
            enable_caching: Whether to cache contextual embeddings
        """
        self.base_adapter = base_adapter
        self.context_window = context_window
        self.context_weight = context_weight
        self.enable_caching = enable_caching
        self._cache: Dict[str, List[float]] = {}
        
        logger.info(f"Initialized contextual adapter with window={context_window}, weight={context_weight}")

    async def generate_embedding(
        self,
        text: str,
        embedding_type: EmbeddingType = EmbeddingType.ERROR,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """
        Generate contextual embedding for text.
        
        Args:
            text: Text to generate embedding for
            embedding_type: Type of embedding
            context: Surrounding context text
            metadata: Additional metadata
            
        Returns:
            Contextual embedding vector
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(text, context, embedding_type)
            
            # Check cache
            if self.enable_caching and cache_key in self._cache:
                logger.debug(f"Cache hit for contextual embedding")
                return self._cache[cache_key]
            
            # Generate base embedding
            base_embedding = await self.base_adapter.generate_embedding(text, embedding_type)
            
            # If no context, return base embedding
            if not context:
                if self.enable_caching:
                    self._cache[cache_key] = base_embedding
                return base_embedding
            
            # Generate contextual enhancement
            contextual_embedding = await self._generate_contextual_embedding(
                text, context, embedding_type, base_embedding
            )
            
            # Cache result
            if self.enable_caching:
                self._cache[cache_key] = contextual_embedding
            
            logger.debug(f"Generated contextual embedding for text: {text[:50]}...")
            return contextual_embedding
            
        except Exception as e:
            logger.error(f"Failed to generate contextual embedding: {e}")
            # Fallback to base adapter
            return await self.base_adapter.generate_embedding(text, embedding_type)

    async def generate_batch_embeddings(
        self,
        texts: List[str],
        embedding_type: EmbeddingType = EmbeddingType.ERROR,
        contexts: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[List[float]]:
        """
        Generate contextual embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            embedding_type: Type of embedding
            contexts: List of context texts (optional)
            metadata: List of metadata dictionaries
            
        Returns:
            List of contextual embedding vectors
        """
        try:
            embeddings = []
            
            # Ensure contexts list matches texts length
            if contexts is None:
                contexts = [None] * len(texts)
            elif len(contexts) != len(texts):
                logger.warning("Contexts length doesn't match texts length, padding with None")
                contexts = contexts + [None] * (len(texts) - len(contexts))
            
            # Generate embeddings with context
            for i, text in enumerate(texts):
                context = contexts[i] if i < len(contexts) else None
                embedding = await self.generate_embedding(text, embedding_type, context)
                embeddings.append(embedding)
            
            logger.debug(f"Generated {len(embeddings)} contextual embeddings in batch")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch contextual embeddings: {e}")
            # Fallback to base adapter
            return await self.base_adapter.generate_batch_embeddings(texts, embedding_type)

    async def _generate_contextual_embedding(
        self,
        text: str,
        context: str,
        embedding_type: EmbeddingType,
        base_embedding: List[float]
    ) -> List[float]:
        """
        Generate contextual enhancement for embedding.
        
        Args:
            text: Original text
            context: Context text
            embedding_type: Type of embedding
            base_embedding: Base embedding to enhance
            
        Returns:
            Enhanced contextual embedding
        """
        try:
            # Extract relevant context around the text
            relevant_context = self._extract_relevant_context(text, context)
            
            # Generate context embedding
            context_embedding = await self.base_adapter.generate_embedding(
                relevant_context, embedding_type
            )
            
            # Combine base and context embeddings
            contextual_embedding = self._combine_embeddings(
                base_embedding, context_embedding, self.context_weight
            )
            
            return contextual_embedding
            
        except Exception as e:
            logger.error(f"Failed to generate contextual enhancement: {e}")
            return base_embedding

    def _extract_relevant_context(self, text: str, context: str) -> str:
        """
        Extract relevant context around the target text.
        
        Args:
            text: Target text
            context: Full context
            
        Returns:
            Relevant context substring
        """
        try:
            # Find text position in context
            text_pos = context.lower().find(text.lower())
            
            if text_pos == -1:
                # Text not found in context, use beginning of context
                return context[:self.context_window]
            
            # Calculate context window around text
            start_pos = max(0, text_pos - self.context_window // 2)
            end_pos = min(len(context), text_pos + len(text) + self.context_window // 2)
            
            relevant_context = context[start_pos:end_pos]
            
            # Ensure we don't cut words in half
            if start_pos > 0:
                space_pos = relevant_context.find(' ')
                if space_pos > 0:
                    relevant_context = relevant_context[space_pos + 1:]
            
            if end_pos < len(context):
                space_pos = relevant_context.rfind(' ')
                if space_pos > 0:
                    relevant_context = relevant_context[:space_pos]
            
            return relevant_context
            
        except Exception as e:
            logger.error(f"Failed to extract relevant context: {e}")
            return context[:self.context_window]

    def _combine_embeddings(
        self,
        base_embedding: List[float],
        context_embedding: List[float],
        context_weight: float
    ) -> List[float]:
        """
        Combine base and context embeddings with weighted average.
        
        Args:
            base_embedding: Base embedding vector
            context_embedding: Context embedding vector
            context_weight: Weight for context embedding
            
        Returns:
            Combined embedding vector
        """
        try:
            if len(base_embedding) != len(context_embedding):
                logger.warning("Embedding dimensions don't match, using base embedding")
                return base_embedding
            
            # Weighted combination
            combined = []
            base_weight = 1.0 - context_weight
            
            for i in range(len(base_embedding)):
                combined_value = (
                    base_weight * base_embedding[i] + 
                    context_weight * context_embedding[i]
                )
                combined.append(combined_value)
            
            # Normalize the combined embedding
            magnitude = sum(x * x for x in combined) ** 0.5
            if magnitude > 0:
                combined = [x / magnitude for x in combined]
            
            return combined
            
        except Exception as e:
            logger.error(f"Failed to combine embeddings: {e}")
            return base_embedding

    def _generate_cache_key(
        self,
        text: str,
        context: Optional[str],
        embedding_type: EmbeddingType
    ) -> str:
        """Generate cache key for contextual embedding."""
        key_data = {
            "text": text,
            "context": context,
            "type": embedding_type.value,
            "window": self.context_window,
            "weight": self.context_weight
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    async def get_model_info(self) -> Dict[str, Any]:
        """Get model information including contextual enhancements."""
        base_info = await self.base_adapter.get_model_info()
        
        contextual_info = {
            "adapter_type": "contextual",
            "context_window": self.context_window,
            "context_weight": self.context_weight,
            "caching_enabled": self.enable_caching,
            "cache_size": len(self._cache),
            "base_adapter": base_info
        }
        
        return contextual_info

    async def health_check(self) -> bool:
        """Check health of contextual adapter and base adapter."""
        try:
            base_healthy = await self.base_adapter.health_check()
            return base_healthy
        except Exception as e:
            logger.error(f"Contextual adapter health check failed: {e}")
            return False

    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("Contextual embedding cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_enabled": self.enable_caching,
            "memory_usage_mb": len(str(self._cache)) / (1024 * 1024)
        }

    # Implement abstract methods by delegating to base adapter
    async def get_model_name(self) -> str:
        """Get model name."""
        return await self.base_adapter.get_model_name()

    async def get_model_version(self) -> str:
        """Get model version."""
        return await self.base_adapter.get_model_version()

    async def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return await self.base_adapter.get_embedding_dimension()

    async def get_max_sequence_length(self) -> int:
        """Get maximum sequence length."""
        return await self.base_adapter.get_max_sequence_length()

    async def get_max_batch_size(self) -> int:
        """Get maximum batch size."""
        return await self.base_adapter.get_max_batch_size()

    async def validate_text(self, text: str) -> bool:
        """Validate text input."""
        return await self.base_adapter.validate_text(text)

    async def preprocess_text(self, text: str) -> str:
        """Preprocess text."""
        return await self.base_adapter.preprocess_text(text)

    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count."""
        return await self.base_adapter.estimate_tokens(text)

    async def warm_up(self) -> bool:
        """Warm up the model."""
        return await self.base_adapter.warm_up()
