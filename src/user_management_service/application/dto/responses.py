"""
Response DTOs for User Management Service

This module contains Pydantic models for response data transfer objects.
These DTOs define the structure of data returned by the service.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field

from ...domain.entities.user import UserRole, UserStatus, Permission


class UserResponse(BaseModel):
    """Response DTO for user data"""
    
    user_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    roles: List[str]
    permissions: List[str]
    status: str
    department: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool
    metadata: Dict[str, str]
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "roles": ["qa_personnel"],
                "permissions": ["submit_error_report", "view_error_reports"],
                "status": "active",
                "department": "Quality Assurance",
                "phone_number": "+1234567890",
                "created_at": "2025-08-19T10:30:00Z",
                "updated_at": "2025-08-19T10:30:00Z",
                "last_login": "2025-08-19T09:15:00Z",
                "is_active": True,
                "metadata": {"employee_id": "EMP001"}
            }
        }


class CreateUserResponse(BaseModel):
    """Response DTO for user creation"""
    
    user_id: str
    username: str
    email: str
    status: str
    message: str
    validation_warnings: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john.doe",
                "email": "john.doe@hospital.org",
                "status": "pending_activation",
                "message": "User created successfully",
                "validation_warnings": []
            }
        }


class AuthenticationResponse(BaseModel):
    """Response DTO for user authentication"""
    
    success: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = Field(default="bearer")
    expires_in: Optional[int] = None  # seconds
    permissions: List[str] = Field(default_factory=list)
    message: str
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "success": True,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john.doe",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "permissions": ["submit_error_report", "view_error_reports"],
                "message": "Authentication successful"
            }
        }


class TokenValidationResponse(BaseModel):
    """Response DTO for token validation"""
    
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    message: str
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "valid": True,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john.doe",
                "permissions": ["submit_error_report", "view_error_reports"],
                "expires_at": "2025-08-19T11:30:00Z",
                "message": "Token is valid"
            }
        }


class TokenRefreshResponse(BaseModel):
    """Response DTO for token refresh"""
    
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = Field(default="bearer")
    expires_in: Optional[int] = None  # seconds
    message: str
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "success": True,
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "message": "Token refreshed successfully"
            }
        }


class UpdateUserResponse(BaseModel):
    """Response DTO for user update"""
    
    user_id: str
    updated_fields: List[str]
    message: str
    validation_warnings: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "updated_fields": ["email", "department"],
                "message": "User updated successfully",
                "validation_warnings": []
            }
        }


class ChangeUserRolesResponse(BaseModel):
    """Response DTO for role changes"""
    
    user_id: str
    previous_roles: List[str]
    new_roles: List[str]
    new_permissions: List[str]
    message: str
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "previous_roles": ["qa_personnel"],
                "new_roles": ["qa_personnel", "mts_personnel"],
                "new_permissions": ["submit_error_report", "view_error_reports", "verify_corrections"],
                "message": "User roles updated successfully"
            }
        }


class ChangeUserStatusResponse(BaseModel):
    """Response DTO for status changes"""
    
    user_id: str
    previous_status: str
    new_status: str
    message: str
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "previous_status": "active",
                "new_status": "suspended",
                "message": "User status updated successfully"
            }
        }


class ChangePasswordResponse(BaseModel):
    """Response DTO for password changes"""
    
    user_id: str
    success: bool
    message: str
    password_strength_score: Optional[float] = None  # 0.0 to 1.0
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "success": True,
                "message": "Password changed successfully",
                "password_strength_score": 0.85
            }
        }


class PaginatedUsersResponse(BaseModel):
    """Response DTO for paginated user lists"""
    
    users: List[UserResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "users": [
                    {
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john.doe",
                        "email": "john.doe@hospital.org",
                        "first_name": "John",
                        "last_name": "Doe",
                        "full_name": "John Doe",
                        "roles": ["qa_personnel"],
                        "permissions": ["submit_error_report"],
                        "status": "active",
                        "department": "Quality Assurance",
                        "created_at": "2025-08-19T10:30:00Z",
                        "updated_at": "2025-08-19T10:30:00Z",
                        "is_active": True,
                        "metadata": {}
                    }
                ],
                "total_count": 1,
                "page": 1,
                "page_size": 20,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        }


class UserAuditLogEntry(BaseModel):
    """Response DTO for audit log entries"""
    
    event_id: str
    event_type: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    timestamp: datetime
    details: Dict[str, str]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "event_id": "evt_123456789",
                "event_type": "user.login_success",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john.doe",
                "timestamp": "2025-08-19T10:30:00Z",
                "details": {"session_id": "sess_abc123"},
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0..."
            }
        }


class PaginatedAuditLogResponse(BaseModel):
    """Response DTO for paginated audit logs"""
    
    entries: List[UserAuditLogEntry]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "entries": [
                    {
                        "event_id": "evt_123456789",
                        "event_type": "user.login_success",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john.doe",
                        "timestamp": "2025-08-19T10:30:00Z",
                        "details": {},
                        "ip_address": "192.168.1.100"
                    }
                ],
                "total_count": 1,
                "page": 1,
                "page_size": 50,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        }


class UserSecurityStatusResponse(BaseModel):
    """Response DTO for user security status"""
    
    user_id: str
    username: str
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    failed_login_attempts: int
    account_locked: bool
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    password_age_days: Optional[int] = None
    security_warnings: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john.doe",
                "risk_level": "low",
                "failed_login_attempts": 0,
                "account_locked": False,
                "locked_until": None,
                "last_login": "2025-08-19T09:15:00Z",
                "password_age_days": 45,
                "security_warnings": []
            }
        }
