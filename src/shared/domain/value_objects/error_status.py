"""
Shared Error Status Value Object

Defines error report status values used across all services.
This is the single source of truth for error status definitions.
"""

from enum import Enum
from typing import Dict, List


class ErrorStatus(str, Enum):
    """
    Enumeration for error report status.
    
    Represents the lifecycle state of error reports:
    - SUBMITTED: Error has been submitted but not yet processed
    - PROCESSING: Error is currently being processed
    - RECTIFIED: Error has been corrected/fixed
    - VERIFIED: Error correction has been verified
    - REJECTED: Error report was rejected (invalid/duplicate)
    """
    
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    RECTIFIED = "rectified"
    VERIFIED = "verified"
    REJECTED = "rejected"
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all error status values"""
        return [status.value for status in cls]
    
    @classmethod
    def get_status_info(cls) -> Dict[str, Dict[str, str]]:
        """Get detailed information about each status"""
        return {
            cls.SUBMITTED.value: {
                "label": "Submitted",
                "description": "Error has been submitted but not yet processed",
                "color": "#2196f3",  # Blue
                "icon": "📝",
                "stage": "1"
            },
            cls.PROCESSING.value: {
                "label": "Processing",
                "description": "Error is currently being processed",
                "color": "#ff9800",  # Orange
                "icon": "⚙️",
                "stage": "2"
            },
            cls.RECTIFIED.value: {
                "label": "Rectified",
                "description": "Error has been corrected/fixed",
                "color": "#4caf50",  # Green
                "icon": "✅",
                "stage": "3"
            },
            cls.VERIFIED.value: {
                "label": "Verified",
                "description": "Error correction has been verified",
                "color": "#4caf50",  # Green
                "icon": "🔍",
                "stage": "4"
            },
            cls.REJECTED.value: {
                "label": "Rejected",
                "description": "Error report was rejected (invalid/duplicate)",
                "color": "#f44336",  # Red
                "icon": "❌",
                "stage": "0"
            }
        }
    
    def get_display_name(self) -> str:
        """Get human-readable display name"""
        info = self.get_status_info()
        return info[self.value]["label"]
    
    def get_description(self) -> str:
        """Get status description"""
        info = self.get_status_info()
        return info[self.value]["description"]
    
    def get_color(self) -> str:
        """Get status color for UI display"""
        info = self.get_status_info()
        return info[self.value]["color"]
    
    def get_icon(self) -> str:
        """Get status icon for UI display"""
        info = self.get_status_info()
        return info[self.value]["icon"]
    
    def get_stage(self) -> int:
        """Get numeric stage (0-4) for workflow ordering"""
        info = self.get_status_info()
        return int(info[self.value]["stage"])
    
    def is_final_state(self) -> bool:
        """Check if this is a final state (verified or rejected)"""
        return self in [self.VERIFIED, self.REJECTED]
    
    def can_transition_to(self, other: 'ErrorStatus') -> bool:
        """Check if transition to another status is valid"""
        valid_transitions = {
            self.SUBMITTED: [self.PROCESSING, self.REJECTED],
            self.PROCESSING: [self.RECTIFIED, self.REJECTED],
            self.RECTIFIED: [self.VERIFIED, self.PROCESSING],  # Can go back for re-processing
            self.VERIFIED: [],  # Final state
            self.REJECTED: []   # Final state
        }
        return other in valid_transitions.get(self, [])
