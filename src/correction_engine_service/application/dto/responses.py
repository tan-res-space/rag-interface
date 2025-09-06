"""
Response DTOs for the Correction Engine Service application layer.

These DTOs define the structure of responses from use cases and API endpoints.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from correction_engine_service.domain.entities.correction_suggestion import (
    CorrectionSuggestion,
)


@dataclass(frozen=True)
class CorrectionResponse:
    """
    Response DTO for text correction.
    """

    original_text: str
    suggestions: List[CorrectionSuggestion]
    processing_time: float
    correction_mode: str
    model_info: Dict[str, str]
    status: str = "success"

    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, "model_info") or self.model_info is None:
            object.__setattr__(self, "model_info", {})


@dataclass(frozen=True)
class BatchCorrectionResponse:
    """
    Response DTO for batch text correction.
    """

    results: List[CorrectionResponse]
    processing_time: float
    batch_size: int
    success_count: int
    failure_count: int
    failures: List[Dict[str, Any]]
    status: str = "success"

    def __post_init__(self):
        """Set default values and validate consistency."""
        if not hasattr(self, "failures") or self.failures is None:
            object.__setattr__(self, "failures", [])

        # Validate consistency
        if self.success_count + self.failure_count != self.batch_size:
            raise ValueError("success_count + failure_count must equal batch_size")


@dataclass(frozen=True)
class ApplyCorrectionResponse:
    """
    Response DTO for applying correction.
    """

    suggestion_id: str
    applied: bool
    corrected_text: str
    feedback_recorded: bool
    processing_time: float
    status: str = "success"


@dataclass(frozen=True)
class RejectCorrectionResponse:
    """
    Response DTO for rejecting correction.
    """

    suggestion_id: str
    rejected: bool
    feedback_recorded: bool
    processing_time: float
    status: str = "success"


@dataclass(frozen=True)
class CorrectionStatisticsResponse:
    """
    Response DTO for correction statistics.
    """

    total_corrections: int
    corrections_by_type: Dict[str, int]
    average_confidence: float
    acceptance_rate: float
    model_performance: Dict[str, Any]
    time_window: Dict[str, str]
    timestamp: str

    def __post_init__(self):
        """Set default values."""
        if not hasattr(self, "timestamp") or not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.utcnow().isoformat())
