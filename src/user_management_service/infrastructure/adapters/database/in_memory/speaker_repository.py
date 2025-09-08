"""
In-Memory Speaker Repository Implementation

Provides an in-memory implementation of the speaker repository for development and testing.
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from .....domain.entities.speaker import Speaker
from .....domain.entities.bucket_transition_request import BucketTransitionRequest
from .....domain.entities.historical_asr_data import HistoricalASRData
from .....domain.value_objects.speaker_bucket import SpeakerBucket
from .....application.ports.speaker_repository_port import ISpeakerRepositoryPort

logger = logging.getLogger(__name__)


class InMemorySpeakerRepository(ISpeakerRepositoryPort):
    """
    In-memory implementation of the speaker repository.
    
    This implementation stores speakers in memory and provides mock data
    for development and testing purposes.
    """

    def __init__(self):
        """Initialize the repository with sample data."""
        self._speakers: Dict[UUID, Speaker] = {}
        self._speakers_by_identifier: Dict[str, Speaker] = {}
        self._historical_data: Dict[UUID, List[HistoricalASRData]] = {}
        self._transition_requests: Dict[UUID, BucketTransitionRequest] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize repository with sample speaker data."""
        sample_speakers = [
            {
                "speaker_identifier": "SPEAKER_001",
                "speaker_name": "Alice Johnson",
                "current_bucket": SpeakerBucket.NO_TOUCH,
                "total_notes_count": 150,
                "processed_notes_count": 150,
                "average_ser_score": 2.1,
                "metadata": {"region": "US-West", "language": "en-US"}
            },
            {
                "speaker_identifier": "SPEAKER_002",
                "speaker_name": "Bob Smith",
                "current_bucket": SpeakerBucket.LOW_TOUCH,
                "total_notes_count": 89,
                "processed_notes_count": 89,
                "average_ser_score": 7.3,
                "metadata": {"region": "US-East", "language": "en-US"}
            },
            {
                "speaker_identifier": "SPEAKER_003",
                "speaker_name": "Carol Davis",
                "current_bucket": SpeakerBucket.MEDIUM_TOUCH,
                "total_notes_count": 45,
                "processed_notes_count": 45,
                "average_ser_score": 18.7,
                "metadata": {"region": "EU-West", "language": "en-GB"}
            },
            {
                "speaker_identifier": "SPEAKER_004",
                "speaker_name": "David Wilson",
                "current_bucket": SpeakerBucket.HIGH_TOUCH,
                "total_notes_count": 23,
                "processed_notes_count": 23,
                "average_ser_score": 42.1,
                "metadata": {"region": "APAC", "language": "en-AU"}
            },
            {
                "speaker_identifier": "SPEAKER_005",
                "speaker_name": "Eva Martinez",
                "current_bucket": SpeakerBucket.NO_TOUCH,
                "total_notes_count": 203,
                "processed_notes_count": 203,
                "average_ser_score": 1.8,
                "metadata": {"region": "US-Central", "language": "en-US"}
            }
        ]

        for speaker_data in sample_speakers:
            speaker = Speaker(
                id=uuid4(),
                speaker_identifier=speaker_data["speaker_identifier"],
                speaker_name=speaker_data["speaker_name"],
                current_bucket=speaker_data["current_bucket"],
                total_notes_count=speaker_data["total_notes_count"],
                processed_notes_count=speaker_data["processed_notes_count"],
                average_ser_score=speaker_data["average_ser_score"],
                metadata=speaker_data["metadata"],
                created_at=datetime.utcnow() - timedelta(days=30),
                updated_at=datetime.utcnow()
            )
            
            self._speakers[speaker.id] = speaker
            self._speakers_by_identifier[speaker.speaker_identifier] = speaker

        logger.info(f"Initialized in-memory speaker repository with {len(sample_speakers)} sample speakers")

    async def create_speaker(self, speaker: Speaker) -> Speaker:
        """Create a new speaker."""
        self._speakers[speaker.id] = speaker
        self._speakers_by_identifier[speaker.speaker_identifier] = speaker
        logger.info(f"Created speaker: {speaker.speaker_identifier}")
        return speaker

    async def get_speaker_by_id(self, speaker_id: UUID) -> Optional[Speaker]:
        """Get speaker by ID."""
        return self._speakers.get(speaker_id)

    async def get_speaker_by_identifier(self, speaker_identifier: str) -> Optional[Speaker]:
        """Get speaker by external identifier."""
        return self._speakers_by_identifier.get(speaker_identifier)

    async def update_speaker(self, speaker: Speaker) -> Speaker:
        """Update an existing speaker."""
        if speaker.id not in self._speakers:
            raise ValueError(f"Speaker with ID {speaker.id} not found")
        
        self._speakers[speaker.id] = speaker
        self._speakers_by_identifier[speaker.speaker_identifier] = speaker
        logger.info(f"Updated speaker: {speaker.speaker_identifier}")
        return speaker

    async def delete_speaker(self, speaker_id: UUID) -> bool:
        """Delete a speaker."""
        speaker = self._speakers.get(speaker_id)
        if not speaker:
            return False
        
        del self._speakers[speaker_id]
        del self._speakers_by_identifier[speaker.speaker_identifier]
        logger.info(f"Deleted speaker: {speaker.speaker_identifier}")
        return True

    async def search_speakers(
        self,
        name_pattern: Optional[str] = None,
        bucket: Optional[SpeakerBucket] = None,
        min_ser_score: Optional[float] = None,
        max_ser_score: Optional[float] = None,
        has_sufficient_data: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Speaker]:
        """Search speakers with filters."""
        speakers = list(self._speakers.values())
        
        # Apply filters
        if name_pattern:
            speakers = [s for s in speakers if name_pattern.lower() in s.speaker_name.lower()]
        
        if bucket:
            speakers = [s for s in speakers if s.current_bucket == bucket]
        
        if min_ser_score is not None:
            speakers = [s for s in speakers if s.average_ser_score >= min_ser_score]
        
        if max_ser_score is not None:
            speakers = [s for s in speakers if s.average_ser_score <= max_ser_score]
        
        if has_sufficient_data is not None:
            # Consider speakers with >50 notes as having sufficient data
            speakers = [s for s in speakers if (s.total_notes_count > 50) == has_sufficient_data]
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return speakers[start_idx:end_idx]

    async def get_speakers_by_bucket(self, bucket: SpeakerBucket) -> List[Speaker]:
        """Get all speakers in a specific bucket."""
        return [s for s in self._speakers.values() if s.current_bucket == bucket]

    async def get_speakers_needing_transition(self) -> List[Speaker]:
        """Get speakers that need bucket transition based on their metrics."""
        # Simple logic: speakers whose SER score doesn't match their bucket
        needing_transition = []
        
        for speaker in self._speakers.values():
            should_transition = False
            
            # Check if speaker's SER score suggests a different bucket
            if speaker.current_bucket == SpeakerBucket.NO_TOUCH and speaker.average_ser_score > 5.0:
                should_transition = True
            elif speaker.current_bucket == SpeakerBucket.LOW_TOUCH and (speaker.average_ser_score < 3.0 or speaker.average_ser_score > 15.0):
                should_transition = True
            elif speaker.current_bucket == SpeakerBucket.MEDIUM_TOUCH and (speaker.average_ser_score < 10.0 or speaker.average_ser_score > 30.0):
                should_transition = True
            elif speaker.current_bucket == SpeakerBucket.HIGH_TOUCH and speaker.average_ser_score < 25.0:
                should_transition = True
            
            if should_transition:
                needing_transition.append(speaker)
        
        return needing_transition

    async def count_speakers_by_bucket(self) -> Dict[str, int]:
        """Count speakers by bucket."""
        counts = {
            "no_touch": 0,
            "low_touch": 0,
            "medium_touch": 0,
            "high_touch": 0,
        }
        
        for speaker in self._speakers.values():
            if speaker.current_bucket == SpeakerBucket.NO_TOUCH:
                counts["no_touch"] += 1
            elif speaker.current_bucket == SpeakerBucket.LOW_TOUCH:
                counts["low_touch"] += 1
            elif speaker.current_bucket == SpeakerBucket.MEDIUM_TOUCH:
                counts["medium_touch"] += 1
            elif speaker.current_bucket == SpeakerBucket.HIGH_TOUCH:
                counts["high_touch"] += 1
        
        return counts

    async def update_speaker_statistics(self, speaker_id: UUID) -> Speaker:
        """Update speaker statistics from historical data."""
        speaker = self._speakers.get(speaker_id)
        if not speaker:
            raise ValueError(f"Speaker with ID {speaker_id} not found")
        
        # Mock statistics update - in real implementation, this would recalculate from historical data
        speaker.updated_at = datetime.utcnow()
        
        logger.info(f"Updated statistics for speaker: {speaker.speaker_identifier}")
        return speaker

    # Historical ASR Data operations
    async def create_historical_asr_data(self, data: HistoricalASRData) -> HistoricalASRData:
        """Create historical ASR data entry."""
        if data.speaker_id not in self._historical_data:
            self._historical_data[data.speaker_id] = []
        self._historical_data[data.speaker_id].append(data)
        return data

    async def get_historical_asr_data_by_speaker(
        self,
        speaker_id: UUID,
        limit: Optional[int] = None,
        include_test_data: bool = True,
    ) -> List[HistoricalASRData]:
        """Get historical ASR data for a speaker."""
        data = self._historical_data.get(speaker_id, [])
        if not include_test_data:
            data = [d for d in data if not getattr(d, 'is_test_data', False)]
        if limit:
            data = data[:limit]
        return data

    async def get_test_data_for_speaker(self, speaker_id: UUID) -> List[HistoricalASRData]:
        """Get test data for a speaker (2% validation data)."""
        data = self._historical_data.get(speaker_id, [])
        return [d for d in data if getattr(d, 'is_test_data', False)]

    async def mark_data_as_test(self, data_ids: List[UUID]) -> int:
        """Mark historical data entries as test data."""
        count = 0
        for speaker_data in self._historical_data.values():
            for data in speaker_data:
                if data.id in data_ids:
                    data.is_test_data = True
                    count += 1
        return count

    # Bucket Transition operations
    async def create_bucket_transition_request(self, request: BucketTransitionRequest) -> BucketTransitionRequest:
        """Create a bucket transition request."""
        self._transition_requests[request.id] = request
        return request

    async def get_bucket_transition_request_by_id(self, request_id: UUID) -> Optional[BucketTransitionRequest]:
        """Get bucket transition request by ID."""
        return self._transition_requests.get(request_id)

    async def get_pending_transition_requests(self) -> List[BucketTransitionRequest]:
        """Get all pending bucket transition requests."""
        return [req for req in self._transition_requests.values() if req.status == "pending"]

    async def update_bucket_transition_request(self, request: BucketTransitionRequest) -> BucketTransitionRequest:
        """Update a bucket transition request."""
        self._transition_requests[request.id] = request
        return request

    async def get_transition_history_for_speaker(self, speaker_id: UUID) -> List[BucketTransitionRequest]:
        """Get bucket transition history for a speaker."""
        return [req for req in self._transition_requests.values() if req.speaker_id == speaker_id]
