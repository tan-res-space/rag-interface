"""
ML Model Secondary Port

Secondary port interface for machine learning model operations.
This is a driven port that defines the contract for ML model adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.rag_integration_service.domain.value_objects.embedding_type import (
    EmbeddingType,
)


class MLModelPort(ABC):
    """
    Secondary port for machine learning model operations.

    This port defines the contract that ML model adapters must implement
    to provide embedding generation and model management functionality.
    """

    @abstractmethod
    async def generate_embedding(
        self, text: str, embedding_type: EmbeddingType = EmbeddingType.ERROR
    ) -> List[float]:
        """
        Generate vector embedding for a single text.

        Args:
            text: Input text to generate embedding for
            embedding_type: Type of embedding to generate

        Returns:
            Vector embedding as list of floats

        Raises:
            MLModelError: If embedding generation fails
            TextTooLongError: If text exceeds model limits
        """
        pass

    @abstractmethod
    async def generate_batch_embeddings(
        self, texts: List[str], embedding_type: EmbeddingType = EmbeddingType.ERROR
    ) -> List[List[float]]:
        """
        Generate vector embeddings for multiple texts in batch.

        Args:
            texts: List of input texts
            embedding_type: Type of embeddings to generate

        Returns:
            List of vector embeddings

        Raises:
            MLModelError: If batch generation fails
            BatchSizeExceededError: If batch size exceeds limits
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.

        Returns:
            Embedding dimension (e.g., 1536 for OpenAI ada-002)
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the current model.

        Returns:
            Model name string
        """
        pass

    @abstractmethod
    def get_model_version(self) -> str:
        """
        Get the version of the current model.

        Returns:
            Model version string
        """
        pass

    @abstractmethod
    def get_max_sequence_length(self) -> int:
        """
        Get the maximum sequence length supported by the model.

        Returns:
            Maximum sequence length in tokens
        """
        pass

    @abstractmethod
    def get_max_batch_size(self) -> int:
        """
        Get the maximum batch size supported by the model.

        Returns:
            Maximum batch size
        """
        pass

    @abstractmethod
    async def preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding generation.

        Args:
            text: Raw input text

        Returns:
            Preprocessed text ready for embedding
        """
        pass

    @abstractmethod
    async def validate_text(self, text: str) -> bool:
        """
        Validate if text is suitable for embedding generation.

        Args:
            text: Input text to validate

        Returns:
            True if text is valid, False otherwise
        """
        pass

    @abstractmethod
    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the ML model is healthy and responsive.

        Returns:
            True if model is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the model.

        Returns:
            Dictionary containing model information
        """
        pass

    @abstractmethod
    async def warm_up(self) -> bool:
        """
        Warm up the model for better performance.

        Returns:
            True if warm-up was successful
        """
        pass


class EmbeddingModelManagerPort(ABC):
    """
    Secondary port for managing multiple embedding models.

    This port defines the contract for managing different embedding models
    and switching between them based on requirements.
    """

    @abstractmethod
    async def get_model(self, model_name: str) -> MLModelPort:
        """
        Get a specific embedding model by name.

        Args:
            model_name: Name of the model to retrieve

        Returns:
            ML model port instance

        Raises:
            ModelNotFoundError: If model is not available
        """
        pass

    @abstractmethod
    async def get_default_model(self) -> MLModelPort:
        """
        Get the default embedding model.

        Returns:
            Default ML model port instance
        """
        pass

    @abstractmethod
    async def list_available_models(self) -> List[str]:
        """
        List all available embedding models.

        Returns:
            List of available model names
        """
        pass

    @abstractmethod
    async def load_model(self, model_name: str, config: Dict[str, Any]) -> bool:
        """
        Load a new embedding model.

        Args:
            model_name: Name of the model to load
            config: Model configuration

        Returns:
            True if model was loaded successfully

        Raises:
            ModelLoadError: If model loading fails
        """
        pass

    @abstractmethod
    async def unload_model(self, model_name: str) -> bool:
        """
        Unload an embedding model to free resources.

        Args:
            model_name: Name of the model to unload

        Returns:
            True if model was unloaded successfully
        """
        pass

    @abstractmethod
    async def get_model_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about model usage and performance.

        Returns:
            Dictionary containing model statistics
        """
        pass
