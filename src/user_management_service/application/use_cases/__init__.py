"""
Use Cases

This module contains use cases that orchestrate business workflows
for the User Management Service.
"""

from .authenticate_user import AuthenticateUserUseCase

__all__ = [
    "AuthenticateUserUseCase"
]
