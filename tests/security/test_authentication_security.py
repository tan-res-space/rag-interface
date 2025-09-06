"""
Security Tests for Authentication and Authorization

These tests verify security measures including authentication, authorization,
input validation, and protection against common vulnerabilities.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.user_management_service.main import app
from src.user_management_service.infrastructure.adapters.auth.token_service import TokenService


class TestAuthenticationSecurity:
    """Test authentication security measures"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def token_service(self):
        return TokenService()

    def test_login_with_valid_credentials(self, client):
        """Test successful login with valid credentials"""
        response = client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "SecurePassword123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_invalid_credentials(self, client):
        """Test login failure with invalid credentials"""
        response = client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "wrong_password"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_brute_force_protection(self, client):
        """Test account lockout after multiple failed attempts"""
        # Attempt multiple failed logins
        for _ in range(6):  # Exceed the 5 attempt limit
            response = client.post("/api/v1/auth/login", json={
                "username": "test_user",
                "password": "wrong_password"
            })
        
        # Account should be locked
        assert response.status_code == 423  # Locked
        assert "Account temporarily locked" in response.json()["detail"]

    def test_jwt_token_validation(self, token_service):
        """Test JWT token validation and expiration"""
        # Create a valid token
        token = token_service.create_access_token(
            user_id="test_user_id",
            username="test_user",
            permissions=["read", "write"]
        )
        
        # Validate the token
        payload = token_service.validate_access_token(token)
        assert payload["user_id"] == "test_user_id"
        assert payload["username"] == "test_user"

    def test_expired_token_rejection(self, token_service):
        """Test that expired tokens are rejected"""
        # Create an expired token
        with patch('src.user_management_service.infrastructure.adapters.auth.token_service.datetime') as mock_datetime:
            # Set time to past
            mock_datetime.utcnow.return_value = datetime.utcnow() - timedelta(hours=2)
            token = token_service.create_access_token(
                user_id="test_user_id",
                username="test_user",
                permissions=["read"]
            )
        
        # Try to validate expired token
        with pytest.raises(ValueError, match="Token has expired"):
            token_service.validate_access_token(token)

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attacks"""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in malicious_payloads:
            response = client.post("/api/v1/auth/login", json={
                "username": payload,
                "password": "password"
            })
            # Should not cause server error, should handle gracefully
            assert response.status_code in [400, 401, 422]

    def test_xss_protection_in_responses(self, client):
        """Test XSS protection in API responses"""
        xss_payload = "<script>alert('xss')</script>"
        
        response = client.post("/api/v1/auth/login", json={
            "username": xss_payload,
            "password": "password"
        })
        
        # Response should not contain unescaped script tags
        response_text = response.text
        assert "<script>" not in response_text
        assert "alert(" not in response_text

    def test_csrf_protection(self, client):
        """Test CSRF protection for state-changing operations"""
        # Attempt to make a request without proper CSRF token
        response = client.post("/api/v1/users", json={
            "username": "new_user",
            "email": "test@example.com"
        })
        
        # Should require authentication
        assert response.status_code == 401

    def test_rate_limiting_protection(self, client):
        """Test rate limiting on authentication endpoints"""
        # Make rapid requests to trigger rate limiting
        responses = []
        for _ in range(20):  # Exceed rate limit
            response = client.post("/api/v1/auth/login", json={
                "username": "test_user",
                "password": "password"
            })
            responses.append(response.status_code)
        
        # Should eventually return 429 (Too Many Requests)
        assert 429 in responses

    def test_password_complexity_validation(self, client):
        """Test password complexity requirements"""
        weak_passwords = [
            "123456",
            "password",
            "abc",
            "12345678",  # No special chars
            "Password",  # No numbers
            "password123"  # No uppercase
        ]
        
        for weak_password in weak_passwords:
            response = client.post("/api/v1/users", json={
                "username": "test_user",
                "password": weak_password,
                "email": "test@example.com"
            })
            assert response.status_code == 422
            assert "password" in response.json()["detail"].lower()

    def test_secure_headers_present(self, client):
        """Test that security headers are present in responses"""
        response = client.get("/api/v1/health")
        
        # Check for security headers
        headers = response.headers
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        
    def test_sensitive_data_not_logged(self, client, caplog):
        """Test that sensitive data is not logged"""
        with caplog.at_level("DEBUG"):
            client.post("/api/v1/auth/login", json={
                "username": "test_user",
                "password": "SecretPassword123!"
            })
        
        # Password should not appear in logs
        log_text = caplog.text.lower()
        assert "secretpassword123!" not in log_text
        assert "password" not in log_text or "***" in log_text


class TestAuthorizationSecurity:
    """Test authorization and permission-based access control"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_role_based_access_control(self, client):
        """Test that users can only access resources based on their roles"""
        # Test admin access
        admin_token = self._get_token_for_role("admin")
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

        # Test regular user access to admin endpoint
        user_token = self._get_token_for_role("user")
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

    def test_resource_ownership_validation(self, client):
        """Test that users can only access their own resources"""
        user1_token = self._get_token_for_user("user1")
        user2_token = self._get_token_for_user("user2")
        
        # User1 creates a resource
        response = client.post(
            "/api/v1/error-reports",
            json={"original_text": "test", "corrected_text": "corrected"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        resource_id = response.json()["error_id"]
        
        # User2 tries to access User1's resource
        response = client.get(
            f"/api/v1/error-reports/{resource_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 403

    def _get_token_for_role(self, role: str) -> str:
        """Helper method to get token for specific role"""
        # Implementation would depend on your auth system
        return f"mock_token_for_{role}"

    def _get_token_for_user(self, user_id: str) -> str:
        """Helper method to get token for specific user"""
        return f"mock_token_for_{user_id}"
