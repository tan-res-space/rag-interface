"""
Shared Database Infrastructure

Common database utilities, connection management, and abstractions
used across multiple services.
"""

from .config import DatabaseConfig, DatabaseType

__all__ = [
    "DatabaseConfig",
    "DatabaseType",
]
