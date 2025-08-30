"""
Request DTOs for the RAG Integration Service application layer.

These DTOs define the structure of requests to use cases and API endpoints.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.rag_integration_service.domain.entities.speaker_rag_processing_job import (
    JobType,
)
from src.rag_integration_service.domain.value_objects.embedding_type import (
    EmbeddingType,
)


@dataclass(frozen=True)
class EmbeddingRequest:
    """
    Request DTO for single embedding generation.
    """

    text: str
    embedding_type: EmbeddingType
    metadata: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    requested_by: Optional[str] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.text or not self.text.strip():
            raise ValueError("text cannot be empty")

        if len(self.text) > 10000:
            raise ValueError("text cannot exceed 10000 characters")

        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass(frozen=True)
class BatchEmbeddingRequest:
    """
    Request DTO for batch embedding generation.
    """

    texts: List[str]
    embedding_type: EmbeddingType
    metadata: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    requested_by: Optional[str] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.texts:
            raise ValueError("texts list cannot be empty")

        if len(self.texts) > 100:
            raise ValueError("batch size cannot exceed 100 texts")

        for i, text in enumerate(self.texts):
            if not text or not text.strip():
                raise ValueError(f"text at index {i} cannot be empty")

            if len(text) > 10000:
                raise ValueError(f"text at index {i} cannot exceed 10000 characters")

        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass(frozen=True)
class SimilaritySearchRequest:
    """
    Request DTO for similarity search operations.
    """

    query_text: Optional[str] = None
    query_vector: Optional[List[float]] = None
    embedding_type: Optional[EmbeddingType] = None
    filters: Optional[Dict[str, Any]] = None
    top_k: int = 10
    threshold: float = 0.7
    include_metadata: bool = True
    requested_by: Optional[str] = None

    def __post_init__(self):
        """Validate request parameters."""
        # Either query_text or query_vector must be provided
        if not self.query_text and not self.query_vector:
            raise ValueError("Either query_text or query_vector must be provided")

        if self.query_text and self.query_vector:
            raise ValueError("Cannot provide both query_text and query_vector")

        # Validate query_text if provided
        if self.query_text:
            if not self.query_text.strip():
                raise ValueError("query_text cannot be empty")

            if len(self.query_text) > 10000:
                raise ValueError("query_text cannot exceed 10000 characters")

            if not self.embedding_type:
                raise ValueError("embedding_type is required when using query_text")

        # Validate query_vector if provided
        if self.query_vector:
            if len(self.query_vector) != 1536:
                raise ValueError("query_vector must be 1536-dimensional")

            if not all(isinstance(x, (int, float)) for x in self.query_vector):
                raise ValueError("query_vector must contain only numeric values")

        # Validate other parameters
        if self.top_k <= 0 or self.top_k > 100:
            raise ValueError("top_k must be between 1 and 100")

        if not (0.0 <= self.threshold <= 1.0):
            raise ValueError("threshold must be between 0.0 and 1.0")

        if self.filters is None:
            object.__setattr__(self, "filters", {})


@dataclass(frozen=True)
class SpeakerSimilarityRequest:
    """
    Request DTO for speaker-specific similarity search.
    """

    speaker_id: str
    query_text: Optional[str] = None
    query_vector: Optional[List[float]] = None
    embedding_type: Optional[EmbeddingType] = None
    top_k: int = 10
    threshold: float = 0.7
    include_metadata: bool = True
    requested_by: Optional[str] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.speaker_id or not self.speaker_id.strip():
            raise ValueError("speaker_id cannot be empty")

        # Either query_text or query_vector must be provided
        if not self.query_text and not self.query_vector:
            raise ValueError("Either query_text or query_vector must be provided")

        if self.query_text and self.query_vector:
            raise ValueError("Cannot provide both query_text and query_vector")

        # Validate query_text if provided
        if self.query_text:
            if not self.query_text.strip():
                raise ValueError("query_text cannot be empty")

            if not self.embedding_type:
                raise ValueError("embedding_type is required when using query_text")

        # Validate query_vector if provided
        if self.query_vector and len(self.query_vector) != 1536:
            raise ValueError("query_vector must be 1536-dimensional")

        # Validate other parameters
        if self.top_k <= 0 or self.top_k > 100:
            raise ValueError("top_k must be between 1 and 100")

        if not (0.0 <= self.threshold <= 1.0):
            raise ValueError("threshold must be between 0.0 and 1.0")


@dataclass(frozen=True)
class CategorySimilarityRequest:
    """
    Request DTO for category-specific similarity search.
    """

    category: str
    query_text: Optional[str] = None
    query_vector: Optional[List[float]] = None
    embedding_type: Optional[EmbeddingType] = None
    top_k: int = 10
    threshold: float = 0.7
    include_metadata: bool = True
    requested_by: Optional[str] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.category or not self.category.strip():
            raise ValueError("category cannot be empty")

        # Either query_text or query_vector must be provided
        if not self.query_text and not self.query_vector:
            raise ValueError("Either query_text or query_vector must be provided")

        if self.query_text and self.query_vector:
            raise ValueError("Cannot provide both query_text and query_vector")

        # Validate query_text if provided
        if self.query_text:
            if not self.query_text.strip():
                raise ValueError("query_text cannot be empty")

            if not self.embedding_type:
                raise ValueError("embedding_type is required when using query_text")

        # Validate query_vector if provided
        if self.query_vector and len(self.query_vector) != 1536:
            raise ValueError("query_vector must be 1536-dimensional")

        # Validate other parameters
        if self.top_k <= 0 or self.top_k > 100:
            raise ValueError("top_k must be between 1 and 100")

        if not (0.0 <= self.threshold <= 1.0):
            raise ValueError("threshold must be between 0.0 and 1.0")


@dataclass(frozen=True)
class PatternAnalysisRequest:
    """
    Request DTO for pattern analysis operations.
    """

    filters: Optional[Dict[str, Any]] = None
    time_window_days: int = 30
    min_pattern_frequency: int = 3
    include_quality_metrics: bool = True
    requested_by: Optional[str] = None

    def __post_init__(self):
        """Validate request parameters."""
        if self.time_window_days <= 0 or self.time_window_days > 365:
            raise ValueError("time_window_days must be between 1 and 365")

        if self.min_pattern_frequency <= 0:
            raise ValueError("min_pattern_frequency must be positive")

        if self.filters is None:
            object.__setattr__(self, "filters", {})


@dataclass(frozen=True)
class QualityMetricsRequest:
    """
    Request DTO for quality metrics calculation.
    """

    filters: Optional[Dict[str, Any]] = None
    time_window_days: int = 30
    group_by: Optional[List[str]] = None
    include_trends: bool = True
    requested_by: Optional[str] = None

    def __post_init__(self):
        """Validate request parameters."""
        if self.time_window_days <= 0 or self.time_window_days > 365:
            raise ValueError("time_window_days must be between 1 and 365")

        if self.filters is None:
            object.__setattr__(self, "filters", {})

        if self.group_by is None:
            object.__setattr__(self, "group_by", [])


@dataclass(frozen=True)
class ProcessErrorEventRequest:
    """
    Request DTO for processing error events from other services.
    """

    error_id: str
    job_id: str
    speaker_id: str
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: str
    context_notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.error_id or not self.error_id.strip():
            raise ValueError("error_id cannot be empty")

        if not self.job_id or not self.job_id.strip():
            raise ValueError("job_id cannot be empty")

        if not self.speaker_id or not self.speaker_id.strip():
            raise ValueError("speaker_id cannot be empty")

        if not self.original_text or not self.original_text.strip():
            raise ValueError("original_text cannot be empty")

        if not self.corrected_text or not self.corrected_text.strip():
            raise ValueError("corrected_text cannot be empty")

        if not self.error_categories:
            raise ValueError("error_categories cannot be empty")

        if not self.severity_level or not self.severity_level.strip():
            raise ValueError("severity_level cannot be empty")

        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


# =====================================================
# SPEAKER RAG PROCESSING REQUEST DTOS
# =====================================================


@dataclass(frozen=True)
class HistoricalDataItem:
    """
    Data item representing historical ASR data for processing.
    """

    historical_data_id: str  # UUID as string
    asr_text: str
    final_text: str
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate historical data item."""
        if not self.historical_data_id:
            raise ValueError("historical_data_id cannot be empty")

        if not self.asr_text or not self.asr_text.strip():
            raise ValueError("asr_text cannot be empty")

        if not self.final_text or not self.final_text.strip():
            raise ValueError("final_text cannot be empty")

        if self.asr_text.strip() == self.final_text.strip():
            raise ValueError("asr_text and final_text cannot be identical")


