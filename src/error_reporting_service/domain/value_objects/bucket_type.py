"""
Bucket Type Value Object
Defines speaker proficiency levels and bucket classifications
"""

from enum import Enum
from typing import Dict, List


class BucketType(Enum):
    """
    Speaker bucket classification levels
    """
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all bucket type values"""
        return [bucket.value for bucket in cls]
    
    @classmethod
    def get_progression_order(cls) -> List['BucketType']:
        """Get bucket types in progression order"""
        return [cls.BEGINNER, cls.INTERMEDIATE, cls.ADVANCED, cls.EXPERT]
    
    @classmethod
    def get_bucket_info(cls) -> Dict[str, Dict[str, str]]:
        """Get detailed information about each bucket type"""
        return {
            cls.BEGINNER.value: {
                "label": "Beginner",
                "description": "New speaker, learning basic transcription patterns",
                "color": "#f44336",  # Red
                "icon": "🌱"
            },
            cls.INTERMEDIATE.value: {
                "label": "Intermediate", 
                "description": "Developing speaker with moderate experience",
                "color": "#ff9800",  # Orange
                "icon": "🌿"
            },
            cls.ADVANCED.value: {
                "label": "Advanced",
                "description": "Experienced speaker with good transcription skills", 
                "color": "#2196f3",  # Blue
                "icon": "🌳"
            },
            cls.EXPERT.value: {
                "label": "Expert",
                "description": "Highly skilled speaker with excellent transcription quality",
                "color": "#4caf50",  # Green
                "icon": "🏆"
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
            self.BEGINNER: 0,
            self.INTERMEDIATE: 1,
            self.ADVANCED: 2,
            self.EXPERT: 3
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
