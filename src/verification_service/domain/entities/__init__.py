"""
Domain Entities

This module contains domain entities that represent core business concepts
in the verification service domain.
"""

from .mt_validation_feedback import ImprovementAssessment, MTValidationFeedback
from .validation_test_session import SessionStatus, ValidationTestSession
from .verification_result import VerificationResult

__all__ = [
    "VerificationResult",
    "ValidationTestSession",
    "SessionStatus",
    "MTValidationFeedback",
    "ImprovementAssessment",
]
