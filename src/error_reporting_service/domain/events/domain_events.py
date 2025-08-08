"""
Domain Events for Error Reporting Service

Domain events represent significant business occurrences that other parts
of the system may need to react to.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class BaseEvent:
    """Base class for all domain events"""

    event_id: str = ""
    event_type: str = ""
    version: str = ""
    timestamp: datetime = None
    source: str = ""
    correlation_id: str = ""

    def __post_init__(self):
        """Set default values if not provided"""
        if not self.event_id:
            object.__setattr__(self, 'event_id', str(uuid4()))
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.utcnow())
        if not self.source:
            object.__setattr__(self, 'source', 'error-reporting-service')
        if not self.correlation_id:
            object.__setattr__(self, 'correlation_id', str(uuid4()))


@dataclass(frozen=True)
class ErrorReportedEvent(BaseEvent):
    """
    Event published when a new error report is submitted.
    
    This event notifies other services that a new error has been reported
    and may trigger downstream processing such as ML analysis.
    """
    
    # Event metadata
    event_type: str = "error.reported"
    version: str = "1.0"
    
    # Event payload
    error_id: str = ""
    speaker_id: str = ""
    job_id: str = ""
    original_text: str = ""
    corrected_text: str = ""
    categories: List[str] = None
    severity: str = ""
    reported_by: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Set default values for collections"""
        super().__post_init__()
        if self.categories is None:
            object.__setattr__(self, 'categories', [])
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class ErrorUpdatedEvent(BaseEvent):
    """
    Event published when an error report is updated.
    
    This event notifies other services that an error report has been modified.
    """
    
    # Event metadata
    event_type: str = "error.updated"
    version: str = "1.0"
    
    # Event payload
    error_id: str = ""
    updated_fields: Dict[str, Any] = None
    updated_by: str = ""
    previous_values: Dict[str, Any] = None
    
    def __post_init__(self):
        """Set default values for dictionaries"""
        super().__post_init__()
        if self.updated_fields is None:
            object.__setattr__(self, 'updated_fields', {})
        if self.previous_values is None:
            object.__setattr__(self, 'previous_values', {})


@dataclass(frozen=True)
class ErrorDeletedEvent(BaseEvent):
    """
    Event published when an error report is deleted.
    
    This event notifies other services that an error report has been removed.
    """
    
    # Event metadata
    event_type: str = "error.deleted"
    version: str = "1.0"
    
    # Event payload
    error_id: str = ""
    deleted_by: str = ""
    reason: str = ""
