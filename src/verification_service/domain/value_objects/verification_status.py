"""
Verification Status Value Object

Defines different statuses for verification processing.
Immutable value object following domain-driven design principles.
"""

from enum import Enum


class VerificationStatus(Enum):
    """
    Enumeration of verification statuses.

    Each status represents a different state in the verification workflow.
    """

    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"

    def is_completed(self) -> bool:
        """
        Check if verification is completed.

        Returns:
            True if status is verified or rejected
        """
        return self in [VerificationStatus.VERIFIED, VerificationStatus.REJECTED]

    def is_pending(self) -> bool:
        """
        Check if verification is pending.

        Returns:
            True if status is pending or needs review
        """
        return self in [VerificationStatus.PENDING, VerificationStatus.NEEDS_REVIEW]

    @classmethod
    def from_string(cls, status_str: str) -> "VerificationStatus":
        """
        Create verification status from string value.

        Args:
            status_str: String representation of the status

        Returns:
            VerificationStatus instance

        Raises:
            ValueError: If status string is invalid
        """
        if not status_str or not status_str.strip():
            raise ValueError("Invalid verification status: empty string")

        status_str = status_str.strip().lower()

        for status in cls:
            if status.value == status_str:
                return status

        raise ValueError(f"Invalid verification status: {status_str}")

    def __str__(self) -> str:
        """String representation of the verification status."""
        return self.value
