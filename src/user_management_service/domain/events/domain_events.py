"""
Domain Events for User Management Service

This module contains domain events that represent significant business events
in the user management domain. These events are used for communication
between bounded contexts and for maintaining audit trails.
"""

from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..entities.user import UserRole, UserStatus


class BaseDomainEvent(BaseModel):
    """Base class for all domain events"""

    event_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0")
    source: str = Field(default="user_management_service")
    correlation_id: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration"""

        use_enum_values = True


class UserCreatedEvent(BaseDomainEvent):
    """
    Event published when a new user is created.

    This event is used to notify other services about new user registration
    and trigger welcome workflows.
    """

    event_type: Literal["user.created"] = "user.created"

    # User data
    user_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    roles: List[str]
    status: str
    department: Optional[str] = None
    created_by: str

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456789",
                "event_type": "user.created",
                "timestamp": "2025-08-19T10:30:00Z",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "first_name": "John",
                "last_name": "Doe",
                "roles": ["qa_personnel"],
                "status": "pending_activation",
                "department": "Quality Assurance",
                "created_by": "admin_user",
            }
        }


class UserActivatedEvent(BaseDomainEvent):
    """
    Event published when a user account is activated.

    This event triggers access provisioning and notification workflows.
    """

    event_type: Literal["user.activated"] = "user.activated"

    user_id: str
    username: str
    email: str
    activated_by: str
    previous_status: str

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456790",
                "event_type": "user.activated",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "activated_by": "admin_user",
                "previous_status": "pending_activation",
            }
        }


class UserSuspendedEvent(BaseDomainEvent):
    """
    Event published when a user account is suspended.

    This event triggers access revocation and audit workflows.
    """

    event_type: Literal["user.suspended"] = "user.suspended"

    user_id: str
    username: str
    email: str
    suspended_by: str
    reason: Optional[str] = None
    previous_status: str

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456791",
                "event_type": "user.suspended",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "suspended_by": "admin_user",
                "reason": "Policy violation",
                "previous_status": "active",
            }
        }


class UserRoleChangedEvent(BaseDomainEvent):
    """
    Event published when user roles are modified.

    This event triggers permission updates and access control changes.
    """

    event_type: Literal["user.role_changed"] = "user.role_changed"

    user_id: str
    username: str
    previous_roles: List[str]
    new_roles: List[str]
    changed_by: str

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456792",
                "event_type": "user.role_changed",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "previous_roles": ["qa_personnel"],
                "new_roles": ["qa_personnel", "mts_personnel"],
                "changed_by": "admin_user",
            }
        }


class UserLoginSuccessEvent(BaseDomainEvent):
    """
    Event published when a user successfully logs in.

    This event is used for audit trails and security monitoring.
    """

    event_type: Literal["user.login_success"] = "user.login_success"

    user_id: str
    username: str
    login_timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456793",
                "event_type": "user.login_success",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "login_timestamp": "2025-08-19T10:30:00Z",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "session_id": "sess_abc123",
            }
        }


class UserLoginFailureEvent(BaseDomainEvent):
    """
    Event published when a user login attempt fails.

    This event is used for security monitoring and threat detection.
    """

    event_type: Literal["user.login_failure"] = "user.login_failure"

    username: str
    failure_reason: str
    attempt_timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    failed_attempts_count: int

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456794",
                "event_type": "user.login_failure",
                "username": "john.doe",
                "failure_reason": "invalid_password",
                "attempt_timestamp": "2025-08-19T10:30:00Z",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "failed_attempts_count": 3,
            }
        }


class UserAccountLockedEvent(BaseDomainEvent):
    """
    Event published when a user account is locked due to security policy.

    This event triggers security alerts and notification workflows.
    """

    event_type: Literal["user.account_locked"] = "user.account_locked"

    user_id: str
    username: str
    email: str
    locked_until: datetime
    reason: str
    failed_attempts: int
    ip_address: Optional[str] = None

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456795",
                "event_type": "user.account_locked",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "locked_until": "2025-08-19T11:00:00Z",
                "reason": "too_many_failed_attempts",
                "failed_attempts": 5,
                "ip_address": "192.168.1.100",
            }
        }


class UserPasswordChangedEvent(BaseDomainEvent):
    """
    Event published when a user password is changed.

    This event is used for audit trails and security notifications.
    """

    event_type: Literal["user.password_changed"] = "user.password_changed"

    user_id: str
    username: str
    changed_by: str  # Could be the user themselves or an admin
    change_reason: str  # 'user_request', 'admin_reset', 'policy_expiry'
    ip_address: Optional[str] = None

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456796",
                "event_type": "user.password_changed",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "changed_by": "usr_987654321",
                "change_reason": "user_request",
                "ip_address": "192.168.1.100",
            }
        }


class UserProfileUpdatedEvent(BaseDomainEvent):
    """
    Event published when user profile information is updated.

    This event is used for audit trails and data synchronization.
    """

    event_type: Literal["user.profile_updated"] = "user.profile_updated"

    user_id: str
    username: str
    updated_fields: List[str]
    updated_by: str

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456797",
                "event_type": "user.profile_updated",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "updated_fields": ["department", "phone_number"],
                "updated_by": "usr_987654321",
            }
        }


class UserDeletedEvent(BaseDomainEvent):
    """
    Event published when a user account is deleted.

    This event triggers data cleanup and audit workflows.
    """

    event_type: Literal["user.deleted"] = "user.deleted"

    user_id: str
    username: str
    email: str
    deleted_by: str
    deletion_reason: Optional[str] = None

    class Config:
        """Pydantic configuration"""

        schema_extra = {
            "example": {
                "event_id": "evt_123456798",
                "event_type": "user.deleted",
                "user_id": "usr_987654321",
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "deleted_by": "admin_user",
                "deletion_reason": "Account closure request",
            }
        }
