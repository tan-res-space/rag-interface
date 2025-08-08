"""
Abstract Event Bus Adapter Interface

Defines the contract for event bus operations that is technology-agnostic.
This interface can be implemented by different messaging technologies
while maintaining consistent behavior.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

from src.error_reporting_service.domain.events.domain_events import BaseEvent


class MessageDeliveryMode(str, Enum):
    """Enumeration for message delivery modes"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class EventMetadata:
    """Metadata for event publishing"""
    correlation_id: Optional[str] = None
    delivery_mode: MessageDeliveryMode = MessageDeliveryMode.AT_LEAST_ONCE
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    headers: Dict[str, str] = field(default_factory=dict)


class IEventBusAdapter(ABC):
    """
    Abstract interface for event bus operations - messaging system agnostic.
    
    This interface defines the contract that all event bus adapters must implement
    to provide messaging capabilities for the Error Reporting Service.
    """
    
    @abstractmethod
    async def publish_event(
        self, 
        topic: str, 
        event: BaseEvent, 
        metadata: Optional[EventMetadata] = None
    ) -> bool:
        """
        Publish event to specified topic.
        
        Args:
            topic: The topic/queue name to publish to
            event: The domain event to publish
            metadata: Optional metadata for the event
            
        Returns:
            True if event was published successfully, False otherwise
            
        Raises:
            EventBusError: If the publish operation fails
        """
        pass
    
    @abstractmethod
    async def subscribe_to_topic(
        self, 
        topic: str, 
        handler: callable,
        consumer_group: Optional[str] = None
    ) -> None:
        """
        Subscribe to topic with event handler.
        
        Args:
            topic: The topic/queue name to subscribe to
            handler: Async function to handle received events
            consumer_group: Optional consumer group for load balancing
            
        Raises:
            EventBusError: If the subscription fails
        """
        pass
    
    @abstractmethod
    async def create_topic(self, topic: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create topic if it doesn't exist.
        
        Args:
            topic: The topic/queue name to create
            config: Optional configuration for the topic
            
        Returns:
            True if topic was created or already exists, False otherwise
            
        Raises:
            EventBusError: If topic creation fails
        """
        pass
    
    @abstractmethod
    async def delete_topic(self, topic: str) -> bool:
        """
        Delete topic.
        
        Args:
            topic: The topic/queue name to delete
            
        Returns:
            True if topic was deleted, False if not found
            
        Raises:
            EventBusError: If topic deletion fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if event bus is healthy and accessible.
        
        Returns:
            True if event bus is healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information for monitoring.
        
        Returns:
            Dictionary containing connection information
        """
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """
        Start the event bus adapter (initialize connections, etc.).
        
        Raises:
            EventBusError: If startup fails
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the event bus adapter (close connections, cleanup, etc.).
        
        Raises:
            EventBusError: If shutdown fails
        """
        pass
