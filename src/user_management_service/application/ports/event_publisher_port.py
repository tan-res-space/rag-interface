"""
Event Publisher Port Interface

This module defines the port interface for publishing domain events.
"""

from abc import ABC, abstractmethod

from ...domain.events.domain_events import (
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


class IEventPublisherPort(ABC):
    """
    Port interface for publishing domain events.

    This interface defines the contract for publishing user management
    domain events to the event bus for inter-service communication.
    """

    @abstractmethod
    async def publish_user_created(self, event: UserCreatedEvent) -> None:
        """
        Publish user created event.

        Args:
            event: User created event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_activated(self, event: UserActivatedEvent) -> None:
        """
        Publish user activated event.

        Args:
            event: User activated event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_suspended(self, event: UserSuspendedEvent) -> None:
        """
        Publish user suspended event.

        Args:
            event: User suspended event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_role_changed(self, event: UserRoleChangedEvent) -> None:
        """
        Publish user role changed event.

        Args:
            event: User role changed event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_login_success(self, event: UserLoginSuccessEvent) -> None:
        """
        Publish user login success event.

        Args:
            event: User login success event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_login_failure(self, event: UserLoginFailureEvent) -> None:
        """
        Publish user login failure event.

        Args:
            event: User login failure event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_account_locked(self, event: UserAccountLockedEvent) -> None:
        """
        Publish user account locked event.

        Args:
            event: User account locked event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_password_changed(
        self, event: UserPasswordChangedEvent
    ) -> None:
        """
        Publish user password changed event.

        Args:
            event: User password changed event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_profile_updated(
        self, event: UserProfileUpdatedEvent
    ) -> None:
        """
        Publish user profile updated event.

        Args:
            event: User profile updated event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """

    @abstractmethod
    async def publish_user_deleted(self, event: UserDeletedEvent) -> None:
        """
        Publish user deleted event.

        Args:
            event: User deleted event to publish

        Raises:
            EventPublishingException: If event publishing fails
        """
