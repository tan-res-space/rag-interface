"""
Error Validation Service

Domain service containing business logic for validating error reports.
This service is stateless and contains pure business logic.
"""

from dataclasses import dataclass
from typing import List, Set, Optional, Dict, Any
from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport, SeverityLevel
)


@dataclass
class ValidationError:
    """Represents a validation error with code, message, and field information"""
    code: str
    message: str
    field: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation containing validity status, errors, and warnings"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]

    def __init__(self, is_valid: bool = True, errors: List[ValidationError] = None, warnings: List[ValidationError] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []


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

    async def validate_error_report_request(self, request) -> ValidationResult:
        """
        Validate error report request DTO.

        Args:
            request: SubmitErrorReportRequest to validate

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []

        # Validate UUIDs
        try:
            from uuid import UUID
            UUID(request.job_id)
        except (ValueError, AttributeError):
            errors.append(ValidationError("INVALID_UUID", "Invalid job_id format", "job_id"))

        try:
            UUID(request.speaker_id)
        except (ValueError, AttributeError):
            errors.append(ValidationError("INVALID_UUID", "Invalid speaker_id format", "speaker_id"))

        try:
            UUID(request.reported_by)
        except (ValueError, AttributeError):
            errors.append(ValidationError("INVALID_UUID", "Invalid reported_by format", "reported_by"))

        # Validate text fields
        if not request.original_text or not request.original_text.strip():
            errors.append(ValidationError("EMPTY_FIELD", "original_text cannot be empty", "original_text"))

        if not request.corrected_text or not request.corrected_text.strip():
            errors.append(ValidationError("EMPTY_FIELD", "corrected_text cannot be empty", "corrected_text"))

        # Validate position range
        if request.start_position < 0:
            errors.append(ValidationError("INVALID_POSITION_RANGE", "start_position must be non-negative", "start_position"))

        if request.end_position <= request.start_position:
            errors.append(ValidationError("INVALID_POSITION_RANGE", "end_position must be greater than start_position", "end_position"))

        # Validate categories
        if not request.error_categories:
            errors.append(ValidationError("EMPTY_FIELD", "error_categories cannot be empty", "error_categories"))

        # Validate severity level
        valid_severities = ["low", "medium", "high", "critical"]
        if request.severity_level not in valid_severities:
            errors.append(ValidationError("INVALID_SEVERITY", f"severity_level must be one of {valid_severities}", "severity_level"))

        # Check context notes length
        if request.context_notes and len(request.context_notes) > 1000:
            errors.append(ValidationError("TEXT_TOO_LONG", "context_notes exceeds maximum length of 1000 characters", "context_notes"))

        # Add warnings for potential issues
        if request.original_text and len(request.original_text) > 5000:
            warnings.append(ValidationError("LONG_TEXT", "original_text is very long, consider splitting", "original_text"))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_text_length(self, text: str) -> ValidationResult:
        """Validate text length constraints"""
        errors = []

        if not text:
            errors.append(ValidationError("EMPTY_TEXT", "Text cannot be empty", "text"))
        elif len(text) > 10000:
            errors.append(ValidationError("TEXT_TOO_LONG", "Text exceeds maximum length of 10000 characters", "text"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_position_range(self, text: str, start_pos: int, end_pos: int) -> ValidationResult:
        """Validate position range against text"""
        errors = []

        if end_pos <= start_pos:
            errors.append(ValidationError("INVALID_RANGE", "end_position must be greater than start_position", "position"))

        if start_pos < 0:
            errors.append(ValidationError("NEGATIVE_POSITION", "start_position must be non-negative", "start_position"))

        if end_pos > len(text):
            errors.append(ValidationError("OUT_OF_BOUNDS", "position range exceeds text length", "end_position"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_severity_level(self, severity: str) -> ValidationResult:
        """Validate severity level"""
        errors = []
        valid_levels = ["low", "medium", "high", "critical"]

        if severity not in valid_levels:
            errors.append(ValidationError("INVALID_SEVERITY", f"Invalid severity level: {severity}", "severity_level"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_custom_categories(self, categories: List[str]) -> ValidationResult:
        """Validate custom error categories"""
        errors = []

        for category in categories:
            if not category or not category.strip():
                errors.append(ValidationError("EMPTY_CATEGORY", "Category cannot be empty", "categories"))
            elif not category.replace("_", "").isalnum():
                errors.append(ValidationError("INVALID_CATEGORY_FORMAT", f"Invalid category format: {category}", "categories"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_medical_terminology_context(self, error_report: ErrorReport) -> ValidationResult:
        """Validate medical terminology in context"""
        # For medical terminology errors, ensure high severity
        if "medical_terminology" in error_report.error_categories:
            if error_report.severity_level != SeverityLevel.HIGH and error_report.severity_level != SeverityLevel.CRITICAL:
                warnings = [ValidationError("SEVERITY_MISMATCH", "Medical terminology errors should typically be high or critical severity", "severity_level")]
                return ValidationResult(is_valid=True, warnings=warnings)

        return ValidationResult(is_valid=True)

    def validate_duplicate_error(self, error_report: ErrorReport, existing_errors: List[ErrorReport]) -> ValidationResult:
        """Check for duplicate error reports"""
        errors = []

        for existing in existing_errors:
            if (existing.job_id == error_report.job_id and
                existing.speaker_id == error_report.speaker_id and
                existing.start_position == error_report.start_position and
                existing.end_position == error_report.end_position and
                existing.original_text == error_report.original_text):
                errors.append(ValidationError("DUPLICATE_ERROR", "Duplicate error report detected", "error_report"))
                break

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_error_consistency(self, error_report: ErrorReport) -> ValidationResult:
        """Validate consistency between original and corrected text"""
        errors = []

        if error_report.original_text == error_report.corrected_text:
            errors.append(ValidationError("TEXT_CONSISTENCY", "Original and corrected text cannot be identical", "corrected_text"))

        # Check if the specified error position actually contains an error
        if (error_report.start_position < len(error_report.original_text) and
            error_report.end_position <= len(error_report.original_text)):
            original_segment = error_report.original_text[error_report.start_position:error_report.end_position]
            corrected_segment = error_report.corrected_text[error_report.start_position:error_report.end_position]

            if original_segment == corrected_segment:
                errors.append(ValidationError("TEXT_CONSISTENCY", "No actual change detected in specified position range", "position"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_context_window(self, error_report: ErrorReport, min_context: int = 10) -> ValidationResult:
        """Validate sufficient context around error"""
        errors = []

        text_length = len(error_report.original_text)
        context_before = error_report.start_position
        context_after = text_length - error_report.end_position

        if context_before < min_context and context_after < min_context and text_length > min_context * 2:
            errors.append(ValidationError("INSUFFICIENT_CONTEXT", "Insufficient context around error for proper analysis", "context"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_speaker_consistency(self, error_reports: List[ErrorReport]) -> ValidationResult:
        """Validate consistency across error reports for same speaker"""
        # This is a placeholder for speaker-specific validation logic
        return ValidationResult(is_valid=True)

    def validate_temporal_consistency(self, error_report: ErrorReport) -> ValidationResult:
        """Validate temporal consistency of error report"""
        errors = []

        from datetime import datetime
        now = datetime.utcnow()

        if error_report.error_timestamp > now:
            errors.append(ValidationError("FUTURE_TIMESTAMP", "Error timestamp cannot be in the future", "error_timestamp"))

        if error_report.reported_at > now:
            errors.append(ValidationError("FUTURE_TIMESTAMP", "Reported timestamp cannot be in the future", "reported_at"))

        if error_report.error_timestamp > error_report.reported_at:
            errors.append(ValidationError("TEMPORAL_INCONSISTENCY", "Error timestamp cannot be after reported timestamp", "timestamps"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_error_batch(self, error_reports: List[ErrorReport]) -> ValidationResult:
        """Validate a batch of error reports"""
        all_errors = []
        all_warnings = []

        for i, error_report in enumerate(error_reports):
            # Validate individual error report
            completeness_issues = self.validate_error_report_completeness(error_report)
            for issue in completeness_issues:
                all_errors.append(ValidationError("BATCH_VALIDATION", f"Error {i}: {issue}", f"error_{i}"))

            # Validate temporal consistency
            temporal_result = self.validate_temporal_consistency(error_report)
            all_errors.extend(temporal_result.errors)
            all_warnings.extend(temporal_result.warnings)

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )

    def validate_error_report(self, error_report: ErrorReport) -> ValidationResult:
        """Comprehensive validation of error report"""
        all_errors = []
        all_warnings = []

        # Basic completeness validation
        completeness_issues = self.validate_error_report_completeness(error_report)
        for issue in completeness_issues:
            all_errors.append(ValidationError("COMPLETENESS", issue, "error_report"))

        # Consistency validation
        consistency_result = self.validate_error_consistency(error_report)
        all_errors.extend(consistency_result.errors)

        # Temporal validation
        temporal_result = self.validate_temporal_consistency(error_report)
        all_errors.extend(temporal_result.errors)

        # Medical terminology context validation
        medical_result = self.validate_medical_terminology_context(error_report)
        all_warnings.extend(medical_result.warnings)

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )
