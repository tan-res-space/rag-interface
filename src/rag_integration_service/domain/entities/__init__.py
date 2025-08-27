"""
Domain Entities

This module contains domain entities that represent core business concepts
in the RAG integration service domain.
"""

from .vector_embedding import VectorEmbedding
from .similarity_result import SimilarityResult
from .speaker_error_correction_pair import SpeakerErrorCorrectionPair
from .speaker_rag_processing_job import SpeakerRAGProcessingJob, JobType, JobStatus

__all__ = [
    "VectorEmbedding",
    "SimilarityResult",
    "SpeakerErrorCorrectionPair",
    "SpeakerRAGProcessingJob",
    "JobType",
    "JobStatus"
]