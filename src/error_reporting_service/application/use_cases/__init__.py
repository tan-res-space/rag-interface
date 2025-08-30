"""
Application Use Cases

This module contains use cases that implement the application's business workflows.
Use cases orchestrate domain logic and coordinate between domain services and infrastructure.
"""

from .submit_error_report import SubmitErrorReportUseCase

__all__ = ["SubmitErrorReportUseCase"]
