"""
Domain Entities

This module contains the core domain entities that represent the business concepts
in the Error Reporting Service domain.

Entities are objects that have a distinct identity and lifecycle.
They encapsulate business rules and maintain data consistency.
"""

from .error_report import ErrorReport, SeverityLevel, ErrorStatus

__all__ = [
    "ErrorReport",
    "SeverityLevel", 
    "ErrorStatus"
]
