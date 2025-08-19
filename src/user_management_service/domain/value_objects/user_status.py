"""
User Status Value Object

Defines different user statuses for account management.
Immutable value object following domain-driven design principles.
"""

from enum import Enum


class UserStatus(Enum):
    """
    Enumeration of user account statuses.
    
    Each status represents a different state in the user lifecycle.
    """
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_ACTIVATION = "pending_activation"
    
    def is_active(self) -> bool:
        """
        Check if user status allows active usage.
        
        Returns:
            True if status is active
        """
        return self == UserStatus.ACTIVE
    
    def is_suspended(self) -> bool:
        """
        Check if user is suspended.
        
        Returns:
            True if status is suspended
        """
        return self == UserStatus.SUSPENDED
    
    def requires_activation(self) -> bool:
        """
        Check if user requires activation.
        
        Returns:
            True if status is pending activation
        """
        return self == UserStatus.PENDING_ACTIVATION
    
    @classmethod
    def from_string(cls, status_str: str) -> "UserStatus":
        """
        Create user status from string value.
        
        Args:
            status_str: String representation of the status
            
        Returns:
            UserStatus instance
            
        Raises:
            ValueError: If status string is invalid
        """
        if not status_str or not status_str.strip():
            raise ValueError("Invalid user status: empty string")
        
        status_str = status_str.strip().lower()
        
        for status in cls:
            if status.value == status_str:
                return status
        
        raise ValueError(f"Invalid user status: {status_str}")
    
    def __str__(self) -> str:
        """String representation of the user status."""
        return self.value
