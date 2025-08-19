"""
Unit tests for CorrectionMode value object.

Following TDD principles for real-time correction processing components.
Tests focus on correction mode validation and behavior.
"""

import pytest
from src.correction_engine_service.domain.value_objects.correction_mode import CorrectionMode


class TestCorrectionModeCreation:
    """Test correction mode value object creation and validation."""
    
    def test_create_conservative_mode(self):
        """Test creating conservative correction mode."""
        # Arrange & Act
        mode = CorrectionMode.CONSERVATIVE
        
        # Assert
        assert mode.value == "conservative"
        assert mode.confidence_threshold == 0.9
        assert mode.max_corrections == 5
        assert mode.description == "High confidence threshold, fewer corrections"
    
    def test_create_balanced_mode(self):
        """Test creating balanced correction mode."""
        # Arrange & Act
        mode = CorrectionMode.BALANCED
        
        # Assert
        assert mode.value == "balanced"
        assert mode.confidence_threshold == 0.8
        assert mode.max_corrections == 10
        assert mode.description == "Medium confidence threshold, moderate corrections"
    
    def test_create_aggressive_mode(self):
        """Test creating aggressive correction mode."""
        # Arrange & Act
        mode = CorrectionMode.AGGRESSIVE
        
        # Assert
        assert mode.value == "aggressive"
        assert mode.confidence_threshold == 0.6
        assert mode.max_corrections == 20
        assert mode.description == "Low confidence threshold, more corrections"
    
    def test_correction_modes_are_comparable(self):
        """Test that correction modes can be compared by confidence threshold."""
        # Arrange
        conservative = CorrectionMode.CONSERVATIVE
        balanced = CorrectionMode.BALANCED
        aggressive = CorrectionMode.AGGRESSIVE
        
        # Act & Assert
        assert conservative.confidence_threshold > balanced.confidence_threshold
        assert balanced.confidence_threshold > aggressive.confidence_threshold
        assert conservative.max_corrections < balanced.max_corrections
        assert balanced.max_corrections < aggressive.max_corrections
    
    def test_from_string_valid_modes(self):
        """Test creating correction mode from string."""
        # Act & Assert
        assert CorrectionMode.from_string("conservative") == CorrectionMode.CONSERVATIVE
        assert CorrectionMode.from_string("balanced") == CorrectionMode.BALANCED
        assert CorrectionMode.from_string("aggressive") == CorrectionMode.AGGRESSIVE
    
    def test_from_string_case_insensitive(self):
        """Test creating correction mode from string is case insensitive."""
        # Act & Assert
        assert CorrectionMode.from_string("CONSERVATIVE") == CorrectionMode.CONSERVATIVE
        assert CorrectionMode.from_string("Balanced") == CorrectionMode.BALANCED
        assert CorrectionMode.from_string("AGGRESSIVE") == CorrectionMode.AGGRESSIVE
    
    def test_from_string_invalid_mode_raises_error(self):
        """Test that invalid mode string raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid correction mode"):
            CorrectionMode.from_string("invalid")
        
        with pytest.raises(ValueError, match="Invalid correction mode"):
            CorrectionMode.from_string("")
    
    def test_is_more_conservative_than(self):
        """Test comparing conservativeness of modes."""
        # Arrange
        conservative = CorrectionMode.CONSERVATIVE
        balanced = CorrectionMode.BALANCED
        aggressive = CorrectionMode.AGGRESSIVE
        
        # Act & Assert
        assert conservative.is_more_conservative_than(balanced)
        assert conservative.is_more_conservative_than(aggressive)
        assert balanced.is_more_conservative_than(aggressive)
        assert not balanced.is_more_conservative_than(conservative)
        assert not aggressive.is_more_conservative_than(balanced)
    
    def test_is_more_aggressive_than(self):
        """Test comparing aggressiveness of modes."""
        # Arrange
        conservative = CorrectionMode.CONSERVATIVE
        balanced = CorrectionMode.BALANCED
        aggressive = CorrectionMode.AGGRESSIVE
        
        # Act & Assert
        assert aggressive.is_more_aggressive_than(balanced)
        assert aggressive.is_more_aggressive_than(conservative)
        assert balanced.is_more_aggressive_than(conservative)
        assert not balanced.is_more_aggressive_than(aggressive)
        assert not conservative.is_more_aggressive_than(balanced)
    
    def test_should_apply_correction_with_confidence(self):
        """Test whether correction should be applied based on confidence."""
        # Arrange
        conservative = CorrectionMode.CONSERVATIVE
        balanced = CorrectionMode.BALANCED
        aggressive = CorrectionMode.AGGRESSIVE
        
        # Act & Assert
        # High confidence - all modes should apply
        assert conservative.should_apply_correction(0.95)
        assert balanced.should_apply_correction(0.95)
        assert aggressive.should_apply_correction(0.95)
        
        # Medium confidence - balanced and aggressive should apply
        assert not conservative.should_apply_correction(0.85)
        assert balanced.should_apply_correction(0.85)
        assert aggressive.should_apply_correction(0.85)
        
        # Low confidence - only aggressive should apply
        assert not conservative.should_apply_correction(0.65)
        assert not balanced.should_apply_correction(0.65)
        assert aggressive.should_apply_correction(0.65)
        
        # Very low confidence - none should apply
        assert not conservative.should_apply_correction(0.5)
        assert not balanced.should_apply_correction(0.5)
        assert not aggressive.should_apply_correction(0.5)


class TestCorrectionModeBusinessRules:
    """Test business rules and edge cases for correction modes."""
    
    def test_default_mode_is_balanced(self):
        """Test that default correction mode is balanced."""
        # Act
        default_mode = CorrectionMode.default()
        
        # Assert
        assert default_mode == CorrectionMode.BALANCED
    
    def test_mode_for_real_time_processing(self):
        """Test recommended mode for real-time processing."""
        # Act
        real_time_mode = CorrectionMode.for_real_time()
        
        # Assert
        assert real_time_mode == CorrectionMode.BALANCED
        assert real_time_mode.confidence_threshold >= 0.8  # High enough for quality
        assert real_time_mode.max_corrections <= 10  # Limited for performance
    
    def test_mode_for_batch_processing(self):
        """Test recommended mode for batch processing."""
        # Act
        batch_mode = CorrectionMode.for_batch_processing()
        
        # Assert
        assert batch_mode == CorrectionMode.AGGRESSIVE
        assert batch_mode.max_corrections >= 15  # More corrections allowed
    
    def test_mode_for_high_accuracy_requirements(self):
        """Test recommended mode for high accuracy requirements."""
        # Act
        high_accuracy_mode = CorrectionMode.for_high_accuracy()
        
        # Assert
        assert high_accuracy_mode == CorrectionMode.CONSERVATIVE
        assert high_accuracy_mode.confidence_threshold >= 0.9  # Very high confidence
    
    def test_correction_mode_immutability(self):
        """Test that correction modes are immutable."""
        # Arrange
        mode = CorrectionMode.BALANCED
        
        # Act & Assert - should not be able to modify attributes
        with pytest.raises(AttributeError):
            mode.confidence_threshold = 0.5
        
        with pytest.raises(AttributeError):
            mode.max_corrections = 100
    
    def test_all_modes_have_valid_thresholds(self):
        """Test that all correction modes have valid confidence thresholds."""
        # Act & Assert
        for mode in CorrectionMode:
            assert 0.0 <= mode.confidence_threshold <= 1.0
            assert mode.max_corrections > 0
            assert mode.max_corrections <= 50  # Reasonable upper limit
            assert len(mode.description) > 0
