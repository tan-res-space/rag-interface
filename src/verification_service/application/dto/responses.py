"""
Response DTOs for Verification Service

Data Transfer Objects for outgoing responses from the verification service.
Includes DTOs for SER calculation results and validation workflows.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from ...domain.value_objects.ser_metrics import SERMetrics


@dataclass
class SERCalculationResponse:
    """
    Response DTO for SER calculation results.
    """

    speaker_id: Optional[UUID]
    historical_data_id: Optional[UUID]
    calculation_type: str
    ser_metrics: SERMetrics
    metadata: Dict[str, Any]
    calculated_at: datetime = None

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.calculated_at is None:
            self.calculated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "speaker_id": str(self.speaker_id) if self.speaker_id else None,
            "historical_data_id": (
                str(self.historical_data_id) if self.historical_data_id else None
            ),
            "calculation_type": self.calculation_type,
            "ser_metrics": self.ser_metrics.to_dict(),
            "metadata": self.metadata,
            "calculated_at": self.calculated_at.isoformat(),
        }


@dataclass
class BatchSERCalculationResponse:
    """
    Response DTO for batch SER calculation results.
    """

    total_calculations: int
    successful_calculations: int
    failed_calculations: int
    results: List[SERCalculationResponse]
    summary_statistics: Dict[str, Any]
    processing_time_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_calculations": self.total_calculations,
            "successful_calculations": self.successful_calculations,
            "failed_calculations": self.failed_calculations,
            "results": [result.to_dict() for result in self.results],
            "summary_statistics": self.summary_statistics,
            "processing_time_seconds": self.processing_time_seconds,
        }


@dataclass
class ValidationSessionResponse:
    """
    Response DTO for validation session information.
    """

    session_id: UUID
    speaker_id: UUID
    session_name: str
    test_data_count: int
    status: str
    mt_user_id: Optional[UUID]
    progress_percentage: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_minutes: Optional[float]
    session_metadata: Dict[str, Any]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "session_id": str(self.session_id),
            "speaker_id": str(self.speaker_id),
            "session_name": self.session_name,
            "test_data_count": self.test_data_count,
            "status": self.status,
            "mt_user_id": str(self.mt_user_id) if self.mt_user_id else None,
            "progress_percentage": self.progress_percentage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "duration_minutes": self.duration_minutes,
            "session_metadata": self.session_metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MTFeedbackResponse:
    """
    Response DTO for MT feedback submission.
    """

    feedback_id: UUID
    session_id: UUID
    historical_data_id: UUID
    mt_feedback_rating: int
    improvement_assessment: str
    recommended_for_bucket_change: bool
    ser_comparison: Optional[Dict[str, Any]] = None
    created_at: datetime = None

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "feedback_id": str(self.feedback_id),
            "session_id": str(self.session_id),
            "historical_data_id": str(self.historical_data_id),
            "mt_feedback_rating": self.mt_feedback_rating,
            "improvement_assessment": self.improvement_assessment,
            "recommended_for_bucket_change": self.recommended_for_bucket_change,
            "ser_comparison": self.ser_comparison,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SERComparisonResponse:
    """
    Response DTO for SER comparison results.
    """

    speaker_id: UUID
    comparison_summary: Dict[str, Any]
    individual_comparisons: List[Dict[str, Any]]
    overall_improvement: Dict[str, Any]
    recommendation: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "speaker_id": str(self.speaker_id),
            "comparison_summary": self.comparison_summary,
            "individual_comparisons": self.individual_comparisons,
            "overall_improvement": self.overall_improvement,
            "recommendation": self.recommendation,
        }


@dataclass
class SpeakerSERAnalysisResponse:
    """
    Response DTO for comprehensive speaker SER analysis.
    """

    speaker_id: UUID
    analysis_period: Dict[str, str]
    current_metrics: Dict[str, Any]
    historical_trend: Optional[List[Dict[str, Any]]] = None
    quality_distribution: Optional[Dict[str, int]] = None
    improvement_opportunities: List[Dict[str, Any]] = None
    bucket_recommendation: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "speaker_id": str(self.speaker_id),
            "analysis_period": self.analysis_period,
            "current_metrics": self.current_metrics,
            "historical_trend": self.historical_trend,
            "quality_distribution": self.quality_distribution,
            "improvement_opportunities": self.improvement_opportunities or [],
            "bucket_recommendation": self.bucket_recommendation,
        }


@dataclass
class ValidationTestDataResponse:
    """
    Response DTO for validation test data item.
    """

    data_id: UUID
    speaker_id: UUID
    original_asr_text: str
    rag_corrected_text: str
    final_reference_text: str
    original_ser_metrics: SERMetrics
    corrected_ser_metrics: SERMetrics
    improvement_metrics: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "data_id": str(self.data_id),
            "speaker_id": str(self.speaker_id),
            "original_asr_text": self.original_asr_text,
            "rag_corrected_text": self.rag_corrected_text,
            "final_reference_text": self.final_reference_text,
            "original_ser_metrics": self.original_ser_metrics.to_dict(),
            "corrected_ser_metrics": self.corrected_ser_metrics.to_dict(),
            "improvement_metrics": self.improvement_metrics,
            "metadata": self.metadata,
        }


@dataclass
class ErrorResponse:
    """
    Response DTO for error cases.
    """

    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "timestamp": self.timestamp.isoformat(),
        }
