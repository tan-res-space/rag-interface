"""
Authentication Port Interface

This module defines the port interface for authentication operations
as specified in the ASR System Architecture Design document.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..dto.requests import (
    AuthenticateUserRequest,
    ValidateTokenRequest,
    RefreshTokenRequest
)
from ..dto.responses import (
    AuthenticationResponse,
    TokenValidationResponse,
    TokenRefreshResponse
)


class IAuthenticationPort(ABC):
    """
    Port interface for authentication operations.
    
    This interface defines the contract for authentication-related operations
    as specified in the architecture design document.
    """
    
    @abstractmethod
    async def authenticate_user(self, request: AuthenticateUserRequest) -> AuthenticationResponse:
        """
        Authenticate a user with username and password.
        
        Business rules:
        1. Validate user credentials
        2. Check account status (active, not locked)
        3. Generate access and refresh tokens
        4. Record login attempt (success/failure)
        5. Update last login timestamp
        
        Args:
            request: Authentication request containing credentials
            
        Returns:
            Authentication response with tokens and user info
            
        Raises:
            AuthenticationError: If authentication fails
            AccountLockedException: If account is locked
            InactiveAccountException: If account is inactive
        """
        pass
    
    @abstractmethod
    async def validate_token(self, request: ValidateTokenRequest) -> TokenValidationResponse:
        """
        Validate an access token and optionally check permissions.
        
        Business rules:
        1. Verify token signature and expiration
        2. Check if user account is still active
        3. Validate required permissions if specified
        4. Return user information and permissions
        
        Args:
            request: Token validation request
            
        Returns:
            Token validation response with user info and permissions
            
        Raises:
            InvalidTokenException: If token is invalid or expired
            InsufficientPermissionsException: If user lacks required permissions
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, request: RefreshTokenRequest) -> TokenRefreshResponse:
        """
        Refresh an access token using a refresh token.
        
        Business rules:
        1. Validate refresh token
        2. Check if user account is still active
        3. Generate new access token
        4. Optionally rotate refresh token
        
        Args:
            request: Token refresh request
            
        Returns:
            Token refresh response with new tokens
            
        Raises:
            InvalidTokenException: If refresh token is invalid
            InactiveAccountException: If account is inactive
        """
        pass
    
    @abstractmethod
    async def logout(self, user_id: str, token: str) -> None:
        """
        Logout a user and invalidate their tokens.
        
        Business rules:
        1. Invalidate access token
        2. Invalidate refresh token
        3. Record logout event
        4. Clear session data
        
        Args:
            user_id: ID of the user to logout
            token: Access token to invalidate
            
        Raises:
            InvalidTokenException: If token is invalid
        """
        pass
    
    @abstractmethod
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Business rules:
        1. Verify current password
        2. Validate new password against policy
        3. Hash and store new password
        4. Invalidate existing tokens
        5. Record password change event
        
        Args:
            user_id: ID of the user
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password was changed successfully
            
        Raises:
            InvalidPasswordException: If current password is incorrect
            WeakPasswordException: If new password doesn't meet policy
        """
        pass
    
    @abstractmethod
    async def reset_password(self, user_id: str, new_password: str, reset_by: str) -> bool:
        """
        Reset a user's password (admin operation).
        
        Business rules:
        1. Validate admin permissions
        2. Validate new password against policy
        3. Hash and store new password
        4. Invalidate existing tokens
        5. Record password reset event
        6. Notify user of password reset
        
        Args:
            user_id: ID of the user
            new_password: New password to set
            reset_by: ID of the admin performing the reset
            
        Returns:
            True if password was reset successfully
            
        Raises:
            InsufficientPermissionsException: If reset_by lacks permissions
            WeakPasswordException: If new password doesn't meet policy
        """
        pass
    
    @abstractmethod
    async def lock_account(self, user_id: str, reason: str, locked_by: Optional[str] = None) -> None:
        """
        Lock a user account.
        
        Business rules:
        1. Set account lock status
        2. Set lock expiration time
        3. Invalidate existing tokens
        4. Record account lock event
        5. Notify user and administrators
        
        Args:
            user_id: ID of the user to lock
            reason: Reason for locking the account
            locked_by: ID of the admin locking the account (None for system)
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def unlock_account(self, user_id: str, unlocked_by: str) -> None:
        """
        Unlock a user account.
        
        Business rules:
        1. Remove account lock status
        2. Reset failed login attempts
        3. Record account unlock event
        4. Notify user of account unlock
        
        Args:
            user_id: ID of the user to unlock
            unlocked_by: ID of the admin unlocking the account
            
        Raises:
            UserNotFoundException: If user doesn't exist
            InsufficientPermissionsException: If unlocked_by lacks permissions
        """
        pass
    
    @abstractmethod
    async def get_user_sessions(self, user_id: str) -> list:
        """
        Get active sessions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of active session information
            
        Raises:
            UserNotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    async def revoke_user_sessions(self, user_id: str, revoked_by: str) -> int:
        """
        Revoke all active sessions for a user.
        
        Business rules:
        1. Invalidate all access tokens
        2. Invalidate all refresh tokens
        3. Clear session data
        4. Record session revocation event
        
        Args:
            user_id: ID of the user
            revoked_by: ID of the admin revoking sessions
            
        Returns:
            Number of sessions revoked
            
        Raises:
            UserNotFoundException: If user doesn't exist
            InsufficientPermissionsException: If revoked_by lacks permissions
        """
        pass
