"""
Shared Type Definitions

Common type definitions, interfaces, and type aliases
used across multiple services in the RAG Interface System.

Components:
- common: Common type aliases and basic types
- interfaces: Shared interface definitions
- protocols: Protocol definitions for duck typing
- enums: Shared enumerations
"""

from .common import (
    ID, Timestamp, Metadata, JSONData,
    ResponseStatus, ServiceHealth, ErrorCode,
    PaginationParams, PaginatedResponse,
    ServiceError, Environment, APIVersion,
    HealthCheckResult
)

__all__ = [
    "ID", "Timestamp", "Metadata", "JSONData",
    "ResponseStatus", "ServiceHealth", "ErrorCode",
    "PaginationParams", "PaginatedResponse",
    "ServiceError", "Environment", "APIVersion",
    "HealthCheckResult",
]
