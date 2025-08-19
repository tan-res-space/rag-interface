"""
Confidence Score Value Object

Represents confidence scores for correction operations with validation and comparison.
Immutable value object following domain-driven design principles.
"""

from typing import List


class ConfidenceScore:
    """
    Value object representing a confidence score between 0.0 and 1.0.
    
    Provides validation, comparison, and classification methods for
    confidence-based decision making in correction processing.
    """
    
    def __init__(self, value: float):
        """
        Initialize confidence score with validation.
        
        Args:
            value: Confidence score between 0.0 and 1.0
            
        Raises:
            ValueError: If value is not between 0.0 and 1.0
        """
        if not (0.0 <= value <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        self._value = float(value)
    
    @property
    def value(self) -> float:
        """Get the confidence score value."""
        return self._value
    
    @classmethod
    def from_percentage(cls, percentage: float) -> "ConfidenceScore":
        """
        Create confidence score from percentage value.
        
        Args:
            percentage: Percentage value between 0.0 and 100.0
            
        Returns:
            ConfidenceScore instance
            
        Raises:
            ValueError: If percentage is not between 0.0 and 100.0
        """
        if not (0.0 <= percentage <= 100.0):
            raise ValueError("Percentage must be between 0.0 and 100.0")
        
        return cls(percentage / 100.0)
    
    def is_high_confidence(self) -> bool:
        """
        Check if this is a high confidence score.
        
        Returns:
            True if confidence >= 0.9
        """
        return self._value >= 0.9
    
    def is_medium_confidence(self) -> bool:
        """
        Check if this is a medium confidence score.
        
        Returns:
            True if 0.6 <= confidence < 0.9
        """
        return 0.6 <= self._value < 0.9
    
    def is_low_confidence(self) -> bool:
        """
        Check if this is a low confidence score.
        
        Returns:
            True if confidence < 0.6
        """
        return self._value < 0.6
    
    def get_confidence_level(self) -> str:
        """
        Get confidence level as string.
        
        Returns:
            "high", "medium", or "low"
        """
        if self.is_high_confidence():
            return "high"
        elif self.is_medium_confidence():
            return "medium"
        else:
            return "low"
    
    def meets_threshold(self, threshold: float) -> bool:
        """
        Check if confidence meets or exceeds threshold.
        
        Args:
            threshold: Threshold value to check against
            
        Returns:
            True if confidence >= threshold
        """
        return self._value >= threshold
    
    def to_percentage(self, decimal_places: int = 1) -> float:
        """
        Convert confidence score to percentage.
        
        Args:
            decimal_places: Number of decimal places to round to
            
        Returns:
            Percentage value
        """
        percentage = self._value * 100.0
        return round(percentage, decimal_places)
    
    @classmethod
    def combine_average(cls, scores: List["ConfidenceScore"]) -> "ConfidenceScore":
        """
        Combine multiple confidence scores using average.
        
        Args:
            scores: List of confidence scores to combine
            
        Returns:
            Combined confidence score
            
        Raises:
            ValueError: If scores list is empty
        """
        if not scores:
            raise ValueError("Cannot combine empty list of scores")
        
        total = sum(score.value for score in scores)
        average = total / len(scores)
        return cls(average)
    
    @classmethod
    def combine_weighted(
        cls, 
        scores: List["ConfidenceScore"], 
        weights: List[float]
    ) -> "ConfidenceScore":
        """
        Combine multiple confidence scores using weighted average.
        
        Args:
            scores: List of confidence scores to combine
            weights: List of weights for each score
            
        Returns:
            Combined confidence score
            
        Raises:
            ValueError: If scores is empty or weights don't match scores
        """
        if not scores:
            raise ValueError("Cannot combine empty list of scores")
        
        if len(scores) != len(weights):
            raise ValueError("Number of weights must match number of scores")
        
        weighted_sum = sum(score.value * weight for score, weight in zip(scores, weights))
        weight_sum = sum(weights)
        
        if weight_sum == 0:
            raise ValueError("Sum of weights cannot be zero")
        
        weighted_average = weighted_sum / weight_sum
        return cls(weighted_average)
    
    # Comparison methods
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return abs(self._value - other._value) < 1e-9
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self._value < other._value
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self._value <= other._value
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self._value > other._value
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self._value >= other._value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(round(self._value, 9))  # Round to avoid floating point issues
    
    def __str__(self) -> str:
        """String representation."""
        return str(self._value)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ConfidenceScore({self._value})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "value": self._value,
            "percentage": self.to_percentage(),
            "level": self.get_confidence_level()
        }
