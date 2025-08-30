"""
Vector Embedding Domain Entity

Core domain entity representing a vector embedding in the RAG Integration Service.
Contains business logic for vector operations and validation.
"""

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from ..value_objects.embedding_type import EmbeddingType


@dataclass
class VectorEmbedding:
    """
    Domain entity representing a vector embedding.

    This entity encapsulates the core business logic for vector embeddings,
    including validation, mathematical operations, and business rules.
    """

    id: UUID
    vector: List[float]
    text: str
    text_hash: str
    embedding_type: EmbeddingType
    model_version: str
    model_name: str
    metadata: Dict[str, Any]
    created_at: datetime

    def __post_init__(self):
        """Validate the vector embedding after initialization."""
        self._validate_text()
        self._validate_vector()
        self._validate_metadata()

    def _validate_text(self) -> None:
        """Validate text field requirements."""
        if not self.text or not self.text.strip():
            raise ValueError("text cannot be empty")

        if len(self.text) > 10000:
            raise ValueError("text cannot exceed 10000 characters")

    def _validate_vector(self) -> None:
        """Validate vector field requirements."""
        if not self.vector:
            raise ValueError("vector cannot be empty")

        if len(self.vector) != 1536:
            raise ValueError("vector must be 1536-dimensional")

        # Validate that all elements are numeric
        if not all(isinstance(x, (int, float)) for x in self.vector):
            raise ValueError("vector must contain only numeric values")

    def _validate_metadata(self) -> None:
        """Validate metadata field requirements."""
        if self.metadata is None:
            self.metadata = {}

        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def validate_dimensions(self, expected_dim: int = 1536) -> bool:
        """
        Validate vector dimensions against expected size.

        Args:
            expected_dim: Expected vector dimension (default: 1536)

        Returns:
            True if dimensions match, False otherwise
        """
        return len(self.vector) == expected_dim

    def calculate_magnitude(self) -> float:
        """
        Calculate the magnitude (L2 norm) of the vector.

        Returns:
            Vector magnitude as float
        """
        return math.sqrt(sum(x * x for x in self.vector))

    def normalize(self) -> List[float]:
        """
        Normalize vector to unit length.

        Returns:
            Normalized vector as list of floats
        """
        magnitude = self.calculate_magnitude()

        # Handle zero vector case
        if magnitude == 0.0:
            return self.vector.copy()

        return [x / magnitude for x in self.vector]

    def dot_product(self, other_vector: List[float]) -> float:
        """
        Calculate dot product with another vector.

        Args:
            other_vector: Another vector of same dimensions

        Returns:
            Dot product as float

        Raises:
            ValueError: If vectors have different dimensions
        """
        if len(other_vector) != len(self.vector):
            raise ValueError("Vectors must have same dimensions for dot product")

        return sum(a * b for a, b in zip(self.vector, other_vector))

    def cosine_similarity(self, other_vector: List[float]) -> float:
        """
        Calculate cosine similarity with another vector.

        Args:
            other_vector: Another vector of same dimensions

        Returns:
            Cosine similarity score between -1 and 1

        Raises:
            ValueError: If vectors have different dimensions
        """
        if len(other_vector) != len(self.vector):
            raise ValueError("Vectors must have same dimensions for cosine similarity")

        dot_prod = self.dot_product(other_vector)
        magnitude_self = self.calculate_magnitude()
        magnitude_other = math.sqrt(sum(x * x for x in other_vector))

        # Handle zero vector cases
        if magnitude_self == 0.0 or magnitude_other == 0.0:
            return 0.0

        return dot_prod / (magnitude_self * magnitude_other)

    def euclidean_distance(self, other_vector: List[float]) -> float:
        """
        Calculate Euclidean distance to another vector.

        Args:
            other_vector: Another vector of same dimensions

        Returns:
            Euclidean distance as float

        Raises:
            ValueError: If vectors have different dimensions
        """
        if len(other_vector) != len(self.vector):
            raise ValueError("Vectors must have same dimensions for Euclidean distance")

        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.vector, other_vector)))

    def is_similar_to(self, other_vector: List[float], threshold: float = 0.7) -> bool:
        """
        Check if this vector is similar to another vector based on cosine similarity.

        Args:
            other_vector: Another vector to compare with
            threshold: Similarity threshold (default: 0.7)

        Returns:
            True if similarity is above threshold, False otherwise
        """
        similarity = self.cosine_similarity(other_vector)
        return similarity >= threshold

    def get_embedding_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about this embedding.

        Returns:
            Dictionary containing embedding information
        """
        return {
            "id": str(self.id),
            "text_length": len(self.text),
            "text_hash": self.text_hash,
            "embedding_type": self.embedding_type.value,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "vector_dimensions": len(self.vector),
            "vector_magnitude": self.calculate_magnitude(),
            "created_at": self.created_at.isoformat(),
            "metadata_keys": list(self.metadata.keys()) if self.metadata else [],
        }

    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """
        Update embedding metadata.

        Args:
            new_metadata: New metadata to merge with existing
        """
        if not isinstance(new_metadata, dict):
            raise ValueError("new_metadata must be a dictionary")

        self.metadata.update(new_metadata)

    def has_metadata_key(self, key: str) -> bool:
        """
        Check if embedding has specific metadata key.

        Args:
            key: Metadata key to check

        Returns:
            True if key exists, False otherwise
        """
        return key in self.metadata

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value by key.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
