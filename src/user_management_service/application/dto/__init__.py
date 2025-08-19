"""
Data Transfer Objects (DTOs)

This module contains request and response DTOs for the User Management Service.
"""

from .requests import (
    CreateUserRequest,
    AuthenticateUserRequest,
    UpdateUserRequest,
    ChangeUserRolesRequest,
    ChangeUserStatusRequest,
    ChangePasswordRequest,
    ValidateTokenRequest,
    RefreshTokenRequest,
    GetUsersRequest,
    GetUserAuditLogRequest
)

from .responses import (
    UserResponse,
    CreateUserResponse,
    AuthenticationResponse,
    TokenValidationResponse,
    TokenRefreshResponse,
    UpdateUserResponse,
    ChangeUserRolesResponse,
    ChangeUserStatusResponse,
    ChangePasswordResponse,
    PaginatedUsersResponse,
    UserAuditLogEntry,
    PaginatedAuditLogResponse,
    UserSecurityStatusResponse
)

__all__ = [
    # Requests
    "CreateUserRequest",
    "AuthenticateUserRequest",
    "UpdateUserRequest",
    "ChangeUserRolesRequest",
    "ChangeUserStatusRequest",
    "ChangePasswordRequest",
    "ValidateTokenRequest",
    "RefreshTokenRequest",
    "GetUsersRequest",
    "GetUserAuditLogRequest",
    
    # Responses
    "UserResponse",
    "CreateUserResponse",
    "AuthenticationResponse",
    "TokenValidationResponse",
    "TokenRefreshResponse",
    "UpdateUserResponse",
    "ChangeUserRolesResponse",
    "ChangeUserStatusResponse",
    "ChangePasswordResponse",
    "PaginatedUsersResponse",
    "UserAuditLogEntry",
    "PaginatedAuditLogResponse",
    "UserSecurityStatusResponse"
]
