"""
Integration tests for User Management Service.

Tests the complete UMS workflow with real adapters.
"""

from uuid import uuid4

import pytest

from src.user_management_service.application.dto.requests import AuthenticateUserRequest
from src.user_management_service.application.use_cases.authenticate_user import (
    AuthenticateUserUseCase,
)
from src.user_management_service.domain.entities.user import (
    User,
    UserProfile,
    UserRole,
    UserStatus,
)
from src.user_management_service.domain.services.user_validation_service import (
    UserValidationService,
)
from src.user_management_service.infrastructure.adapters.auth.password_service import (
    PasswordServiceAdapter,
)
from src.user_management_service.infrastructure.adapters.auth.token_service import (
    TokenServiceAdapter,
)
from src.user_management_service.infrastructure.adapters.database.in_memory.adapter import (
    InMemoryUserRepositoryAdapter,
)
from src.user_management_service.infrastructure.adapters.messaging.in_memory.adapter import (
    InMemoryEventPublisherAdapter,
)


class TestUMSIntegration:
    """Integration test cases for User Management Service"""

    @pytest.fixture
    async def user_repository(self):
        """Create user repository adapter"""
        return InMemoryUserRepositoryAdapter()

    @pytest.fixture
    async def password_service(self):
        """Create password service adapter"""
        return PasswordServiceAdapter()

    @pytest.fixture
    async def token_service(self):
        """Create token service adapter"""
        return TokenServiceAdapter()

    @pytest.fixture
    async def event_publisher(self):
        """Create event publisher adapter"""
        return InMemoryEventPublisherAdapter()

    @pytest.fixture
    def validation_service(self):
        """Create validation service"""
        return UserValidationService()

    @pytest.fixture
    async def authenticate_use_case(
        self,
        user_repository,
        password_service,
        token_service,
        event_publisher,
        validation_service,
    ):
        """Create authenticate user use case with real adapters"""
        return AuthenticateUserUseCase(
            user_repository=user_repository,
            password_service=password_service,
            token_service=token_service,
            event_publisher=event_publisher,
            validation_service=validation_service,
        )

    @pytest.fixture
    async def test_user(self, user_repository, password_service):
        """Create and save a test user"""
        profile = UserProfile(
            first_name="John",
            last_name="Doe",
            email="john.doe@hospital.org",
            department="Quality Assurance",
        )

        user = User(
            user_id=uuid4(),
            username="john.doe",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            status=UserStatus.ACTIVE,
        )

        # Save user and password
        saved_user = await user_repository.save(user)
        await password_service.change_password(str(user.user_id), "SecurePassword123!")

        return saved_user

    @pytest.mark.asyncio
    async def test_complete_authentication_workflow(
        self, authenticate_use_case, test_user, event_publisher
    ):
        """Test complete authentication workflow with real adapters"""

        # Create authentication request
        auth_request = AuthenticateUserRequest(
            username="john.doe",
            password="SecurePassword123!",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0...",
        )

        # Execute authentication
        response = await authenticate_use_case.execute(auth_request)

        # Verify successful authentication
        assert response.success is True
        assert response.user_id == str(test_user.user_id)
        assert response.username == "john.doe"
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.expires_in > 0
        assert len(response.permissions) > 0
        assert "submit_error_report" in response.permissions
        assert response.message == "Authentication successful"

        # Verify events were published
        published_events = event_publisher.get_published_events()
        assert len(published_events) == 1
        assert published_events[0]["event_type"] == "user.login_success"

    @pytest.mark.asyncio
    async def test_authentication_with_invalid_password(
        self, authenticate_use_case, test_user, event_publisher
    ):
        """Test authentication with invalid password"""

        # Create authentication request with wrong password
        auth_request = AuthenticateUserRequest(
            username="john.doe",
            password="WrongPassword123!",
            ip_address="192.168.1.100",
        )

        # Execute authentication
        response = await authenticate_use_case.execute(auth_request)

        # Verify failed authentication
        assert response.success is False
        assert response.user_id is None
        assert response.access_token is None
        assert response.message == "Invalid username or password"

        # Verify failure event was published
        published_events = event_publisher.get_published_events()
        failure_events = [
            e for e in published_events if e["event_type"] == "user.login_failure"
        ]
        assert len(failure_events) == 1

    @pytest.mark.asyncio
    async def test_authentication_with_nonexistent_user(
        self, authenticate_use_case, event_publisher
    ):
        """Test authentication with nonexistent user"""

        # Create authentication request for nonexistent user
        auth_request = AuthenticateUserRequest(
            username="nonexistent.user",
            password="SomePassword123!",
            ip_address="192.168.1.100",
        )

        # Execute authentication
        response = await authenticate_use_case.execute(auth_request)

        # Verify failed authentication
        assert response.success is False
        assert response.user_id is None
        assert response.access_token is None
        assert response.message == "Invalid username or password"

        # Verify failure event was published
        published_events = event_publisher.get_published_events()
        failure_events = [
            e for e in published_events if e["event_type"] == "user.login_failure"
        ]
        assert len(failure_events) == 1

    @pytest.mark.asyncio
    async def test_user_repository_operations(self, user_repository):
        """Test user repository operations"""

        # Create test user
        profile = UserProfile(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@hospital.org",
            department="Medical Transcription",
        )

        user = User(
            username="jane.smith", profile=profile, roles={UserRole.MTS_PERSONNEL}
        )

        # Save user
        saved_user = await user_repository.save(user)
        assert saved_user.user_id == user.user_id
        assert saved_user.username == "jane.smith"

        # Get user by ID
        retrieved_user = await user_repository.get_by_id(user.user_id)
        assert retrieved_user is not None
        assert retrieved_user.username == "jane.smith"

        # Get user by username
        retrieved_user = await user_repository.get_by_username("jane.smith")
        assert retrieved_user is not None
        assert retrieved_user.user_id == user.user_id

        # Get user by email
        retrieved_user = await user_repository.get_by_email("jane.smith@hospital.org")
        assert retrieved_user is not None
        assert retrieved_user.user_id == user.user_id

        # Check existence
        exists = await user_repository.exists_by_username("jane.smith")
        assert exists is True

        exists = await user_repository.exists_by_email("jane.smith@hospital.org")
        assert exists is True

        # Get user count
        count = await user_repository.get_user_count()
        assert count >= 1

    @pytest.mark.asyncio
    async def test_password_service_operations(self, password_service):
        """Test password service operations"""

        user_id = str(uuid4())
        password = "TestPassword123!"

        # Test password policy validation
        errors = await password_service.validate_password_policy(password)
        assert len(errors) == 0  # Should be valid

        # Test weak password
        weak_errors = await password_service.validate_password_policy("123456")
        assert len(weak_errors) > 0

        # Test password strength calculation
        strength = await password_service.calculate_password_strength(password)
        assert 0.0 <= strength <= 1.0
        assert strength > 0.5  # Should be reasonably strong

        # Test compromised password check
        is_compromised = await password_service.is_password_compromised("password")
        assert is_compromised is True

        is_compromised = await password_service.is_password_compromised(password)
        assert is_compromised is False

        # Test password change
        success = await password_service.change_password(user_id, password)
        assert success is True

        # Test password verification
        is_valid = await password_service.verify_password(user_id, password)
        assert is_valid is True

        is_valid = await password_service.verify_password(user_id, "wrong_password")
        assert is_valid is False

        # Test secure password generation
        generated_password = await password_service.generate_secure_password(16)
        assert len(generated_password) == 16

        # Generated password should be strong
        strength = await password_service.calculate_password_strength(
            generated_password
        )
        assert strength > 0.7

    @pytest.mark.asyncio
    async def test_token_service_operations(self, token_service):
        """Test token service operations"""

        user_id = str(uuid4())
        username = "test.user"
        permissions = ["submit_error_report", "view_error_reports"]

        # Create access token
        access_token = await token_service.create_access_token(
            user_id=user_id, username=username, permissions=permissions
        )
        assert access_token is not None
        assert access_token.startswith("ums_access_")

        # Create refresh token
        refresh_token = await token_service.create_refresh_token(user_id)
        assert refresh_token is not None
        assert refresh_token.startswith("ums_refresh_")

        # Validate access token
        claims = await token_service.validate_access_token(access_token)
        assert claims["user_id"] == user_id
        assert claims["username"] == username
        assert claims["permissions"] == permissions
        assert claims["token_type"] == "access"

        # Validate refresh token
        refresh_claims = await token_service.validate_refresh_token(refresh_token)
        assert refresh_claims["user_id"] == user_id
        assert refresh_claims["token_type"] == "refresh"

        # Test token revocation
        is_revoked = await token_service.is_token_revoked(access_token)
        assert is_revoked is False

        success = await token_service.revoke_token(access_token)
        assert success is True

        is_revoked = await token_service.is_token_revoked(access_token)
        assert is_revoked is True

        # Revoked token should not validate
        with pytest.raises(ValueError, match="Token has been revoked"):
            await token_service.validate_access_token(access_token)

    @pytest.mark.asyncio
    async def test_event_publisher_operations(self, event_publisher):
        """Test event publisher operations"""


        from src.user_management_service.domain.events.domain_events import (
            UserCreatedEvent,
        )

        # Create and publish event
        event = UserCreatedEvent(
            event_id="test_event_123",
            user_id="user_123",
            username="test.user",
            email="test@hospital.org",
            first_name="Test",
            last_name="User",
            roles=["qa_personnel"],
            status="pending_activation",
            created_by="admin",
        )

        await event_publisher.publish_user_created(event)

        # Verify event was published
        published_events = event_publisher.get_published_events()
        assert len(published_events) == 1

        published_event = published_events[0]
        assert published_event["event_type"] == "user.created"
        assert published_event["event"]["user_id"] == "user_123"
        assert published_event["event"]["username"] == "test.user"

        # Test event filtering
        created_events = event_publisher.get_events_by_type("user.created")
        assert len(created_events) == 1

        other_events = event_publisher.get_events_by_type("user.deleted")
        assert len(other_events) == 0

        # Test event count
        total_count = event_publisher.get_event_count()
        assert total_count == 1

        type_count = event_publisher.get_event_count_by_type("user.created")
        assert type_count == 1
