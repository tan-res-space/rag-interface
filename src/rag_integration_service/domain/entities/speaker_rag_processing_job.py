"""
Speaker RAG Processing Job Domain Entity

Represents background jobs for speaker-specific RAG processing.
Core domain entity for managing RAG processing workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from decimal import Decimal
from enum import Enum


class JobType(str, Enum):
    """Enumeration for RAG processing job types"""
    HISTORICAL_ANALYSIS = "historical_analysis"
    ERROR_PAIR_GENERATION = "error_pair_generation"
    VECTORIZATION = "vectorization"
    RAG_CORRECTION = "rag_correction"


class JobStatus(str, Enum):
    """Enumeration for job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SpeakerRAGProcessingJob:
    """
    Domain entity representing a speaker-specific RAG processing job.
    
    This entity encapsulates the workflow for processing speaker data through
    various RAG pipeline stages including analysis, vectorization, and correction.
    """
    
    id: UUID
    speaker_id: UUID
    job_type: JobType
    status: JobStatus = JobStatus.PENDING
    total_records: Optional[int] = None
    processed_records: int = 0
    error_records: int = 0
    progress_percentage: Decimal = Decimal('0.00')
    error_message: Optional[str] = None
    job_metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the processing job after initialization."""
        self._validate_required_fields()
        self._validate_progress_data()
        self._validate_status_consistency()
        self._set_defaults()
    
    def _validate_required_fields(self) -> None:
        """Validate required fields."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")
        
        if not isinstance(self.job_type, JobType):
            raise ValueError("job_type must be a valid JobType")
        
        if not isinstance(self.status, JobStatus):
            raise ValueError("status must be a valid JobStatus")
    
    def _validate_progress_data(self) -> None:
        """Validate progress-related fields."""
        if self.processed_records < 0:
            raise ValueError("processed_records cannot be negative")
        
        if self.error_records < 0:
            raise ValueError("error_records cannot be negative")
        
        if self.total_records is not None:
            if self.total_records < 0:
                raise ValueError("total_records cannot be negative")
            
            if self.processed_records + self.error_records > self.total_records:
                raise ValueError("processed + error records cannot exceed total records")
        
        if self.progress_percentage < 0 or self.progress_percentage > 100:
            raise ValueError("progress_percentage must be between 0 and 100")
    
    def _validate_status_consistency(self) -> None:
        """Validate status consistency with timestamps."""
        if self.status == JobStatus.RUNNING and self.started_at is None:
            self.started_at = datetime.utcnow()
        
        if self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            if self.completed_at is None:
                self.completed_at = datetime.utcnow()
    
    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_pending(self) -> bool:
        """Check if job is pending."""
        return self.status == JobStatus.PENDING
    
    def is_running(self) -> bool:
        """Check if job is running."""
        return self.status == JobStatus.RUNNING
    
    def is_completed(self) -> bool:
        """Check if job is completed."""
        return self.status == JobStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if job is failed."""
        return self.status == JobStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """Check if job is cancelled."""
        return self.status == JobStatus.CANCELLED
    
    def is_finished(self) -> bool:
        """Check if job is in a finished state."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def can_be_started(self) -> bool:
        """Check if job can be started."""
        return self.status == JobStatus.PENDING
    
    def can_be_cancelled(self) -> bool:
        """Check if job can be cancelled."""
        return self.status in [JobStatus.PENDING, JobStatus.RUNNING]
    
    def start_job(self) -> None:
        """
        Start the processing job.
        
        Raises:
            ValueError: If job cannot be started
        """
        if not self.can_be_started():
            raise ValueError(f"Job cannot be started from status: {self.status}")
        
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.progress_percentage = Decimal('0.00')
    
    def complete_job(self) -> None:
        """
        Complete the processing job.
        
        Raises:
            ValueError: If job is not running
        """
        if not self.is_running():
            raise ValueError(f"Job cannot be completed from status: {self.status}")
        
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = Decimal('100.00')
    
    def fail_job(self, error_message: str) -> None:
        """
        Mark job as failed.
        
        Args:
            error_message: Error message describing the failure
            
        Raises:
            ValueError: If job is not running
        """
        if not self.is_running():
            raise ValueError(f"Job cannot be failed from status: {self.status}")
        
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    def cancel_job(self, reason: str) -> None:
        """
        Cancel the processing job.
        
        Args:
            reason: Reason for cancellation
            
        Raises:
            ValueError: If job cannot be cancelled
        """
        if not self.can_be_cancelled():
            raise ValueError(f"Job cannot be cancelled from status: {self.status}")
        
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        self.job_metadata["cancellation_reason"] = reason
    
    def update_progress(self, processed: int, errors: int = 0) -> None:
        """
        Update job progress.
        
        Args:
            processed: Number of processed records
            errors: Number of error records
            
        Raises:
            ValueError: If job is not running or invalid progress
        """
        if not self.is_running():
            raise ValueError("Can only update progress for running jobs")
        
        if processed < self.processed_records:
            raise ValueError("Processed records cannot decrease")
        
        if errors < 0:
            raise ValueError("Error records cannot be negative")
        
        self.processed_records = processed
        self.error_records = errors
        
        # Calculate progress percentage
        if self.total_records and self.total_records > 0:
            total_processed = self.processed_records + self.error_records
            self.progress_percentage = Decimal(str((total_processed / self.total_records) * 100))
            self.progress_percentage = min(self.progress_percentage, Decimal('100.00'))
    
    def set_total_records(self, total: int) -> None:
        """
        Set total number of records to process.
        
        Args:
            total: Total number of records
            
        Raises:
            ValueError: If total is invalid
        """
        if total < 0:
            raise ValueError("Total records cannot be negative")
        
        if total < self.processed_records + self.error_records:
            raise ValueError("Total records cannot be less than already processed records")
        
        self.total_records = total
        
        # Recalculate progress if job is running
        if self.is_running() and total > 0:
            total_processed = self.processed_records + self.error_records
            self.progress_percentage = Decimal(str((total_processed / total) * 100))
    
    def get_duration_minutes(self) -> Optional[float]:
        """
        Get job duration in minutes.
        
        Returns:
            Duration in minutes, or None if not applicable
        """
        if self.started_at is None:
            return None
        
        end_time = self.completed_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds() / 60
    
    def get_processing_rate(self) -> Optional[float]:
        """
        Get processing rate in records per minute.
        
        Returns:
            Processing rate, or None if not applicable
        """
        duration = self.get_duration_minutes()
        if duration is None or duration == 0:
            return None
        
        return self.processed_records / duration
    
    def get_estimated_completion_time(self) -> Optional[datetime]:
        """
        Get estimated completion time based on current progress.
        
        Returns:
            Estimated completion time, or None if not applicable
        """
        if not self.is_running() or not self.total_records:
            return None
        
        rate = self.get_processing_rate()
        if rate is None or rate == 0:
            return None
        
        remaining_records = self.total_records - (self.processed_records + self.error_records)
        if remaining_records <= 0:
            return datetime.utcnow()
        
        estimated_minutes = remaining_records / rate
        return datetime.utcnow() + datetime.timedelta(minutes=estimated_minutes)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the job.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.job_metadata[key] = value
    
    def get_job_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the processing job.
        
        Returns:
            Dictionary containing job summary
        """
        return {
            "id": str(self.id),
            "speaker_id": str(self.speaker_id),
            "job_type": self.job_type.value,
            "status": self.status.value,
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "error_records": self.error_records,
            "progress_percentage": float(self.progress_percentage),
            "duration_minutes": self.get_duration_minutes(),
            "processing_rate": self.get_processing_rate(),
            "estimated_completion": self.get_estimated_completion_time().isoformat() if self.get_estimated_completion_time() else None,
            "error_message": self.error_message,
            "can_be_started": self.can_be_started(),
            "can_be_cancelled": self.can_be_cancelled(),
            "is_finished": self.is_finished(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.job_metadata
        }
    
    def __eq__(self, other: "SpeakerRAGProcessingJob") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, SpeakerRAGProcessingJob):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation of the processing job."""
        return f"SpeakerRAGProcessingJob(id={self.id}, speaker_id={self.speaker_id}, type={self.job_type.value}, status={self.status.value})"
