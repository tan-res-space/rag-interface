"""
Speaker Profile Domain Entity
Manages speaker information, bucket classification, and performance metrics
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

from ..value_objects.bucket_type import BucketType
from ..value_objects.speaker_metrics import SpeakerMetrics


@dataclass
class SpeakerProfile:
    """
    Speaker profile entity containing bucket classification and performance data
    """
    speaker_id: str
    current_bucket: BucketType
    created_at: datetime
    updated_at: datetime
    total_reports: int = 0
    total_errors_found: int = 0
    total_corrections_made: int = 0
    average_error_rate: float = 0.0
    average_correction_accuracy: float = 0.0
    last_report_date: Optional[datetime] = None
    bucket_change_count: int = 0
    days_in_current_bucket: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate speaker profile data"""
        if not self.speaker_id:
            raise ValueError("Speaker ID is required")
        
        if self.total_reports < 0:
            raise ValueError("Total reports cannot be negative")
            
        if not (0.0 <= self.average_error_rate <= 1.0):
            raise ValueError("Average error rate must be between 0.0 and 1.0")
            
        if not (0.0 <= self.average_correction_accuracy <= 1.0):
            raise ValueError("Average correction accuracy must be between 0.0 and 1.0")
    
    def update_metrics(self, metrics: SpeakerMetrics) -> None:
        """Update speaker metrics based on new performance data"""
        self.total_reports = metrics.total_reports
        self.total_errors_found = metrics.total_errors_found
        self.total_corrections_made = metrics.total_corrections_made
        self.average_error_rate = metrics.average_error_rate
        self.average_correction_accuracy = metrics.average_correction_accuracy
        self.last_report_date = metrics.last_report_date
        self.updated_at = datetime.utcnow()
    
    def change_bucket(self, new_bucket: BucketType, reason: str) -> 'BucketChangeLog':
        """Change speaker bucket and create change log entry"""
        if new_bucket == self.current_bucket:
            raise ValueError("New bucket must be different from current bucket")
        
        old_bucket = self.current_bucket
        self.current_bucket = new_bucket
        self.bucket_change_count += 1
        self.days_in_current_bucket = 0
        self.updated_at = datetime.utcnow()
        
        # Create change log entry
        change_log = BucketChangeLog(
            change_id=str(uuid.uuid4()),
            speaker_id=self.speaker_id,
            old_bucket=old_bucket,
            new_bucket=new_bucket,
            change_reason=reason,
            changed_at=self.updated_at,
            metrics_at_change=SpeakerMetrics(
                total_reports=self.total_reports,
                total_errors_found=self.total_errors_found,
                total_corrections_made=self.total_corrections_made,
                average_error_rate=self.average_error_rate,
                average_correction_accuracy=self.average_correction_accuracy,
                last_report_date=self.last_report_date
            )
        )
        
        return change_log
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of speaker performance"""
        return {
            "speaker_id": self.speaker_id,
            "current_bucket": self.current_bucket.value,
            "total_reports": self.total_reports,
            "average_error_rate": round(self.average_error_rate, 3),
            "average_correction_accuracy": round(self.average_correction_accuracy, 3),
            "days_in_current_bucket": self.days_in_current_bucket,
            "bucket_change_count": self.bucket_change_count,
            "last_report_date": self.last_report_date.isoformat() if self.last_report_date else None
        }


@dataclass
class BucketChangeLog:
    """
    Log entry for bucket changes with audit trail
    """
    change_id: str
    speaker_id: str
    old_bucket: BucketType
    new_bucket: BucketType
    change_reason: str
    changed_at: datetime
    metrics_at_change: SpeakerMetrics
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate bucket change log data"""
        if not self.change_id:
            raise ValueError("Change ID is required")
        
        if not self.speaker_id:
            raise ValueError("Speaker ID is required")
            
        if not self.change_reason:
            raise ValueError("Change reason is required")
        
        if self.old_bucket == self.new_bucket:
            raise ValueError("Old and new bucket cannot be the same")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "change_id": self.change_id,
            "speaker_id": self.speaker_id,
            "old_bucket": self.old_bucket.value,
            "new_bucket": self.new_bucket.value,
            "change_reason": self.change_reason,
            "changed_at": self.changed_at.isoformat(),
            "metrics_at_change": self.metrics_at_change.to_dict(),
            "metadata": self.metadata
        }


class BucketProgressionDirection(Enum):
    """Direction of bucket progression"""
    PROMOTION = "promotion"
    DEMOTION = "demotion"
    STABLE = "stable"


@dataclass
class BucketProgressionRecommendation:
    """
    Recommendation for bucket progression based on analysis
    """
    speaker_id: str
    current_bucket: BucketType
    recommended_bucket: Optional[BucketType]
    direction: BucketProgressionDirection
    confidence_score: float
    reason: str
    metrics_used: SpeakerMetrics
    analysis_date: datetime
    
    def __post_init__(self):
        """Validate progression recommendation"""
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        if self.recommended_bucket == self.current_bucket:
            self.direction = BucketProgressionDirection.STABLE
        elif self.recommended_bucket and self.recommended_bucket.value > self.current_bucket.value:
            self.direction = BucketProgressionDirection.PROMOTION
        elif self.recommended_bucket and self.recommended_bucket.value < self.current_bucket.value:
            self.direction = BucketProgressionDirection.DEMOTION
    
    def should_change_bucket(self, min_confidence: float = 0.7) -> bool:
        """Determine if bucket should be changed based on confidence threshold"""
        return (
            self.recommended_bucket is not None and
            self.recommended_bucket != self.current_bucket and
            self.confidence_score >= min_confidence
        )
