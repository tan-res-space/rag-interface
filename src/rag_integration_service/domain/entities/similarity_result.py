"""
Similarity Result Domain Entity

Represents the result of a vector similarity search operation.
Contains similarity scoring, ranking, and metadata information.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass
class SimilarityResult:
    """
    Domain entity representing a similarity search result.

    This entity encapsulates similarity scoring, ranking logic,
    and metadata associated with similar vector embeddings.
    """

    embedding_id: UUID
    similarity_score: float
    text: str
    metadata: Dict[str, Any]
    distance_metric: str = "cosine"

    def __post_init__(self):
        """Validate the similarity result after initialization."""
        self._validate_similarity_score()
        self._validate_text()
        self._validate_metadata()

    def _validate_similarity_score(self) -> None:
        """Validate similarity score is within valid range."""
        if not (0.0 <= self.similarity_score <= 1.0):
            raise ValueError("similarity_score must be between 0.0 and 1.0")

    def _validate_text(self) -> None:
        """Validate text field requirements."""
        if not self.text or not self.text.strip():
            raise ValueError("text cannot be empty")

    def _validate_metadata(self) -> None:
        """Validate metadata field requirements."""
        if self.metadata is None:
            self.metadata = {}

        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def is_above_threshold(self, threshold: float) -> bool:
        """
        Check if similarity score is above or equal to threshold.

        Args:
            threshold: Similarity threshold to check against

        Returns:
            True if similarity score >= threshold, False otherwise
        """
        return self.similarity_score >= threshold

    def get_confidence_level(self) -> str:
        """
        Get confidence level based on similarity score.

        Returns:
            Confidence level as string: "high", "medium", or "low"
        """
        if self.similarity_score >= 0.8:
            return "high"
        elif self.similarity_score >= 0.6:
            return "medium"
        else:
            return "low"

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

    def has_metadata_key(self, key: str) -> bool:
        """
        Check if metadata contains specific key.

        Args:
            key: Metadata key to check

        Returns:
            True if key exists, False otherwise
        """
        return key in self.metadata

    def get_speaker_id(self) -> Optional[str]:
        """
        Get speaker ID from metadata.

        Returns:
            Speaker ID if available, None otherwise
        """
        return self.get_metadata_value("speaker_id")

    def get_job_id(self) -> Optional[str]:
        """
        Get job ID from metadata.

        Returns:
            Job ID if available, None otherwise
        """
        return self.get_metadata_value("job_id")

    def get_error_categories(self) -> list:
        """
        Get error categories from metadata.

        Returns:
            List of error categories, empty list if not available
        """
        return self.get_metadata_value("error_categories", [])

    def get_quality_metrics(self) -> Dict[str, float]:
        """
        Get quality metrics from metadata.

        Returns:
            Dictionary of quality metrics, empty dict if not available
        """
        return self.get_metadata_value("quality_metrics", {})

    def is_high_confidence(self) -> bool:
        """
        Check if this is a high confidence result.

        Returns:
            True if confidence level is high, False otherwise
        """
        return self.get_confidence_level() == "high"

    def is_same_speaker(self, speaker_id: str) -> bool:
        """
        Check if result is from the same speaker.

        Args:
            speaker_id: Speaker ID to compare with

        Returns:
            True if same speaker, False otherwise
        """
        return self.get_speaker_id() == speaker_id

    def is_same_job(self, job_id: str) -> bool:
        """
        Check if result is from the same job.

        Args:
            job_id: Job ID to compare with

        Returns:
            True if same job, False otherwise
        """
        return self.get_job_id() == job_id

    def has_error_category(self, category: str) -> bool:
        """
        Check if result has specific error category.

        Args:
            category: Error category to check

        Returns:
            True if category exists, False otherwise
        """
        return category in self.get_error_categories()

    def get_result_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the similarity result.

        Returns:
            Dictionary containing result summary
        """
        return {
            "embedding_id": str(self.embedding_id),
            "similarity_score": self.similarity_score,
            "confidence_level": self.get_confidence_level(),
            "distance_metric": self.distance_metric,
            "text_length": len(self.text),
            "speaker_id": self.get_speaker_id(),
            "job_id": self.get_job_id(),
            "error_categories": self.get_error_categories(),
            "has_quality_metrics": bool(self.get_quality_metrics()),
            "metadata_keys": list(self.metadata.keys()),
        }

    # Comparison methods for sorting and ranking
    def __lt__(self, other: "SimilarityResult") -> bool:
        """Less than comparison based on similarity score."""
        if not isinstance(other, SimilarityResult):
            return NotImplemented
        return self.similarity_score < other.similarity_score

    def __le__(self, other: "SimilarityResult") -> bool:
        """Less than or equal comparison based on similarity score."""
        if not isinstance(other, SimilarityResult):
            return NotImplemented
        return self.similarity_score <= other.similarity_score

    def __gt__(self, other: "SimilarityResult") -> bool:
        """Greater than comparison based on similarity score."""
        if not isinstance(other, SimilarityResult):
            return NotImplemented
        return self.similarity_score > other.similarity_score

    def __ge__(self, other: "SimilarityResult") -> bool:
        """Greater than or equal comparison based on similarity score."""
        if not isinstance(other, SimilarityResult):
            return NotImplemented
        return self.similarity_score >= other.similarity_score

    def __eq__(self, other: "SimilarityResult") -> bool:
        """Equality comparison based on similarity score."""
        if not isinstance(other, SimilarityResult):
            return NotImplemented
        return abs(self.similarity_score - other.similarity_score) < 1e-9

    def __hash__(self) -> int:
        """Hash based on embedding ID for use in sets and dicts."""
        return hash(self.embedding_id)
