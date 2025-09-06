"""
Process Speaker RAG Data Use Case

Application use case for processing speaker-specific RAG data.
Orchestrates error-correction pair generation, vectorization, and speaker-specific training data preparation.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ...domain.entities.speaker_error_correction_pair import SpeakerErrorCorrectionPair
from ...domain.entities.speaker_rag_processing_job import (
    JobType,
    SpeakerRAGProcessingJob,
)
from ...domain.services.speaker_rag_processing_service import (
    SpeakerRAGProcessingService,
)
from ..dto.requests import (
    CreateSpeakerRAGJobRequest,
    GenerateErrorCorrectionPairsRequest,
    ProcessSpeakerHistoricalDataRequest,
)
from ..dto.responses import (
    ErrorCorrectionPairResponse,
    ProcessingJobResponse,
    SpeakerRAGProcessingResponse,
)
from ..ports.secondary.speaker_rag_repository_port import ISpeakerRAGRepositoryPort
from ..ports.secondary.vector_storage_port import VectorStoragePort


class ProcessSpeakerRAGDataUseCase:
    """
    Use case for processing speaker-specific RAG data.

    This use case orchestrates the complete workflow for processing speaker historical data,
    generating error-correction pairs, and preparing speaker-specific training data.
    """

    def __init__(
        self,
        speaker_rag_repository: ISpeakerRAGRepositoryPort,
        vector_storage: VectorStoragePort,
        rag_processing_service: SpeakerRAGProcessingService,
    ):
        """
        Initialize the use case with required dependencies.

        Args:
            speaker_rag_repository: Repository for speaker RAG data
            vector_storage: Vector storage for embeddings
            rag_processing_service: Domain service for RAG processing
        """
        self._speaker_rag_repo = speaker_rag_repository
        self._vector_storage = vector_storage
        self._rag_service = rag_processing_service

    async def process_speaker_historical_data(
        self, request: ProcessSpeakerHistoricalDataRequest
    ) -> SpeakerRAGProcessingResponse:
        """
        Process historical data for a speaker to generate error-correction pairs.

        Args:
            request: Processing request with speaker data

        Returns:
            Processing response with results
        """
        # Create processing job
        job = SpeakerRAGProcessingJob(
            id=uuid4(),
            speaker_id=request.speaker_id,
            job_type=JobType.HISTORICAL_ANALYSIS,
            total_records=len(request.historical_data_items),
        )

        created_job = await self._speaker_rag_repo.create_processing_job(job)

        try:
            # Start the job
            created_job.start_job()
            await self._speaker_rag_repo.update_processing_job(created_job)

            # Process each historical data item
            all_pairs = []
            processed_count = 0
            error_count = 0

            for data_item in request.historical_data_items:
                try:
                    # Extract error-correction pairs
                    pairs = self._rag_service.extract_error_correction_pairs(
                        asr_text=data_item.asr_text,
                        final_text=data_item.final_text,
                        speaker_id=request.speaker_id,
                        historical_data_id=data_item.historical_data_id,
                        context_window=request.context_window,
                    )

                    # Save pairs to repository
                    if pairs:
                        saved_pairs = await self._speaker_rag_repo.batch_create_error_correction_pairs(
                            pairs
                        )
                        all_pairs.extend(saved_pairs)

                    processed_count += 1

                except Exception as e:
                    error_count += 1
                    created_job.add_metadata(f"error_{error_count}", str(e))

                # Update job progress
                created_job.update_progress(processed_count, error_count)
                await self._speaker_rag_repo.update_processing_job(created_job)

            # Complete the job
            created_job.complete_job()
            await self._speaker_rag_repo.update_processing_job(created_job)

            # Generate statistics
            error_statistics = self._rag_service.calculate_speaker_error_frequency(
                all_pairs
            )

            return SpeakerRAGProcessingResponse(
                job_id=created_job.id,
                speaker_id=request.speaker_id,
                total_pairs_generated=len(all_pairs),
                error_statistics=error_statistics,
                processing_summary=created_job.get_job_summary(),
            )

        except Exception as e:
            # Fail the job
            created_job.fail_job(str(e))
            await self._speaker_rag_repo.update_processing_job(created_job)
            raise

    async def generate_error_correction_pairs(
        self, request: GenerateErrorCorrectionPairsRequest
    ) -> List[ErrorCorrectionPairResponse]:
        """
        Generate error-correction pairs from ASR and final text.

        Args:
            request: Request with text data

        Returns:
            List of generated error-correction pairs
        """
        # Extract pairs using domain service
        pairs = self._rag_service.extract_error_correction_pairs(
            asr_text=request.asr_text,
            final_text=request.final_text,
            speaker_id=request.speaker_id,
            historical_data_id=request.historical_data_id,
            context_window=request.context_window,
        )

        # Save pairs if requested
        if request.save_pairs and pairs:
            saved_pairs = (
                await self._speaker_rag_repo.batch_create_error_correction_pairs(pairs)
            )
            pairs = saved_pairs

        # Convert to response DTOs
        return [self._pair_to_response(pair) for pair in pairs]

    async def vectorize_speaker_error_pairs(
        self, speaker_id: UUID, batch_size: int = 100
    ) -> ProcessingJobResponse:
        """
        Vectorize error-correction pairs for a speaker.

        Args:
            speaker_id: Speaker identifier
            batch_size: Batch size for vectorization

        Returns:
            Processing job response
        """
        # Create vectorization job
        job = SpeakerRAGProcessingJob(
            id=uuid4(), speaker_id=speaker_id, job_type=JobType.VECTORIZATION
        )

        created_job = await self._speaker_rag_repo.create_processing_job(job)

        try:
            # Get error-correction pairs for speaker
            pairs = await self._speaker_rag_repo.get_error_correction_pairs_by_speaker(
                speaker_id=speaker_id,
                min_confidence=0.3,  # Only vectorize high-confidence pairs
            )

            if not pairs:
                created_job.complete_job()
                await self._speaker_rag_repo.update_processing_job(created_job)
                return self._job_to_response(created_job)

            # Set total records and start job
            created_job.set_total_records(len(pairs))
            created_job.start_job()
            await self._speaker_rag_repo.update_processing_job(created_job)

            # Process pairs in batches
            processed_count = 0
            error_count = 0

            for i in range(0, len(pairs), batch_size):
                batch = pairs[i : i + batch_size]

                try:
                    # Vectorize batch
                    await self._vectorize_pair_batch(batch, speaker_id)
                    processed_count += len(batch)

                except Exception as e:
                    error_count += len(batch)
                    created_job.add_metadata(f"batch_error_{i}", str(e))

                # Update progress
                created_job.update_progress(processed_count, error_count)
                await self._speaker_rag_repo.update_processing_job(created_job)

            # Complete job
            created_job.complete_job()
            await self._speaker_rag_repo.update_processing_job(created_job)

            return self._job_to_response(created_job)

        except Exception as e:
            created_job.fail_job(str(e))
            await self._speaker_rag_repo.update_processing_job(created_job)
            raise

    async def get_speaker_error_patterns(self, speaker_id: UUID) -> Dict[str, Any]:
        """
        Get error patterns analysis for a speaker.

        Args:
            speaker_id: Speaker identifier

        Returns:
            Error patterns analysis
        """
        # Get error-correction pairs
        pairs = await self._speaker_rag_repo.get_error_correction_pairs_by_speaker(
            speaker_id
        )

        if not pairs:
            return {
                "speaker_id": str(speaker_id),
                "error_patterns": {},
                "total_pairs": 0,
            }

        # Analyze patterns
        error_statistics = self._rag_service.calculate_speaker_error_frequency(pairs)
        categorized_pairs = self._rag_service.categorize_error_patterns(pairs)

        return {
            "speaker_id": str(speaker_id),
            "total_pairs": len(pairs),
            "error_statistics": error_statistics,
            "error_patterns": {
                error_type: len(type_pairs)
                for error_type, type_pairs in categorized_pairs.items()
            },
            "high_confidence_pairs": len([p for p in pairs if p.is_high_confidence()]),
            "training_suitable_pairs": len(
                [p for p in pairs if p.is_suitable_for_training()]
            ),
        }

    async def create_processing_job(
        self, request: CreateSpeakerRAGJobRequest
    ) -> ProcessingJobResponse:
        """
        Create a new speaker RAG processing job.

        Args:
            request: Job creation request

        Returns:
            Created job response
        """
        job = SpeakerRAGProcessingJob(
            id=uuid4(),
            speaker_id=request.speaker_id,
            job_type=request.job_type,
            job_metadata=request.metadata or {},
        )

        created_job = await self._speaker_rag_repo.create_processing_job(job)
        return self._job_to_response(created_job)

    async def get_processing_job_status(
        self, job_id: UUID
    ) -> Optional[ProcessingJobResponse]:
        """
        Get processing job status.

        Args:
            job_id: Job identifier

        Returns:
            Job response or None if not found
        """
        job = await self._speaker_rag_repo.get_processing_job_by_id(job_id)
        if not job:
            return None

        return self._job_to_response(job)

    async def _vectorize_pair_batch(
        self, pairs: List[SpeakerErrorCorrectionPair], speaker_id: UUID
    ) -> None:
        """
        Vectorize a batch of error-correction pairs.

        Args:
            pairs: List of error-correction pairs
            speaker_id: Speaker identifier
        """
        for pair in pairs:
            # Create training example
            pair.get_training_example()

            # Generate embedding for the input context
            # Note: This would integrate with the existing embedding generation
            # For now, we'll just link the pair to speaker-specific embeddings
            await self._speaker_rag_repo.link_embedding_to_speaker(
                embedding_id=uuid4(),  # Placeholder - would be actual embedding ID
                speaker_id=speaker_id,
                error_correction_pair_id=pair.id,
            )

    def _pair_to_response(
        self, pair: SpeakerErrorCorrectionPair
    ) -> ErrorCorrectionPairResponse:
        """Convert error-correction pair to response DTO."""
        summary = pair.get_pair_summary()

        return ErrorCorrectionPairResponse(
            pair_id=UUID(summary["id"]),
            speaker_id=UUID(summary["speaker_id"]),
            historical_data_id=UUID(summary["historical_data_id"]),
            error_text=summary["error_text"],
            correction_text=summary["correction_text"],
            error_type=summary["error_type"],
            confidence_score=summary["confidence_score"],
            has_context=summary["has_context"],
            suitable_for_training=summary["suitable_for_training"],
            created_at=pair.created_at,
        )

    def _job_to_response(self, job: SpeakerRAGProcessingJob) -> ProcessingJobResponse:
        """Convert processing job to response DTO."""
        summary = job.get_job_summary()

        return ProcessingJobResponse(
            job_id=job.id,
            speaker_id=job.speaker_id,
            job_type=summary["job_type"],
            status=summary["status"],
            progress_percentage=summary["progress_percentage"],
            total_records=summary["total_records"],
            processed_records=summary["processed_records"],
            error_records=summary["error_records"],
            duration_minutes=summary["duration_minutes"],
            error_message=summary["error_message"],
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )
