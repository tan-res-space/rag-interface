"""
User Repository Port Interface

This module defines the port interface for user data persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ...domain.entities.user import User, UserRole, UserStatus


class IUserRepositoryPort(ABC):
    """
    Port interface for user data persistence operations.
    
    This interface defines the contract for user data access operations
    following the Repository pattern.
    """
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Save a user entity.
        
        Args:
            user: User entity to save
            
        Returns:
            Saved user entity
            
        Raises:
            DuplicateUsernameException: If username already exists
            DuplicateEmailException: If email already exists
            RepositoryException: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User entity if found, None otherwise
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User entity if found, None otherwise
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_roles(self, roles: List[UserRole], limit: int = 100) -> List[User]:
        """
        Find users by roles.
        
        Args:
            roles: List of roles to search for
            limit: Maximum number of users to return
            
        Returns:
            List of users with any of the specified roles
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_status(self, status: UserStatus, limit: int = 100) -> List[User]:
        """
        Find users by status.
        
        Args:
            status: User status to search for
            limit: Maximum number of users to return
            
        Returns:
            List of users with the specified status
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_department(self, department: str, limit: int = 100) -> List[User]:
        """
        Find users by department.
        
        Args:
            department: Department to search for
            limit: Maximum number of users to return
            
        Returns:
            List of users in the specified department
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def search_users(self, search_term: str, limit: int = 20) -> List[User]:
        """
        Search users by username, email, or name.
        
        Args:
            search_term: Term to search for
            limit: Maximum number of users to return
            
        Returns:
            List of matching users
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def get_users_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        roles: Optional[List[UserRole]] = None,
        status: Optional[UserStatus] = None,
        department: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple:
        """
        Get users with pagination and filtering.
        
        Args:
            page: Page number (1-based)
            page_size: Number of users per page
            roles: Optional list of roles to filter by
            status: Optional status to filter by
            department: Optional department to filter by
            search_term: Optional search term
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (users_list, total_count)
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            True if user was deleted, False if not found
            
        Raises:
            RepositoryException: If delete operation fails
        """
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """
        Check if a user exists with the given username.
        
        Args:
            username: Username to check
            
        Returns:
            True if user exists, False otherwise
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists with the given email.
        
        Args:
            email: Email to check
            
        Returns:
            True if user exists, False otherwise
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def get_user_count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            Total user count
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def get_user_count_by_status(self, status: UserStatus) -> int:
        """
        Get number of users by status.
        
        Args:
            status: User status to count
            
        Returns:
            Number of users with the specified status
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def get_user_count_by_role(self, role: UserRole) -> int:
        """
        Get number of users by role.
        
        Args:
            role: User role to count
            
        Returns:
            Number of users with the specified role
            
        Raises:
            RepositoryException: If query operation fails
        """
        pass
    
    @abstractmethod
    async def bulk_update_status(self, user_ids: List[UUID], status: UserStatus) -> int:
        """
        Bulk update user status.
        
        Args:
            user_ids: List of user IDs to update
            status: New status to set
            
        Returns:
            Number of users updated
            
        Raises:
            RepositoryException: If update operation fails
        """
        pass
