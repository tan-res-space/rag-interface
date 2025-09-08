"""
Similarity Result Value Object

Value object representing the result of a similarity search operation.
Contains the embedding, similarity score, and associated metadata.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID

from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding


@dataclass(frozen=True)
class SimilarityResult:
    """
    Similarity search result value object.
    
    Represents a single result from a vector similarity search,
    including the embedding, similarity score, and metadata.
    """
    
    embedding_id: UUID
    similarity_score: float
    embedding: Optional[VectorEmbedding] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate similarity result data."""
        if not isinstance(self.embedding_id, UUID):
            raise ValueError("embedding_id must be a UUID")
        
        if not isinstance(self.similarity_score, (int, float)):
            raise ValueError("similarity_score must be a number")
        
        if self.similarity_score < 0.0 or self.similarity_score > 1.0:
            raise ValueError("similarity_score must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "embedding_id": str(self.embedding_id),
            "similarity_score": self.similarity_score,
        }
        
        if self.embedding:
            result["embedding"] = {
                "id": str(self.embedding.id),
                "text": self.embedding.text,
                "embedding_type": self.embedding.embedding_type.value if self.embedding.embedding_type else None,
                "model_name": self.embedding.model_name,
                "model_version": self.embedding.model_version,
                "created_at": self.embedding.created_at.isoformat() if self.embedding.created_at else None
            }
        
        if self.metadata:
            result["metadata"] = self.metadata
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimilarityResult":
        """Create from dictionary representation."""
        embedding_id = UUID(data["embedding_id"])
        similarity_score = float(data["similarity_score"])
        
        embedding = None
        if "embedding" in data and data["embedding"]:
            # Note: This would need proper VectorEmbedding reconstruction
            # For now, we'll leave it as None and rely on lazy loading
            pass
        
        metadata = data.get("metadata")
        
        return cls(
            embedding_id=embedding_id,
            similarity_score=similarity_score,
            embedding=embedding,
            metadata=metadata
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"SimilarityResult(id={self.embedding_id}, score={self.similarity_score:.3f})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"SimilarityResult("
            f"embedding_id={self.embedding_id}, "
            f"similarity_score={self.similarity_score}, "
            f"has_embedding={self.embedding is not None}, "
            f"has_metadata={self.metadata is not None})"
        )
