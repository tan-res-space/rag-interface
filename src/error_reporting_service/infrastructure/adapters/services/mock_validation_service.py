"""
Mock Error Validation Service Implementation

Simple mock implementation for testing and development.
"""

from error_reporting_service.application.ports.secondary.validation_service_port import ErrorValidationService
from error_reporting_service.domain.entities.error_report import ErrorReport


class MockErrorValidationService(ErrorValidationService):
    """
    Mock implementation of the error validation service.
    
    Always validates successfully for testing purposes.
    """

    async def validate_error_report(self, error_report: ErrorReport) -> bool:
        """
        Validate an error report (mock implementation).

        Args:
            error_report: The error report to validate

        Returns:
            Always True for mock implementation
        """
        # Basic validation - just check required fields exist
        if not error_report.original_text or not error_report.corrected_text:
            return False
        
        if not error_report.error_categories:
            return False
            
        return True

    async def validate_text_correction(self, original: str, corrected: str) -> bool:
        """
        Validate text correction (mock implementation).

        Args:
            original: Original text
            corrected: Corrected text

        Returns:
            Always True for mock implementation
        """
        return len(original) > 0 and len(corrected) > 0

    async def validate_categories(self, categories: list) -> bool:
        """
        Validate error categories (mock implementation).

        Args:
            categories: List of error categories

        Returns:
            Always True for mock implementation
        """
        return len(categories) > 0
