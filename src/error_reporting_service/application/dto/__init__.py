"""
Data Transfer Objects (DTOs)

This module contains DTOs for request and response models used in the application layer.
DTOs define the contract between the application and external systems.
"""

from .requests import SubmitErrorReportRequest
from .responses import SubmitErrorReportResponse

__all__ = [
    "SubmitErrorReportRequest",
    "SubmitErrorReportResponse"
]
