"""
Unit tests for User entity.

Tests the User domain entity business logic and validation rules.
"""

from datetime import datetime, timedelta
from uuid import uuid4


from src.user_management_service.domain.entities.user import (
    Permission,
    User,
    UserProfile,
    UserRole,
    UserStatus,
)


class TestUserEntity:
    """Test cases for User entity"""

    def test_user_creation_with_valid_data(self):
        """Test creating a user with valid data"""

        profile = UserProfile(
            first_name="John",
            last_name="Doe",
            email="john.doe@hospital.org",
            department="Quality Assurance",
        )

        user = User(username="john.doe", profile=profile, roles={UserRole.QA_PERSONNEL})

        assert user.username == "john.doe"
        assert user.profile.first_name == "John"
        assert user.profile.last_name == "Doe"
        assert user.profile.email == "john.doe@hospital.org"
        assert UserRole.QA_PERSONNEL in user.roles
        assert user.status == UserStatus.PENDING_ACTIVATION
        assert isinstance(user.user_id, type(uuid4()))

    def test_user_permissions_qa_personnel(self):
        """Test permissions for QA personnel role"""

        profile = UserProfile(
            first_name="Jane", last_name="Smith", email="jane.smith@hospital.org"
        )

        user = User(
            username="jane.smith", profile=profile, roles={UserRole.QA_PERSONNEL}
        )

        permissions = user.get_permissions()

        assert Permission.SUBMIT_ERROR_REPORT in permissions
        assert Permission.VIEW_ERROR_REPORTS in permissions
        assert Permission.EDIT_ERROR_REPORTS in permissions
        assert Permission.VERIFY_CORRECTIONS not in permissions
        assert Permission.MANAGE_USERS not in permissions

    def test_user_permissions_mts_personnel(self):
        """Test permissions for MTS personnel role"""

        profile = UserProfile(
            first_name="Bob", last_name="Johnson", email="bob.johnson@hospital.org"
        )

        user = User(
            username="bob.johnson", profile=profile, roles={UserRole.MTS_PERSONNEL}
        )

        permissions = user.get_permissions()

        assert Permission.VERIFY_CORRECTIONS in permissions
        assert Permission.VIEW_VERIFICATION_DASHBOARD in permissions
        assert Permission.EXPORT_VERIFICATION_DATA in permissions
        assert Permission.VIEW_ERROR_REPORTS in permissions
        assert Permission.SUBMIT_ERROR_REPORT not in permissions
        assert Permission.MANAGE_USERS not in permissions

    def test_user_permissions_system_admin(self):
        """Test permissions for system admin role"""

        profile = UserProfile(
            first_name="Admin", last_name="User", email="admin@hospital.org"
        )

        user = User(username="admin", profile=profile, roles={UserRole.SYSTEM_ADMIN})

        permissions = user.get_permissions()

        # System admin should have all permissions
        all_permissions = list(Permission)
        for permission in all_permissions:
            assert permission in permissions

    def test_user_permissions_multiple_roles(self):
        """Test permissions for user with multiple roles"""

        profile = UserProfile(
            first_name="Multi", last_name="Role", email="multi.role@hospital.org"
        )

        user = User(
            username="multi.role",
            profile=profile,
            roles={UserRole.QA_PERSONNEL, UserRole.MTS_PERSONNEL},
        )

        permissions = user.get_permissions()

        # Should have permissions from both roles
        assert Permission.SUBMIT_ERROR_REPORT in permissions  # QA
        assert Permission.VERIFY_CORRECTIONS in permissions  # MTS
        assert Permission.VIEW_ERROR_REPORTS in permissions  # Both
        assert Permission.MANAGE_USERS not in permissions  # Neither

    def test_user_is_active_when_status_active_and_has_roles(self):
        """Test user is active when status is active and has roles"""

        profile = UserProfile(
            first_name="Active", last_name="User", email="active@hospital.org"
        )

        user = User(
            username="active.user",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            status=UserStatus.ACTIVE,
        )

        assert user.is_active() is True

    def test_user_is_not_active_when_status_inactive(self):
        """Test user is not active when status is inactive"""

        profile = UserProfile(
            first_name="Inactive", last_name="User", email="inactive@hospital.org"
        )

        user = User(
            username="inactive.user",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            status=UserStatus.INACTIVE,
        )

        assert user.is_active() is False

    def test_user_is_not_active_when_account_locked(self):
        """Test user is not active when account is locked"""

        profile = UserProfile(
            first_name="Locked", last_name="User", email="locked@hospital.org"
        )

        user = User(
            username="locked.user",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            status=UserStatus.ACTIVE,
            account_locked_until=datetime.utcnow() + timedelta(minutes=30),
        )

        assert user.is_active() is False

    def test_user_is_not_active_when_no_roles(self):
        """Test user is not active when has no roles"""

        profile = UserProfile(
            first_name="No", last_name="Roles", email="noroles@hospital.org"
        )

        user = User(
            username="no.roles", profile=profile, roles=set(), status=UserStatus.ACTIVE
        )

        assert user.is_active() is False

    def test_user_login_success_updates_fields(self):
        """Test recording successful login updates relevant fields"""

        profile = UserProfile(
            first_name="Login", last_name="Test", email="login@hospital.org"
        )

        user = User(
            username="login.test",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            failed_login_attempts=3,
            account_locked_until=datetime.utcnow() + timedelta(minutes=10),
        )

        user.record_login_success()

        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None
        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)

    def test_user_login_failure_increments_attempts(self):
        """Test recording failed login increments attempt counter"""

        profile = UserProfile(
            first_name="Fail", last_name="Test", email="fail@hospital.org"
        )

        user = User(
            username="fail.test",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            failed_login_attempts=2,
        )

        user.record_login_failure()

        assert user.failed_login_attempts == 3

    def test_user_login_failure_locks_account_after_5_attempts(self):
        """Test account gets locked after 5 failed attempts"""

        profile = UserProfile(
            first_name="Lock", last_name="Test", email="lock@hospital.org"
        )

        user = User(
            username="lock.test",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            failed_login_attempts=4,
        )

        user.record_login_failure()

        assert user.failed_login_attempts == 5
        assert user.account_locked_until is not None
        assert user.account_locked_until > datetime.utcnow()

    def test_user_role_management(self):
        """Test adding and removing roles"""

        profile = UserProfile(
            first_name="Role", last_name="Test", email="role@hospital.org"
        )

        user = User(
            username="role.test", profile=profile, roles={UserRole.QA_PERSONNEL}
        )

        # Add role
        user.add_role(UserRole.MTS_PERSONNEL)
        assert UserRole.MTS_PERSONNEL in user.roles
        assert len(user.roles) == 2

        # Remove role
        user.remove_role(UserRole.QA_PERSONNEL)
        assert UserRole.QA_PERSONNEL not in user.roles
        assert UserRole.MTS_PERSONNEL in user.roles
        assert len(user.roles) == 1

    def test_user_account_activation(self):
        """Test account activation"""

        profile = UserProfile(
            first_name="Activate", last_name="Test", email="activate@hospital.org"
        )

        user = User(
            username="activate.test",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            status=UserStatus.PENDING_ACTIVATION,
        )

        user.activate_account()

        assert user.status == UserStatus.ACTIVE

    def test_user_account_suspension(self):
        """Test account suspension"""

        profile = UserProfile(
            first_name="Suspend", last_name="Test", email="suspend@hospital.org"
        )

        user = User(
            username="suspend.test",
            profile=profile,
            roles={UserRole.QA_PERSONNEL},
            status=UserStatus.ACTIVE,
        )

        user.suspend_account("Policy violation")

        assert user.status == UserStatus.SUSPENDED
        assert user.metadata.get("suspension_reason") == "Policy violation"

    def test_user_get_full_name(self):
        """Test getting user's full name"""

        profile = UserProfile(
            first_name="John", last_name="Doe", email="john.doe@hospital.org"
        )

        user = User(username="john.doe", profile=profile, roles={UserRole.QA_PERSONNEL})

        assert user.get_full_name() == "John Doe"

    def test_user_equality(self):
        """Test user equality based on user_id"""

        profile1 = UserProfile(
            first_name="User", last_name="One", email="user1@hospital.org"
        )

        profile2 = UserProfile(
            first_name="User", last_name="Two", email="user2@hospital.org"
        )

        user_id = uuid4()

        user1 = User(
            user_id=user_id,
            username="user1",
            profile=profile1,
            roles={UserRole.QA_PERSONNEL},
        )

        user2 = User(
            user_id=user_id,
            username="user2",  # Different username
            profile=profile2,  # Different profile
            roles={UserRole.MTS_PERSONNEL},  # Different roles
        )

        user3 = User(username="user3", profile=profile1, roles={UserRole.QA_PERSONNEL})

        # Same user_id should be equal
        assert user1 == user2

        # Different user_id should not be equal
        assert user1 != user3
        assert user2 != user3
