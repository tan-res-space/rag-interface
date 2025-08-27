"""
SER (Sentence Edit Rate) Metrics Value Object

Represents comprehensive SER calculation results with validation and analysis methods.
Immutable value object following domain-driven design principles.
"""

from dataclasses import dataclass
from typing import Dict, Any
from decimal import Decimal


@dataclass(frozen=True)
class SERMetrics:
    """
    Value object representing comprehensive SER metrics for sentence pair analysis.
    
    SER (Sentence Edit Rate) measures the quality of ASR output by calculating
    the edit distance normalized by reference length. Lower scores indicate better quality.
    """
    
    ser_score: Decimal
    insert_percentage: Decimal
    delete_percentage: Decimal
    move_percentage: Decimal
    edit_percentage: Decimal
    edit_distance: int
    reference_length: int
    hypothesis_length: int
    quality_score: Decimal  # Derived quality score (100 - SER)
    
    def __post_init__(self):
        """Validate SER metrics after initialization."""
        self._validate_percentages()
        self._validate_distances()
        self._validate_lengths()
        self._validate_consistency()
    
    def _validate_percentages(self) -> None:
        """Validate percentage fields."""
        percentages = [
            self.ser_score, self.insert_percentage, self.delete_percentage,
            self.move_percentage, self.edit_percentage, self.quality_score
        ]
        
        for percentage in percentages:
            if percentage < 0:
                raise ValueError("Percentage values cannot be negative")
            
            # SER can exceed 100% in extreme cases, but others should be reasonable
            if percentage > 200 and percentage != self.ser_score:
                raise ValueError(f"Percentage value {percentage} seems unreasonably high")
    
    def _validate_distances(self) -> None:
        """Validate distance and length fields."""
        if self.edit_distance < 0:
            raise ValueError("edit_distance cannot be negative")
    
    def _validate_lengths(self) -> None:
        """Validate length fields."""
        if self.reference_length <= 0:
            raise ValueError("reference_length must be positive")
        
        if self.hypothesis_length <= 0:
            raise ValueError("hypothesis_length must be positive")
    
    def _validate_consistency(self) -> None:
        """Validate consistency between metrics."""
        # Quality score should be 100 - SER (with some tolerance for rounding)
        expected_quality = 100 - self.ser_score
        if abs(self.quality_score - expected_quality) > Decimal('0.1'):
            raise ValueError("quality_score is inconsistent with ser_score")
        
        # Edit percentage should match SER score
        if abs(self.edit_percentage - self.ser_score) > Decimal('0.1'):
            raise ValueError("edit_percentage is inconsistent with ser_score")
    
    @classmethod
    def create(
        cls,
        ser_score: float,
        insert_percentage: float,
        delete_percentage: float,
        move_percentage: float,
        edit_distance: int,
        reference_length: int,
        hypothesis_length: int
    ) -> "SERMetrics":
        """
        Create SERMetrics with automatic quality score calculation.
        
        Args:
            ser_score: SER score (edit distance / reference length * 100)
            insert_percentage: Percentage of insertions
            delete_percentage: Percentage of deletions
            move_percentage: Percentage of moves/reorderings
            edit_distance: Raw edit distance
            reference_length: Length of reference text
            hypothesis_length: Length of hypothesis text
            
        Returns:
            SERMetrics instance
        """
        ser_decimal = Decimal(str(ser_score))
        quality_score = max(Decimal('0'), Decimal('100') - ser_decimal)
        
        return cls(
            ser_score=ser_decimal,
            insert_percentage=Decimal(str(insert_percentage)),
            delete_percentage=Decimal(str(delete_percentage)),
            move_percentage=Decimal(str(move_percentage)),
            edit_percentage=ser_decimal,  # Edit percentage equals SER score
            edit_distance=edit_distance,
            reference_length=reference_length,
            hypothesis_length=hypothesis_length,
            quality_score=quality_score
        )
    
    def is_high_quality(self) -> bool:
        """
        Check if this represents high quality ASR output.
        
        Returns:
            True if SER score < 5% (high quality threshold)
        """
        return self.ser_score < Decimal('5.0')
    
    def is_medium_quality(self) -> bool:
        """
        Check if this represents medium quality ASR output.
        
        Returns:
            True if 5% <= SER score < 20%
        """
        return Decimal('5.0') <= self.ser_score < Decimal('20.0')
    
    def is_low_quality(self) -> bool:
        """
        Check if this represents low quality ASR output.
        
        Returns:
            True if SER score >= 20%
        """
        return self.ser_score >= Decimal('20.0')
    
    def get_quality_level(self) -> str:
        """
        Get quality level description.
        
        Returns:
            Quality level string
        """
        if self.is_high_quality():
            return "high"
        elif self.is_medium_quality():
            return "medium"
        else:
            return "low"
    
    def get_dominant_error_type(self) -> str:
        """
        Get the dominant error type based on percentages.
        
        Returns:
            Dominant error type
        """
        error_types = {
            "insertions": self.insert_percentage,
            "deletions": self.delete_percentage,
            "moves": self.move_percentage
        }
        
        return max(error_types, key=error_types.get)
    
    def has_significant_improvements_over(self, other: "SERMetrics", threshold: float = 5.0) -> bool:
        """
        Check if this metrics shows significant improvement over another.
        
        Args:
            other: Other SERMetrics to compare against
            threshold: Minimum improvement threshold in percentage points
            
        Returns:
            True if this shows significant improvement
        """
        improvement = other.ser_score - self.ser_score
        return improvement >= Decimal(str(threshold))
    
    def calculate_improvement_percentage(self, baseline: "SERMetrics") -> Decimal:
        """
        Calculate improvement percentage compared to baseline.
        
        Args:
            baseline: Baseline SERMetrics to compare against
            
        Returns:
            Improvement percentage (positive = improvement, negative = degradation)
        """
        if baseline.ser_score == 0:
            return Decimal('0')  # Avoid division by zero
        
        improvement = baseline.ser_score - self.ser_score
        return (improvement / baseline.ser_score) * Decimal('100')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with all metrics
        """
        return {
            "ser_score": float(self.ser_score),
            "insert_percentage": float(self.insert_percentage),
            "delete_percentage": float(self.delete_percentage),
            "move_percentage": float(self.move_percentage),
            "edit_percentage": float(self.edit_percentage),
            "edit_distance": self.edit_distance,
            "reference_length": self.reference_length,
            "hypothesis_length": self.hypothesis_length,
            "quality_score": float(self.quality_score),
            "quality_level": self.get_quality_level(),
            "dominant_error_type": self.get_dominant_error_type()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SERMetrics":
        """
        Create SERMetrics from dictionary.
        
        Args:
            data: Dictionary with metrics data
            
        Returns:
            SERMetrics instance
        """
        return cls(
            ser_score=Decimal(str(data["ser_score"])),
            insert_percentage=Decimal(str(data["insert_percentage"])),
            delete_percentage=Decimal(str(data["delete_percentage"])),
            move_percentage=Decimal(str(data["move_percentage"])),
            edit_percentage=Decimal(str(data["edit_percentage"])),
            edit_distance=data["edit_distance"],
            reference_length=data["reference_length"],
            hypothesis_length=data["hypothesis_length"],
            quality_score=Decimal(str(data["quality_score"]))
        )
    
    def __str__(self) -> str:
        """String representation of SER metrics."""
        return f"SERMetrics(ser={self.ser_score}%, quality={self.quality_score}%)"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"SERMetrics(ser_score={self.ser_score}, quality_score={self.quality_score}, "
            f"edit_distance={self.edit_distance}, ref_len={self.reference_length})"
        )
