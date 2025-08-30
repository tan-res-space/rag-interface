"""
Password Service Port Interface

This module defines the port interface for password operations.
"""

from abc import ABC, abstractmethod
from typing import List


class IPasswordServicePort(ABC):
    """
    Port interface for password operations.

    This interface defines the contract for password-related operations
    including hashing, verification, and policy validation.
    """

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """
        Hash a password using secure hashing algorithm.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string

        Raises:
            PasswordServiceException: If hashing fails
        """
        pass

    @abstractmethod
    async def verify_password(self, user_id: str, password: str) -> bool:
        """
        Verify a password against stored hash.

        Args:
            user_id: ID of the user
            password: Plain text password to verify

        Returns:
            True if password is correct, False otherwise

        Raises:
            PasswordServiceException: If verification fails
        """
        pass

    @abstractmethod
    async def store_password_hash(self, user_id: str, password_hash: str) -> bool:
        """
        Store password hash for a user.

        Args:
            user_id: ID of the user
            password_hash: Hashed password to store

        Returns:
            True if stored successfully

        Raises:
            PasswordServiceException: If storage fails
        """
        pass

    @abstractmethod
    async def validate_password_policy(self, password: str) -> List[str]:
        """
        Validate password against security policy.

        Args:
            password: Password to validate

        Returns:
            List of validation errors (empty if valid)
        """
        pass

    @abstractmethod
    async def calculate_password_strength(self, password: str) -> float:
        """
        Calculate password strength score.

        Args:
            password: Password to analyze

        Returns:
            Strength score between 0.0 and 1.0
        """
        pass

    @abstractmethod
    async def is_password_compromised(self, password: str) -> bool:
        """
        Check if password appears in known breach databases.

        Args:
            password: Password to check

        Returns:
            True if password is compromised, False otherwise
        """
        pass

    @abstractmethod
    async def generate_secure_password(self, length: int = 16) -> str:
        """
        Generate a secure random password.

        Args:
            length: Length of password to generate

        Returns:
            Generated secure password
        """
        pass
