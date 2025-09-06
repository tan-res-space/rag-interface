"""
Error Reporting Service

Core error management and processing service following Hexagonal Architecture.
Handles error submission, validation, categorization, and processing workflows.

Architecture:
- domain: Core business logic and entities
- application: Use cases and application services  
- infrastructure: Adapters for external concerns

Documentation:
- Architecture Design: docs/architecture/01_Error_Reporting_Service_Design.md
- API Reference: docs/api/enhanced_error_reporting_api.md
- User Guide: docs/user-guides/ASR_Error_Reporting_PRD.md
"""

__version__ = "1.0.0"

# Service metadata
SERVICE_NAME = "error_reporting"
SERVICE_PORT = 8000
SERVICE_DESCRIPTION = "Core error management and processing service"

__all__ = [
    "SERVICE_NAME",
    "SERVICE_PORT", 
    "SERVICE_DESCRIPTION",
]
