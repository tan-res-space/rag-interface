"""
Quality Score Value Object

Represents quality scores for verification operations with validation and comparison.
Immutable value object following domain-driven design principles.
"""


class QualityScore:
    """
    Value object representing a quality score between 0.0 and 1.0.
    
    Provides validation, comparison, and classification methods for
    quality-based decision making in verification processing.
    """
    
    def __init__(self, value: float):
        """
        Initialize quality score with validation.
        
        Args:
            value: Quality score between 0.0 and 1.0
            
        Raises:
            ValueError: If value is not between 0.0 and 1.0
        """
        if not (0.0 <= value <= 1.0):
            raise ValueError("Quality score must be between 0.0 and 1.0")
        
        self._value = float(value)
    
    @property
    def value(self) -> float:
        """Get the quality score value."""
        return self._value
    
    def is_high_quality(self) -> bool:
        """
        Check if this is a high quality score.
        
        Returns:
            True if quality >= 0.8
        """
        return self._value >= 0.8
    
    def is_medium_quality(self) -> bool:
        """
        Check if this is a medium quality score.
        
        Returns:
            True if 0.6 <= quality < 0.8
        """
        return 0.6 <= self._value < 0.8
    
    def is_low_quality(self) -> bool:
        """
        Check if this is a low quality score.
        
        Returns:
            True if quality < 0.6
        """
        return self._value < 0.6
    
    def get_quality_level(self) -> str:
        """
        Get quality level as string.
        
        Returns:
            "high", "medium", or "low"
        """
        if self.is_high_quality():
            return "high"
        elif self.is_medium_quality():
            return "medium"
        else:
            return "low"
    
    # Comparison methods
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, QualityScore):
            return NotImplemented
        return abs(self._value - other._value) < 1e-9
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, QualityScore):
            return NotImplemented
        return self._value < other._value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(round(self._value, 9))
    
    def __str__(self) -> str:
        """String representation."""
        return str(self._value)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"QualityScore({self._value})"
