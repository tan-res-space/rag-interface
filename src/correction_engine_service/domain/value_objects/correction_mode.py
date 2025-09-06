"""
Correction Mode Value Object

Defines different modes for correction processing with associated thresholds and limits.
Immutable value object following domain-driven design principles.
"""

from enum import Enum


class CorrectionMode(Enum):
    """
    Enumeration of correction processing modes.

    Each mode defines different confidence thresholds and correction limits
    to balance between accuracy and coverage in real-time correction processing.
    """

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

    def __init__(self, value: str):
        """Initialize correction mode with its string value."""
        self._value_ = value

        # Define mode-specific parameters
        if value == "conservative":
            self._confidence_threshold = 0.9
            self._max_corrections = 5
            self._description = "High confidence threshold, fewer corrections"
        elif value == "balanced":
            self._confidence_threshold = 0.8
            self._max_corrections = 10
            self._description = "Medium confidence threshold, moderate corrections"
        elif value == "aggressive":
            self._confidence_threshold = 0.6
            self._max_corrections = 20
            self._description = "Low confidence threshold, more corrections"
        else:
            raise ValueError(f"Invalid correction mode: {value}")

    @property
    def confidence_threshold(self) -> float:
        """Get the confidence threshold for this mode."""
        return self._confidence_threshold

    @property
    def max_corrections(self) -> int:
        """Get the maximum number of corrections for this mode."""
        return self._max_corrections

    @property
    def description(self) -> str:
        """Get the description of this mode."""
        return self._description

    @classmethod
    def from_string(cls, mode_str: str) -> "CorrectionMode":
        """
        Create correction mode from string value.

        Args:
            mode_str: String representation of the mode

        Returns:
            CorrectionMode instance

        Raises:
            ValueError: If mode string is invalid
        """
        if not mode_str or not mode_str.strip():
            raise ValueError("Invalid correction mode: empty string")

        mode_str = mode_str.strip().lower()

        for mode in cls:
            if mode.value == mode_str:
                return mode

        raise ValueError(f"Invalid correction mode: {mode_str}")

    @classmethod
    def default(cls) -> "CorrectionMode":
        """Get the default correction mode."""
        return cls.BALANCED

    @classmethod
    def for_real_time(cls) -> "CorrectionMode":
        """Get recommended mode for real-time processing."""
        return cls.BALANCED

    @classmethod
    def for_batch_processing(cls) -> "CorrectionMode":
        """Get recommended mode for batch processing."""
        return cls.AGGRESSIVE

    @classmethod
    def for_high_accuracy(cls) -> "CorrectionMode":
        """Get recommended mode for high accuracy requirements."""
        return cls.CONSERVATIVE

    def is_more_conservative_than(self, other: "CorrectionMode") -> bool:
        """
        Check if this mode is more conservative than another.

        Args:
            other: Other correction mode to compare with

        Returns:
            True if this mode is more conservative
        """
        return self.confidence_threshold > other.confidence_threshold

    def is_more_aggressive_than(self, other: "CorrectionMode") -> bool:
        """
        Check if this mode is more aggressive than another.

        Args:
            other: Other correction mode to compare with

        Returns:
            True if this mode is more aggressive
        """
        return self.confidence_threshold < other.confidence_threshold

    def should_apply_correction(self, confidence: float) -> bool:
        """
        Determine if a correction should be applied based on confidence.

        Args:
            confidence: Confidence score for the correction (0.0 to 1.0)

        Returns:
            True if correction should be applied
        """
        return confidence >= self.confidence_threshold

    def __str__(self) -> str:
        """String representation of the correction mode."""
        return f"CorrectionMode.{self.name} (threshold={self.confidence_threshold}, max={self.max_corrections})"

    def __repr__(self) -> str:
        """Detailed string representation of the correction mode."""
        return (
            f"CorrectionMode(value='{self.value}', "
            f"confidence_threshold={self.confidence_threshold}, "
            f"max_corrections={self.max_corrections})"
        )

    def to_dict(self) -> dict:
        """Convert correction mode to dictionary representation."""
        return {
            "mode": self.value,
            "confidence_threshold": self.confidence_threshold,
            "max_corrections": self.max_corrections,
            "description": self.description,
        }
