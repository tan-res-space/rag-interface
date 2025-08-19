"""
Unit tests for User domain entity.

Following TDD principles for authentication and authorization components.
Tests focus on user creation, validation, and business logic.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from src.user_management_service.domain.entities.user import User
from src.user_management_service.domain.value_objects.user_role import UserRole
from src.user_management_service.domain.value_objects.user_status import UserStatus


class TestUserCreation:
    """Test user entity creation and validation."""
    
    def test_create_valid_user(self):
        """Test creating a valid user."""
        # Arrange
        user_id = uuid4()
        username = "testuser"
        email = "test@example.com"
        roles = [UserRole.QA_PERSONNEL]
        
        # Act
        user = User(
            id=user_id,
            username=username,
            email=email,
            roles=roles,
            status=UserStatus.ACTIVE
        )
        
        # Assert
        assert user.id == user_id
        assert user.username == username
        assert user.email == email
        assert user.roles == roles
        assert user.status == UserStatus.ACTIVE
        assert isinstance(user.created_at, datetime)
    
    def test_create_user_with_empty_username_raises_error(self):
        """Test that empty username raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="username cannot be empty"):
            User(
                id=uuid4(),
                username="",
                email="test@example.com",
                roles=[UserRole.QA_PERSONNEL],
                status=UserStatus.ACTIVE
            )
    
    def test_create_user_with_invalid_email_raises_error(self):
        """Test that invalid email raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                id=uuid4(),
                username="testuser",
                email="invalid-email",
                roles=[UserRole.QA_PERSONNEL],
                status=UserStatus.ACTIVE
            )
    
    def test_user_is_active(self):
        """Test checking if user is active."""
        # Arrange
        active_user = User(
            id=uuid4(),
            username="activeuser",
            email="active@example.com",
            roles=[UserRole.QA_PERSONNEL],
            status=UserStatus.ACTIVE
        )
        
        inactive_user = User(
            id=uuid4(),
            username="inactiveuser",
            email="inactive@example.com",
            roles=[UserRole.QA_PERSONNEL],
            status=UserStatus.INACTIVE
        )
        
        # Act & Assert
        assert active_user.is_active()
        assert not inactive_user.is_active()
    
    def test_user_has_role(self):
        """Test checking if user has specific role."""
        # Arrange
        user = User(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            roles=[UserRole.QA_PERSONNEL, UserRole.VIEWER],
            status=UserStatus.ACTIVE
        )
        
        # Act & Assert
        assert user.has_role(UserRole.QA_PERSONNEL)
        assert user.has_role(UserRole.VIEWER)
        assert not user.has_role(UserRole.ADMIN)
    
    def test_user_can_perform_action(self):
        """Test checking if user can perform specific actions."""
        # Arrange
        qa_user = User(
            id=uuid4(),
            username="qauser",
            email="qa@example.com",
            roles=[UserRole.QA_PERSONNEL],
            status=UserStatus.ACTIVE
        )
        
        admin_user = User(
            id=uuid4(),
            username="adminuser",
            email="admin@example.com",
            roles=[UserRole.ADMIN],
            status=UserStatus.ACTIVE
        )
        
        # Act & Assert
        assert qa_user.can_submit_error_reports()
        assert not qa_user.can_delete_error_reports()
        assert admin_user.can_delete_error_reports()
        assert admin_user.can_manage_users()


class TestUserMethods:
    """Test user methods and business logic."""
    
    def test_get_user_summary(self):
        """Test getting user summary."""
        # Arrange
        user = User(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            roles=[UserRole.QA_PERSONNEL, UserRole.VIEWER],
            status=UserStatus.ACTIVE
        )
        
        # Act
        summary = user.get_user_summary()
        
        # Assert
        assert "id" in summary
        assert summary["username"] == "testuser"
        assert summary["email"] == "test@example.com"
        assert summary["status"] == "active"
        assert summary["is_active"] is True
        assert len(summary["roles"]) == 2
