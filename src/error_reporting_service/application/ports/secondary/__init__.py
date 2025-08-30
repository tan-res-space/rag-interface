"""
Secondary Ports (Driven Adapters)

These ports define interfaces for external dependencies that the application
layer needs to interact with, such as databases, message queues, and external services.
"""

from .event_publisher_port import EventPublisher
from .repository_port import ErrorReportRepository

__all__ = ["ErrorReportRepository", "EventPublisher"]
