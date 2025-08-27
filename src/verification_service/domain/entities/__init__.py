"""
Domain Entities

This module contains domain entities that represent core business concepts
in the verification service domain.
"""

from .verification_result import VerificationResult
from .validation_test_session import ValidationTestSession, SessionStatus
from .mt_validation_feedback import MTValidationFeedback, ImprovementAssessment

__all__ = [
    "VerificationResult",
    "ValidationTestSession",
    "SessionStatus",
    "MTValidationFeedback",
    "ImprovementAssessment"
]