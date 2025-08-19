"""
In-Memory Event Publisher Adapter

This adapter provides an in-memory implementation of the event publisher
for testing and demonstration purposes.
"""

import logging
from typing import List

from .....application.ports.event_publisher_port import IEventPublisherPort
from .....domain.events.domain_events import (
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


logger = logging.getLogger(__name__)


class InMemoryEventPublisherAdapter(IEventPublisherPort):
    """
    In-memory implementation of the event publisher adapter.
    
    Stores events in memory for testing and demonstration purposes.
    Not suitable for production use.
    """
    
    def __init__(self):
        """Initialize the in-memory event publisher"""
        self._published_events: List[dict] = []
        
        logger.info("Initialized in-memory event publisher adapter")
    
    async def publish_user_created(self, event: UserCreatedEvent) -> None:
        """Publish user created event"""
        
        event_data = {
            "event_type": "user.created",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.info(f"Published user created event: {event.user_id}")
    
    async def publish_user_activated(self, event: UserActivatedEvent) -> None:
        """Publish user activated event"""
        
        event_data = {
            "event_type": "user.activated",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.info(f"Published user activated event: {event.user_id}")
    
    async def publish_user_suspended(self, event: UserSuspendedEvent) -> None:
        """Publish user suspended event"""
        
        event_data = {
            "event_type": "user.suspended",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.info(f"Published user suspended event: {event.user_id}")
    
    async def publish_user_role_changed(self, event: UserRoleChangedEvent) -> None:
        """Publish user role changed event"""
        
        event_data = {
            "event_type": "user.role_changed",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.info(f"Published user role changed event: {event.user_id}")
    
    async def publish_user_login_success(self, event: UserLoginSuccessEvent) -> None:
        """Publish user login success event"""
        
        event_data = {
            "event_type": "user.login_success",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.debug(f"Published user login success event: {event.user_id}")
    
    async def publish_user_login_failure(self, event: UserLoginFailureEvent) -> None:
        """Publish user login failure event"""
        
        event_data = {
            "event_type": "user.login_failure",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.warning(f"Published user login failure event: {event.username}")
    
    async def publish_user_account_locked(self, event: UserAccountLockedEvent) -> None:
        """Publish user account locked event"""
        
        event_data = {
            "event_type": "user.account_locked",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.warning(f"Published user account locked event: {event.user_id}")
    
    async def publish_user_password_changed(self, event: UserPasswordChangedEvent) -> None:
        """Publish user password changed event"""
        
        event_data = {
            "event_type": "user.password_changed",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.info(f"Published user password changed event: {event.user_id}")
    
    async def publish_user_profile_updated(self, event: UserProfileUpdatedEvent) -> None:
        """Publish user profile updated event"""
        
        event_data = {
            "event_type": "user.profile_updated",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.info(f"Published user profile updated event: {event.user_id}")
    
    async def publish_user_deleted(self, event: UserDeletedEvent) -> None:
        """Publish user deleted event"""
        
        event_data = {
            "event_type": "user.deleted",
            "event": event.dict(),
            "published_at": event.timestamp.isoformat()
        }
        
        self._published_events.append(event_data)
        logger.info(f"Published user deleted event: {event.user_id}")
    
    # Utility methods for testing and monitoring
    def get_published_events(self) -> List[dict]:
        """Get all published events (for testing)"""
        return self._published_events.copy()
    
    def get_events_by_type(self, event_type: str) -> List[dict]:
        """Get events by type (for testing)"""
        return [event for event in self._published_events if event["event_type"] == event_type]
    
    def clear_events(self) -> None:
        """Clear all published events (for testing)"""
        self._published_events.clear()
        logger.debug("Cleared all published events")
    
    def get_event_count(self) -> int:
        """Get total number of published events"""
        return len(self._published_events)
    
    def get_event_count_by_type(self, event_type: str) -> int:
        """Get number of events by type"""
        return len(self.get_events_by_type(event_type))
    
    # Health check methods
    async def health_check(self) -> dict:
        """Perform health check"""
        return {
            "status": "healthy",
            "adapter_type": "in_memory",
            "published_events_count": len(self._published_events)
        }
    
    async def get_connection_info(self) -> dict:
        """Get connection information"""
        return {
            "adapter_type": "in_memory",
            "published_events_count": len(self._published_events),
            "event_types": list(set(event["event_type"] for event in self._published_events))
        }
