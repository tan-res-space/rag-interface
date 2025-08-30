"""
Infrastructure Adapters

This module contains all adapter implementations for the User Management Service.
"""

from .auth import PasswordServiceAdapter, TokenServiceAdapter
from .database import DatabaseAdapterFactory, InMemoryUserRepositoryAdapter
from .messaging import EventBusAdapterFactory, InMemoryEventPublisherAdapter

__all__ = [
    "DatabaseAdapterFactory",
    "InMemoryUserRepositoryAdapter",
    "EventBusAdapterFactory",
    "InMemoryEventPublisherAdapter",
    "PasswordServiceAdapter",
    "TokenServiceAdapter",
]
