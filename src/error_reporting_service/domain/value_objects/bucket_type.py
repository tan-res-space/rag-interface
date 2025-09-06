"""
Bucket Type Value Object
Defines ASR output quality-based bucket classifications
"""

from enum import Enum
from typing import Dict, List


class BucketType(Enum):
    """
    Quality-based speaker bucket classification levels
    """
    NO_TOUCH = "no_touch"
    LOW_TOUCH = "low_touch"
    MEDIUM_TOUCH = "medium_touch"
    HIGH_TOUCH = "high_touch"
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all bucket type values"""
        return [bucket.value for bucket in cls]
    
    @classmethod
    def get_progression_order(cls) -> List['BucketType']:
        """Get bucket types in progression order (from lowest to highest quality)"""
        return [cls.HIGH_TOUCH, cls.MEDIUM_TOUCH, cls.LOW_TOUCH, cls.NO_TOUCH]
    
    @classmethod
    def get_bucket_info(cls) -> Dict[str, Dict[str, str]]:
        """Get detailed information about each bucket type"""
        return {
            cls.NO_TOUCH.value: {
                "label": "No Touch",
                "description": "Very high quality ASR draft, no corrections needed",
                "color": "#4caf50",  # Green
                "icon": "🏆"
            },
            cls.LOW_TOUCH.value: {
                "label": "Low Touch",
                "description": "High quality ASR draft, minimal corrections required",
                "color": "#2196f3",  # Blue
                "icon": "🌟"
            },
            cls.MEDIUM_TOUCH.value: {
                "label": "Medium Touch",
                "description": "Medium quality ASR draft, some corrections needed",
                "color": "#ff9800",  # Orange
                "icon": "⚡"
            },
            cls.HIGH_TOUCH.value: {
                "label": "High Touch",
                "description": "Low quality ASR draft, significant corrections required",
                "color": "#f44336",  # Red
                "icon": "🔧"
            }
        }
    
    def get_display_name(self) -> str:
        """Get human-readable display name"""
        info = self.get_bucket_info()
        return info[self.value]["label"]
    
    def get_description(self) -> str:
        """Get bucket description"""
        info = self.get_bucket_info()
        return info[self.value]["description"]
    
    def get_color(self) -> str:
        """Get bucket color for UI display"""
        info = self.get_bucket_info()
        return info[self.value]["color"]
    
    def get_icon(self) -> str:
        """Get bucket icon for UI display"""
        info = self.get_bucket_info()
        return info[self.value]["icon"]
    
    def get_level(self) -> int:
        """Get numeric level (0-3) for comparison"""
        levels = {
            self.HIGH_TOUCH: 0,
            self.MEDIUM_TOUCH: 1,
            self.LOW_TOUCH: 2,
            self.NO_TOUCH: 3
        }
        return levels[self]
    
    def is_higher_than(self, other: 'BucketType') -> bool:
        """Check if this bucket is higher level than another"""
        return self.get_level() > other.get_level()
    
    def is_lower_than(self, other: 'BucketType') -> bool:
        """Check if this bucket is lower level than another"""
        return self.get_level() < other.get_level()
    
    def get_next_level(self) -> 'BucketType':
        """Get next higher bucket level"""
        progression = self.get_progression_order()
        current_index = progression.index(self)
        if current_index < len(progression) - 1:
            return progression[current_index + 1]
        return self  # Already at highest level
    
    def get_previous_level(self) -> 'BucketType':
        """Get previous lower bucket level"""
        progression = self.get_progression_order()
        current_index = progression.index(self)
        if current_index > 0:
            return progression[current_index - 1]
        return self  # Already at lowest level
