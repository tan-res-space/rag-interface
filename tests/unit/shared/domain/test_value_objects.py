"""
Tests for Shared Value Objects

Unit tests for shared value objects like BucketType, SeverityLevel, and ErrorStatus.
"""

from src.shared.domain.value_objects import BucketType, SeverityLevel, ErrorStatus


class TestBucketType:
    """Test cases for BucketType value object"""
    
    def test_bucket_type_values(self):
        """Test that all bucket type values are correct"""
        assert BucketType.NO_TOUCH.value == "no_touch"
        assert BucketType.LOW_TOUCH.value == "low_touch"
        assert BucketType.MEDIUM_TOUCH.value == "medium_touch"
        assert BucketType.HIGH_TOUCH.value == "high_touch"
    
    def test_get_all_values(self):
        """Test getting all bucket type values"""
        values = BucketType.get_all_values()
        expected = ["no_touch", "low_touch", "medium_touch", "high_touch"]
        assert set(values) == set(expected)
    
    def test_get_progression_order(self):
        """Test bucket progression order"""
        order = BucketType.get_progression_order()
        expected = [BucketType.HIGH_TOUCH, BucketType.MEDIUM_TOUCH, BucketType.LOW_TOUCH, BucketType.NO_TOUCH]
        assert order == expected
    
    def test_get_display_name(self):
        """Test getting display names"""
        assert BucketType.NO_TOUCH.get_display_name() == "No Touch"
        assert BucketType.HIGH_TOUCH.get_display_name() == "High Touch"
    
    def test_get_level(self):
        """Test getting numeric levels"""
        assert BucketType.HIGH_TOUCH.get_level() == 0
        assert BucketType.MEDIUM_TOUCH.get_level() == 1
        assert BucketType.LOW_TOUCH.get_level() == 2
        assert BucketType.NO_TOUCH.get_level() == 3
    
    def test_level_comparison(self):
        """Test level comparison methods"""
        assert BucketType.NO_TOUCH.is_higher_than(BucketType.HIGH_TOUCH)
        assert BucketType.HIGH_TOUCH.is_lower_than(BucketType.NO_TOUCH)
        assert not BucketType.LOW_TOUCH.is_higher_than(BucketType.NO_TOUCH)


class TestSeverityLevel:
    """Test cases for SeverityLevel value object"""
    
    def test_severity_level_values(self):
        """Test that all severity level values are correct"""
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.CRITICAL.value == "critical"
    
    def test_get_all_values(self):
        """Test getting all severity level values"""
        values = SeverityLevel.get_all_values()
        expected = ["low", "medium", "high", "critical"]
        assert set(values) == set(expected)
    
    def test_get_display_name(self):
        """Test getting display names"""
        assert SeverityLevel.LOW.get_display_name() == "Low"
        assert SeverityLevel.CRITICAL.get_display_name() == "Critical"
    
    def test_get_priority(self):
        """Test getting numeric priorities"""
        assert SeverityLevel.LOW.get_priority() == 1
        assert SeverityLevel.MEDIUM.get_priority() == 2
        assert SeverityLevel.HIGH.get_priority() == 3
        assert SeverityLevel.CRITICAL.get_priority() == 4
    
    def test_priority_comparison(self):
        """Test priority comparison methods"""
        assert SeverityLevel.CRITICAL.is_higher_than(SeverityLevel.LOW)
        assert SeverityLevel.LOW.is_lower_than(SeverityLevel.CRITICAL)
        assert not SeverityLevel.MEDIUM.is_higher_than(SeverityLevel.HIGH)


class TestErrorStatus:
    """Test cases for ErrorStatus value object"""
    
    def test_error_status_values(self):
        """Test that all error status values are correct"""
        assert ErrorStatus.SUBMITTED.value == "submitted"
        assert ErrorStatus.PROCESSING.value == "processing"
        assert ErrorStatus.RECTIFIED.value == "rectified"
        assert ErrorStatus.VERIFIED.value == "verified"
        assert ErrorStatus.REJECTED.value == "rejected"
    
    def test_get_all_values(self):
        """Test getting all error status values"""
        values = ErrorStatus.get_all_values()
        expected = ["submitted", "processing", "rectified", "verified", "rejected"]
        assert set(values) == set(expected)
    
    def test_is_final_state(self):
        """Test checking for final states"""
        assert ErrorStatus.VERIFIED.is_final_state()
        assert ErrorStatus.REJECTED.is_final_state()
        assert not ErrorStatus.SUBMITTED.is_final_state()
        assert not ErrorStatus.PROCESSING.is_final_state()
        assert not ErrorStatus.RECTIFIED.is_final_state()
    
    def test_can_transition_to(self):
        """Test valid status transitions"""
        # From SUBMITTED
        assert ErrorStatus.SUBMITTED.can_transition_to(ErrorStatus.PROCESSING)
        assert ErrorStatus.SUBMITTED.can_transition_to(ErrorStatus.REJECTED)
        assert not ErrorStatus.SUBMITTED.can_transition_to(ErrorStatus.VERIFIED)
        
        # From PROCESSING
        assert ErrorStatus.PROCESSING.can_transition_to(ErrorStatus.RECTIFIED)
        assert ErrorStatus.PROCESSING.can_transition_to(ErrorStatus.REJECTED)
        assert not ErrorStatus.PROCESSING.can_transition_to(ErrorStatus.SUBMITTED)
        
        # From final states
        assert not ErrorStatus.VERIFIED.can_transition_to(ErrorStatus.PROCESSING)
        assert not ErrorStatus.REJECTED.can_transition_to(ErrorStatus.SUBMITTED)
