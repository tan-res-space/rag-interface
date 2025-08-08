"""
Secondary Ports (Driven Adapters)

These ports define interfaces for external dependencies that the application
layer needs to interact with, such as databases, message queues, and external services.
"""

from .repository_port import ErrorReportRepository
from .event_publisher_port import EventPublisher

__all__ = [
    "ErrorReportRepository",
    "EventPublisher"
]
