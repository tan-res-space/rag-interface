"""
Domain Services

This module contains domain services that implement business logic
that doesn't naturally fit within a single entity.

Domain services are stateless and contain pure business logic.
"""

from .categorization_service import ErrorCategorizationService
from .validation_service import ErrorValidationService

__all__ = ["ErrorValidationService", "ErrorCategorizationService"]
