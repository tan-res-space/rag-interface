"""
Authenticate User Use Case

This module contains the use case for user authentication.
It orchestrates the authentication process according to business rules.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ...domain.entities.user import User
from ...domain.events.domain_events import (
    UserAccountLockedEvent,
    UserLoginFailureEvent,
    UserLoginSuccessEvent,
)
from ...domain.services.user_validation_service import UserValidationService
from ..dto.requests import AuthenticateUserRequest
from ..dto.responses import AuthenticationResponse
from ..ports.event_publisher_port import IEventPublisherPort
from ..ports.password_service_port import IPasswordServicePort
from ..ports.token_service_port import ITokenServicePort
from ..ports.user_repository_port import IUserRepositoryPort

logger = logging.getLogger(__name__)


class AuthenticateUserUseCase:
    """
    Use case for authenticating users.

    This use case handles the complete authentication workflow including
    credential validation, account status checks, token generation, and
    audit logging.
    """

    def __init__(
        self,
        user_repository: IUserRepositoryPort,
        password_service: IPasswordServicePort,
        token_service: ITokenServicePort,
        event_publisher: IEventPublisherPort,
        validation_service: UserValidationService,
    ):
        """
        Initialize the authenticate user use case.

        Args:
            user_repository: Repository for user data access
            password_service: Service for password operations
            token_service: Service for token operations
            event_publisher: Service for publishing domain events
            validation_service: Service for user validation
        """
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service
        self._event_publisher = event_publisher
        self._validation_service = validation_service

    async def execute(self, request: AuthenticateUserRequest) -> AuthenticationResponse:
        """
        Execute the user authentication use case.

        Business workflow:
        1. Validate request data
        2. Find user by username
        3. Check account status and lock status
        4. Verify password
        5. Generate tokens
        6. Update user login information
        7. Publish success event
        8. Return authentication response

        Args:
            request: Authentication request

        Returns:
            Authentication response with tokens and user info
        """
        logger.info(f"Authenticating user: {request.username}")

        try:
            # 1. Find user by username
            user = await self._find_user_by_username(request.username)
            if not user:
                await self._handle_authentication_failure(
                    request.username,
                    "user_not_found",
                    request.ip_address,
                    request.user_agent,
                )
                return AuthenticationResponse(
                    success=False, message="Invalid username or password"
                )

            # 2. Check account status
            if not self._check_account_status(user):
                await self._handle_authentication_failure(
                    request.username,
                    "account_inactive",
                    request.ip_address,
                    request.user_agent,
                    user,
                )
                return AuthenticationResponse(
                    success=False, message="Account is not active"
                )

            # 3. Check if account is locked
            if self._is_account_locked(user):
                await self._handle_authentication_failure(
                    request.username,
                    "account_locked",
                    request.ip_address,
                    request.user_agent,
                    user,
                )
                return AuthenticationResponse(
                    success=False, message="Account is temporarily locked"
                )

            # 4. Verify password
            if not await self._verify_password(user, request.password):
                await self._handle_authentication_failure(
                    request.username,
                    "invalid_password",
                    request.ip_address,
                    request.user_agent,
                    user,
                )

                # Check if account should be locked after this failure
                if user.failed_login_attempts >= 5:
                    await self._lock_account(user, request.ip_address)

                return AuthenticationResponse(
                    success=False, message="Invalid username or password"
                )

            # 5. Generate tokens
            access_token, refresh_token, expires_in = await self._generate_tokens(user)

            # 6. Update user login information
            await self._update_user_login_success(user)

            # 7. Publish success event
            await self._publish_login_success_event(
                user, request.ip_address, request.user_agent
            )

            # 8. Return success response
            logger.info(f"User authenticated successfully: {user.username}")
            return AuthenticationResponse(
                success=True,
                user_id=str(user.user_id),
                username=user.username,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                permissions=[perm.value for perm in user.get_permissions()],
                message="Authentication successful",
            )

        except Exception as e:
            logger.error(f"Authentication error for user {request.username}: {str(e)}")
            await self._handle_authentication_failure(
                request.username, "system_error", request.ip_address, request.user_agent
            )
            return AuthenticationResponse(
                success=False, message="Authentication failed due to system error"
            )

    async def _find_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        try:
            return await self._user_repository.get_by_username(username)
        except Exception:
            return None

    def _check_account_status(self, user: User) -> bool:
        """Check if user account is in valid status for authentication"""
        return user.is_active()

    def _is_account_locked(self, user: User) -> bool:
        """Check if account is currently locked"""
        if user.account_locked_until is None:
            return False
        return user.account_locked_until > datetime.utcnow()

    async def _verify_password(self, user: User, password: str) -> bool:
        """Verify user password"""
        return await self._password_service.verify_password(str(user.user_id), password)

    async def _generate_tokens(self, user: User) -> tuple:
        """Generate access and refresh tokens"""
        access_token = await self._token_service.create_access_token(
            user_id=str(user.user_id),
            username=user.username,
            permissions=[perm.value for perm in user.get_permissions()],
        )

        refresh_token = await self._token_service.create_refresh_token(
            user_id=str(user.user_id)
        )

        expires_in = await self._token_service.get_token_expiry_seconds()

        return access_token, refresh_token, expires_in

    async def _update_user_login_success(self, user: User) -> None:
        """Update user with successful login information"""
        user.record_login_success()
        await self._user_repository.save(user)

    async def _handle_authentication_failure(
        self,
        username: str,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user: Optional[User] = None,
    ) -> None:
        """Handle authentication failure"""

        # Update user failed attempts if user exists
        if user:
            user.record_login_failure()
            await self._user_repository.save(user)

        # Publish failure event
        event = UserLoginFailureEvent(
            event_id=str(uuid4()),
            username=username,
            failure_reason=reason,
            attempt_timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            failed_attempts_count=user.failed_login_attempts if user else 1,
        )

        await self._event_publisher.publish_user_login_failure(event)

        logger.warning(f"Authentication failure for {username}: {reason}")

    async def _lock_account(self, user: User, ip_address: Optional[str] = None) -> None:
        """Lock user account due to too many failed attempts"""

        # Publish account locked event
        event = UserAccountLockedEvent(
            event_id=str(uuid4()),
            user_id=str(user.user_id),
            username=user.username,
            email=user.profile.email,
            locked_until=user.account_locked_until,
            reason="too_many_failed_attempts",
            failed_attempts=user.failed_login_attempts,
            ip_address=ip_address,
        )

        await self._event_publisher.publish_user_account_locked(event)

        logger.warning(
            f"Account locked for user {user.username} due to failed attempts"
        )

    async def _publish_login_success_event(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Publish successful login event"""

        event = UserLoginSuccessEvent(
            event_id=str(uuid4()),
            user_id=str(user.user_id),
            username=user.username,
            login_timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=str(uuid4()),  # Generate session ID
        )

        await self._event_publisher.publish_user_login_success(event)
