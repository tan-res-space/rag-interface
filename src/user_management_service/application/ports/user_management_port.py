"""
User Management Port Interface

This module defines the port interface for user management operations
as specified in the ASR System Architecture Design document.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..dto.requests import (
    ChangeUserRolesRequest,
    ChangeUserStatusRequest,
    CreateUserRequest,
    GetUserAuditLogRequest,
    GetUsersRequest,
    UpdateUserRequest,
)
from ..dto.responses import (
    ChangeUserRolesResponse,
    ChangeUserStatusResponse,
    CreateUserResponse,
    PaginatedAuditLogResponse,
    PaginatedUsersResponse,
    UpdateUserResponse,
    UserResponse,
    UserSecurityStatusResponse,
)


class IUserManagementPort(ABC):
    """
    Port interface for user management operations.

    This interface defines the contract for user management operations
    as specified in the architecture design document.
    """

    @abstractmethod
    async def create_user(self, request: CreateUserRequest) -> CreateUserResponse:
        """
        Create a new user account.

        Business rules:
        1. Username must be unique
        2. Email must be unique and from approved domains
        3. Password must meet security policy
        4. User must have at least one role
        5. Creator must have MANAGE_USERS permission

        Args:
            request: User creation request

        Returns:
            User creation response with user ID and status

        Raises:
            DuplicateUsernameException: If username already exists
            DuplicateEmailException: If email already exists
            WeakPasswordException: If password doesn't meet policy
            InsufficientPermissionsException: If creator lacks permissions
        """
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> UserResponse:
        """
        Get user information by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            User information

        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> UserResponse:
        """
        Get user information by username.

        Args:
            username: Username of the user to retrieve

        Returns:
            User information

        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserResponse:
        """
        Get user information by email.

        Args:
            email: Email of the user to retrieve

        Returns:
            User information

        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass

    @abstractmethod
    async def get_users(self, request: GetUsersRequest) -> PaginatedUsersResponse:
        """
        Get users with filtering, sorting, and pagination.

        Args:
            request: User query request with filters and pagination

        Returns:
            Paginated list of users
        """
        pass

    @abstractmethod
    async def update_user(
        self, user_id: str, request: UpdateUserRequest
    ) -> UpdateUserResponse:
        """
        Update user profile information.

        Business rules:
        1. Updater must have MANAGE_USERS permission or be the user themselves
        2. Email must be unique if changed
        3. Email domain must be approved if changed

        Args:
            user_id: ID of the user to update
            request: User update request

        Returns:
            User update response

        Raises:
            UserNotFoundException: If user doesn't exist
            DuplicateEmailException: If new email already exists
            InsufficientPermissionsException: If updater lacks permissions
        """
        pass

    @abstractmethod
    async def change_user_roles(
        self, request: ChangeUserRolesRequest
    ) -> ChangeUserRolesResponse:
        """
        Change user roles.

        Business rules:
        1. Changer must have ASSIGN_ROLES permission
        2. Role combinations must be valid
        3. User must have at least one role

        Args:
            request: Role change request

        Returns:
            Role change response

        Raises:
            UserNotFoundException: If user doesn't exist
            InvalidRoleCombinationException: If role combination is invalid
            InsufficientPermissionsException: If changer lacks permissions
        """
        pass

    @abstractmethod
    async def change_user_status(
        self, request: ChangeUserStatusRequest
    ) -> ChangeUserStatusResponse:
        """
        Change user account status.

        Business rules:
        1. Changer must have MANAGE_USERS permission
        2. Status transitions must be valid
        3. Suspended users have tokens revoked

        Args:
            request: Status change request

        Returns:
            Status change response

        Raises:
            UserNotFoundException: If user doesn't exist
            InvalidStatusTransitionException: If status transition is invalid
            InsufficientPermissionsException: If changer lacks permissions
        """
        pass

    @abstractmethod
    async def activate_user(self, user_id: str, activated_by: str) -> bool:
        """
        Activate a pending user account.

        Business rules:
        1. Activator must have MANAGE_USERS permission
        2. User must be in PENDING_ACTIVATION status
        3. Send welcome notification to user

        Args:
            user_id: ID of the user to activate
            activated_by: ID of the user performing activation

        Returns:
            True if user was activated successfully

        Raises:
            UserNotFoundException: If user doesn't exist
            InvalidStatusException: If user is not pending activation
            InsufficientPermissionsException: If activator lacks permissions
        """
        pass

    @abstractmethod
    async def suspend_user(self, user_id: str, reason: str, suspended_by: str) -> bool:
        """
        Suspend a user account.

        Business rules:
        1. Suspender must have MANAGE_USERS permission
        2. Revoke all active sessions
        3. Send suspension notification

        Args:
            user_id: ID of the user to suspend
            reason: Reason for suspension
            suspended_by: ID of the user performing suspension

        Returns:
            True if user was suspended successfully

        Raises:
            UserNotFoundException: If user doesn't exist
            InsufficientPermissionsException: If suspender lacks permissions
        """
        pass

    @abstractmethod
    async def delete_user(
        self, user_id: str, deleted_by: str, reason: Optional[str] = None
    ) -> bool:
        """
        Delete a user account.

        Business rules:
        1. Deleter must have MANAGE_USERS permission
        2. Cannot delete system administrators
        3. Anonymize user data for audit trail
        4. Revoke all active sessions

        Args:
            user_id: ID of the user to delete
            deleted_by: ID of the user performing deletion
            reason: Optional reason for deletion

        Returns:
            True if user was deleted successfully

        Raises:
            UserNotFoundException: If user doesn't exist
            CannotDeleteAdminException: If trying to delete system admin
            InsufficientPermissionsException: If deleter lacks permissions
        """
        pass

    @abstractmethod
    async def get_user_audit_log(
        self, request: GetUserAuditLogRequest
    ) -> PaginatedAuditLogResponse:
        """
        Get audit log entries for user activities.

        Args:
            request: Audit log request with filters and pagination

        Returns:
            Paginated audit log entries

        Raises:
            InsufficientPermissionsException: If requester lacks VIEW_AUDIT_LOGS permission
        """
        pass

    @abstractmethod
    async def get_user_security_status(
        self, user_id: str
    ) -> UserSecurityStatusResponse:
        """
        Get security status information for a user.

        Args:
            user_id: ID of the user

        Returns:
            User security status information

        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass

    @abstractmethod
    async def search_users(
        self, search_term: str, limit: int = 20
    ) -> List[UserResponse]:
        """
        Search users by username, email, or name.

        Args:
            search_term: Term to search for
            limit: Maximum number of results to return

        Returns:
            List of matching users
        """
        pass

    @abstractmethod
    async def get_user_statistics(self) -> dict:
        """
        Get user statistics for dashboard.

        Returns:
            Dictionary with user statistics (total, active, by role, etc.)

        Raises:
            InsufficientPermissionsException: If requester lacks VIEW_SYSTEM_METRICS permission
        """
        pass

    @abstractmethod
    async def bulk_update_users(
        self, user_ids: List[str], updates: dict, updated_by: str
    ) -> dict:
        """
        Perform bulk updates on multiple users.

        Business rules:
        1. Updater must have MANAGE_USERS permission
        2. All or nothing transaction
        3. Record bulk update event

        Args:
            user_ids: List of user IDs to update
            updates: Dictionary of fields to update
            updated_by: ID of the user performing the update

        Returns:
            Dictionary with update results

        Raises:
            InsufficientPermissionsException: If updater lacks permissions
        """
        pass
