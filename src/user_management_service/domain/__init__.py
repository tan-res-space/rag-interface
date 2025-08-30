"""
Domain Layer

This layer contains the business logic and domain entities for the User Management Service.
It is independent of external concerns and contains pure business logic.
"""

from .entities import Permission, User, UserProfile, UserRole, UserStatus
from .events import (
    UserAccountLockedEvent,
    UserActivatedEvent,
    UserCreatedEvent,
    UserDeletedEvent,
    UserLoginFailureEvent,
    UserLoginSuccessEvent,
    UserPasswordChangedEvent,
    UserProfileUpdatedEvent,
    UserRoleChangedEvent,
    UserSuspendedEvent,
)
from .services import UserValidationService

__all__ = [
    # Entities
    "User",
    "UserRole",
    "UserStatus",
    "Permission",
    "UserProfile",
    # Services
    "UserValidationService",
    # Events
    "UserCreatedEvent",
    "UserActivatedEvent",
    "UserSuspendedEvent",
    "UserRoleChangedEvent",
    "UserLoginSuccessEvent",
    "UserLoginFailureEvent",
    "UserAccountLockedEvent",
    "UserPasswordChangedEvent",
    "UserProfileUpdatedEvent",
    "UserDeletedEvent",
]