@dataclass(frozen=True)
class ProcessSpeakerHistoricalDataRequest:
    """
    Request DTO for processing speaker historical data to generate error-correction pairs.
    """

    speaker_id: str  # UUID as string
    historical_data_items: List[HistoricalDataItem]
    context_window: int = 50
    min_confidence_threshold: float = 0.3
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.speaker_id:
            raise ValueError("speaker_id cannot be empty")

        if not self.historical_data_items:
            raise ValueError("historical_data_items cannot be empty")

        if len(self.historical_data_items) > 1000:
            raise ValueError(
                "Cannot process more than 1000 historical data items at once"
            )

        if self.context_window < 0 or self.context_window > 200:
            raise ValueError("context_window must be between 0 and 200")

        if self.min_confidence_threshold < 0 or self.min_confidence_threshold > 1:
            raise ValueError("min_confidence_threshold must be between 0 and 1")


@dataclass(frozen=True)
class GenerateErrorCorrectionPairsRequest:
    """
    Request DTO for generating error-correction pairs from single ASR/final text pair.
    """

    speaker_id: str  # UUID as string
    historical_data_id: str  # UUID as string
    asr_text: str
    final_text: str
    context_window: int = 50
    save_pairs: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.speaker_id:
            raise ValueError("speaker_id cannot be empty")

        if not self.historical_data_id:
            raise ValueError("historical_data_id cannot be empty")

        if not self.asr_text or not self.asr_text.strip():
            raise ValueError("asr_text cannot be empty")

        if not self.final_text or not self.final_text.strip():
            raise ValueError("final_text cannot be empty")

        if self.asr_text.strip() == self.final_text.strip():
            raise ValueError("asr_text and final_text cannot be identical")


