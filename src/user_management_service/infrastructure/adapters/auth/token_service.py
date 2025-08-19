"""
Token Service Adapter

This adapter provides JWT token creation, validation, and management.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from ....application.ports.token_service_port import ITokenServicePort
from ...config.settings import settings


logger = logging.getLogger(__name__)


class TokenServiceAdapter(ITokenServicePort):
    """
    Token service adapter implementation.
    
    Provides JWT token operations for authentication and authorization.
    For demo purposes, uses simple token format. In production, use proper JWT library.
    """
    
    def __init__(self):
        """Initialize the token service adapter"""
        self._revoked_tokens: Set[str] = set()
        self._user_sessions: Dict[str, List[Dict]] = {}  # user_id -> list of sessions
        
        logger.info("Initialized token service adapter")
    
    async def create_access_token(
        self, 
        user_id: str, 
        username: str, 
        permissions: List[str],
        expires_in_seconds: Optional[int] = None
    ) -> str:
        """Create an access token for a user"""
        
        if expires_in_seconds is None:
            expires_in_seconds = settings.auth.access_token_expire_minutes * 60
        
        # Create token payload
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=expires_in_seconds)
        
        payload = {
            "user_id": user_id,
            "username": username,
            "permissions": permissions,
            "token_type": "access",
            "issued_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "issuer": "user_management_service"
        }
        
        # For demo purposes, create a simple token
        # In production, use proper JWT library like PyJWT
        token_data = json.dumps(payload)
        token = f"ums_access_{self._encode_token_data(token_data)}"
        
        # Store session info
        session_info = {
            "token": token,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "token_type": "access"
        }
        
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = []
        self._user_sessions[user_id].append(session_info)
        
        logger.debug(f"Created access token for user: {username}")
        return token
    
    async def create_refresh_token(self, user_id: str) -> str:
        """Create a refresh token for a user"""
        
        expires_in_seconds = settings.auth.refresh_token_expire_days * 24 * 60 * 60
        
        # Create token payload
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=expires_in_seconds)
        
        payload = {
            "user_id": user_id,
            "token_type": "refresh",
            "issued_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "issuer": "user_management_service"
        }
        
        # For demo purposes, create a simple token
        token_data = json.dumps(payload)
        token = f"ums_refresh_{self._encode_token_data(token_data)}"
        
        # Store session info
        session_info = {
            "token": token,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "token_type": "refresh"
        }
        
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = []
        self._user_sessions[user_id].append(session_info)
        
        logger.debug(f"Created refresh token for user: {user_id}")
        return token
    
    async def validate_access_token(self, token: str) -> Dict[str, any]:
        """Validate an access token and return claims"""
        
        if token in self._revoked_tokens:
            raise ValueError("Token has been revoked")
        
        if not token.startswith("ums_access_"):
            raise ValueError("Invalid token format")
        
        try:
            # Decode token data
            token_data = self._decode_token_data(token[11:])  # Remove "ums_access_" prefix
            payload = json.loads(token_data)
            
            # Check token type
            if payload.get("token_type") != "access":
                raise ValueError("Invalid token type")
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload["expires_at"])
            if datetime.utcnow() > expires_at:
                raise ValueError("Token has expired")
            
            logger.debug(f"Validated access token for user: {payload.get('username')}")
            return payload
            
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise ValueError(f"Invalid token: {str(e)}")
    
    async def validate_refresh_token(self, token: str) -> Dict[str, any]:
        """Validate a refresh token and return claims"""
        
        if token in self._revoked_tokens:
            raise ValueError("Token has been revoked")
        
        if not token.startswith("ums_refresh_"):
            raise ValueError("Invalid token format")
        
        try:
            # Decode token data
            token_data = self._decode_token_data(token[12:])  # Remove "ums_refresh_" prefix
            payload = json.loads(token_data)
            
            # Check token type
            if payload.get("token_type") != "refresh":
                raise ValueError("Invalid token type")
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload["expires_at"])
            if datetime.utcnow() > expires_at:
                raise ValueError("Token has expired")
            
            logger.debug(f"Validated refresh token for user: {payload.get('user_id')}")
            return payload
            
        except Exception as e:
            logger.warning(f"Refresh token validation failed: {str(e)}")
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    async def refresh_access_token(self, refresh_token: str) -> tuple:
        """Create new access token using refresh token"""
        
        # Validate refresh token
        payload = await self.validate_refresh_token(refresh_token)
        user_id = payload["user_id"]
        
        # For demo purposes, we'll need to get user info from somewhere
        # In a real implementation, you'd fetch user data from the repository
        username = f"user_{user_id}"  # Placeholder
        permissions = ["basic_access"]  # Placeholder
        
        # Create new access token
        new_access_token = await self.create_access_token(user_id, username, permissions)
        
        # Optionally create new refresh token (token rotation)
        new_refresh_token = await self.create_refresh_token(user_id)
        
        # Revoke old refresh token
        await self.revoke_token(refresh_token)
        
        expires_in = settings.auth.access_token_expire_minutes * 60
        
        logger.debug(f"Refreshed tokens for user: {user_id}")
        return new_access_token, new_refresh_token, expires_in
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke a token (add to blacklist)"""
        
        try:
            self._revoked_tokens.add(token)
            
            # Remove from user sessions
            for user_id, sessions in self._user_sessions.items():
                self._user_sessions[user_id] = [
                    session for session in sessions 
                    if session["token"] != token
                ]
            
            logger.debug(f"Revoked token: {token[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke token: {str(e)}")
            return False
    
    async def revoke_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a user"""
        
        revoked_count = 0
        
        if user_id in self._user_sessions:
            sessions = self._user_sessions[user_id]
            
            for session in sessions:
                self._revoked_tokens.add(session["token"])
                revoked_count += 1
            
            # Clear user sessions
            self._user_sessions[user_id] = []
        
        logger.debug(f"Revoked {revoked_count} tokens for user: {user_id}")
        return revoked_count
    
    async def is_token_revoked(self, token: str) -> bool:
        """Check if a token has been revoked"""
        return token in self._revoked_tokens
    
    async def get_token_expiry_seconds(self) -> int:
        """Get default token expiry time in seconds"""
        return settings.auth.access_token_expire_minutes * 60
    
    async def decode_token_claims(self, token: str) -> Dict[str, any]:
        """Decode token claims without validation"""
        
        try:
            if token.startswith("ums_access_"):
                token_data = self._decode_token_data(token[11:])
            elif token.startswith("ums_refresh_"):
                token_data = self._decode_token_data(token[12:])
            else:
                raise ValueError("Invalid token format")
            
            return json.loads(token_data)
            
        except Exception as e:
            logger.warning(f"Failed to decode token claims: {str(e)}")
            raise ValueError(f"Cannot decode token: {str(e)}")
    
    async def get_user_active_sessions(self, user_id: str) -> List[Dict[str, any]]:
        """Get active sessions for a user"""
        
        if user_id not in self._user_sessions:
            return []
        
        # Filter out expired and revoked sessions
        active_sessions = []
        now = datetime.utcnow()
        
        for session in self._user_sessions[user_id]:
            # Check if token is revoked
            if session["token"] in self._revoked_tokens:
                continue
            
            # Check if token is expired
            expires_at = datetime.fromisoformat(session["expires_at"])
            if now > expires_at:
                continue
            
            active_sessions.append({
                "created_at": session["created_at"],
                "expires_at": session["expires_at"],
                "token_type": session["token_type"]
            })
        
        return active_sessions
    
    def _encode_token_data(self, data: str) -> str:
        """Encode token data (simple base64 for demo)"""
        import base64
        return base64.b64encode(data.encode()).decode()
    
    def _decode_token_data(self, encoded_data: str) -> str:
        """Decode token data (simple base64 for demo)"""
        import base64
        return base64.b64decode(encoded_data.encode()).decode()
    
    # Health check methods
    async def health_check(self) -> dict:
        """Perform health check"""
        return {
            "status": "healthy",
            "service_type": "token_service",
            "revoked_tokens_count": len(self._revoked_tokens),
            "active_users_count": len(self._user_sessions)
        }
    
    async def get_service_info(self) -> dict:
        """Get service information"""
        return {
            "service_type": "token_service",
            "algorithm": "demo_simple",
            "access_token_expire_minutes": settings.auth.access_token_expire_minutes,
            "refresh_token_expire_days": settings.auth.refresh_token_expire_days,
            "revoked_tokens_count": len(self._revoked_tokens),
            "active_sessions_count": sum(len(sessions) for sessions in self._user_sessions.values())
        }
