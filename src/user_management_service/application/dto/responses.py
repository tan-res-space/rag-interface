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
from ...domain.value_objects.speaker_bucket import SpeakerBucket


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


# =====================================================
# SPEAKER MANAGEMENT RESPONSE DTOS
# =====================================================

class SpeakerResponse(BaseModel):
    """Response DTO for speaker data"""

    speaker_id: str
    speaker_identifier: str
    speaker_name: str
    current_bucket: str
    bucket_description: str
    total_notes_count: int
    processed_notes_count: int
    processing_progress: float
    average_ser_score: Optional[float] = None
    recommended_bucket: str
    should_transition: bool
    quality_trend: str
    priority_score: int
    has_sufficient_data: bool
    last_processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "speaker_id": "550e8400-e29b-41d4-a716-446655440000",
                "speaker_identifier": "SPK001",
                "speaker_name": "Dr. John Smith",
                "current_bucket": "high_touch",
                "bucket_description": "Speakers with low ASR quality requiring significant corrections",
                "total_notes_count": 150,
                "processed_notes_count": 120,
                "processing_progress": 80.0,
                "average_ser_score": 25.5,
                "recommended_bucket": "medium_touch",
                "should_transition": True,
                "quality_trend": "improving",
                "priority_score": 2,
                "has_sufficient_data": True,
                "last_processed_at": "2025-08-19T14:30:00Z",
                "created_at": "2025-08-01T10:00:00Z",
                "updated_at": "2025-08-19T14:30:00Z"
            }
        }


class SpeakerListResponse(BaseModel):
    """Response DTO for speaker list with pagination"""

    speakers: List[SpeakerResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "speakers": [],
                "total_count": 25,
                "page": 1,
                "page_size": 10,
                "total_pages": 3
            }
        }


class HistoricalASRDataResponse(BaseModel):
    """Response DTO for historical ASR data"""

    data_id: str
    speaker_id: str
    instanote_job_id: Optional[str] = None
    note_type: Optional[str] = None
    asr_engine: Optional[str] = None
    asr_word_count: int
    final_word_count: int
    text_length_difference: int
    text_length_ratio: float
    has_significant_changes: bool
    is_test_data: bool
    suitable_for_training: bool
    suitable_for_testing: bool
    processing_date: Optional[datetime] = None
    processing_age_days: Optional[int] = None
    is_recent_data: bool
    created_at: datetime

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "data_id": "550e8400-e29b-41d4-a716-446655440000",
                "speaker_id": "550e8400-e29b-41d4-a716-446655440001",
                "instanote_job_id": "JOB123456",
                "note_type": "consultation",
                "asr_engine": "whisper_v2",
                "asr_word_count": 245,
                "final_word_count": 250,
                "text_length_difference": 5,
                "text_length_ratio": 1.02,
                "has_significant_changes": True,
                "is_test_data": False,
                "suitable_for_training": True,
                "suitable_for_testing": True,
                "processing_date": "2025-08-15T09:30:00Z",
                "processing_age_days": 4,
                "is_recent_data": True,
                "created_at": "2025-08-15T09:30:00Z"
            }
        }


class BucketTransitionRequestResponse(BaseModel):
    """Response DTO for bucket transition request"""

    request_id: str
    speaker_id: str
    from_bucket: str
    to_bucket: str
    transition_type: str
    transition_reason: str
    ser_improvement: Optional[float] = None
    status: str
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None
    approval_notes: Optional[str] = None
    is_urgent: bool
    priority_score: int
    processing_time_hours: Optional[float] = None
    created_at: datetime
    approved_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "speaker_id": "550e8400-e29b-41d4-a716-446655440001",
                "from_bucket": "high_touch",
                "to_bucket": "medium_touch",
                "transition_type": "improvement",
                "transition_reason": "Significant improvement in SER scores after RAG corrections",
                "ser_improvement": 15.5,
                "status": "pending",
                "requested_by": "550e8400-e29b-41d4-a716-446655440002",
                "approved_by": None,
                "approval_notes": None,
                "is_urgent": False,
                "priority_score": 3,
                "processing_time_hours": None,
                "created_at": "2025-08-19T10:00:00Z",
                "approved_at": None
            }
        }


class SpeakerBucketStatsResponse(BaseModel):
    """Response DTO for speaker bucket statistics"""

    bucket_counts: Dict[str, int]
    total_speakers: int
    speakers_needing_transition: int
    average_ser_by_bucket: Dict[str, float]
    quality_distribution: Dict[str, int]

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "bucket_counts": {
                    "no_touch": 15,
                    "low_touch": 25,
                    "medium_touch": 35,
                    "high_touch": 45
                },
                "total_speakers": 120,
                "speakers_needing_transition": 8,
                "average_ser_by_bucket": {
                    "no_touch": 3.2,
                    "low_touch": 8.5,
                    "medium_touch": 22.1,
                    "high_touch": 45.8
                },
                "quality_distribution": {
                    "high": 40,
                    "medium": 50,
                    "low": 30
                }
            }
        }