@dataclass(frozen=True)
class CreateSpeakerRAGJobRequest:
    """
    Request DTO for creating a speaker RAG processing job.
    """

    speaker_id: str  # UUID as string
    job_type: JobType
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.speaker_id:
            raise ValueError("speaker_id cannot be empty")

        if not isinstance(self.job_type, JobType):
            raise ValueError("job_type must be a valid JobType")


@dataclass(frozen=True)
class VectorizeErrorPairsRequest:
    """
    Request DTO for vectorizing error-correction pairs for a speaker.
    """

    speaker_id: str  # UUID as string
    batch_size: int = 100
    min_confidence: float = 0.3
    error_types: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate request parameters."""
        if not self.speaker_id:
            raise ValueError("speaker_id cannot be empty")

        if self.batch_size <= 0 or self.batch_size > 500:
            raise ValueError("batch_size must be between 1 and 500")

        if self.min_confidence < 0 or self.min_confidence > 1:
            raise ValueError("min_confidence must be between 0 and 1")


@dataclass(frozen=True)
class GetSpeakerErrorPatternsRequest:
    """
    Request DTO for getting error patterns analysis for a speaker.
    """

    speaker_id: str  # UUID as string
    error_type_filter: Optional[str] = None
    min_confidence: Optional[float] = None
    include_examples: bool = True
    max_examples_per_type: int = 5

    def __post_init__(self):
        """Validate request parameters."""
        if not self.speaker_id:
            raise ValueError("speaker_id cannot be empty")

        if self.min_confidence is not None and (
            self.min_confidence < 0 or self.min_confidence > 1
        ):
            raise ValueError("min_confidence must be between 0 and 1")

        if self.max_examples_per_type < 0 or self.max_examples_per_type > 20:
            raise ValueError("max_examples_per_type must be between 0 and 20")
