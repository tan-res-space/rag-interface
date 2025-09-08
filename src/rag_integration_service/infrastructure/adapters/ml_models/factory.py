"""
ML Model Adapter Factory

Factory for creating ML model adapters based on configuration.
Supports multiple providers and model types.
"""

import logging
import os
from typing import Any, Dict, Optional

from rag_integration_service.application.ports.secondary.ml_model_port import MLModelPort

logger = logging.getLogger(__name__)


class MLModelAdapterFactory:
    """Factory for creating ML model adapters."""

    @staticmethod
    async def create_adapter(
        provider: str,
        model_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> MLModelPort:
        """
        Create an ML model adapter based on provider and configuration.
        
        Args:
            provider: ML provider name (openai, mock, huggingface, etc.)
            model_name: Name of the model to use
            config: Additional configuration parameters
            
        Returns:
            ML model adapter instance
            
        Raises:
            ValueError: If provider is not supported
            RuntimeError: If adapter creation fails
        """
        config = config or {}
        provider = provider.lower()
        
        logger.info(f"Creating ML model adapter: {provider}/{model_name}")
        
        try:
            if provider == "openai":
                return await MLModelAdapterFactory._create_openai_adapter(model_name, config)
            elif provider == "mock":
                return await MLModelAdapterFactory._create_mock_adapter(model_name, config)
            elif provider == "huggingface":
                return await MLModelAdapterFactory._create_huggingface_adapter(model_name, config)
            else:
                raise ValueError(f"Unsupported ML provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to create ML adapter {provider}/{model_name}: {e}")
            raise RuntimeError(f"ML adapter creation failed: {e}")

    @staticmethod
    async def _create_openai_adapter(model_name: str, config: Dict[str, Any]) -> MLModelPort:
        """Create OpenAI adapter."""
        from .openai_adapter import OpenAIEmbeddingAdapter
        
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        adapter = OpenAIEmbeddingAdapter(
            api_key=api_key,
            model_name=model_name,
            max_retries=config.get("max_retries", 3),
            timeout=config.get("timeout", 30)
        )
        
        # Warm up the adapter
        if config.get("warm_up", True):
            await adapter.warm_up()
        
        logger.info(f"Created OpenAI adapter for model: {model_name}")
        return adapter

    @staticmethod
    async def _create_mock_adapter(model_name: str, config: Dict[str, Any]) -> MLModelPort:
        """Create mock adapter."""
        from .mock_adapter import MockEmbeddingAdapter
        
        adapter = MockEmbeddingAdapter(
            model_name=model_name,
            embedding_dimension=config.get("embedding_dimension", 1536),
            max_sequence_length=config.get("max_sequence_length", 8191),
            max_batch_size=config.get("max_batch_size", 100),
            simulate_latency=config.get("simulate_latency", True)
        )
        
        # Warm up the adapter
        if config.get("warm_up", True):
            await adapter.warm_up()
        
        logger.info(f"Created mock adapter for model: {model_name}")
        return adapter

    @staticmethod
    async def _create_huggingface_adapter(model_name: str, config: Dict[str, Any]) -> MLModelPort:
        """Create Hugging Face adapter (placeholder for future implementation)."""
        # This would be implemented when Hugging Face support is needed
        raise NotImplementedError("Hugging Face adapter not yet implemented")

    @staticmethod
    def get_supported_providers() -> list[str]:
        """Get list of supported ML providers."""
        return ["openai", "mock"]

    @staticmethod
    def get_default_config(provider: str) -> Dict[str, Any]:
        """Get default configuration for a provider."""
        configs = {
            "openai": {
                "max_retries": 3,
                "timeout": 30,
                "warm_up": True
            },
            "mock": {
                "embedding_dimension": 1536,
                "max_sequence_length": 8191,
                "max_batch_size": 100,
                "simulate_latency": True,
                "warm_up": True
            }
        }
        return configs.get(provider.lower(), {})

    @staticmethod
    async def create_from_env() -> MLModelPort:
        """
        Create ML model adapter from environment variables.
        
        Environment variables:
        - ML_PROVIDER: Provider name (default: mock)
        - ML_MODEL_NAME: Model name (default: mock-embedding-model)
        - OPENAI_API_KEY: OpenAI API key (for OpenAI provider)
        - ML_EMBEDDING_DIMENSION: Embedding dimension (for mock provider)
        """
        provider = os.getenv("ML_PROVIDER", "mock")
        model_name = os.getenv("ML_MODEL_NAME")
        
        # Set default model names based on provider
        if not model_name:
            if provider == "openai":
                model_name = "text-embedding-3-small"
            else:
                model_name = "mock-embedding-model"
        
        # Build configuration from environment
        config = MLModelAdapterFactory.get_default_config(provider)
        
        # Add environment-specific overrides
        if provider == "openai":
            if os.getenv("OPENAI_API_KEY"):
                config["api_key"] = os.getenv("OPENAI_API_KEY")
        elif provider == "mock":
            if os.getenv("ML_EMBEDDING_DIMENSION"):
                config["embedding_dimension"] = int(os.getenv("ML_EMBEDDING_DIMENSION"))
            if os.getenv("ML_SIMULATE_LATENCY"):
                config["simulate_latency"] = os.getenv("ML_SIMULATE_LATENCY").lower() == "true"
        
        return await MLModelAdapterFactory.create_adapter(provider, model_name, config)


class EmbeddingModelManager:
    """
    Manager for multiple embedding models.
    
    Allows loading and managing different embedding models simultaneously.
    """
    
    def __init__(self):
        self._models: Dict[str, MLModelPort] = {}
        self._default_model: Optional[str] = None

    async def load_model(
        self,
        model_id: str,
        provider: str,
        model_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Load a new embedding model."""
        try:
            adapter = await MLModelAdapterFactory.create_adapter(provider, model_name, config)
            self._models[model_id] = adapter
            
            # Set as default if it's the first model
            if self._default_model is None:
                self._default_model = model_id
            
            logger.info(f"Loaded model {model_id}: {provider}/{model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False

    async def get_model(self, model_id: str) -> MLModelPort:
        """Get a specific model by ID."""
        if model_id not in self._models:
            raise ValueError(f"Model not found: {model_id}")
        return self._models[model_id]

    async def get_default_model(self) -> MLModelPort:
        """Get the default model."""
        if self._default_model is None:
            raise RuntimeError("No default model available")
        return await self.get_model(self._default_model)

    def list_models(self) -> list[str]:
        """List all loaded model IDs."""
        return list(self._models.keys())

    async def unload_model(self, model_id: str) -> bool:
        """Unload a model to free resources."""
        if model_id not in self._models:
            return False
        
        model = self._models[model_id]
        
        # Close the model if it has a close method
        if hasattr(model, 'close'):
            await model.close()
        
        del self._models[model_id]
        
        # Update default if needed
        if self._default_model == model_id:
            self._default_model = next(iter(self._models.keys())) if self._models else None
        
        logger.info(f"Unloaded model: {model_id}")
        return True

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all loaded models."""
        results = {}
        for model_id, model in self._models.items():
            try:
                results[model_id] = await model.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {model_id}: {e}")
                results[model_id] = False
        return results

    async def close_all(self):
        """Close all models and free resources."""
        for model_id in list(self._models.keys()):
            await self.unload_model(model_id)
