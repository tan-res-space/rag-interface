"""
In-Memory Event Bus Adapter Implementation

This module contains an in-memory implementation of the IEventBusAdapter interface
for testing and demonstration purposes.
"""

from typing import Dict, Any, Optional, List, Callable
import asyncio
from collections import defaultdict
from copy import deepcopy

from src.error_reporting_service.domain.events.domain_events import BaseEvent
from src.error_reporting_service.infrastructure.adapters.messaging.abstract.event_bus_adapter import (
    IEventBusAdapter, EventMetadata
)


class InMemoryEventBusAdapter(IEventBusAdapter):
    """
    In-memory implementation of the event bus adapter.
    
    Stores events in memory and provides synchronous event handling
    for testing and demonstration purposes.
    """
    
    def __init__(self):
        """Initialize the in-memory event bus adapter"""
        self._topics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._is_started = False
    
    async def publish_event(
        self, 
        topic: str, 
        event: BaseEvent, 
        metadata: Optional[EventMetadata] = None
    ) -> bool:
        """Publish event to in-memory topic"""
        try:
            # Convert event to dictionary for storage
            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "version": event.version,
                "timestamp": event.timestamp,
                "source": event.source,
                "correlation_id": event.correlation_id,
                "payload": event.__dict__
            }
            
            if metadata:
                event_data["metadata"] = metadata.__dict__
            
            # Store event in topic
            self._topics[topic].append(deepcopy(event_data))
            
            # Notify subscribers
            await self._notify_subscribers(topic, event_data)
            
            return True
        except Exception:
            return False
    
    async def subscribe_to_topic(
        self, 
        topic: str, 
        handler: Callable,
        consumer_group: Optional[str] = None
    ) -> None:
        """Subscribe to topic with event handler"""
        self._subscribers[topic].append(handler)
    
    async def create_topic(self, topic: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Create topic if it doesn't exist"""
        if topic not in self._topics:
            self._topics[topic] = []
        return True
    
    async def delete_topic(self, topic: str) -> bool:
        """Delete topic"""
        if topic in self._topics:
            del self._topics[topic]
            if topic in self._subscribers:
                del self._subscribers[topic]
            return True
        return False
    
    async def health_check(self) -> bool:
        """Check if event bus is healthy (always healthy for in-memory)"""
        return True
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for monitoring"""
        return {
            "adapter_type": "in_memory",
            "topics": list(self._topics.keys()),
            "total_events": sum(len(events) for events in self._topics.values()),
            "subscribers": {topic: len(handlers) for topic, handlers in self._subscribers.items()},
            "is_started": self._is_started
        }
    
    async def start(self) -> None:
        """Start the event bus adapter"""
        self._is_started = True
    
    async def stop(self) -> None:
        """Stop the event bus adapter"""
        self._is_started = False
        self._topics.clear()
        self._subscribers.clear()
    
    async def _notify_subscribers(self, topic: str, event_data: Dict[str, Any]) -> None:
        """Notify all subscribers of a topic about a new event"""
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                try:
                    # Call handler asynchronously
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data)
                    else:
                        handler(event_data)
                except Exception:
                    # Log error in real implementation
                    pass
    
    # Additional methods for testing
    def get_events_for_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get all events for a topic (for testing)"""
        return deepcopy(self._topics.get(topic, []))
    
    def get_event_count(self, topic: str) -> int:
        """Get event count for a topic (for testing)"""
        return len(self._topics.get(topic, []))
    
    def clear_all_events(self) -> None:
        """Clear all events (for testing)"""
        self._topics.clear()
    
    def clear_topic(self, topic: str) -> None:
        """Clear events for a specific topic (for testing)"""
        if topic in self._topics:
            self._topics[topic].clear()
