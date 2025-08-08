"""
Error Validation Service

Domain service containing business logic for validating error reports.
This service is stateless and contains pure business logic.
"""

from typing import List, Set
from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport, SeverityLevel
)


class ErrorValidationService:
    """
    Domain service for error validation business logic.
    
    Contains business rules for validating error reports and assessing
    their severity based on domain knowledge.
    """
    
    def __init__(self):
        """Initialize the validation service with business rules"""
        self._valid_categories = {
            "pronunciation",
            "medical_terminology", 
            "grammar",
            "context",
            "speaker_specific",
            "audio_quality",
            "patient_safety",
            "spelling"
        }
        
        self._critical_categories = {
            "patient_safety"
        }
        
        self._high_priority_categories = {
            "medical_terminology"
        }
    
    def validate_error_categories(self, categories: List[str]) -> bool:
        """
        Validate error categories against business rules.
        
        Args:
            categories: List of error category strings
            
        Returns:
            True if all categories are valid, False otherwise
        """
        if not categories:
            return False
        
        return all(category in self._valid_categories for category in categories)
    
    def assess_severity(self, error_report: ErrorReport) -> SeverityLevel:
        """
        Assess error severity based on business rules.
        
        Business rules:
        1. Patient safety errors are always CRITICAL
        2. Medical terminology errors are HIGH priority
        3. Long text errors (>100 chars) are MEDIUM priority
        4. All other errors are LOW priority
        
        Args:
            error_report: The error report to assess
            
        Returns:
            Assessed severity level
        """
        # Check for critical categories first
        if any(category in self._critical_categories for category in error_report.error_categories):
            return SeverityLevel.CRITICAL
        
        # Check for high priority categories
        if any(category in self._high_priority_categories for category in error_report.error_categories):
            return SeverityLevel.HIGH
        
        # Check text length for medium priority
        if len(error_report.original_text) > 100:
            return SeverityLevel.MEDIUM
        
        # Default to low priority
        return SeverityLevel.LOW
    
    def validate_context_integrity(self, error_report: ErrorReport) -> bool:
        """
        Validate error context and position integrity.
        
        Business rules:
        1. Start position must be non-negative
        2. End position must be within text bounds
        3. Position range must be valid
        
        Args:
            error_report: The error report to validate
            
        Returns:
            True if context is valid, False otherwise
        """
        # Check for negative start position
        if error_report.start_position < 0:
            return False
        
        # Check if positions are within text bounds
        text_length = len(error_report.original_text)
        if error_report.start_position >= text_length:
            return False
        
        if error_report.end_position > text_length:
            return False
        
        # Position range validation is handled by the entity itself
        # This method focuses on context-specific validation
        return True
    
    def get_valid_categories(self) -> Set[str]:
        """
        Get the set of valid error categories.
        
        Returns:
            Set of valid category strings
        """
        return self._valid_categories.copy()
    
    def is_critical_category(self, category: str) -> bool:
        """
        Check if a category is considered critical.
        
        Args:
            category: Category string to check
            
        Returns:
            True if category is critical, False otherwise
        """
        return category in self._critical_categories
    
    def is_high_priority_category(self, category: str) -> bool:
        """
        Check if a category is considered high priority.
        
        Args:
            category: Category string to check
            
        Returns:
            True if category is high priority, False otherwise
        """
        return category in self._high_priority_categories
    
    def validate_error_report_completeness(self, error_report: ErrorReport) -> List[str]:
        """
        Validate error report completeness and return any issues.
        
        Args:
            error_report: The error report to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        # Check required fields
        if not error_report.original_text.strip():
            issues.append("Original text cannot be empty")
        
        if not error_report.corrected_text.strip():
            issues.append("Corrected text cannot be empty")
        
        if not error_report.error_categories:
            issues.append("At least one error category is required")
        
        # Check business rules
        if not self.validate_error_categories(error_report.error_categories):
            issues.append("One or more error categories are invalid")
        
        if not self.validate_context_integrity(error_report):
            issues.append("Error position is invalid or out of bounds")
        
        return issues
    
    def calculate_error_impact_score(self, error_report: ErrorReport) -> float:
        """
        Calculate an impact score for the error based on various factors.
        
        Args:
            error_report: The error report to score
            
        Returns:
            Impact score between 0.0 and 1.0
        """
        score = 0.0
        
        # Base score from severity
        severity_scores = {
            SeverityLevel.LOW: 0.2,
            SeverityLevel.MEDIUM: 0.4,
            SeverityLevel.HIGH: 0.7,
            SeverityLevel.CRITICAL: 1.0
        }
        score += severity_scores.get(error_report.severity_level, 0.2)
        
        # Adjust for error length (longer errors may have more impact)
        error_length = error_report.get_error_length()
        if error_length > 50:
            score += 0.1
        elif error_length > 20:
            score += 0.05
        
        # Adjust for medical terminology
        if error_report.is_medical_terminology_error():
            score += 0.1
        
        # Ensure score stays within bounds
        return min(1.0, max(0.0, score))
