"""
Shared Domain Components

This module contains domain models, entities, value objects, and events
that are shared across multiple services in the RAG Interface System.

Components:
- entities: Common domain entities used across services
- value_objects: Shared value objects and enums
- events: Domain events for inter-service communication
- exceptions: Common domain exceptions
"""

from .value_objects import BucketType, ErrorStatus, SeverityLevel

__all__ = [
    "BucketType",
    "ErrorStatus",
    "SeverityLevel",
]
