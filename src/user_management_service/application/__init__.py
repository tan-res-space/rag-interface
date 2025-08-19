"""
Application Layer

This layer contains use cases, DTOs, and port interfaces for the User Management Service.
It orchestrates business workflows and defines contracts with the infrastructure layer.
"""

from .dto import (
    CreateUserRequest,
    AuthenticateUserRequest,
    UserResponse,
    AuthenticationResponse
)

from .ports import (
    IAuthenticationPort,
    IAuthorizationPort,
    IUserManagementPort,
    IUserRepositoryPort
)

from .use_cases import (
    AuthenticateUserUseCase
)

__all__ = [
    # DTOs
    "CreateUserRequest",
    "AuthenticateUserRequest", 
    "UserResponse",
    "AuthenticationResponse",
    
    # Ports
    "IAuthenticationPort",
    "IAuthorizationPort",
    "IUserManagementPort",
    "IUserRepositoryPort",
    
    # Use Cases
    "AuthenticateUserUseCase"
]
