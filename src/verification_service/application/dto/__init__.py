"""
Data Transfer Objects

This module contains DTOs for requests and responses
in the verification service application layer.
"""

from .requests import (
    CalculateSERRequest,
    BatchCalculateSERRequest,
    StartValidationSessionRequest,
    SubmitMTFeedbackRequest,
    CompleteValidationSessionRequest,
    GetSERComparisonRequest,
    GetSpeakerSERAnalysisRequest
)

from .responses import (
    SERCalculationResponse,
    BatchSERCalculationResponse,
    ValidationSessionResponse,
    MTFeedbackResponse,
    SERComparisonResponse,
    SpeakerSERAnalysisResponse,
    ValidationTestDataResponse,
    ErrorResponse
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
    "ErrorResponse"
]