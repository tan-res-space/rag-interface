"""
Domain Events

This module contains domain events that represent significant business events
in the user management domain.
"""

from .domain_events import (
    BaseDomainEvent,
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
    "UserDeletedEvent"
]
