"""
Event Publisher Port Interface

Defines the contract for publishing domain events.
This is a secondary port (driven adapter) that will be implemented
by infrastructure adapters.
"""

from abc import ABC, abstractmethod

from error_reporting_service.domain.events.domain_events import (
    ErrorDeletedEvent,
    ErrorReportedEvent,
    ErrorUpdatedEvent,
)


class EventPublisher(ABC):
    """
    Abstract event publisher interface for domain events.

    This port defines the contract that infrastructure adapters must implement
    to provide event publishing capabilities.
    """

    @abstractmethod
    async def publish_error_reported(self, event: ErrorReportedEvent) -> None:
        """
        Publish an error reported event.

        Args:
            event: The error reported event to publish

        Raises:
            EventPublishingError: If the publish operation fails
        """
        pass

    @abstractmethod
    async def publish_error_updated(self, event: ErrorUpdatedEvent) -> None:
        """
        Publish an error updated event.

        Args:
            event: The error updated event to publish

        Raises:
            EventPublishingError: If the publish operation fails
        """
        pass

    @abstractmethod
    async def publish_error_deleted(self, event: ErrorDeletedEvent) -> None:
        """
        Publish an error deleted event.

        Args:
            event: The error deleted event to publish

        Raises:
            EventPublishingError: If the publish operation fails
        """
        pass
