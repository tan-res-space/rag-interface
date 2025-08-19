"""
User Domain Entity

This module contains the User entity and related value objects for the User Management Service.
Implements business rules and domain logic for user management.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class UserRole(str, Enum):
    """User roles in the system"""
    QA_PERSONNEL = "qa_personnel"
    MTS_PERSONNEL = "mts_personnel"
    SYSTEM_ADMIN = "system_admin"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_ACTIVATION = "pending_activation"


class Permission(str, Enum):
    """System permissions"""
    # Error reporting permissions
    SUBMIT_ERROR_REPORT = "submit_error_report"
    VIEW_ERROR_REPORTS = "view_error_reports"
    EDIT_ERROR_REPORTS = "edit_error_reports"
    DELETE_ERROR_REPORTS = "delete_error_reports"
    
    # Verification permissions
    VERIFY_CORRECTIONS = "verify_corrections"
    VIEW_VERIFICATION_DASHBOARD = "view_verification_dashboard"
    EXPORT_VERIFICATION_DATA = "export_verification_data"
    
    # User management permissions
    MANAGE_USERS = "manage_users"
    ASSIGN_ROLES = "assign_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    # System administration
    SYSTEM_CONFIGURATION = "system_configuration"
    VIEW_SYSTEM_METRICS = "view_system_metrics"


class UserProfile(BaseModel):
    """User profile information"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    department: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email domain for healthcare organization"""
        # Business rule: Only allow specific healthcare domains
        allowed_domains = ['hospital.org', 'clinic.com', 'healthcare.gov']
        domain = v.split('@')[1].lower()
        if domain not in allowed_domains:
            raise ValueError(f'Email domain {domain} not allowed')
        return v.lower()


class User(BaseModel):
    """
    User domain entity representing a system user.
    
    Contains business rules for user management, role assignment,
    and permission validation.
    """
    
    user_id: UUID = Field(default_factory=uuid4)
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9._-]+$')
    profile: UserProfile
    roles: Set[UserRole] = Field(default_factory=set)
    status: UserStatus = Field(default=UserStatus.PENDING_ACTIVATION)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0, ge=0)
    account_locked_until: Optional[datetime] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True
        
    def __eq__(self, other) -> bool:
        """Equality based on user_id"""
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id
    
    def __hash__(self) -> int:
        """Hash based on user_id"""
        return hash(self.user_id)
    
    def get_permissions(self) -> Set[Permission]:
        """
        Get all permissions for this user based on their roles.
        
        Business rules for role-based permissions:
        - QA_PERSONNEL: Can submit and view error reports
        - MTS_PERSONNEL: Can verify corrections and view dashboard
        - SYSTEM_ADMIN: Has all permissions
        - VIEWER: Can only view data
        
        Returns:
            Set of permissions for this user
        """
        permissions = set()
        
        for role in self.roles:
            if role == UserRole.QA_PERSONNEL:
                permissions.update([
                    Permission.SUBMIT_ERROR_REPORT,
                    Permission.VIEW_ERROR_REPORTS,
                    Permission.EDIT_ERROR_REPORTS
                ])
            elif role == UserRole.MTS_PERSONNEL:
                permissions.update([
                    Permission.VERIFY_CORRECTIONS,
                    Permission.VIEW_VERIFICATION_DASHBOARD,
                    Permission.EXPORT_VERIFICATION_DATA,
                    Permission.VIEW_ERROR_REPORTS
                ])
            elif role == UserRole.SYSTEM_ADMIN:
                permissions.update(list(Permission))
            elif role == UserRole.VIEWER:
                permissions.update([
                    Permission.VIEW_ERROR_REPORTS,
                    Permission.VIEW_VERIFICATION_DASHBOARD
                ])
        
        return permissions
    
    def has_permission(self, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if user has the permission, False otherwise
        """
        return permission in self.get_permissions()
    
    def is_active(self) -> bool:
        """
        Check if user account is active.
        
        Business rules:
        - Status must be ACTIVE
        - Account must not be locked
        - User must have at least one role
        
        Returns:
            True if user is active, False otherwise
        """
        if self.status != UserStatus.ACTIVE:
            return False
        
        if self.account_locked_until and self.account_locked_until > datetime.utcnow():
            return False
        
        if not self.roles:
            return False
        
        return True
    
    def add_role(self, role: UserRole) -> None:
        """
        Add a role to the user.
        
        Business rule: Users can have multiple roles
        
        Args:
            role: Role to add
        """
        self.roles.add(role)
        self.updated_at = datetime.utcnow()
    
    def remove_role(self, role: UserRole) -> None:
        """
        Remove a role from the user.
        
        Business rule: Users must have at least one role to be active
        
        Args:
            role: Role to remove
        """
        self.roles.discard(role)
        self.updated_at = datetime.utcnow()
    
    def record_login_success(self) -> None:
        """
        Record successful login.
        
        Business rule: Reset failed attempts on successful login
        """
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.updated_at = datetime.utcnow()
    
    def record_login_failure(self) -> None:
        """
        Record failed login attempt.
        
        Business rule: Lock account after 5 failed attempts for 30 minutes
        """
        self.failed_login_attempts += 1
        self.updated_at = datetime.utcnow()
        
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def activate_account(self) -> None:
        """
        Activate user account.
        
        Business rule: Can only activate pending accounts
        """
        if self.status == UserStatus.PENDING_ACTIVATION:
            self.status = UserStatus.ACTIVE
            self.updated_at = datetime.utcnow()
    
    def suspend_account(self, reason: str = "") -> None:
        """
        Suspend user account.
        
        Args:
            reason: Reason for suspension
        """
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
        if reason:
            self.metadata["suspension_reason"] = reason
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        return f"{self.profile.first_name} {self.profile.last_name}"
    
    def update_profile(self, profile_updates: Dict[str, str]) -> None:
        """
        Update user profile information.
        
        Args:
            profile_updates: Dictionary of profile fields to update
        """
        for field, value in profile_updates.items():
            if hasattr(self.profile, field):
                setattr(self.profile, field, value)
        
        self.updated_at = datetime.utcnow()
