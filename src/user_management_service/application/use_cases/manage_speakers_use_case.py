"""
Manage Speakers Use Case

Application use case for speaker management operations.
Orchestrates speaker CRUD operations, bucket management, and statistics.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ...domain.entities.bucket_transition_request import BucketTransitionRequest
from ...domain.entities.historical_asr_data import HistoricalASRData
from ...domain.entities.speaker import Speaker
from ...domain.value_objects.speaker_bucket import SpeakerBucket
from ..dto.requests import (
    ApproveBucketTransitionRequest,
    CreateBucketTransitionRequest,
    CreateHistoricalASRDataRequest,
    CreateSpeakerRequest,
    MarkTestDataRequest,
    RejectBucketTransitionRequest,
    SearchSpeakersRequest,
    UpdateSpeakerRequest,
)
from ..dto.responses import (
    BucketTransitionRequestResponse,
    HistoricalASRDataResponse,
    SpeakerBucketStatsResponse,
    SpeakerListResponse,
    SpeakerResponse,
)
from ..ports.speaker_repository_port import ISpeakerRepositoryPort


class ManageSpeakersUseCase:
    """
    Use case for managing speakers in the bucket management system.

    This use case orchestrates speaker management operations including
    CRUD operations, bucket transitions, and historical data management.
    """

    def __init__(self, speaker_repository: ISpeakerRepositoryPort):
        """
        Initialize the use case with required repositories.

        Args:
            speaker_repository: Repository for speaker data operations
        """
        self._speaker_repo = speaker_repository

    async def create_speaker(self, request: CreateSpeakerRequest) -> SpeakerResponse:
        """
        Create a new speaker.

        Args:
            request: Speaker creation request

        Returns:
            Created speaker response

        Raises:
            ValueError: If speaker already exists or validation fails
        """
        # Check if speaker already exists
        existing_speaker = await self._speaker_repo.get_speaker_by_identifier(
            request.speaker_identifier
        )
        if existing_speaker:
            raise ValueError(
                f"Speaker with identifier '{request.speaker_identifier}' already exists"
            )

        # Create speaker entity
        speaker = Speaker(
            id=uuid4(),
            speaker_identifier=request.speaker_identifier,
            speaker_name=request.speaker_name,
            current_bucket=request.current_bucket,
            metadata=request.metadata or {},
        )

        # Save speaker
        created_speaker = await self._speaker_repo.create_speaker(speaker)

        # Convert to response
        return self._speaker_to_response(created_speaker)

    async def get_speaker_by_id(self, speaker_id: UUID) -> Optional[SpeakerResponse]:
        """
        Get speaker by ID.

        Args:
            speaker_id: Speaker identifier

        Returns:
            Speaker response or None if not found
        """
        speaker = await self._speaker_repo.get_speaker_by_id(speaker_id)
        if not speaker:
            return None

        return self._speaker_to_response(speaker)

    async def get_speaker_by_identifier(
        self, speaker_identifier: str
    ) -> Optional[SpeakerResponse]:
        """
        Get speaker by external identifier.

        Args:
            speaker_identifier: External speaker identifier

        Returns:
            Speaker response or None if not found
        """
        speaker = await self._speaker_repo.get_speaker_by_identifier(speaker_identifier)
        if not speaker:
            return None

        return self._speaker_to_response(speaker)

    async def update_speaker(
        self, speaker_id: UUID, request: UpdateSpeakerRequest
    ) -> SpeakerResponse:
        """
        Update an existing speaker.

        Args:
            speaker_id: Speaker identifier
            request: Speaker update request

        Returns:
            Updated speaker response

        Raises:
            ValueError: If speaker not found
        """
        speaker = await self._speaker_repo.get_speaker_by_id(speaker_id)
        if not speaker:
            raise ValueError(f"Speaker with ID {speaker_id} not found")

        # Update fields if provided
        if request.speaker_name is not None:
            speaker.speaker_name = request.speaker_name

        if request.current_bucket is not None:
            speaker.transition_bucket(request.current_bucket)

        if request.metadata is not None:
            speaker.metadata.update(request.metadata)

        # Save updated speaker
        updated_speaker = await self._speaker_repo.update_speaker(speaker)

        return self._speaker_to_response(updated_speaker)

    async def search_speakers(
        self, request: SearchSpeakersRequest
    ) -> SpeakerListResponse:
        """
        Search speakers with filters and pagination.

        Args:
            request: Search request with filters

        Returns:
            Paginated speaker list response
        """
        # Calculate offset for pagination
        offset = (request.page - 1) * request.page_size

        # Search speakers
        speakers = await self._speaker_repo.search_speakers(
            name_pattern=request.name_pattern,
            bucket=request.bucket,
            min_ser_score=(
                Decimal(str(request.min_ser_score)) if request.min_ser_score else None
            ),
            max_ser_score=(
                Decimal(str(request.max_ser_score)) if request.max_ser_score else None
            ),
            has_sufficient_data=request.has_sufficient_data,
            limit=request.page_size,
            offset=offset,
        )

        # Convert to responses
        speaker_responses = [self._speaker_to_response(speaker) for speaker in speakers]

        # Calculate pagination info (simplified - in real implementation, would need total count)
        total_count = len(speaker_responses)  # This is a simplification
        total_pages = (total_count + request.page_size - 1) // request.page_size

        return SpeakerListResponse(
            speakers=speaker_responses,
            total_count=total_count,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
        )

    async def get_speakers_by_bucket(
        self, bucket: SpeakerBucket
    ) -> List[SpeakerResponse]:
        """
        Get all speakers in a specific bucket.

        Args:
            bucket: Speaker bucket to filter by

        Returns:
            List of speakers in the bucket
        """
        speakers = await self._speaker_repo.get_speakers_by_bucket(bucket)
        return [self._speaker_to_response(speaker) for speaker in speakers]

    async def get_speakers_needing_transition(self) -> List[SpeakerResponse]:
        """
        Get speakers that need bucket transition.

        Returns:
            List of speakers needing transition
        """
        speakers = await self._speaker_repo.get_speakers_needing_transition()
        return [self._speaker_to_response(speaker) for speaker in speakers]

    async def get_bucket_statistics(self) -> SpeakerBucketStatsResponse:
        """
        Get speaker bucket statistics.

        Returns:
            Bucket statistics response
        """
        bucket_counts = await self._speaker_repo.count_speakers_by_bucket()

        # Calculate additional statistics (simplified implementation)
        total_speakers = sum(bucket_counts.values())
        speakers_needing_transition = len(
            await self._speaker_repo.get_speakers_needing_transition()
        )

        # Placeholder for average SER by bucket and quality distribution
        average_ser_by_bucket = {
            "no_touch": 3.2,
            "low_touch": 8.5,
            "medium_touch": 22.1,
            "high_touch": 45.8,
        }

        quality_distribution = {
            "high": bucket_counts.get("no_touch", 0)
            + bucket_counts.get("low_touch", 0),
            "medium": bucket_counts.get("medium_touch", 0),
            "low": bucket_counts.get("high_touch", 0),
        }

        return SpeakerBucketStatsResponse(
            bucket_counts=bucket_counts,
            total_speakers=total_speakers,
            speakers_needing_transition=speakers_needing_transition,
            average_ser_by_bucket=average_ser_by_bucket,
            quality_distribution=quality_distribution,
        )

    async def update_speaker_statistics(self, speaker_id: UUID) -> SpeakerResponse:
        """
        Update speaker statistics from historical data.

        Args:
            speaker_id: Speaker identifier

        Returns:
            Updated speaker response

        Raises:
            ValueError: If speaker not found
        """
        updated_speaker = await self._speaker_repo.update_speaker_statistics(speaker_id)
        return self._speaker_to_response(updated_speaker)

    def _speaker_to_response(self, speaker: Speaker) -> SpeakerResponse:
        """
        Convert speaker entity to response DTO.

        Args:
            speaker: Speaker entity

        Returns:
            Speaker response DTO
        """
        summary = speaker.get_speaker_summary()

        return SpeakerResponse(
            speaker_id=summary["id"],
            speaker_identifier=summary["speaker_identifier"],
            speaker_name=summary["speaker_name"],
            current_bucket=summary["current_bucket"],
            bucket_description=summary["bucket_description"],
            total_notes_count=summary["total_notes_count"],
            processed_notes_count=summary["processed_notes_count"],
            processing_progress=summary["processing_progress"],
            average_ser_score=summary["average_ser_score"],
            recommended_bucket=summary["recommended_bucket"],
            should_transition=summary["should_transition"],
            quality_trend=summary["quality_trend"],
            priority_score=summary["priority_score"],
            has_sufficient_data=summary["has_sufficient_data"],
            last_processed_at=speaker.last_processed_at,
            created_at=speaker.created_at,
            updated_at=speaker.updated_at,
        )
