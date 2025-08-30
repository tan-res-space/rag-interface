"""
Domain Events

This module contains domain events that represent significant business occurrences
in the Error Reporting Service domain.

Domain events are used for communication between bounded contexts and
for triggering side effects in response to domain changes.
"""

from .domain_events import ErrorDeletedEvent, ErrorReportedEvent, ErrorUpdatedEvent

__all__ = ["ErrorReportedEvent", "ErrorUpdatedEvent", "ErrorDeletedEvent"]
