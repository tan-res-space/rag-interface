"""
Token Service Port Interface

This module defines the port interface for token operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional


class ITokenServicePort(ABC):
    """
    Port interface for token operations.

    This interface defines the contract for JWT token operations
    including creation, validation, and management.
    """

    @abstractmethod
    async def create_access_token(
        self,
        user_id: str,
        username: str,
        permissions: List[str],
        expires_in_seconds: Optional[int] = None,
    ) -> str:
        """
        Create an access token for a user.

        Args:
            user_id: ID of the user
            username: Username of the user
            permissions: List of user permissions
            expires_in_seconds: Optional custom expiration time

        Returns:
            JWT access token string

        Raises:
            TokenServiceException: If token creation fails
        """
        pass

    @abstractmethod
    async def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token for a user.

        Args:
            user_id: ID of the user

        Returns:
            JWT refresh token string

        Raises:
            TokenServiceException: If token creation fails
        """
        pass

    @abstractmethod
    async def validate_access_token(self, token: str) -> Dict[str, any]:
        """
        Validate an access token and return claims.

        Args:
            token: JWT access token to validate

        Returns:
            Dictionary containing token claims

        Raises:
            InvalidTokenException: If token is invalid or expired
        """
        pass

    @abstractmethod
    async def validate_refresh_token(self, token: str) -> Dict[str, any]:
        """
        Validate a refresh token and return claims.

        Args:
            token: JWT refresh token to validate

        Returns:
            Dictionary containing token claims

        Raises:
            InvalidTokenException: If token is invalid or expired
        """
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> tuple:
        """
        Create new access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token, expires_in)

        Raises:
            InvalidTokenException: If refresh token is invalid
        """
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (add to blacklist).

        Args:
            token: Token to revoke

        Returns:
            True if token was revoked successfully

        Raises:
            TokenServiceException: If revocation fails
        """
        pass

    @abstractmethod
    async def revoke_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a user.

        Args:
            user_id: ID of the user

        Returns:
            Number of tokens revoked

        Raises:
            TokenServiceException: If revocation fails
        """
        pass

    @abstractmethod
    async def is_token_revoked(self, token: str) -> bool:
        """
        Check if a token has been revoked.

        Args:
            token: Token to check

        Returns:
            True if token is revoked, False otherwise
        """
        pass

    @abstractmethod
    async def get_token_expiry_seconds(self) -> int:
        """
        Get default token expiry time in seconds.

        Returns:
            Token expiry time in seconds
        """
        pass

    @abstractmethod
    async def decode_token_claims(self, token: str) -> Dict[str, any]:
        """
        Decode token claims without validation.

        Args:
            token: Token to decode

        Returns:
            Dictionary containing token claims

        Raises:
            TokenServiceException: If token cannot be decoded
        """
        pass

    @abstractmethod
    async def get_user_active_sessions(self, user_id: str) -> List[Dict[str, any]]:
        """
        Get active sessions for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of active session information
        """
        pass
