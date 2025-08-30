"""
Speaker Repository Port

Abstract interface for speaker data persistence operations.
Defines the contract for speaker repository implementations.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from ...domain.entities.bucket_transition_request import BucketTransitionRequest
from ...domain.entities.historical_asr_data import HistoricalASRData
from ...domain.entities.speaker import Speaker
from ...domain.value_objects.speaker_bucket import SpeakerBucket


class ISpeakerRepositoryPort(ABC):
    """
    Abstract interface for speaker repository operations.

    This port defines the contract for speaker data persistence,
    including CRUD operations, search, and bucket management.
    """

    @abstractmethod
    async def create_speaker(self, speaker: Speaker) -> Speaker:
        """
        Create a new speaker.

        Args:
            speaker: Speaker entity to create

        Returns:
            Created speaker entity

        Raises:
            ValueError: If speaker already exists
            RepositoryError: If creation fails
        """
        pass

    @abstractmethod
    async def get_speaker_by_id(self, speaker_id: UUID) -> Optional[Speaker]:
        """
        Get speaker by ID.

        Args:
            speaker_id: Speaker identifier

        Returns:
            Speaker entity or None if not found
        """
        pass

    @abstractmethod
    async def get_speaker_by_identifier(
        self, speaker_identifier: str
    ) -> Optional[Speaker]:
        """
        Get speaker by external identifier.

        Args:
            speaker_identifier: External speaker identifier

        Returns:
            Speaker entity or None if not found
        """
        pass

    @abstractmethod
    async def update_speaker(self, speaker: Speaker) -> Speaker:
        """
        Update an existing speaker.

        Args:
            speaker: Speaker entity to update

        Returns:
            Updated speaker entity

        Raises:
            ValueError: If speaker not found
            RepositoryError: If update fails
        """
        pass

    @abstractmethod
    async def delete_speaker(self, speaker_id: UUID) -> bool:
        """
        Delete a speaker.

        Args:
            speaker_id: Speaker identifier

        Returns:
            True if deleted, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        pass

    @abstractmethod
    async def search_speakers(
        self,
        name_pattern: Optional[str] = None,
        bucket: Optional[SpeakerBucket] = None,
        min_ser_score: Optional[Decimal] = None,
        max_ser_score: Optional[Decimal] = None,
        has_sufficient_data: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Speaker]:
        """
        Search speakers with filters.

        Args:
            name_pattern: Name pattern to search for
            bucket: Filter by speaker bucket
            min_ser_score: Minimum SER score filter
            max_ser_score: Maximum SER score filter
            has_sufficient_data: Filter by data sufficiency
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of matching speakers
        """
        pass

    @abstractmethod
    async def get_speakers_by_bucket(self, bucket: SpeakerBucket) -> List[Speaker]:
        """
        Get all speakers in a specific bucket.

        Args:
            bucket: Speaker bucket to filter by

        Returns:
            List of speakers in the bucket
        """
        pass

    @abstractmethod
    async def get_speakers_needing_transition(self) -> List[Speaker]:
        """
        Get speakers that need bucket transition based on their metrics.

        Returns:
            List of speakers needing transition
        """
        pass

    @abstractmethod
    async def count_speakers_by_bucket(self) -> Dict[str, int]:
        """
        Get count of speakers by bucket.

        Returns:
            Dictionary with bucket counts
        """
        pass

    @abstractmethod
    async def update_speaker_statistics(self, speaker_id: UUID) -> Speaker:
        """
        Update speaker statistics from historical data.

        Args:
            speaker_id: Speaker identifier

        Returns:
            Updated speaker entity

        Raises:
            ValueError: If speaker not found
        """
        pass

    # Historical ASR Data operations

    @abstractmethod
    async def create_historical_asr_data(
        self, data: HistoricalASRData
    ) -> HistoricalASRData:
        """
        Create historical ASR data entry.

        Args:
            data: Historical ASR data to create

        Returns:
            Created historical data entity
        """
        pass

    @abstractmethod
    async def get_historical_asr_data_by_speaker(
        self,
        speaker_id: UUID,
        limit: Optional[int] = None,
        include_test_data: bool = True,
    ) -> List[HistoricalASRData]:
        """
        Get historical ASR data for a speaker.

        Args:
            speaker_id: Speaker identifier
            limit: Maximum number of records to return
            include_test_data: Whether to include test data

        Returns:
            List of historical ASR data
        """
        pass

    @abstractmethod
    async def get_test_data_for_speaker(
        self, speaker_id: UUID
    ) -> List[HistoricalASRData]:
        """
        Get test data for a speaker (2% validation data).

        Args:
            speaker_id: Speaker identifier

        Returns:
            List of test data entries
        """
        pass

    @abstractmethod
    async def mark_data_as_test(self, data_ids: List[UUID]) -> int:
        """
        Mark historical data entries as test data.

        Args:
            data_ids: List of data IDs to mark as test

        Returns:
            Number of records updated
        """
        pass

    # Bucket Transition operations

    @abstractmethod
    async def create_bucket_transition_request(
        self, request: BucketTransitionRequest
    ) -> BucketTransitionRequest:
        """
        Create a bucket transition request.

        Args:
            request: Bucket transition request to create

        Returns:
            Created transition request
        """
        pass

    @abstractmethod
    async def get_bucket_transition_request_by_id(
        self, request_id: UUID
    ) -> Optional[BucketTransitionRequest]:
        """
        Get bucket transition request by ID.

        Args:
            request_id: Request identifier

        Returns:
            Transition request or None if not found
        """
        pass

    @abstractmethod
    async def get_pending_transition_requests(self) -> List[BucketTransitionRequest]:
        """
        Get all pending bucket transition requests.

        Returns:
            List of pending transition requests
        """
        pass

    @abstractmethod
    async def update_bucket_transition_request(
        self, request: BucketTransitionRequest
    ) -> BucketTransitionRequest:
        """
        Update a bucket transition request.

        Args:
            request: Transition request to update

        Returns:
            Updated transition request
        """
        pass

    @abstractmethod
    async def get_transition_history_for_speaker(
        self, speaker_id: UUID
    ) -> List[BucketTransitionRequest]:
        """
        Get bucket transition history for a speaker.

        Args:
            speaker_id: Speaker identifier

        Returns:
            List of transition requests for the speaker
        """
        pass
