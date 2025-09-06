"""
Speaker Profile Repository Interface
Defines contract for speaker profile data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..entities.speaker_profile import SpeakerProfile, BucketChangeLog
from ..value_objects.bucket_type import BucketType


class SpeakerProfileRepository(ABC):
    """
    Abstract repository for speaker profile management
    """
    
    @abstractmethod
    async def get_by_speaker_id(self, speaker_id: str) -> Optional[SpeakerProfile]:
        """Get speaker profile by speaker ID"""
    
    @abstractmethod
    async def save(self, speaker_profile: SpeakerProfile) -> SpeakerProfile:
        """Save or update speaker profile"""
    
    @abstractmethod
    async def create_if_not_exists(self, speaker_id: str, initial_bucket: BucketType) -> SpeakerProfile:
        """Create speaker profile if it doesn't exist"""
    
    @abstractmethod
    async def get_all_profiles(self, limit: int = 100, offset: int = 0) -> List[SpeakerProfile]:
        """Get all speaker profiles with pagination"""
    
    @abstractmethod
    async def get_profiles_by_bucket(self, bucket_type: BucketType) -> List[SpeakerProfile]:
        """Get all speaker profiles in a specific bucket"""
    
    @abstractmethod
    async def get_profiles_for_evaluation(self, days_since_last_change: int = 7) -> List[SpeakerProfile]:
        """Get profiles that are eligible for bucket evaluation"""
    
    @abstractmethod
    async def save_bucket_change_log(self, change_log: BucketChangeLog) -> BucketChangeLog:
        """Save bucket change log entry"""
    
    @abstractmethod
    async def get_bucket_change_history(
        self, 
        speaker_id: str, 
        limit: int = 50
    ) -> List[BucketChangeLog]:
        """Get bucket change history for a speaker"""
    
    @abstractmethod
    async def get_recent_bucket_changes(
        self, 
        speaker_id: str, 
        days: int = 30
    ) -> List[BucketChangeLog]:
        """Get recent bucket changes for a speaker within specified days"""
    
    @abstractmethod
    async def get_bucket_statistics(self) -> Dict[str, Any]:
        """Get overall bucket distribution statistics"""
    
    @abstractmethod
    async def delete_profile(self, speaker_id: str) -> bool:
        """Delete speaker profile and associated data"""
