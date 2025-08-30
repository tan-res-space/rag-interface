"""
Authorization Port Interface

Secondary port for authorization operations in the Error Reporting Service.
Defines the contract for authorization adapters following Hexagonal Architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AuthorizationPort(ABC):
    """
    Abstract interface for authorization operations.

    This port defines the contract that authorization adapters must implement
    to provide access control functionality for the Error Reporting Service.
    """

    @abstractmethod
    async def can_access_error_report(self, user_id: str, error_id: str) -> bool:
        """
        Check if a user can access a specific error report.

        Args:
            user_id: The user requesting access
            error_id: The error report ID

        Returns:
            True if access is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def can_create_error_report(self, user_id: str) -> bool:
        """
        Check if a user can create error reports.

        Args:
            user_id: The user requesting to create

        Returns:
            True if creation is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def can_update_error_report(self, user_id: str, error_id: str) -> bool:
        """
        Check if a user can update a specific error report.

        Args:
            user_id: The user requesting to update
            error_id: The error report ID

        Returns:
            True if update is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def can_delete_error_report(self, user_id: str, error_id: str) -> bool:
        """
        Check if a user can delete a specific error report.

        Args:
            user_id: The user requesting to delete
            error_id: The error report ID

        Returns:
            True if deletion is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def can_search_errors(self, user_id: str) -> bool:
        """
        Check if a user can search error reports.

        Args:
            user_id: The user requesting to search

        Returns:
            True if search is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get all permissions for a user.

        Args:
            user_id: The user ID

        Returns:
            List of permission strings
        """
        pass

    @abstractmethod
    async def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user_id: The user ID
            permission: The permission to check

        Returns:
            True if user has permission, False otherwise
        """
        pass

    @abstractmethod
    async def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get all roles for a user.

        Args:
            user_id: The user ID

        Returns:
            List of role strings
        """
        pass

    @abstractmethod
    async def has_role(self, user_id: str, role: str) -> bool:
        """
        Check if a user has a specific role.

        Args:
            user_id: The user ID
            role: The role to check

        Returns:
            True if user has role, False otherwise
        """
        pass

    @abstractmethod
    async def get_accessible_error_reports(
        self, user_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Get list of error report IDs accessible to a user.

        Args:
            user_id: The user ID
            filters: Optional filters to apply

        Returns:
            List of accessible error report IDs
        """
        pass

    @abstractmethod
    async def can_access_speaker_data(self, user_id: str, speaker_id: str) -> bool:
        """
        Check if a user can access data for a specific speaker.

        Args:
            user_id: The user ID
            speaker_id: The speaker ID

        Returns:
            True if access is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def can_access_job_data(self, user_id: str, job_id: str) -> bool:
        """
        Check if a user can access data for a specific job.

        Args:
            user_id: The user ID
            job_id: The job ID

        Returns:
            True if access is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def get_organization_id(self, user_id: str) -> Optional[str]:
        """
        Get the organization ID for a user.

        Args:
            user_id: The user ID

        Returns:
            Organization ID if found, None otherwise
        """
        pass

    @abstractmethod
    async def can_access_organization_data(
        self, user_id: str, organization_id: str
    ) -> bool:
        """
        Check if a user can access data for a specific organization.

        Args:
            user_id: The user ID
            organization_id: The organization ID

        Returns:
            True if access is allowed, False otherwise
        """
        pass

    @abstractmethod
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate an authentication token and return user information.

        Args:
            token: The authentication token

        Returns:
            Dictionary containing user information if valid

        Raises:
            AuthenticationError: If token is invalid
        """
        pass

    @abstractmethod
    async def check_rate_limit(self, user_id: str, action: str) -> bool:
        """
        Check if a user has exceeded rate limits for an action.

        Args:
            user_id: The user ID
            action: The action being performed

        Returns:
            True if within rate limits, False if exceeded
        """
        pass

    @abstractmethod
    async def log_access_attempt(
        self, user_id: str, resource: str, action: str, success: bool
    ) -> None:
        """
        Log an access attempt for auditing purposes.

        Args:
            user_id: The user ID
            resource: The resource being accessed
            action: The action being performed
            success: Whether the access was successful
        """
        pass
