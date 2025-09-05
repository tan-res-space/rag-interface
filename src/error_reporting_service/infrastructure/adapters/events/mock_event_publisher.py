"""
Mock Event Publisher Implementation

Simple mock implementation of the EventPublisher interface for testing and development.
"""

from src.error_reporting_service.application.ports.secondary.event_publisher_port import EventPublisher
from src.error_reporting_service.domain.events.domain_events import (
    ErrorDeletedEvent,
    ErrorReportedEvent,
    ErrorUpdatedEvent,
)


class MockEventPublisher(EventPublisher):
    """
    Mock implementation of the event publisher interface.
    
    Stores events in memory for testing and development purposes.
    Not suitable for production use.
    """

    def __init__(self):
        """Initialize the mock event publisher"""
        self._published_events = []

    async def publish_error_reported(self, event: ErrorReportedEvent) -> None:
        """
        Publish an error reported event (mock implementation).

        Args:
            event: The error reported event to publish
        """
        self._published_events.append({
            "type": "error_reported",
            "event": event,
            "timestamp": event.timestamp
        })
        print(f"Mock: Published error reported event for error {event.error_id}")

    async def publish_error_updated(self, event: ErrorUpdatedEvent) -> None:
        """
        Publish an error updated event (mock implementation).

        Args:
            event: The error updated event to publish
        """
        self._published_events.append({
            "type": "error_updated", 
            "event": event,
            "timestamp": event.timestamp
        })
        print(f"Mock: Published error updated event for error {event.error_id}")

    async def publish_error_deleted(self, event: ErrorDeletedEvent) -> None:
        """
        Publish an error deleted event (mock implementation).

        Args:
            event: The error deleted event to publish
        """
        self._published_events.append({
            "type": "error_deleted",
            "event": event, 
            "timestamp": event.timestamp
        })
        print(f"Mock: Published error deleted event for error {event.error_id}")

    def get_published_events(self):
        """Get all published events (for testing)"""
        return self._published_events.copy()

    def clear_events(self):
        """Clear all published events (for testing)"""
        self._published_events.clear()
