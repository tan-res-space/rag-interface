"""
In-Memory Speaker Profile Repository Implementation
For testing and development purposes
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import copy

from src.error_reporting_service.domain.repositories.speaker_profile_repository import SpeakerProfileRepository
from src.error_reporting_service.domain.entities.speaker_profile import SpeakerProfile, BucketChangeLog
from src.error_reporting_service.domain.value_objects.bucket_type import BucketType


class InMemorySpeakerProfileAdapter(SpeakerProfileRepository):
    """
    In-memory implementation of speaker profile repository
    """
    
    def __init__(self):
        self._profiles: Dict[str, SpeakerProfile] = {}
        self._change_logs: List[BucketChangeLog] = []
    
    async def get_by_speaker_id(self, speaker_id: str) -> Optional[SpeakerProfile]:
        """Get speaker profile by speaker ID"""
        return copy.deepcopy(self._profiles.get(speaker_id))
    
    async def save(self, speaker_profile: SpeakerProfile) -> SpeakerProfile:
        """Save or update speaker profile"""
        speaker_profile.updated_at = datetime.utcnow()
        self._profiles[speaker_profile.speaker_id] = copy.deepcopy(speaker_profile)
        return copy.deepcopy(speaker_profile)
    
    async def create_if_not_exists(self, speaker_id: str, initial_bucket: BucketType) -> SpeakerProfile:
        """Create speaker profile if it doesn't exist"""
        if speaker_id in self._profiles:
            return copy.deepcopy(self._profiles[speaker_id])
        
        now = datetime.utcnow()
        profile = SpeakerProfile(
            speaker_id=speaker_id,
            current_bucket=initial_bucket,
            created_at=now,
            updated_at=now,
            total_reports=0,
            total_errors_found=0,
            total_corrections_made=0,
            average_error_rate=0.0,
            average_correction_accuracy=0.0,
            last_report_date=None,
            bucket_change_count=0,
            days_in_current_bucket=0,
            metadata={}
        )
        
        self._profiles[speaker_id] = copy.deepcopy(profile)
        return copy.deepcopy(profile)
    
    async def get_all_profiles(self, limit: int = 100, offset: int = 0) -> List[SpeakerProfile]:
        """Get all speaker profiles with pagination"""
        profiles = list(self._profiles.values())
        start_idx = offset
        end_idx = offset + limit
        return [copy.deepcopy(p) for p in profiles[start_idx:end_idx]]
    
    async def get_profiles_by_bucket(self, bucket_type: BucketType) -> List[SpeakerProfile]:
        """Get all speaker profiles in a specific bucket"""
        profiles = [
            copy.deepcopy(profile) 
            for profile in self._profiles.values() 
            if profile.current_bucket == bucket_type
        ]
        return profiles
    
    async def get_profiles_for_evaluation(self, days_since_last_change: int = 7) -> List[SpeakerProfile]:
        """Get profiles that are eligible for bucket evaluation"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_since_last_change)
        
        eligible_profiles = []
        for profile in self._profiles.values():
            # Check if enough time has passed since last bucket change
            last_change = self._get_last_bucket_change(profile.speaker_id)
            if last_change is None or last_change.changed_at <= cutoff_date:
                # Check if speaker has recent activity
                if profile.last_report_date and profile.last_report_date >= cutoff_date:
                    eligible_profiles.append(copy.deepcopy(profile))
        
        return eligible_profiles
    
    async def save_bucket_change_log(self, change_log: BucketChangeLog) -> BucketChangeLog:
        """Save bucket change log entry"""
        self._change_logs.append(copy.deepcopy(change_log))
        return copy.deepcopy(change_log)
    
    async def get_bucket_change_history(
        self, 
        speaker_id: str, 
        limit: int = 50
    ) -> List[BucketChangeLog]:
        """Get bucket change history for a speaker"""
        speaker_changes = [
            copy.deepcopy(log) 
            for log in self._change_logs 
            if log.speaker_id == speaker_id
        ]
        
        # Sort by change date (most recent first)
        speaker_changes.sort(key=lambda x: x.changed_at, reverse=True)
        
        return speaker_changes[:limit]
    
    async def get_recent_bucket_changes(
        self, 
        speaker_id: str, 
        days: int = 30
    ) -> List[BucketChangeLog]:
        """Get recent bucket changes for a speaker within specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_changes = [
            copy.deepcopy(log)
            for log in self._change_logs
            if log.speaker_id == speaker_id and log.changed_at >= cutoff_date
        ]
        
        # Sort by change date (most recent first)
        recent_changes.sort(key=lambda x: x.changed_at, reverse=True)
        
        return recent_changes
    
    async def get_bucket_statistics(self) -> Dict[str, Any]:
        """Get overall bucket distribution statistics"""
        bucket_counts = {bucket.value: 0 for bucket in BucketType}
        total_profiles = len(self._profiles)
        
        for profile in self._profiles.values():
            bucket_counts[profile.current_bucket.value] += 1
        
        # Calculate percentages
        bucket_percentages = {}
        for bucket, count in bucket_counts.items():
            percentage = (count / total_profiles * 100) if total_profiles > 0 else 0
            bucket_percentages[bucket] = round(percentage, 2)
        
        # Calculate change statistics
        total_changes = len(self._change_logs)
        recent_changes = len([
            log for log in self._change_logs 
            if log.changed_at >= datetime.utcnow() - timedelta(days=30)
        ])
        
        return {
            "total_profiles": total_profiles,
            "bucket_distribution": bucket_counts,
            "bucket_percentages": bucket_percentages,
            "total_bucket_changes": total_changes,
            "recent_bucket_changes": recent_changes,
            "average_changes_per_profile": round(total_changes / total_profiles, 2) if total_profiles > 0 else 0
        }
    
    async def delete_profile(self, speaker_id: str) -> bool:
        """Delete speaker profile and associated data"""
        if speaker_id in self._profiles:
            del self._profiles[speaker_id]
            
            # Remove associated change logs
            self._change_logs = [
                log for log in self._change_logs 
                if log.speaker_id != speaker_id
            ]
            
            return True
        return False
    
    def _get_last_bucket_change(self, speaker_id: str) -> Optional[BucketChangeLog]:
        """Get the most recent bucket change for a speaker"""
        speaker_changes = [
            log for log in self._change_logs 
            if log.speaker_id == speaker_id
        ]
        
        if not speaker_changes:
            return None
        
        # Return most recent change
        return max(speaker_changes, key=lambda x: x.changed_at)
    
    # Additional helper methods for testing
    def clear_all_data(self):
        """Clear all data (for testing)"""
        self._profiles.clear()
        self._change_logs.clear()
    
    def get_profile_count(self) -> int:
        """Get total number of profiles"""
        return len(self._profiles)
    
    def get_change_log_count(self) -> int:
        """Get total number of change log entries"""
        return len(self._change_logs)
