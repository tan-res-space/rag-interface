"""
Domain Events

This module contains domain events that represent significant business events
in the user management domain.
"""

from .domain_events import (
    BaseDomainEvent,
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

__all__ = [
    "BaseDomainEvent",
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
