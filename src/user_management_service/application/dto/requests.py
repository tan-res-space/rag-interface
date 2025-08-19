"""
Request DTOs for User Management Service

This module contains Pydantic models for request data transfer objects.
These DTOs define the structure and validation rules for incoming requests.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ...domain.entities.user import UserRole, UserStatus


class CreateUserRequest(BaseModel):
    """Request DTO for creating a new user"""
    
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9._-]+$')
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=12, max_length=128)
    roles: Set[UserRole] = Field(..., min_items=1)
    department: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    created_by: UUID
    metadata: Dict[str, str] = Field(default_factory=dict)
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email domain for healthcare organization"""
        allowed_domains = ['hospital.org', 'clinic.com', 'healthcare.gov']
        domain = v.split('@')[1].lower()
        if domain not in allowed_domains:
            raise ValueError(f'Email domain {domain} not allowed')
        return v.lower()
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        schema_extra = {
            "example": {
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePassword123!",
                "roles": ["qa_personnel"],
                "department": "Quality Assurance",
                "phone_number": "+1234567890",
                "created_by": "550e8400-e29b-41d4-a716-446655440000",
                "metadata": {"employee_id": "EMP001"}
            }
        }


class AuthenticateUserRequest(BaseModel):
    """Request DTO for user authentication"""
    
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "username": "john.doe",
                "password": "SecurePassword123!",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0..."
            }
        }


class UpdateUserRequest(BaseModel):
    """Request DTO for updating user information"""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    department: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    updated_by: UUID
    metadata: Optional[Dict[str, str]] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email domain for healthcare organization"""
        if v is None:
            return v
        allowed_domains = ['hospital.org', 'clinic.com', 'healthcare.gov']
        domain = v.split('@')[1].lower()
        if domain not in allowed_domains:
            raise ValueError(f'Email domain {domain} not allowed')
        return v.lower()
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john.smith@hospital.org",
                "department": "Quality Assurance",
                "phone_number": "+1234567890",
                "updated_by": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ChangeUserRolesRequest(BaseModel):
    """Request DTO for changing user roles"""
    
    user_id: UUID
    new_roles: Set[UserRole] = Field(..., min_items=1)
    changed_by: UUID
    reason: Optional[str] = Field(None, max_length=500)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "new_roles": ["qa_personnel", "mts_personnel"],
                "changed_by": "550e8400-e29b-41d4-a716-446655440001",
                "reason": "Promotion to senior role"
            }
        }


class ChangeUserStatusRequest(BaseModel):
    """Request DTO for changing user status"""
    
    user_id: UUID
    new_status: UserStatus
    changed_by: UUID
    reason: Optional[str] = Field(None, max_length=500)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "new_status": "suspended",
                "changed_by": "550e8400-e29b-41d4-a716-446655440001",
                "reason": "Policy violation"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request DTO for changing user password"""
    
    user_id: UUID
    current_password: Optional[str] = Field(None, min_length=1)  # None for admin reset
    new_password: str = Field(..., min_length=12, max_length=128)
    changed_by: UUID
    change_reason: str = Field(..., pattern=r'^(user_request|admin_reset|policy_expiry)$')
    ip_address: Optional[str] = None
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword123!",
                "changed_by": "550e8400-e29b-41d4-a716-446655440000",
                "change_reason": "user_request",
                "ip_address": "192.168.1.100"
            }
        }


class ValidateTokenRequest(BaseModel):
    """Request DTO for token validation"""
    
    token: str = Field(..., min_length=1)
    required_permissions: Optional[List[str]] = None
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "required_permissions": ["submit_error_report", "view_error_reports"]
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request DTO for token refresh"""
    
    refresh_token: str = Field(..., min_length=1)
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class GetUsersRequest(BaseModel):
    """Request DTO for getting users with filters"""
    
    roles: Optional[Set[UserRole]] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    search_term: Optional[str] = Field(None, max_length=100)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern=r'^(username|email|created_at|last_login)$')
    sort_order: str = Field(default="desc", pattern=r'^(asc|desc)$')
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        schema_extra = {
            "example": {
                "roles": ["qa_personnel"],
                "status": "active",
                "department": "Quality Assurance",
                "search_term": "john",
                "page": 1,
                "page_size": 20,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class GetUserAuditLogRequest(BaseModel):
    """Request DTO for getting user audit logs"""
    
    user_id: Optional[UUID] = None
    event_types: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_types": ["user.login_success", "user.login_failure"],
                "start_date": "2025-08-01T00:00:00Z",
                "end_date": "2025-08-19T23:59:59Z",
                "page": 1,
                "page_size": 50
            }
        }
