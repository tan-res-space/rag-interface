"""
Event Bus Adapter Factory

This module provides a factory for creating event bus adapters based on configuration.
"""

import logging

from ....application.ports.event_publisher_port import IEventPublisherPort
from ...config.settings import EventBusConfig
from .in_memory.adapter import InMemoryEventPublisherAdapter

logger = logging.getLogger(__name__)


class EventBusAdapterFactory:
    """
    Factory for creating event bus adapters.

    Supports multiple event bus types through configuration.
    """

    @staticmethod
    async def create(config: EventBusConfig) -> IEventPublisherPort:
        """
        Create an event bus adapter based on configuration.

        Args:
            config: Event bus configuration

        Returns:
            Event bus adapter instance

        Raises:
            ValueError: If event bus type is not supported
        """

        logger.info(f"Creating event bus adapter for type: {config.type}")

        if config.type == "in_memory":
            adapter = InMemoryEventPublisherAdapter()
            logger.info("Created in-memory event bus adapter")
            return adapter

        elif config.type == "kafka":
            # Kafka adapter would be implemented here
            # For now, fall back to in-memory
            logger.warning("Kafka adapter not implemented, using in-memory adapter")
            adapter = InMemoryEventPublisherAdapter()
            return adapter

        else:
            raise ValueError(f"Unsupported event bus type: {config.type}")

    @staticmethod
    def get_supported_types() -> list:
        """Get list of supported event bus types"""
        return ["in_memory", "kafka"]

    @staticmethod
    async def test_connection(config: EventBusConfig) -> dict:
        """
        Test event bus connection.

        Args:
            config: Event bus configuration

        Returns:
            Connection test results
        """

        try:
            adapter = await EventBusAdapterFactory.create(config)
            health_info = await adapter.health_check()
            connection_info = await adapter.get_connection_info()

            return {
                "status": "success",
                "event_bus_type": config.type,
                "health": health_info,
                "connection": connection_info,
            }

        except Exception as e:
            logger.error(f"Event bus connection test failed: {str(e)}")
            return {"status": "failed", "event_bus_type": config.type, "error": str(e)}
