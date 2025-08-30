"""
Data Transfer Objects

This module contains DTOs for requests and responses
in the verification service application layer.
"""

from .requests import (
    BatchCalculateSERRequest,
    CalculateSERRequest,
    CompleteValidationSessionRequest,
    GetSERComparisonRequest,
    GetSpeakerSERAnalysisRequest,
    StartValidationSessionRequest,
    SubmitMTFeedbackRequest,
)
from .responses import (
    BatchSERCalculationResponse,
    ErrorResponse,
    MTFeedbackResponse,
    SERCalculationResponse,
    SERComparisonResponse,
    SpeakerSERAnalysisResponse,
    ValidationSessionResponse,
    ValidationTestDataResponse,
)

__all__ = [
    # Requests
    "CalculateSERRequest",
    "BatchCalculateSERRequest",
    "StartValidationSessionRequest",
    "SubmitMTFeedbackRequest",
    "CompleteValidationSessionRequest",
    "GetSERComparisonRequest",
    "GetSpeakerSERAnalysisRequest",
    # Responses
    "SERCalculationResponse",
    "BatchSERCalculationResponse",
    "ValidationSessionResponse",
    "MTFeedbackResponse",
    "SERComparisonResponse",
    "SpeakerSERAnalysisResponse",
    "ValidationTestDataResponse",
    "ErrorResponse",
]
