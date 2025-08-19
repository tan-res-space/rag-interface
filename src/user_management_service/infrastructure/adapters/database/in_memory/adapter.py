"""
In-Memory Database Adapter for User Management Service

This adapter provides an in-memory implementation of the user repository
for testing and demonstration purposes.
"""

import logging
from copy import deepcopy
from typing import Dict, List, Optional
from uuid import UUID

from .....application.ports.user_repository_port import IUserRepositoryPort
from .....domain.entities.user import User, UserRole, UserStatus


logger = logging.getLogger(__name__)


class InMemoryUserRepositoryAdapter(IUserRepositoryPort):
    """
    In-memory implementation of the user repository adapter.
    
    Stores user data in memory for testing and demonstration purposes.
    Not suitable for production use.
    """
    
    def __init__(self):
        """Initialize the in-memory adapter"""
        self._users: Dict[UUID, User] = {}
        self._username_index: Dict[str, UUID] = {}
        self._email_index: Dict[str, UUID] = {}
        self._transaction_data: Optional[Dict[UUID, User]] = None
        
        logger.info("Initialized in-memory user repository adapter")
    
    async def save(self, user: User) -> User:
        """Save user to in-memory storage"""
        
        # Check for duplicate username (excluding current user)
        existing_user_id = self._username_index.get(user.username)
        if existing_user_id and existing_user_id != user.user_id:
            raise ValueError(f"Username '{user.username}' already exists")
        
        # Check for duplicate email (excluding current user)
        existing_user_id = self._email_index.get(user.profile.email)
        if existing_user_id and existing_user_id != user.user_id:
            raise ValueError(f"Email '{user.profile.email}' already exists")
        
        if self._transaction_data is not None:
            # We're in a transaction
            self._transaction_data[user.user_id] = deepcopy(user)
        else:
            self._users[user.user_id] = deepcopy(user)
            self._username_index[user.username] = user.user_id
            self._email_index[user.profile.email] = user.user_id
        
        logger.debug(f"Saved user: {user.username}")
        return deepcopy(user)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID from in-memory storage"""
        
        storage = self._transaction_data if self._transaction_data is not None else self._users
        user = storage.get(user_id)
        
        if user:
            logger.debug(f"Retrieved user by ID: {user_id}")
            return deepcopy(user)
        
        logger.debug(f"User not found by ID: {user_id}")
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username from in-memory storage"""
        
        user_id = self._username_index.get(username)
        if user_id:
            return await self.get_by_id(user_id)
        
        logger.debug(f"User not found by username: {username}")
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email from in-memory storage"""
        
        user_id = self._email_index.get(email)
        if user_id:
            return await self.get_by_id(user_id)
        
        logger.debug(f"User not found by email: {email}")
        return None
    
    async def find_by_roles(self, roles: List[UserRole], limit: int = 100) -> List[User]:
        """Find users by roles"""
        
        storage = self._transaction_data if self._transaction_data is not None else self._users
        matching_users = []
        
        for user in storage.values():
            if any(role in user.roles for role in roles):
                matching_users.append(deepcopy(user))
                if len(matching_users) >= limit:
                    break
        
        logger.debug(f"Found {len(matching_users)} users with roles: {roles}")
        return matching_users
    
    async def find_by_status(self, status: UserStatus, limit: int = 100) -> List[User]:
        """Find users by status"""
        
        storage = self._transaction_data if self._transaction_data is not None else self._users
        matching_users = []
        
        for user in storage.values():
            if user.status == status:
                matching_users.append(deepcopy(user))
                if len(matching_users) >= limit:
                    break
        
        logger.debug(f"Found {len(matching_users)} users with status: {status}")
        return matching_users
    
    async def find_by_department(self, department: str, limit: int = 100) -> List[User]:
        """Find users by department"""
        
        storage = self._transaction_data if self._transaction_data is not None else self._users
        matching_users = []
        
        for user in storage.values():
            if user.profile.department and user.profile.department.lower() == department.lower():
                matching_users.append(deepcopy(user))
                if len(matching_users) >= limit:
                    break
        
        logger.debug(f"Found {len(matching_users)} users in department: {department}")
        return matching_users
    
    async def search_users(self, search_term: str, limit: int = 20) -> List[User]:
        """Search users by username, email, or name"""
        
        storage = self._transaction_data if self._transaction_data is not None else self._users
        matching_users = []
        search_lower = search_term.lower()
        
        for user in storage.values():
            if (search_lower in user.username.lower() or
                search_lower in user.profile.email.lower() or
                search_lower in user.profile.first_name.lower() or
                search_lower in user.profile.last_name.lower()):
                matching_users.append(deepcopy(user))
                if len(matching_users) >= limit:
                    break
        
        logger.debug(f"Found {len(matching_users)} users matching search: {search_term}")
        return matching_users
    
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
        """Get users with pagination and filtering"""
        
        storage = self._transaction_data if self._transaction_data is not None else self._users
        filtered_users = []
        
        # Apply filters
        for user in storage.values():
            # Role filter
            if roles and not any(role in user.roles for role in roles):
                continue
            
            # Status filter
            if status and user.status != status:
                continue
            
            # Department filter
            if department and (not user.profile.department or 
                             user.profile.department.lower() != department.lower()):
                continue
            
            # Search filter
            if search_term:
                search_lower = search_term.lower()
                if not (search_lower in user.username.lower() or
                       search_lower in user.profile.email.lower() or
                       search_lower in user.profile.first_name.lower() or
                       search_lower in user.profile.last_name.lower()):
                    continue
            
            filtered_users.append(user)
        
        # Sort users
        reverse = sort_order == "desc"
        if sort_by == "username":
            filtered_users.sort(key=lambda u: u.username, reverse=reverse)
        elif sort_by == "email":
            filtered_users.sort(key=lambda u: u.profile.email, reverse=reverse)
        elif sort_by == "last_login":
            filtered_users.sort(key=lambda u: u.last_login or u.created_at, reverse=reverse)
        else:  # created_at
            filtered_users.sort(key=lambda u: u.created_at, reverse=reverse)
        
        # Apply pagination
        total_count = len(filtered_users)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_users = filtered_users[start_index:end_index]
        
        logger.debug(f"Retrieved {len(paginated_users)} users (page {page}, total {total_count})")
        return [deepcopy(user) for user in paginated_users], total_count
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user"""
        
        if self._transaction_data is not None:
            # We're in a transaction
            if user_id in self._transaction_data:
                del self._transaction_data[user_id]
                return True
        else:
            if user_id in self._users:
                user = self._users[user_id]
                del self._users[user_id]
                del self._username_index[user.username]
                del self._email_index[user.profile.email]
                logger.debug(f"Deleted user: {user.username}")
                return True
        
        logger.debug(f"User not found for deletion: {user_id}")
        return False
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        return username in self._username_index
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        return email in self._email_index
    
    async def get_user_count(self) -> int:
        """Get total number of users"""
        storage = self._transaction_data if self._transaction_data is not None else self._users
        return len(storage)
    
    async def get_user_count_by_status(self, status: UserStatus) -> int:
        """Get number of users by status"""
        storage = self._transaction_data if self._transaction_data is not None else self._users
        return sum(1 for user in storage.values() if user.status == status)
    
    async def get_user_count_by_role(self, role: UserRole) -> int:
        """Get number of users by role"""
        storage = self._transaction_data if self._transaction_data is not None else self._users
        return sum(1 for user in storage.values() if role in user.roles)
    
    async def bulk_update_status(self, user_ids: List[UUID], status: UserStatus) -> int:
        """Bulk update user status"""
        updated_count = 0
        
        for user_id in user_ids:
            user = await self.get_by_id(user_id)
            if user:
                user.status = status
                await self.save(user)
                updated_count += 1
        
        logger.debug(f"Bulk updated {updated_count} users to status: {status}")
        return updated_count
    
    # Transaction support methods
    async def begin_transaction(self) -> None:
        """Begin a transaction"""
        self._transaction_data = deepcopy(self._users)
        logger.debug("Transaction started")
    
    async def commit_transaction(self) -> None:
        """Commit a transaction"""
        if self._transaction_data is not None:
            self._users = self._transaction_data
            # Rebuild indexes
            self._username_index = {user.username: user.user_id for user in self._users.values()}
            self._email_index = {user.profile.email: user.user_id for user in self._users.values()}
            self._transaction_data = None
            logger.debug("Transaction committed")
    
    async def rollback_transaction(self) -> None:
        """Rollback a transaction"""
        self._transaction_data = None
        logger.debug("Transaction rolled back")
    
    # Health check methods
    async def health_check(self) -> dict:
        """Perform health check"""
        return {
            "status": "healthy",
            "adapter_type": "in_memory",
            "user_count": len(self._users),
            "transaction_active": self._transaction_data is not None
        }
    
    async def get_connection_info(self) -> dict:
        """Get connection information"""
        return {
            "adapter_type": "in_memory",
            "user_count": len(self._users),
            "username_index_size": len(self._username_index),
            "email_index_size": len(self._email_index)
        }
