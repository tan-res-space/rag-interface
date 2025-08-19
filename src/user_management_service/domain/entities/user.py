"""
User Domain Entity

Represents a user with authentication and authorization capabilities.
Core domain entity for the user management service.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID

from ..value_objects.user_role import UserRole
from ..value_objects.user_status import UserStatus


# Placeholder classes for compatibility with existing imports
class Permission:
    """Placeholder Permission class"""
    pass


class UserProfile:
    """Placeholder UserProfile class"""
    pass


@dataclass
class User:
    """
    Domain entity representing a user.
    
    This entity encapsulates user authentication, authorization,
    and profile management for the ASR Error Reporting System.
    """
    
    id: UUID
    username: str
    email: str
    roles: List[UserRole]
    status: UserStatus
    first_name: str = ""
    last_name: str = ""
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    last_login_at: datetime = None
    
    def __post_init__(self):
        """Validate the user after initialization."""
        self._validate_username()
        self._validate_email()
        self._validate_roles()
        self._set_defaults()
    
    def _validate_username(self) -> None:
        """Validate username field."""
        if not self.username or not self.username.strip():
            raise ValueError("username cannot be empty")
        
        if len(self.username) < 3:
            raise ValueError("username must be at least 3 characters long")
        
        if len(self.username) > 50:
            raise ValueError("username cannot exceed 50 characters")
    
    def _validate_email(self) -> None:
        """Validate email field."""
        if not self.email or not self.email.strip():
            raise ValueError("email cannot be empty")
        
        # Simple email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValueError("Invalid email format")
    
    def _validate_roles(self) -> None:
        """Validate roles field."""
        if not self.roles:
            raise ValueError("User must have at least one role")
        
        if not all(isinstance(role, UserRole) for role in self.roles):
            raise ValueError("All roles must be UserRole instances")
    
    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.metadata is None:
            self.metadata = {}
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """
        Check if user is active.
        
        Returns:
            True if user status is active
        """
        return self.status.is_active()
    
    def has_role(self, role: UserRole) -> bool:
        """
        Check if user has specific role.
        
        Args:
            role: Role to check for
            
        Returns:
            True if user has the role
        """
        return role in self.roles
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            permission: Permission to check for
            
        Returns:
            True if user has the permission
        """
        for role in self.roles:
            if permission in role.get_permissions():
                return True
        return False
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.has_permission("manage_users")
    
    def can_delete_error_reports(self) -> bool:
        """Check if user can delete error reports."""
        return self.has_permission("delete_error_reports")
    
    def can_submit_error_reports(self) -> bool:
        """Check if user can submit error reports."""
        return self.has_permission("submit_error_reports")
    
    def can_verify_corrections(self) -> bool:
        """Check if user can verify corrections."""
        return self.has_permission("verify_corrections")
    
    def can_access_analytics(self) -> bool:
        """Check if user can access analytics."""
        return self.has_permission("access_analytics")
    
    def can_view_all_reports(self) -> bool:
        """Check if user can view all reports."""
        return self.has_permission("view_all_reports")
    
    def get_full_name(self) -> str:
        """
        Get user's full name.
        
        Returns:
            Full name or username if names not provided
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    def get_user_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the user.
        
        Returns:
            Dictionary containing user summary
        """
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "full_name": self.get_full_name(),
            "roles": [role.value for role in self.roles],
            "status": self.status.value,
            "is_active": self.is_active(),
            "permissions": self._get_all_permissions(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "metadata_keys": list(self.metadata.keys())
        }
    
    def _get_all_permissions(self) -> List[str]:
        """Get all permissions from all roles."""
        all_permissions = set()
        for role in self.roles:
            all_permissions.update(role.get_permissions())
        return sorted(list(all_permissions))
    
    def __eq__(self, other: "User") -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
