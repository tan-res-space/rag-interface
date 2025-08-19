"""
Domain Layer

This layer contains the business logic and domain entities for the User Management Service.
It is independent of external concerns and contains pure business logic.
"""

from .entities import User, UserRole, UserStatus, Permission, UserProfile
from .services import UserValidationService
from .events import (
    UserCreatedEvent,
    UserActivatedEvent,
    UserSuspendedEvent,
    UserRoleChangedEvent,
    UserLoginSuccessEvent,
    UserLoginFailureEvent,
    UserAccountLockedEvent,
    UserPasswordChangedEvent,
    UserProfileUpdatedEvent,
    UserDeletedEvent
)

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
    "UserDeletedEvent"
]
