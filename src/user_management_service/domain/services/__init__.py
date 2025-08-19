"""
Domain Services

This module contains domain services that implement business logic
that doesn't naturally fit within a single entity.

Domain services are stateless and contain pure business logic.
"""

from .user_validation_service import UserValidationService

__all__ = [
    "UserValidationService"
]
