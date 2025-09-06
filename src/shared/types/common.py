"""
Common Type Definitions

Basic types and type aliases used across multiple services.
"""

from typing import Any, Dict, List, Optional, TypeVar, Union
from uuid import UUID
from datetime import datetime
from enum import Enum

# Common type aliases
ID = Union[str, UUID]
Timestamp = datetime
Metadata = Dict[str, Any]
JSONData = Dict[str, Any]

# Generic types
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Common response types
class ResponseStatus(str, Enum):
    """Standard response status values"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    PARTIAL = "partial"


class ServiceHealth(str, Enum):
    """Service health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# Pagination types
class PaginationParams:
    """Standard pagination parameters"""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size


class PaginatedResponse:
    """Standard paginated response structure"""
    
    def __init__(
        self,
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        has_next: bool = False,
        has_previous: bool = False
    ):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.has_next = has_next
        self.has_previous = has_previous
        self.total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "items": self.items,
            "pagination": {
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_previous": self.has_previous
            }
        }


# Error types
class ErrorCode(str, Enum):
    """Standard error codes"""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    CONFLICT = "conflict"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMITED = "rate_limited"
    BAD_REQUEST = "bad_request"


class ServiceError(Exception):
    """Base exception for service errors"""
    
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details
            }
        }


# Configuration types
class Environment(str, Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


# API types
class APIVersion(str, Enum):
    """API version identifiers"""
    V1 = "v1"
    V2 = "v2"


# Health check types
class HealthCheckResult:
    """Health check result structure"""
    
    def __init__(
        self,
        service: str,
        status: ServiceHealth,
        timestamp: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None,
        dependencies: Optional[Dict[str, ServiceHealth]] = None
    ):
        self.service = service
        self.status = status
        self.timestamp = timestamp or datetime.utcnow()
        self.details = details or {}
        self.dependencies = dependencies or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "service": self.service,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "dependencies": {k: v.value for k, v in self.dependencies.items()}
        }
