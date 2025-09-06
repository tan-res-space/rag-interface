"""
Mock Error Categorization Service Implementation

Simple mock implementation for testing and development.
"""

from typing import List
from error_reporting_service.application.ports.secondary.categorization_service_port import ErrorCategorizationService


class MockErrorCategorizationService(ErrorCategorizationService):
    """
    Mock implementation of the error categorization service.
    
    Returns predefined categories for testing purposes.
    """

    async def suggest_categories(self, original_text: str, corrected_text: str) -> List[str]:
        """
        Suggest error categories based on text (mock implementation).

        Args:
            original_text: Original text with errors
            corrected_text: Corrected text

        Returns:
            List of suggested categories
        """
        # Simple keyword-based categorization for testing
        categories = []
        
        text_lower = original_text.lower()
        
        if any(word in text_lower for word in ['hypertension', 'diabetes', 'medication', 'blood pressure']):
            categories.append('medical_terminology')
        
        if any(word in text_lower for word in ['the', 'a', 'an', 'is', 'are']):
            categories.append('grammar')
            
        if any(char.isdigit() for char in original_text):
            categories.append('numerical')
            
        # Default category if none found
        if not categories:
            categories.append('general')
            
        return categories

    async def validate_categories(self, categories: List[str]) -> bool:
        """
        Validate error categories (mock implementation).

        Args:
            categories: List of categories to validate

        Returns:
            Always True for mock implementation
        """
        return len(categories) > 0

    async def get_available_categories(self) -> List[str]:
        """
        Get list of available categories (mock implementation).

        Returns:
            List of available categories
        """
        return [
            'medical_terminology',
            'grammar',
            'pronunciation',
            'numerical',
            'proper_nouns',
            'technical_terms',
            'general'
        ]
