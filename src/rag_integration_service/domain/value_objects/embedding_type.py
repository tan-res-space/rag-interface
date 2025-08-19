"""
Embedding Type Value Object

Defines the types of embeddings that can be generated in the RAG Integration Service.
This value object ensures type safety and provides clear semantics for different embedding purposes.
"""

from enum import Enum


class EmbeddingType(str, Enum):
    """
    Enumeration of embedding types for different text processing purposes.
    
    Each type represents a specific use case in the ASR error reporting system:
    - ERROR: Embeddings for original error text
    - CORRECTION: Embeddings for corrected text
    - CONTEXT: Embeddings for contextual information
    """
    
    ERROR = "error"
    CORRECTION = "correction"
    CONTEXT = "context"
    
    def __str__(self) -> str:
        """Return string representation of the embedding type."""
        return self.value
    
    def is_error_type(self) -> bool:
        """Check if this is an error embedding type."""
        return self == EmbeddingType.ERROR
    
    def is_correction_type(self) -> bool:
        """Check if this is a correction embedding type."""
        return self == EmbeddingType.CORRECTION
    
    def is_context_type(self) -> bool:
        """Check if this is a context embedding type."""
        return self == EmbeddingType.CONTEXT
    
    @classmethod
    def from_string(cls, value: str) -> "EmbeddingType":
        """
        Create EmbeddingType from string value.
        
        Args:
            value: String representation of embedding type
            
        Returns:
            EmbeddingType instance
            
        Raises:
            ValueError: If value is not a valid embedding type
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_types = [e.value for e in cls]
            raise ValueError(f"Invalid embedding type '{value}'. Valid types: {valid_types}")
    
    def get_description(self) -> str:
        """
        Get human-readable description of the embedding type.
        
        Returns:
            Description string
        """
        descriptions = {
            EmbeddingType.ERROR: "Original error text embedding for pattern recognition",
            EmbeddingType.CORRECTION: "Corrected text embedding for learning improvements",
            EmbeddingType.CONTEXT: "Contextual information embedding for enhanced analysis"
        }
        return descriptions[self]
