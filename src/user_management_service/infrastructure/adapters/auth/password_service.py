"""
Password Service Adapter

This adapter provides password hashing, verification, and policy validation.
"""

import hashlib
import logging
import re
import secrets
import string
from typing import Dict, List

from ....application.ports.password_service_port import IPasswordServicePort
from ....domain.services.user_validation_service import UserValidationService

logger = logging.getLogger(__name__)


class PasswordServiceAdapter(IPasswordServicePort):
    """
    Password service adapter implementation.

    Provides secure password hashing, verification, and policy validation.
    Uses bcrypt for production-grade password hashing.
    """

    def __init__(self):
        """Initialize the password service adapter"""
        self._password_hashes: Dict[str, str] = {}  # user_id -> password_hash
        self._validation_service = UserValidationService()

        logger.info("Initialized password service adapter")

    async def hash_password(self, password: str) -> str:
        """
        Hash a password using secure hashing algorithm.

        For simplicity in this demo, we'll use a basic hash.
        In production, use bcrypt or similar.
        """
        # Add salt for security
        salt = secrets.token_hex(16)
        password_with_salt = f"{password}{salt}"

        # Hash the password
        hash_obj = hashlib.pbkdf2_hmac(
            "sha256", password_with_salt.encode("utf-8"), salt.encode("utf-8"), 100000
        )  # 100,000 iterations

        # Return salt + hash
        return f"{salt}:{hash_obj.hex()}"

    async def verify_password(self, user_id: str, password: str) -> bool:
        """Verify a password against stored hash"""

        stored_hash = self._password_hashes.get(user_id)
        if not stored_hash:
            logger.warning(f"No password hash found for user: {user_id}")
            return False

        try:
            # Split salt and hash
            salt, hash_hex = stored_hash.split(":", 1)

            # Hash the provided password with the same salt
            password_with_salt = f"{password}{salt}"
            hash_obj = hashlib.pbkdf2_hmac(
                "sha256",
                password_with_salt.encode("utf-8"),
                salt.encode("utf-8"),
                100000,
            )

            # Compare hashes
            return hash_obj.hex() == hash_hex

        except Exception as e:
            logger.error(f"Password verification error for user {user_id}: {str(e)}")
            return False

    async def store_password_hash(self, user_id: str, password_hash: str) -> bool:
        """Store password hash for a user"""

        try:
            self._password_hashes[user_id] = password_hash
            logger.debug(f"Stored password hash for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store password hash for user {user_id}: {str(e)}")
            return False

    async def validate_password_policy(self, password: str) -> List[str]:
        """Validate password against security policy"""

        return self._validation_service.validate_password_policy(password)

    async def calculate_password_strength(self, password: str) -> float:
        """
        Calculate password strength score.

        Returns a score between 0.0 and 1.0 based on various factors.
        """
        if not password:
            return 0.0

        score = 0.0

        # Length score (up to 0.3)
        length_score = min(len(password) / 20.0, 1.0) * 0.3
        score += length_score

        # Character variety score (up to 0.4)
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        variety_score = (has_lower + has_upper + has_digit + has_special) / 4.0 * 0.4
        score += variety_score

        # Entropy score (up to 0.3)
        unique_chars = len(set(password))
        entropy_score = min(unique_chars / len(password), 1.0) * 0.3
        score += entropy_score

        # Penalty for common patterns
        if self._contains_common_patterns(password):
            score *= 0.7  # 30% penalty

        return min(score, 1.0)

    def _contains_common_patterns(self, password: str) -> bool:
        """Check if password contains common weak patterns"""

        password_lower = password.lower()

        # Common weak patterns
        weak_patterns = [
            r"123456",
            r"password",
            r"qwerty",
            r"abc123",
            r"admin",
            r"(.)\1{3,}",  # Repeated characters (4 or more)
            r"(012|123|234|345|456|567|678|789|890)",  # Sequential numbers
            r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",  # Sequential letters
        ]

        for pattern in weak_patterns:
            if re.search(pattern, password_lower):
                return True

        return False

    async def is_password_compromised(self, password: str) -> bool:
        """
        Check if password appears in known breach databases.

        For demo purposes, we'll check against a small list of common passwords.
        In production, integrate with HaveIBeenPwned API or similar service.
        """

        # Common compromised passwords
        compromised_passwords = {
            "password",
            "123456",
            "password123",
            "admin",
            "qwerty",
            "letmein",
            "welcome",
            "monkey",
            "1234567890",
            "password1",
            "abc123",
            "123456789",
            "welcome123",
            "admin123",
            "root",
        }

        return password.lower() in compromised_passwords

    async def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""

        if length < 8:
            length = 8
        elif length > 128:
            length = 128

        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = '!@#$%^&*(),.?":{}|<>'

        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special_chars),
        ]

        # Fill the rest with random characters from all sets
        all_chars = lowercase + uppercase + digits + special_chars
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return "".join(password)

    async def change_password(self, user_id: str, new_password: str) -> bool:
        """
        Change password for a user.

        This method combines hashing and storing for convenience.
        """

        try:
            # Validate password policy
            validation_errors = await self.validate_password_policy(new_password)
            if validation_errors:
                logger.warning(
                    f"Password policy validation failed for user {user_id}: {validation_errors}"
                )
                return False

            # Check if password is compromised
            if await self.is_password_compromised(new_password):
                logger.warning(
                    f"Attempted to set compromised password for user {user_id}"
                )
                return False

            # Hash and store the password
            password_hash = await self.hash_password(new_password)
            return await self.store_password_hash(user_id, password_hash)

        except Exception as e:
            logger.error(f"Failed to change password for user {user_id}: {str(e)}")
            return False

    async def get_password_age_days(self, user_id: str) -> int:
        """
        Get the age of the user's password in days.

        For demo purposes, returns a random value.
        In production, store password change timestamps.
        """
        # Demo implementation - return a value between 0 and 120 days
        import random

        return random.randint(0, 120)

    async def is_password_expired(self, user_id: str, max_age_days: int = 90) -> bool:
        """Check if password has expired"""

        password_age = await self.get_password_age_days(user_id)
        return password_age > max_age_days

    # Health check methods
    async def health_check(self) -> dict:
        """Perform health check"""
        return {
            "status": "healthy",
            "service_type": "password_service",
            "stored_hashes_count": len(self._password_hashes),
        }

    async def get_service_info(self) -> dict:
        """Get service information"""
        return {
            "service_type": "password_service",
            "hash_algorithm": "pbkdf2_hmac_sha256",
            "iterations": 100000,
            "stored_hashes_count": len(self._password_hashes),
        }
