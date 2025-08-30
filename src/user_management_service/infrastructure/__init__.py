"""
Infrastructure Layer

This layer contains adapters that implement the port interfaces defined
in the application layer. It handles external concerns like databases,
authentication services, and message queues.
"""

from .adapters import (
    DatabaseAdapterFactory,
    EventBusAdapterFactory,
    PasswordServiceAdapter,
    TokenServiceAdapter,
)
from .config import settings

__all__ = [
    "DatabaseAdapterFactory",
    "EventBusAdapterFactory",
    "PasswordServiceAdapter",
    "TokenServiceAdapter",
    "settings",
]
