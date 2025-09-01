"""
User Role Value Object

Defines different user roles with associated permissions.
Immutable value object following domain-driven design principles.
"""

from enum import Enum
from typing import List


class UserRole(Enum):
    """
    Enumeration of user roles with associated permissions.

    Each role defines different access levels and capabilities
    within the ASR Error Reporting System.
    """

    ADMIN = "admin"
    QA_PERSONNEL = "qa_personnel"
    MTS_PERSONNEL = "mts_personnel"
    SYSTEM_ADMIN = "system_admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

    def get_permissions(self) -> List[str]:
        """
        Get permissions associated with this role.

        Returns:
            List of permission strings
        """
        permission_map = {
            UserRole.ADMIN: [
                "manage_users",
                "delete_error_reports",
                "view_all_reports",
                "submit_error_reports",
                "verify_corrections",
                "access_analytics",
                "manage_system_settings",
            ],
            UserRole.SYSTEM_ADMIN: [
                "manage_users",
                "delete_error_reports",
                "view_all_reports",
                "submit_error_reports",
                "verify_corrections",
                "access_analytics",
                "manage_system_settings",
                "system_administration",
            ],
            UserRole.QA_PERSONNEL: [
                "submit_error_reports",
                "view_own_reports",
                "view_all_reports",
                "edit_error_reports",
                "access_analytics",
            ],
            UserRole.MTS_PERSONNEL: [
                "view_own_reports",
                "view_all_reports",
                "verify_corrections",
                "export_verification_data",
                "access_analytics",
                "medical_transcription",
            ],
            UserRole.DEVELOPER: [
                "view_all_reports",
                "access_analytics",
                "submit_error_reports",
            ],
            UserRole.VIEWER: ["view_own_reports"],
        }
        return permission_map.get(self, [])

    def can_manage_users(self) -> bool:
        """Check if role can manage users."""
        return "manage_users" in self.get_permissions()

    def can_delete_error_reports(self) -> bool:
        """Check if role can delete error reports."""
        return "delete_error_reports" in self.get_permissions()

    def can_submit_error_reports(self) -> bool:
        """Check if role can submit error reports."""
        return "submit_error_reports" in self.get_permissions()

    def can_verify_corrections(self) -> bool:
        """Check if role can verify corrections."""
        return "verify_corrections" in self.get_permissions()

    def can_access_analytics(self) -> bool:
        """Check if role can access analytics."""
        return "access_analytics" in self.get_permissions()

    def can_view_all_reports(self) -> bool:
        """Check if role can view all reports."""
        return "view_all_reports" in self.get_permissions()

    @classmethod
    def from_string(cls, role_str: str) -> "UserRole":
        """
        Create user role from string value.

        Args:
            role_str: String representation of the role

        Returns:
            UserRole instance

        Raises:
            ValueError: If role string is invalid
        """
        if not role_str or not role_str.strip():
            raise ValueError("Invalid user role: empty string")

        role_str = role_str.strip().lower()

        for role in cls:
            if role.value == role_str:
                return role

        raise ValueError(f"Invalid user role: {role_str}")

    def __str__(self) -> str:
        """String representation of the user role."""
        return self.value
