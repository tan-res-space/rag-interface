"""
Shared Value Objects

Common value objects and enums that are used across multiple services.
These represent immutable values and shared enumerations.
"""

from .bucket_type import BucketType
from .error_status import ErrorStatus
from .severity_level import SeverityLevel

__all__ = [
    "BucketType",
    "ErrorStatus",
    "SeverityLevel",
]
