"""
Mock Event Publisher

Implements the EventPublisher port with no-op methods for development/testing.
"""

from error_reporting_service.application.ports.secondary.event_publisher_port import (
    EventPublisher,
)


class MockEventPublisher(EventPublisher):
    async def publish_error_reported(self, event) -> None:  # type: ignore[override]
        return None

    async def publish_error_updated(self, event) -> None:  # type: ignore[override]
        return None

    async def publish_error_deleted(self, event) -> None:  # type: ignore[override]
        return None

