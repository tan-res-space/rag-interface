"""
Data Transfer Objects (DTOs)

This module contains request and response DTOs for the User Management Service.
"""

from .requests import (
    AuthenticateUserRequest,
    ChangePasswordRequest,
    ChangeUserRolesRequest,
    ChangeUserStatusRequest,
    CreateUserRequest,
    GetUserAuditLogRequest,
    GetUsersRequest,
    RefreshTokenRequest,
    UpdateUserRequest,
    ValidateTokenRequest,
)
from .responses import (
    AuthenticationResponse,
    ChangePasswordResponse,
    ChangeUserRolesResponse,
    ChangeUserStatusResponse,
    CreateUserResponse,
    PaginatedAuditLogResponse,
    PaginatedUsersResponse,
    TokenRefreshResponse,
    TokenValidationResponse,
    UpdateUserResponse,
    UserAuditLogEntry,
    UserResponse,
    UserSecurityStatusResponse,
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
    "UserSecurityStatusResponse",
]
