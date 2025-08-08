"""
Event Bus Adapter Factory

This module contains the factory for creating event bus adapters
based on configuration.
"""

from src.error_reporting_service.infrastructure.config.messaging_config import (
    EventBusConfig, EventBusType
)
from src.error_reporting_service.infrastructure.adapters.messaging.abstract.event_bus_adapter import (
    IEventBusAdapter
)


class EventBusAdapterFactory:
    """Factory for creating event bus adapters"""
    
    @staticmethod
    async def create(config: EventBusConfig) -> IEventBusAdapter:
        """
        Create event bus adapter based on configuration.
        
        Args:
            config: Event bus configuration
            
        Returns:
            Event bus adapter instance
            
        Raises:
            ValueError: If event bus type is not supported
        """
        if config.type == EventBusType.KAFKA:
            from .kafka.adapter import KafkaAdapter
            bootstrap_servers = config.get_connection_string()
            return KafkaAdapter(bootstrap_servers, config.client_id)
        
        elif config.type == EventBusType.AZURE_SERVICEBUS:
            from .azure_servicebus.adapter import AzureServiceBusAdapter
            return AzureServiceBusAdapter(config.connection_string)
        
        elif config.type == EventBusType.AWS_SQS:
            from .aws_sqs.adapter import AWSSQSAdapter
            return AWSSQSAdapter(
                region_name=config.region_name,
                access_key_id=config.access_key_id,
                secret_access_key=config.secret_access_key
            )
        
        elif config.type == EventBusType.RABBITMQ:
            from .rabbitmq.adapter import RabbitMQAdapter
            return RabbitMQAdapter(config.connection_string, config.virtual_host)
        
        elif config.type == EventBusType.IN_MEMORY:
            from .in_memory.adapter import InMemoryEventBusAdapter
            return InMemoryEventBusAdapter()
        
        else:
            # Default to in-memory for unsupported types
            from .in_memory.adapter import InMemoryEventBusAdapter
            return InMemoryEventBusAdapter()
    
    @staticmethod
    def get_supported_types() -> list:
        """Get list of supported event bus types"""
        return [bus_type.value for bus_type in EventBusType]
