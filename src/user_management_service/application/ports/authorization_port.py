"""
Authorization Port Interface

This module defines the port interface for authorization operations
as specified in the ASR System Architecture Design document.
"""

from abc import ABC, abstractmethod
from typing import List, Set
from uuid import UUID

from ...domain.entities.user import Permission, UserRole


class IAuthorizationPort(ABC):
    """
    Port interface for authorization operations.
    
    This interface defines the contract for authorization-related operations
    as specified in the architecture design document.
    """
    
    @abstractmethod
    async def check_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if a user has a specific permission.
        
        Business rules:
        1. User must be active
        2. User must have the required permission through their roles
        3. Account must not be locked or suspended
        
        Args:
            user_id: ID of the user to check
            permission: Permission to check
            
        Returns:
            True if user has the permission, False otherwise
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def check_permissions(self, user_id: str, permissions: List[Permission]) -> dict:
        """
        Check multiple permissions for a user.
        
        Args:
            user_id: ID of the user to check
            permissions: List of permissions to check
            
        Returns:
            Dictionary mapping permission to boolean result
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """
        Get all permissions for a user based on their roles.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Set of permissions for the user
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: str) -> Set[UserRole]:
        """
        Get all roles for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Set of roles for the user
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def assign_role(self, user_id: str, role: UserRole, assigned_by: str) -> bool:
        """
        Assign a role to a user.
        
        Business rules:
        1. Assigner must have ASSIGN_ROLES permission
        2. Role combinations must be valid (e.g., SYSTEM_ADMIN cannot have other roles)
        3. Record role assignment event
        
        Args:
            user_id: ID of the user
            role: Role to assign
            assigned_by: ID of the user assigning the role
            
        Returns:
            True if role was assigned successfully
            
        Raises:
            UserNotFoundException: If user doesn't exist
            InsufficientPermissionsException: If assigned_by lacks permissions
            InvalidRoleCombinationException: If role combination is invalid
        """
        pass
    
    @abstractmethod
    async def revoke_role(self, user_id: str, role: UserRole, revoked_by: str) -> bool:
        """
        Revoke a role from a user.
        
        Business rules:
        1. Revoker must have ASSIGN_ROLES permission
        2. User must have at least one role remaining after revocation
        3. Record role revocation event
        
        Args:
            user_id: ID of the user
            role: Role to revoke
            revoked_by: ID of the user revoking the role
            
        Returns:
            True if role was revoked successfully
            
        Raises:
            UserNotFoundException: If user doesn't exist
            InsufficientPermissionsException: If revoked_by lacks permissions
            LastRoleException: If this would remove the user's last role
        """
        pass
    
    @abstractmethod
    async def update_user_roles(self, user_id: str, new_roles: Set[UserRole], updated_by: str) -> bool:
        """
        Update all roles for a user.
        
        Business rules:
        1. Updater must have ASSIGN_ROLES permission
        2. New role combinations must be valid
        3. User must have at least one role
        4. Record role update event
        
        Args:
            user_id: ID of the user
            new_roles: New set of roles for the user
            updated_by: ID of the user updating the roles
            
        Returns:
            True if roles were updated successfully
            
        Raises:
            UserNotFoundException: If user doesn't exist
            InsufficientPermissionsException: If updated_by lacks permissions
            InvalidRoleCombinationException: If role combination is invalid
            EmptyRolesException: If new_roles is empty
        """
        pass
    
    @abstractmethod
    async def can_access_resource(self, user_id: str, resource_type: str, resource_id: str, action: str) -> bool:
        """
        Check if a user can perform an action on a specific resource.
        
        Business rules:
        1. User must be active
        2. User must have appropriate permissions for the action
        3. Resource-specific access rules may apply
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource (e.g., 'error_report', 'verification')
            resource_id: ID of the specific resource
            action: Action to perform (e.g., 'read', 'write', 'delete')
            
        Returns:
            True if user can access the resource, False otherwise
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def get_accessible_resources(self, user_id: str, resource_type: str, action: str) -> List[str]:
        """
        Get list of resource IDs that a user can access.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource
            action: Action to perform
            
        Returns:
            List of resource IDs the user can access
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def create_permission_context(self, user_id: str) -> dict:
        """
        Create a permission context for a user session.
        
        This context can be cached and used for efficient permission checks
        during a user session.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Permission context dictionary
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def validate_role_hierarchy(self, roles: Set[UserRole]) -> bool:
        """
        Validate that a set of roles follows the role hierarchy rules.
        
        Business rules:
        1. SYSTEM_ADMIN cannot have other roles
        2. Role combinations must be logically consistent
        
        Args:
            roles: Set of roles to validate
            
        Returns:
            True if role combination is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_role_permissions(self, role: UserRole) -> Set[Permission]:
        """
        Get all permissions associated with a specific role.
        
        Args:
            role: Role to get permissions for
            
        Returns:
            Set of permissions for the role
        """
        pass
    
    @abstractmethod
    async def audit_permission_check(self, user_id: str, permission: Permission, granted: bool, context: dict) -> None:
        """
        Record a permission check for audit purposes.
        
        Args:
            user_id: ID of the user
            permission: Permission that was checked
            granted: Whether the permission was granted
            context: Additional context about the check
        """
        pass
