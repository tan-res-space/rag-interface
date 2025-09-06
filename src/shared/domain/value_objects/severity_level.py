"""
Shared Severity Level Value Object

Defines error severity levels used across all services.
This is the single source of truth for severity level definitions.
"""

from enum import Enum
from typing import Dict, List


class SeverityLevel(str, Enum):
    """
    Enumeration for error severity levels.
    
    Used to categorize the impact and urgency of errors across all services:
    - LOW: Minor issues that don't affect core functionality
    - MEDIUM: Issues that may impact user experience but have workarounds
    - HIGH: Significant issues that affect core functionality
    - CRITICAL: Severe issues that prevent system operation
    """
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all severity level values"""
        return [level.value for level in cls]
    
    @classmethod
    def get_severity_info(cls) -> Dict[str, Dict[str, str]]:
        """Get detailed information about each severity level"""
        return {
            cls.LOW.value: {
                "label": "Low",
                "description": "Minor issues that don't affect core functionality",
                "color": "#4caf50",  # Green
                "icon": "ℹ️",
                "priority": "1"
            },
            cls.MEDIUM.value: {
                "label": "Medium", 
                "description": "Issues that may impact user experience but have workarounds",
                "color": "#ff9800",  # Orange
                "icon": "⚠️",
                "priority": "2"
            },
            cls.HIGH.value: {
                "label": "High",
                "description": "Significant issues that affect core functionality",
                "color": "#f44336",  # Red
                "icon": "🚨",
                "priority": "3"
            },
            cls.CRITICAL.value: {
                "label": "Critical",
                "description": "Severe issues that prevent system operation",
                "color": "#d32f2f",  # Dark Red
                "icon": "🔥",
                "priority": "4"
            }
        }
    
    def get_display_name(self) -> str:
        """Get human-readable display name"""
        info = self.get_severity_info()
        return info[self.value]["label"]
    
    def get_description(self) -> str:
        """Get severity description"""
        info = self.get_severity_info()
        return info[self.value]["description"]
    
    def get_color(self) -> str:
        """Get severity color for UI display"""
        info = self.get_severity_info()
        return info[self.value]["color"]
    
    def get_icon(self) -> str:
        """Get severity icon for UI display"""
        info = self.get_severity_info()
        return info[self.value]["icon"]
    
    def get_priority(self) -> int:
        """Get numeric priority (1-4) for comparison"""
        info = self.get_severity_info()
        return int(info[self.value]["priority"])
    
    def is_higher_than(self, other: 'SeverityLevel') -> bool:
        """Check if this severity is higher than another"""
        return self.get_priority() > other.get_priority()
    
    def is_lower_than(self, other: 'SeverityLevel') -> bool:
        """Check if this severity is lower than another"""
        return self.get_priority() < other.get_priority()
