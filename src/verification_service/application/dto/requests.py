"""
Request DTOs for Verification Service

Data Transfer Objects for incoming requests to the verification service.
Includes DTOs for SER calculation and validation workflows.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from uuid import UUID


@dataclass
class CalculateSERRequest:
    """
    Request DTO for calculating SER metrics for a single text pair.
    """
    
    asr_text: str
    reference_text: str
    calculation_type: str  # "original" or "rag_corrected"
    speaker_id: Optional[UUID] = None
    historical_data_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.asr_text or not self.asr_text.strip():
            raise ValueError("asr_text cannot be empty")
        
        if not self.reference_text or not self.reference_text.strip():
            raise ValueError("reference_text cannot be empty")
        
        if self.calculation_type not in ["original", "rag_corrected"]:
            raise ValueError("calculation_type must be 'original' or 'rag_corrected'")


@dataclass
class BatchCalculateSERRequest:
    """
    Request DTO for calculating SER metrics for multiple text pairs.
    """
    
    calculation_items: List[CalculateSERRequest]
    batch_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.calculation_items:
            raise ValueError("calculation_items cannot be empty")
        
        if len(self.calculation_items) > 1000:
            raise ValueError("Batch size exceeds maximum allowed (1000)")


@dataclass
class StartValidationSessionRequest:
    """
    Request DTO for starting an MT validation session.
    """
    
    speaker_id: UUID
    session_name: str
    test_data_ids: List[UUID]
    mt_user_id: UUID
    session_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")
        
        if not self.session_name or not self.session_name.strip():
            raise ValueError("session_name cannot be empty")
        
        if not self.test_data_ids:
            raise ValueError("test_data_ids cannot be empty")
        
        if not self.mt_user_id:
            raise ValueError("mt_user_id is required")


@dataclass
class SubmitMTFeedbackRequest:
    """
    Request DTO for submitting MT validation feedback.
    """
    
    session_id: UUID
    historical_data_id: UUID
    original_asr_text: str
    rag_corrected_text: str
    final_reference_text: str
    mt_feedback_rating: int  # 1-5 scale
    mt_comments: Optional[str] = None
    improvement_assessment: str = "none"  # significant, moderate, minimal, none, worse
    recommended_for_bucket_change: bool = False
    feedback_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.session_id:
            raise ValueError("session_id is required")
        
        if not self.historical_data_id:
            raise ValueError("historical_data_id is required")
        
        if not all([self.original_asr_text, self.rag_corrected_text, self.final_reference_text]):
            raise ValueError("All text fields are required")
        
        if not (1 <= self.mt_feedback_rating <= 5):
            raise ValueError("mt_feedback_rating must be between 1 and 5")
        
        valid_assessments = ["significant", "moderate", "minimal", "none", "worse"]
        if self.improvement_assessment not in valid_assessments:
            raise ValueError(f"improvement_assessment must be one of {valid_assessments}")


@dataclass
class CompleteValidationSessionRequest:
    """
    Request DTO for completing an MT validation session.
    """
    
    session_id: UUID
    completion_notes: Optional[str] = None
    session_summary: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.session_id:
            raise ValueError("session_id is required")


@dataclass
class GetSERComparisonRequest:
    """
    Request DTO for getting SER comparison between original and corrected texts.
    """
    
    speaker_id: UUID
    historical_data_ids: List[UUID]
    include_individual_metrics: bool = True
    include_summary_statistics: bool = True
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")
        
        if not self.historical_data_ids:
            raise ValueError("historical_data_ids cannot be empty")


@dataclass
class GetSpeakerSERAnalysisRequest:
    """
    Request DTO for getting comprehensive SER analysis for a speaker.
    """
    
    speaker_id: UUID
    include_historical_trend: bool = True
    include_quality_distribution: bool = True
    include_error_pattern_analysis: bool = False
    date_range_start: Optional[str] = None  # ISO format date
    date_range_end: Optional[str] = None    # ISO format date
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.speaker_id:
            raise ValueError("speaker_id is required")
