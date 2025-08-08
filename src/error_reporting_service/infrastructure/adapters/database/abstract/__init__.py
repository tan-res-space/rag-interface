"""
Abstract Database Adapter Interfaces

This module contains the abstract interfaces that define the contract
for database operations in a technology-agnostic way.
"""

from .database_adapter import IDatabaseAdapter

__all__ = [
    "IDatabaseAdapter"
]
