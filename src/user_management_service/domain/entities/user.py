"""
User Domain Entity

Represents a user with authentication and authorization capabilities.
Core domain entity for the user management service.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from ..value_objects.user_role import UserRole
from ..value_objects.user_status import UserStatus


# Permission constants for compatibility with existing imports
class PermissionMeta(type):
    """Metaclass to make Permission class iterable"""
    def __iter__(cls):
        return iter([
            cls.SUBMIT_ERROR_REPORT,
            cls.VIEW_OWN_REPORTS,
            cls.VIEW_ALL_REPORTS,
            cls.VIEW_ERROR_REPORTS,
            cls.EDIT_ERROR_REPORTS,
            cls.DELETE_ERROR_REPORTS,
            cls.VERIFY_CORRECTIONS,
            cls.VIEW_VERIFICATION_DASHBOARD,
            cls.EXPORT_VERIFICATION_DATA,
            cls.ACCESS_ANALYTICS,
            cls.MANAGE_USERS,
            cls.MANAGE_SYSTEM_SETTINGS,
            cls.SYSTEM_ADMINISTRATION,
            cls.MEDICAL_TRANSCRIPTION,
        ])

class Permission(metaclass=PermissionMeta):
    """Permission constants for user authorization"""

    # Core permissions
    SUBMIT_ERROR_REPORT = "submit_error_reports"
    VIEW_OWN_REPORTS = "view_own_reports"
    VIEW_ALL_REPORTS = "view_all_reports"
    VIEW_ERROR_REPORTS = "view_all_reports"  # Alias for compatibility
    EDIT_ERROR_REPORTS = "edit_error_reports"
    DELETE_ERROR_REPORTS = "delete_error_reports"
    VERIFY_CORRECTIONS = "verify_corrections"
    VIEW_VERIFICATION_DASHBOARD = "verify_corrections"  # Alias for compatibility
    EXPORT_VERIFICATION_DATA = "export_verification_data"
    ACCESS_ANALYTICS = "access_analytics"
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    SYSTEM_ADMINISTRATION = "system_administration"
    MEDICAL_TRANSCRIPTION = "medical_transcription"


@dataclass
class UserProfile:
    """
    User profile containing personal and professional information.

    This value object encapsulates user profile data including
    personal details and organizational information.
    """

    first_name: str = ""
    last_name: str = ""
    email: str = ""
    department: str = ""
    phone_number: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate the profile after initialization."""
        if self.metadata is None:
            self.metadata = {}
        self._validate_email()

    def _validate_email(self) -> None:
        """Validate email format if provided."""
        if self.email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValueError("Invalid email format")

    def get_full_name(self) -> str:
        """Get the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return ""

    def is_complete(self) -> bool:
        """Check if the profile has all required information."""
        return bool(self.first_name and self.last_name and self.email)


@dataclass
class User:
    """
    Domain entity representing a user.

    This entity encapsulates user authentication, authorization,
    and profile management for the ASR Error Reporting System.
    """

    username: str
    profile: UserProfile
    roles: List[UserRole]
    user_id: UUID = None
    status: UserStatus = UserStatus.PENDING_ACTIVATION
    failed_login_attempts: int = 0
    account_locked_until: datetime = None
    last_login: datetime = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate the user after initialization."""
        self._validate_username()
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

    def _validate_roles(self) -> None:
        """Validate roles field."""
        # Convert set to list if needed for compatibility
        if isinstance(self.roles, set):
            self.roles = list(self.roles)

        # Allow empty roles for testing purposes, but validate types if roles exist
        if self.roles and not all(isinstance(role, UserRole) for role in self.roles):
            raise ValueError("All roles must be UserRole instances")

    def _set_defaults(self) -> None:
        """Set default values for optional fields."""
        if self.metadata is None:
            self.metadata = {}

        if self.created_at is None:
            self.created_at = datetime.utcnow()

        if self.user_id is None:
            from uuid import uuid4
            self.user_id = uuid4()

    def is_active(self) -> bool:
        """
        Check if user is active.

        Returns:
            True if user status is active, account is not locked, and has roles
        """
        return (self.status.is_active() and
                not self.is_account_locked() and
                bool(self.roles))

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
        return self.profile.get_full_name() or self.username

    def record_login_success(self) -> None:
        """Record a successful login attempt."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login = datetime.utcnow()

    def record_login_failure(self) -> None:
        """Record a failed login attempt."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)

    def is_account_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.account_locked_until is None:
            return False
        return datetime.utcnow() < self.account_locked_until

    def activate_account(self) -> None:
        """Activate the user account."""
        self.status = UserStatus.ACTIVE

    def suspend_account(self, reason: str = None) -> None:
        """Suspend the user account."""
        self.status = UserStatus.SUSPENDED
        if reason and self.metadata is not None:
            self.metadata['suspension_reason'] = reason

    def add_role(self, role: UserRole) -> None:
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: UserRole) -> None:
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)

    def get_user_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the user.

        Returns:
            Dictionary containing user summary
        """
        return {
            "id": str(self.user_id),
            "username": self.username,
            "email": self.profile.email,
            "full_name": self.get_full_name(),
            "roles": [role.value for role in self.roles],
            "status": self.status.value,
            "is_active": self.is_active(),
            "permissions": self._get_all_permissions(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": (
                self.last_login.isoformat() if self.last_login else None
            ),
            "metadata_keys": list(self.metadata.keys()),
        }

    def _get_all_permissions(self) -> List[str]:
        """Get all permissions from all roles."""
        permissions = set()
        for role in self.roles:
            permissions.update(role.get_permissions())
        return list(permissions)

    def get_permissions(self) -> List[str]:
        """Get all permissions from all roles (public method)."""
        return self._get_all_permissions()

    def __eq__(self, other) -> bool:
        """Check equality based on user_id."""
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        """Hash based on user_id."""
        return hash(self.user_id)

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
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
