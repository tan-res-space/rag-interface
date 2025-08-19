"""
Unit tests for Authenticate User Use Case.

Tests the authentication workflow and business logic.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta
from uuid import uuid4

from src.user_management_service.application.use_cases.authenticate_user import AuthenticateUserUseCase
from src.user_management_service.application.dto.requests import AuthenticateUserRequest
from src.user_management_service.domain.entities.user import User, UserRole, UserStatus, UserProfile
from src.user_management_service.domain.services.user_validation_service import UserValidationService


class TestAuthenticateUserUseCase:
    """Test cases for Authenticate User Use Case"""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_password_service(self):
        """Mock password service"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_token_service(self):
        """Mock token service"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_publisher(self):
        """Mock event publisher"""
        return AsyncMock()
    
    @pytest.fixture
    def validation_service(self):
        """Real validation service"""
        return UserValidationService()
    
    @pytest.fixture
    def use_case(self, mock_user_repository, mock_password_service, 
                 mock_token_service, mock_event_publisher, validation_service):
        """Create use case instance with mocked dependencies"""
        return AuthenticateUserUseCase(
            user_repository=mock_user_repository,
            password_service=mock_password_service,
            token_service=mock_token_service,
            event_publisher=mock_event_publisher,
            validation_service=validation_service
        )
    
    @pytest.fixture
    def valid_user(self):
        """Create a valid active user"""
        profile = UserProfile(
            first_name="John",
            last_name="Doe",
            email="john.doe@hospital.org",
            department="Quality Assurance"
        )
        
        return User(
            user_id=uuid4(),
            username="john.doe",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            status=UserStatus.ACTIVE
        )
    
    @pytest.fixture
    def auth_request(self):
        """Create authentication request"""
        return AuthenticateUserRequest(
            username="john.doe",
            password="SecurePassword123!",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0..."
        )
    
    @pytest.mark.asyncio
    async def test_successful_authentication(self, use_case, mock_user_repository,
                                           mock_password_service, mock_token_service,
                                           mock_event_publisher, valid_user, auth_request):
        """Test successful user authentication"""
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = valid_user
        mock_password_service.verify_password.return_value = True
        mock_token_service.create_access_token.return_value = "access_token_123"
        mock_token_service.create_refresh_token.return_value = "refresh_token_123"
        mock_token_service.get_token_expiry_seconds.return_value = 1800
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify response
        assert response.success is True
        assert response.user_id == str(valid_user.user_id)
        assert response.username == valid_user.username
        assert response.access_token == "access_token_123"
        assert response.refresh_token == "refresh_token_123"
        assert response.expires_in == 1800
        assert "submit_error_report" in response.permissions
        assert response.message == "Authentication successful"
        
        # Verify interactions
        mock_user_repository.get_by_username.assert_called_once_with("john.doe")
        mock_password_service.verify_password.assert_called_once_with(
            str(valid_user.user_id), "SecurePassword123!"
        )
        mock_user_repository.save.assert_called_once()
        mock_event_publisher.publish_user_login_success.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_user_not_found(self, use_case, mock_user_repository,
                                                mock_event_publisher, auth_request):
        """Test authentication when user is not found"""
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = None
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify response
        assert response.success is False
        assert response.user_id is None
        assert response.access_token is None
        assert response.message == "Invalid username or password"
        
        # Verify interactions
        mock_user_repository.get_by_username.assert_called_once_with("john.doe")
        mock_event_publisher.publish_user_login_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_inactive_user(self, use_case, mock_user_repository,
                                              mock_event_publisher, valid_user, auth_request):
        """Test authentication with inactive user"""
        
        # Make user inactive
        valid_user.status = UserStatus.INACTIVE
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = valid_user
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify response
        assert response.success is False
        assert response.message == "Account is not active"
        
        # Verify interactions
        mock_event_publisher.publish_user_login_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_locked_account(self, use_case, mock_user_repository,
                                                mock_event_publisher, valid_user, auth_request):
        """Test authentication with locked account"""
        
        # Lock the account
        valid_user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = valid_user
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify response
        assert response.success is False
        assert response.message == "Account is temporarily locked"
        
        # Verify interactions
        mock_event_publisher.publish_user_login_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_invalid_password(self, use_case, mock_user_repository,
                                                  mock_password_service, mock_event_publisher,
                                                  valid_user, auth_request):
        """Test authentication with invalid password"""
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = valid_user
        mock_password_service.verify_password.return_value = False
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify response
        assert response.success is False
        assert response.message == "Invalid username or password"
        
        # Verify interactions
        mock_password_service.verify_password.assert_called_once_with(
            str(valid_user.user_id), "SecurePassword123!"
        )
        mock_user_repository.save.assert_called_once()  # To update failed attempts
        mock_event_publisher.publish_user_login_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_locks_account_after_5_failures(self, use_case, mock_user_repository,
                                                               mock_password_service, mock_event_publisher,
                                                               valid_user, auth_request):
        """Test account gets locked after 5 failed attempts"""
        
        # Set user to have 4 failed attempts
        valid_user.failed_login_attempts = 4
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = valid_user
        mock_password_service.verify_password.return_value = False
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify response
        assert response.success is False
        
        # Verify user was updated with lock
        assert valid_user.failed_login_attempts == 5
        assert valid_user.account_locked_until is not None
        
        # Verify interactions
        mock_user_repository.save.assert_called_once()
        mock_event_publisher.publish_user_login_failure.assert_called_once()
        mock_event_publisher.publish_user_account_locked.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_system_error(self, use_case, mock_user_repository,
                                              mock_event_publisher, auth_request):
        """Test authentication handles system errors gracefully"""
        
        # Setup mocks to raise exception
        mock_user_repository.get_by_username.side_effect = Exception("Database error")
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify response
        assert response.success is False
        assert response.message == "Authentication failed due to system error"
        
        # Verify interactions
        mock_event_publisher.publish_user_login_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_updates_user_on_success(self, use_case, mock_user_repository,
                                                         mock_password_service, mock_token_service,
                                                         valid_user, auth_request):
        """Test user is updated with login success information"""
        
        # Set some failed attempts to verify they get reset
        valid_user.failed_login_attempts = 3
        valid_user.account_locked_until = datetime.utcnow() + timedelta(minutes=10)
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = valid_user
        mock_password_service.verify_password.return_value = True
        mock_token_service.create_access_token.return_value = "access_token"
        mock_token_service.create_refresh_token.return_value = "refresh_token"
        mock_token_service.get_token_expiry_seconds.return_value = 1800
        
        # Execute use case
        response = await use_case.execute(auth_request)
        
        # Verify user was updated
        assert response.success is True
        assert valid_user.failed_login_attempts == 0
        assert valid_user.account_locked_until is None
        assert valid_user.last_login is not None
        
        # Verify user was saved
        mock_user_repository.save.assert_called_once_with(valid_user)
    
    @pytest.mark.asyncio
    async def test_authentication_generates_correct_tokens(self, use_case, mock_user_repository,
                                                          mock_password_service, mock_token_service,
                                                          valid_user, auth_request):
        """Test correct tokens are generated with user information"""
        
        # Setup mocks
        mock_user_repository.get_by_username.return_value = valid_user
        mock_password_service.verify_password.return_value = True
        mock_token_service.create_access_token.return_value = "access_token"
        mock_token_service.create_refresh_token.return_value = "refresh_token"
        mock_token_service.get_token_expiry_seconds.return_value = 1800
        
        # Execute use case
        await use_case.execute(auth_request)
        
        # Verify token creation calls
        mock_token_service.create_access_token.assert_called_once_with(
            user_id=str(valid_user.user_id),
            username=valid_user.username,
            permissions=[perm.value for perm in valid_user.get_permissions()]
        )
        
        mock_token_service.create_refresh_token.assert_called_once_with(
            user_id=str(valid_user.user_id)
        )
