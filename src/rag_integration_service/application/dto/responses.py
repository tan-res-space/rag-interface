"""
Response DTOs for the RAG Integration Service application layer.

These DTOs define the structure of responses from use cases and API endpoints.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.rag_integration_service.domain.entities.vector_embedding import VectorEmbedding
from src.rag_integration_service.domain.entities.similarity_result import SimilarityResult


@dataclass(frozen=True)
class EmbeddingResponse:
    """
    Response DTO for single embedding generation.
    """
    
    embedding: VectorEmbedding
    processing_time: float
    model_info: Dict[str, str]
    status: str = "success"
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'model_info') or self.model_info is None:
            object.__setattr__(self, 'model_info', {})


@dataclass(frozen=True)
class BatchEmbeddingResponse:
    """
    Response DTO for batch embedding generation.
    """
    
    embeddings: List[VectorEmbedding]
    processing_time: float
    model_info: Dict[str, str]
    batch_size: int
    success_count: int
    failure_count: int
    failures: List[Dict[str, Any]]
    status: str = "success"
    
    def __post_init__(self):
        """Set default values and validate consistency."""
        if not hasattr(self, 'model_info') or self.model_info is None:
            object.__setattr__(self, 'model_info', {})
        
        if not hasattr(self, 'failures') or self.failures is None:
            object.__setattr__(self, 'failures', [])
        
        # Validate consistency
        if self.success_count + self.failure_count != self.batch_size:
            raise ValueError("success_count + failure_count must equal batch_size")
        
        if len(self.embeddings) != self.success_count:
            raise ValueError("number of embeddings must equal success_count")


@dataclass(frozen=True)
class SimilaritySearchResponse:
    """
    Response DTO for similarity search operations.
    """
    
    results: List[SimilarityResult]
    query_info: Dict[str, Any]
    search_time: float
    total_results: int
    status: str = "success"
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'query_info') or self.query_info is None:
            object.__setattr__(self, 'query_info', {})


@dataclass(frozen=True)
class PatternAnalysisResponse:
    """
    Response DTO for pattern analysis operations.
    """
    
    patterns: List[Dict[str, Any]]
    analysis_summary: Dict[str, Any]
    time_window: Dict[str, str]
    processing_time: float
    status: str = "success"
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'patterns') or self.patterns is None:
            object.__setattr__(self, 'patterns', [])
        
        if not hasattr(self, 'analysis_summary') or self.analysis_summary is None:
            object.__setattr__(self, 'analysis_summary', {})
        
        if not hasattr(self, 'time_window') or self.time_window is None:
            object.__setattr__(self, 'time_window', {})


@dataclass(frozen=True)
class QualityMetricsResponse:
    """
    Response DTO for quality metrics calculation.
    """
    
    metrics: Dict[str, Any]
    trends: Optional[Dict[str, Any]]
    aggregations: Dict[str, Any]
    time_window: Dict[str, str]
    processing_time: float
    status: str = "success"
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'metrics') or self.metrics is None:
            object.__setattr__(self, 'metrics', {})
        
        if not hasattr(self, 'aggregations') or self.aggregations is None:
            object.__setattr__(self, 'aggregations', {})
        
        if not hasattr(self, 'time_window') or self.time_window is None:
            object.__setattr__(self, 'time_window', {})


@dataclass(frozen=True)
class ProcessErrorEventResponse:
    """
    Response DTO for error event processing.
    """
    
    error_id: str
    embeddings_created: List[str]
    patterns_updated: List[str]
    processing_time: float
    status: str = "success"
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'embeddings_created') or self.embeddings_created is None:
            object.__setattr__(self, 'embeddings_created', [])
        
        if not hasattr(self, 'patterns_updated') or self.patterns_updated is None:
            object.__setattr__(self, 'patterns_updated', [])


@dataclass(frozen=True)
class HealthCheckResponse:
    """
    Response DTO for health check operations.
    """
    
    status: str
    version: str
    uptime: int
    dependencies: Dict[str, str]
    model_info: Dict[str, Any]
    vector_db_info: Dict[str, Any]
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'dependencies') or self.dependencies is None:
            object.__setattr__(self, 'dependencies', {})
        
        if not hasattr(self, 'model_info') or self.model_info is None:
            object.__setattr__(self, 'model_info', {})
        
        if not hasattr(self, 'vector_db_info') or self.vector_db_info is None:
            object.__setattr__(self, 'vector_db_info', {})


@dataclass(frozen=True)
class ErrorResponse:
    """
    Response DTO for error cases.
    """
    
    success: bool
    error: Dict[str, Any]
    timestamp: str
    request_id: str
    version: str
    
    def __post_init__(self):
        """Set default values."""
        object.__setattr__(self, 'success', False)
        
        if not hasattr(self, 'timestamp') or not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.utcnow().isoformat())
        
        if not hasattr(self, 'version') or not self.version:
            object.__setattr__(self, 'version', "1.0.0")


@dataclass(frozen=True)
class ValidationErrorResponse:
    """
    Response DTO for validation errors.
    """
    
    success: bool
    error: Dict[str, Any]
    validation_errors: List[Dict[str, str]]
    timestamp: str
    request_id: str
    
    def __post_init__(self):
        """Set default values."""
        object.__setattr__(self, 'success', False)
        
        if not hasattr(self, 'timestamp') or not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.utcnow().isoformat())
        
        if not hasattr(self, 'validation_errors') or self.validation_errors is None:
            object.__setattr__(self, 'validation_errors', [])


@dataclass(frozen=True)
class StatisticsResponse:
    """
    Response DTO for statistics operations.
    """
    
    embedding_statistics: Dict[str, Any]
    vector_db_statistics: Dict[str, Any]
    model_statistics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    timestamp: str
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'embedding_statistics') or self.embedding_statistics is None:
            object.__setattr__(self, 'embedding_statistics', {})
        
        if not hasattr(self, 'vector_db_statistics') or self.vector_db_statistics is None:
            object.__setattr__(self, 'vector_db_statistics', {})
        
        if not hasattr(self, 'model_statistics') or self.model_statistics is None:
            object.__setattr__(self, 'model_statistics', {})
        
        if not hasattr(self, 'performance_metrics') or self.performance_metrics is None:
            object.__setattr__(self, 'performance_metrics', {})
        
        if not hasattr(self, 'timestamp') or not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.utcnow().isoformat())


@dataclass(frozen=True)
class PaginatedResponse:
    """
    Generic response DTO for paginated results.
    """
    
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    
    def __post_init__(self):
        """Calculate total pages."""
        if self.size > 0:
            calculated_pages = (self.total + self.size - 1) // self.size
            object.__setattr__(self, 'pages', calculated_pages)
        else:
            object.__setattr__(self, 'pages', 0)


@dataclass(frozen=True)
class ModelInfoResponse:
    """
    Response DTO for model information.
    """
    
    model_name: str
    model_version: str
    embedding_dimension: int
    max_sequence_length: int
    max_batch_size: int
    is_loaded: bool
    performance_metrics: Dict[str, float]
    
    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, 'performance_metrics') or self.performance_metrics is None:
            object.__setattr__(self, 'performance_metrics', {})
