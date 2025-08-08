"""
Messaging Configuration

This module contains messaging configuration classes and enums.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class EventBusType(str, Enum):
    """Enumeration for supported event bus types"""
    KAFKA = "kafka"
    AZURE_SERVICEBUS = "azure_servicebus"
    AWS_SQS = "aws_sqs"
    RABBITMQ = "rabbitmq"
    IN_MEMORY = "in_memory"  # For testing


@dataclass
class EventBusConfig:
    """Event bus configuration settings"""
    type: EventBusType = EventBusType.KAFKA
    connection_string: str = "localhost:9092"
    client_id: str = "error-reporting-service"
    
    # Kafka specific
    bootstrap_servers: Optional[str] = None
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    
    # Azure Service Bus specific
    namespace: Optional[str] = None
    shared_access_key_name: Optional[str] = None
    shared_access_key: Optional[str] = None
    
    # AWS SQS specific
    region_name: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    
    # RabbitMQ specific
    virtual_host: str = "/"
    heartbeat: int = 600
    
    def get_connection_string(self) -> str:
        """Get the appropriate connection string for the event bus type"""
        if self.type == EventBusType.KAFKA:
            return self.bootstrap_servers or self.connection_string
        elif self.type == EventBusType.AZURE_SERVICEBUS:
            return self.connection_string
        elif self.type == EventBusType.AWS_SQS:
            return f"sqs://{self.region_name}"
        elif self.type == EventBusType.RABBITMQ:
            return self.connection_string
        elif self.type == EventBusType.IN_MEMORY:
            return "in-memory"
        else:
            raise ValueError(f"Unsupported event bus type: {self.type}")
