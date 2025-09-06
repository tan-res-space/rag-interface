"""
Speaker RAG Repository Port

Abstract interface for speaker-specific RAG data persistence operations.
Defines the contract for speaker RAG repository implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from ....domain.entities.speaker_error_correction_pair import SpeakerErrorCorrectionPair
from ....domain.entities.speaker_rag_processing_job import (
    JobStatus,
    JobType,
    SpeakerRAGProcessingJob,
)


class ISpeakerRAGRepositoryPort(ABC):
    """
    Abstract interface for speaker-specific RAG repository operations.

    This port defines the contract for speaker RAG data persistence,
    including error-correction pairs, processing jobs, and speaker-specific embeddings.
    """

    # Error-Correction Pair operations

    @abstractmethod
    async def create_error_correction_pair(
        self, pair: SpeakerErrorCorrectionPair
    ) -> SpeakerErrorCorrectionPair:
        """
        Create a new error-correction pair.

        Args:
            pair: Error-correction pair to create

        Returns:
            Created error-correction pair

        Raises:
            RepositoryError: If creation fails
        """

    @abstractmethod
    async def get_error_correction_pair_by_id(
        self, pair_id: UUID
    ) -> Optional[SpeakerErrorCorrectionPair]:
        """
        Get error-correction pair by ID.

        Args:
            pair_id: Pair identifier

        Returns:
            Error-correction pair or None if not found
        """

    @abstractmethod
    async def get_error_correction_pairs_by_speaker(
        self,
        speaker_id: UUID,
        error_type: Optional[str] = None,
        min_confidence: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> List[SpeakerErrorCorrectionPair]:
        """
        Get error-correction pairs for a speaker.

        Args:
            speaker_id: Speaker identifier
            error_type: Filter by error type
            min_confidence: Minimum confidence threshold
            limit: Maximum number of pairs to return

        Returns:
            List of error-correction pairs
        """

    @abstractmethod
    async def get_error_correction_pairs_by_historical_data(
        self, historical_data_id: UUID
    ) -> List[SpeakerErrorCorrectionPair]:
        """
        Get error-correction pairs for specific historical data.

        Args:
            historical_data_id: Historical data identifier

        Returns:
            List of error-correction pairs
        """

    @abstractmethod
    async def update_error_correction_pair(
        self, pair: SpeakerErrorCorrectionPair
    ) -> SpeakerErrorCorrectionPair:
        """
        Update an error-correction pair.

        Args:
            pair: Error-correction pair to update

        Returns:
            Updated error-correction pair

        Raises:
            ValueError: If pair not found
        """

    @abstractmethod
    async def delete_error_correction_pair(self, pair_id: UUID) -> bool:
        """
        Delete an error-correction pair.

        Args:
            pair_id: Pair identifier

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def batch_create_error_correction_pairs(
        self, pairs: List[SpeakerErrorCorrectionPair]
    ) -> List[SpeakerErrorCorrectionPair]:
        """
        Create multiple error-correction pairs in batch.

        Args:
            pairs: List of error-correction pairs to create

        Returns:
            List of created error-correction pairs
        """

    # Processing Job operations

    @abstractmethod
    async def create_processing_job(
        self, job: SpeakerRAGProcessingJob
    ) -> SpeakerRAGProcessingJob:
        """
        Create a new processing job.

        Args:
            job: Processing job to create

        Returns:
            Created processing job
        """

    @abstractmethod
    async def get_processing_job_by_id(
        self, job_id: UUID
    ) -> Optional[SpeakerRAGProcessingJob]:
        """
        Get processing job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Processing job or None if not found
        """

    @abstractmethod
    async def get_processing_jobs_by_speaker(
        self,
        speaker_id: UUID,
        job_type: Optional[JobType] = None,
        status: Optional[JobStatus] = None,
    ) -> List[SpeakerRAGProcessingJob]:
        """
        Get processing jobs for a speaker.

        Args:
            speaker_id: Speaker identifier
            job_type: Filter by job type
            status: Filter by job status

        Returns:
            List of processing jobs
        """

    @abstractmethod
    async def get_pending_processing_jobs(self) -> List[SpeakerRAGProcessingJob]:
        """
        Get all pending processing jobs.

        Returns:
            List of pending processing jobs
        """

    @abstractmethod
    async def get_running_processing_jobs(self) -> List[SpeakerRAGProcessingJob]:
        """
        Get all running processing jobs.

        Returns:
            List of running processing jobs
        """

    @abstractmethod
    async def update_processing_job(
        self, job: SpeakerRAGProcessingJob
    ) -> SpeakerRAGProcessingJob:
        """
        Update a processing job.

        Args:
            job: Processing job to update

        Returns:
            Updated processing job
        """

    @abstractmethod
    async def delete_processing_job(self, job_id: UUID) -> bool:
        """
        Delete a processing job.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted, False if not found
        """

    # Speaker-specific embedding operations

    @abstractmethod
    async def link_embedding_to_speaker(
        self,
        embedding_id: UUID,
        speaker_id: UUID,
        error_correction_pair_id: Optional[UUID] = None,
    ) -> bool:
        """
        Link an embedding to a speaker and optionally to an error-correction pair.

        Args:
            embedding_id: Embedding identifier
            speaker_id: Speaker identifier
            error_correction_pair_id: Optional error-correction pair identifier

        Returns:
            True if linked successfully
        """

    @abstractmethod
    async def get_speaker_embeddings(
        self, speaker_id: UUID, limit: Optional[int] = None
    ) -> List[UUID]:
        """
        Get embedding IDs for a speaker.

        Args:
            speaker_id: Speaker identifier
            limit: Maximum number of embeddings to return

        Returns:
            List of embedding IDs
        """

    @abstractmethod
    async def get_embeddings_by_error_correction_pair(
        self, pair_id: UUID
    ) -> List[UUID]:
        """
        Get embedding IDs for an error-correction pair.

        Args:
            pair_id: Error-correction pair identifier

        Returns:
            List of embedding IDs
        """

    # Statistics and analytics operations

    @abstractmethod
    async def get_speaker_error_statistics(self, speaker_id: UUID) -> Dict[str, Any]:
        """
        Get error statistics for a speaker.

        Args:
            speaker_id: Speaker identifier

        Returns:
            Dictionary with error statistics
        """

    @abstractmethod
    async def get_error_type_distribution(
        self, speaker_id: Optional[UUID] = None
    ) -> Dict[str, int]:
        """
        Get distribution of error types.

        Args:
            speaker_id: Optional speaker identifier for speaker-specific stats

        Returns:
            Dictionary mapping error types to counts
        """

    @abstractmethod
    async def get_processing_job_statistics(self) -> Dict[str, Any]:
        """
        Get processing job statistics.

        Returns:
            Dictionary with job statistics
        """

    @abstractmethod
    async def cleanup_old_jobs(
        self, older_than_days: int = 30, keep_failed_jobs: bool = True
    ) -> int:
        """
        Clean up old processing jobs.

        Args:
            older_than_days: Delete jobs older than this many days
            keep_failed_jobs: Whether to keep failed jobs for debugging

        Returns:
            Number of jobs deleted
        """
