"""
Unit tests for VerificationResult domain entity.

Following TDD principles for verification and analytics components.
Tests focus on verification result creation, validation, and business logic.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from src.verification_service.domain.entities.verification_result import (
    VerificationResult,
)
from src.verification_service.domain.value_objects.quality_score import QualityScore
from src.verification_service.domain.value_objects.verification_status import (
    VerificationStatus,
)


class TestVerificationResultCreation:
    """Test verification result entity creation and validation."""

    def test_create_valid_verification_result(self):
        """Test creating a valid verification result."""
        # Arrange
        result_id = uuid4()
        correction_id = uuid4()
        quality_score = QualityScore(0.85)
        status = VerificationStatus.VERIFIED

        # Act
        result = VerificationResult(
            id=result_id,
            correction_id=correction_id,
            quality_score=quality_score,
            status=status,
            verified_by="user123",
            verification_notes="Good correction",
        )

        # Assert
        assert result.id == result_id
        assert result.correction_id == correction_id
        assert result.quality_score == quality_score
        assert result.status == status
        assert result.verified_by == "user123"
        assert result.verification_notes == "Good correction"
        assert isinstance(result.verified_at, datetime)

    def test_create_verification_result_with_empty_verified_by_raises_error(self):
        """Test that empty verified_by raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="verified_by cannot be empty"):
            VerificationResult(
                id=uuid4(),
                correction_id=uuid4(),
                quality_score=QualityScore(0.8),
                status=VerificationStatus.VERIFIED,
                verified_by="",
                verification_notes="test",
            )

    def test_verification_result_is_verified(self):
        """Test checking if result is verified."""
        # Arrange
        verified_result = VerificationResult(
            id=uuid4(),
            correction_id=uuid4(),
            quality_score=QualityScore(0.9),
            status=VerificationStatus.VERIFIED,
            verified_by="user123",
        )

        rejected_result = VerificationResult(
            id=uuid4(),
            correction_id=uuid4(),
            quality_score=QualityScore(0.3),
            status=VerificationStatus.REJECTED,
            verified_by="user123",
        )

        # Act & Assert
        assert verified_result.is_verified()
        assert not rejected_result.is_verified()

    def test_verification_result_is_high_quality(self):
        """Test checking if result is high quality."""
        # Arrange
        high_quality = VerificationResult(
            id=uuid4(),
            correction_id=uuid4(),
            quality_score=QualityScore(0.95),
            status=VerificationStatus.VERIFIED,
            verified_by="user123",
        )

        low_quality = VerificationResult(
            id=uuid4(),
            correction_id=uuid4(),
            quality_score=QualityScore(0.6),
            status=VerificationStatus.VERIFIED,
            verified_by="user123",
        )

        # Act & Assert
        assert high_quality.is_high_quality()
        assert not low_quality.is_high_quality()


class TestVerificationResultMethods:
    """Test verification result methods and business logic."""

    def test_get_verification_summary(self):
        """Test getting verification summary."""
        # Arrange
        result = VerificationResult(
            id=uuid4(),
            correction_id=uuid4(),
            quality_score=QualityScore(0.85),
            status=VerificationStatus.VERIFIED,
            verified_by="user123",
            verification_notes="Excellent correction",
        )

        # Act
        summary = result.get_verification_summary()

        # Assert
        assert "id" in summary
        assert summary["quality_score"] == 0.85
        assert summary["status"] == "verified"
        assert summary["verified_by"] == "user123"
        assert summary["is_verified"] is True
        assert summary["is_high_quality"] is True
