"""
JWT Authentication System

JWT-based authentication and authorization for the RAG Interface system.
Provides secure token generation, validation, and role-based access control.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security scheme
security = HTTPBearer()


class JWTAuth:
    """
    JWT Authentication handler.
    
    Provides methods for token generation, validation, and user authentication.
    """

    def __init__(
        self,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = REFRESH_TOKEN_EXPIRE_DAYS
    ):
        """
        Initialize JWT authentication.
        
        Args:
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm
            access_token_expire_minutes: Access token expiration time
            refresh_token_expire_days: Refresh token expiration time
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            JWT refresh token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """
        Get current user from JWT token.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            User information from token
        """
        token = credentials.credentials
        payload = self.verify_token(token)
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", [])
        }

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)


class RoleBasedAuth:
    """
    Role-based access control (RBAC) system.
    
    Provides role and permission checking for API endpoints.
    """

    def __init__(self, jwt_auth: JWTAuth):
        """
        Initialize RBAC system.
        
        Args:
            jwt_auth: JWT authentication instance
        """
        self.jwt_auth = jwt_auth

    def require_roles(self, required_roles: List[str]):
        """
        Decorator to require specific roles.
        
        Args:
            required_roles: List of required roles
            
        Returns:
            Dependency function for FastAPI
        """
        def role_checker(current_user: Dict[str, Any] = Depends(self.jwt_auth.get_current_user)):
            user_roles = current_user.get("roles", [])
            
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {required_roles}"
                )
            
            return current_user
        
        return role_checker

    def require_permissions(self, required_permissions: List[str]):
        """
        Decorator to require specific permissions.
        
        Args:
            required_permissions: List of required permissions
            
        Returns:
            Dependency function for FastAPI
        """
        def permission_checker(current_user: Dict[str, Any] = Depends(self.jwt_auth.get_current_user)):
            user_permissions = current_user.get("permissions", [])
            
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permissions}"
                )
            
            return current_user
        
        return permission_checker

    def require_admin(self):
        """Require admin role."""
        return self.require_roles(["admin"])

    def require_user(self):
        """Require user role (any authenticated user)."""
        return self.require_roles(["user", "admin", "moderator"])


# Global instances
jwt_auth = JWTAuth()
rbac = RoleBasedAuth(jwt_auth)


# Convenience dependency functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user."""
    return jwt_auth.get_current_user(credentials)


def require_admin(current_user: Dict[str, Any] = Depends(rbac.require_admin())):
    """Require admin role."""
    return current_user


def require_user(current_user: Dict[str, Any] = Depends(rbac.require_user())):
    """Require user role."""
    return current_user


def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    """Optional authentication - returns user if authenticated, None otherwise."""
    if credentials is None:
        return None
    
    try:
        return jwt_auth.get_current_user(credentials)
    except HTTPException:
        return None


class APIKeyAuth:
    """
    API Key authentication for service-to-service communication.
    
    Provides API key validation for internal service calls.
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize API key authentication.
        
        Args:
            api_keys: Dictionary of service_name -> api_key
        """
        self.api_keys = api_keys or {
            "error_reporting": os.getenv("ERROR_REPORTING_API_KEY", "default-key"),
            "rag_integration": os.getenv("RAG_INTEGRATION_API_KEY", "default-key"),
            "dashboard": os.getenv("DASHBOARD_API_KEY", "default-key")
        }

    def verify_api_key(self, api_key: str) -> Optional[str]:
        """
        Verify API key and return service name.
        
        Args:
            api_key: API key to verify
            
        Returns:
            Service name if valid, None otherwise
        """
        for service_name, valid_key in self.api_keys.items():
            if api_key == valid_key:
                return service_name
        return None

    def require_api_key(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """
        Require valid API key.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Service name
            
        Raises:
            HTTPException: If API key is invalid
        """
        api_key = credentials.credentials
        service_name = self.verify_api_key(api_key)
        
        if service_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return service_name


# Global API key auth instance
api_key_auth = APIKeyAuth()


def require_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Require valid API key for service-to-service communication."""
    return api_key_auth.require_api_key(credentials)
