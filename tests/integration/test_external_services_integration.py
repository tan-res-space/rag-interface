"""
Integration tests for external service integrations.

These tests verify the integration between the Error Reporting Service
and external services like User Management Service, including authentication,
authorization, and service communication.
Following TDD principles and Hexagonal Architecture patterns.
"""

from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import aioresponses
import httpx
import pytest

from src.error_reporting_service.domain.entities.error_report import (
    SeverityLevel,
)
# from src.error_reporting_service.infrastructure.adapters.external.auth_client import (
#     UserManagementServiceClient,
# )
from src.error_reporting_service.infrastructure.adapters.external.notification_client import (
    NotificationServiceClient,
)
from tests.factories import ErrorReportFactory


@pytest.mark.integration
@pytest.mark.external_services
class TestUserManagementServiceIntegration:
    """Integration tests for User Management Service"""

    @pytest.fixture
    def ums_client(self):
        """Create User Management Service client"""
        return UserManagementServiceClient(
            base_url="http://localhost:8001", api_key="test-api-key", timeout=30.0
        )

    @pytest.mark.asyncio
    async def test_validate_jwt_token_success(self, ums_client):
        """Test successful JWT token validation"""
        # Arrange
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"
        expected_user_data = {
            "user_id": str(uuid4()),
            "username": "test_user",
            "email": "test@example.com",
            "roles": ["qa_personnel"],
            "organization_id": str(uuid4()),
            "permissions": ["error_report:create", "error_report:read"],
        }

        with aioresponses.aioresponses() as m:
            m.post(
                "http://localhost:8001/api/v1/auth/validate-token",
                payload={"valid": True, "user": expected_user_data},
                status=200,
            )

            # Act
            result = await ums_client.validate_token(token)

            # Assert
            assert result["valid"] is True
            assert result["user"]["user_id"] == expected_user_data["user_id"]
            assert result["user"]["username"] == expected_user_data["username"]
            assert "qa_personnel" in result["user"]["roles"]

    @pytest.mark.asyncio
    async def test_validate_jwt_token_invalid(self, ums_client):
        """Test JWT token validation with invalid token"""
        # Arrange
        invalid_token = "invalid.jwt.token"

        with aioresponses.aioresponses() as m:
            m.post(
                "http://localhost:8001/api/v1/auth/validate-token",
                payload={"valid": False, "error": "Invalid token"},
                status=401,
            )

            # Act & Assert
            with pytest.raises(httpx.HTTPStatusError):
                await ums_client.validate_token(invalid_token)

    @pytest.mark.asyncio
    async def test_get_user_permissions_success(self, ums_client):
        """Test successful retrieval of user permissions"""
        # Arrange
        user_id = str(uuid4())
        expected_permissions = [
            "error_report:create",
            "error_report:read",
            "error_report:update",
            "error_search:execute",
        ]

        with aioresponses.aioresponses() as m:
            m.get(
                f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                payload={"permissions": expected_permissions},
                status=200,
            )

            # Act
            permissions = await ums_client.get_user_permissions(user_id)

            # Assert
            assert len(permissions) == 4
            assert "error_report:create" in permissions
            assert "error_search:execute" in permissions

    @pytest.mark.asyncio
    async def test_check_user_authorization_success(self, ums_client):
        """Test successful user authorization check"""
        # Arrange
        user_id = str(uuid4())
        resource = "error_report"
        action = "create"

        with aioresponses.aioresponses() as m:
            m.post(
                "http://localhost:8001/api/v1/auth/authorize",
                payload={"authorized": True},
                status=200,
            )

            # Act
            is_authorized = await ums_client.check_authorization(
                user_id, resource, action
            )

            # Assert
            assert is_authorized is True

    @pytest.mark.asyncio
    async def test_check_user_authorization_denied(self, ums_client):
        """Test user authorization denial"""
        # Arrange
        user_id = str(uuid4())
        resource = "error_report"
        action = "delete"

        with aioresponses.aioresponses() as m:
            m.post(
                "http://localhost:8001/api/v1/auth/authorize",
                payload={"authorized": False, "reason": "Insufficient permissions"},
                status=403,
            )

            # Act
            is_authorized = await ums_client.check_authorization(
                user_id, resource, action
            )

            # Assert
            assert is_authorized is False

    @pytest.mark.asyncio
    async def test_service_unavailable_handling(self, ums_client):
        """Test handling of User Management Service unavailability"""
        # Arrange
        token = "test.jwt.token"

        with aioresponses.aioresponses() as m:
            m.post(
                "http://localhost:8001/api/v1/auth/validate-token",
                exception=httpx.ConnectError("Service unavailable"),
            )

            # Act & Assert
            with pytest.raises(httpx.ConnectError):
                await ums_client.validate_token(token)

    @pytest.mark.asyncio
    async def test_timeout_handling(self, ums_client):
        """Test handling of service timeout"""
        # Arrange
        user_id = str(uuid4())

        with aioresponses.aioresponses() as m:
            m.get(
                f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                exception=httpx.TimeoutException("Request timeout"),
            )

            # Act & Assert
            with pytest.raises(httpx.TimeoutException):
                await ums_client.get_user_permissions(user_id)

    @pytest.mark.asyncio
    async def test_retry_mechanism_on_failure(self, ums_client):
        """Test retry mechanism on service failure"""
        # Arrange
        user_id = str(uuid4())
        expected_permissions = ["error_report:read"]

        with aioresponses.aioresponses() as m:
            # First two calls fail, third succeeds
            m.get(
                f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                exception=httpx.ConnectError("Connection failed"),
            )
            m.get(
                f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                exception=httpx.ConnectError("Connection failed"),
            )
            m.get(
                f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                payload={"permissions": expected_permissions},
                status=200,
            )

            # Act
            permissions = await ums_client.get_user_permissions(user_id)

            # Assert
            assert permissions == expected_permissions


@pytest.mark.integration
@pytest.mark.external_services
class TestNotificationServiceIntegration:
    """Integration tests for Notification Service"""

    @pytest.fixture
    def notification_client(self):
        """Create Notification Service client"""
        return NotificationServiceClient(
            base_url="http://localhost:8002",
            api_key="test-notification-key",
            timeout=30.0,
        )

    @pytest.mark.asyncio
    async def test_send_critical_error_notification_success(self, notification_client):
        """Test successful sending of critical error notification"""
        # Arrange
        error_report = ErrorReportFactory.create(
            severity_level=SeverityLevel.CRITICAL, error_categories=["patient_safety"]
        )

        notification_data = {
            "type": "critical_error",
            "error_id": str(error_report.error_id),
            "severity": "critical",
            "categories": error_report.error_categories,
            "original_text": error_report.original_text,
            "corrected_text": error_report.corrected_text,
        }

        with aioresponses.aioresponses() as m:
            m.post(
                "http://localhost:8002/api/v1/notifications/send",
                payload={
                    "notification_id": str(uuid4()),
                    "status": "sent",
                    "recipients": ["admin@example.com", "qa-lead@example.com"],
                },
                status=200,
            )

            # Act
            result = await notification_client.send_critical_error_notification(
                notification_data
            )

            # Assert
            assert result["status"] == "sent"
            assert len(result["recipients"]) == 2

    @pytest.mark.asyncio
    async def test_send_batch_notifications_success(self, notification_client):
        """Test successful sending of batch notifications"""
        # Arrange
        error_reports = ErrorReportFactory.create_batch(5)
        notifications = [
            {
                "type": "error_summary",
                "error_id": str(report.error_id),
                "severity": report.severity_level.value,
            }
            for report in error_reports
        ]

        with aioresponses.aioresponses() as m:
            m.post(
                "http://localhost:8002/api/v1/notifications/batch",
                payload={
                    "batch_id": str(uuid4()),
                    "status": "processed",
                    "sent_count": 5,
                    "failed_count": 0,
                },
                status=200,
            )

            # Act
            result = await notification_client.send_batch_notifications(notifications)

            # Assert
            assert result["status"] == "processed"
            assert result["sent_count"] == 5
            assert result["failed_count"] == 0

    @pytest.mark.asyncio
    async def test_notification_service_health_check(self, notification_client):
        """Test notification service health check"""
        # Arrange
        with aioresponses.aioresponses() as m:
            m.get(
                "http://localhost:8002/health",
                payload={"status": "healthy", "version": "1.0.0", "uptime": 3600},
                status=200,
            )

            # Act
            health_status = await notification_client.health_check()

            # Assert
            assert health_status["status"] == "healthy"
            assert health_status["uptime"] == 3600


@pytest.mark.integration
@pytest.mark.external_services
class TestServiceCircuitBreaker:
    """Integration tests for circuit breaker pattern in external service calls"""

    @pytest.fixture
    def circuit_breaker_client(self):
        """Create client with circuit breaker"""
        return UserManagementServiceClient(
            base_url="http://localhost:8001",
            api_key="test-api-key",
            timeout=30.0,
            circuit_breaker_enabled=True,
            failure_threshold=3,
            recovery_timeout=60,
        )

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self, circuit_breaker_client):
        """Test circuit breaker opens after consecutive failures"""
        # Arrange
        user_id = str(uuid4())

        with aioresponses.aioresponses() as m:
            # Configure multiple failures
            for _ in range(4):
                m.get(
                    f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                    exception=httpx.ConnectError("Service down"),
                )

            # Act - Make calls that will trigger circuit breaker
            for i in range(4):
                try:
                    await circuit_breaker_client.get_user_permissions(user_id)
                except Exception:
                    pass

            # Assert - Circuit breaker should be open now
            assert circuit_breaker_client.circuit_breaker.is_open() is True

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self, circuit_breaker_client):
        """Test circuit breaker half-open state and recovery"""
        # Arrange
        user_id = str(uuid4())
        expected_permissions = ["error_report:read"]

        # First, open the circuit breaker
        with aioresponses.aioresponses() as m:
            for _ in range(3):
                m.get(
                    f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                    exception=httpx.ConnectError("Service down"),
                )

            for i in range(3):
                try:
                    await circuit_breaker_client.get_user_permissions(user_id)
                except Exception:
                    pass

        # Wait for recovery timeout (simulate)
        circuit_breaker_client.circuit_breaker._last_failure_time = (
            datetime.utcnow() - timedelta(seconds=61)
        )

        # Now service is back up
        with aioresponses.aioresponses() as m:
            m.get(
                f"http://localhost:8001/api/v1/users/{user_id}/permissions",
                payload={"permissions": expected_permissions},
                status=200,
            )

            # Act
            permissions = await circuit_breaker_client.get_user_permissions(user_id)

            # Assert
            assert permissions == expected_permissions
            assert circuit_breaker_client.circuit_breaker.is_closed() is True


@pytest.mark.integration
@pytest.mark.external_services
class TestServiceMeshIntegration:
    """Integration tests for service mesh features"""

    @pytest.mark.asyncio
    async def test_service_discovery_integration(self):
        """Test service discovery integration"""
        # Arrange
        with patch(
            "src.error_reporting_service.infrastructure.adapters.external.service_discovery.ServiceDiscovery"
        ) as mock_discovery:
            mock_discovery.return_value.discover_service.return_value = {
                "host": "user-management-service.default.svc.cluster.local",
                "port": 8001,
                "health_check_url": "/health",
            }

            # Act
            client = UserManagementServiceClient.from_service_discovery(
                "user-management"
            )

            # Assert
            assert (
                "user-management-service.default.svc.cluster.local" in client.base_url
            )

    @pytest.mark.asyncio
    async def test_distributed_tracing_headers(self, ums_client):
        """Test distributed tracing headers are properly propagated"""
        # Arrange
        trace_id = str(uuid4())
        span_id = str(uuid4())

        with aioresponses.aioresponses() as m:

            def request_callback(url, **kwargs):
                headers = kwargs.get("headers", {})
                assert "X-Trace-Id" in headers
                assert "X-Span-Id" in headers
                assert headers["X-Trace-Id"] == trace_id
                return aioresponses.CallbackResult(
                    status=200,
                    payload={"valid": True, "user": {"user_id": str(uuid4())}},
                )

            m.post(
                "http://localhost:8001/api/v1/auth/validate-token",
                callback=request_callback,
            )

            # Act
            with patch(
                "src.error_reporting_service.infrastructure.adapters.external.tracing.get_current_trace_context"
            ) as mock_trace:
                mock_trace.return_value = {"trace_id": trace_id, "span_id": span_id}

                result = await ums_client.validate_token("test.token")

                # Assert
                assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_load_balancing_across_instances(self):
        """Test load balancing across multiple service instances"""
        # Arrange
        service_instances = [
            "http://ums-instance-1:8001",
            "http://ums-instance-2:8001",
            "http://ums-instance-3:8001",
        ]

        with patch(
            "src.error_reporting_service.infrastructure.adapters.external.load_balancer.LoadBalancer"
        ) as mock_lb:
            mock_lb.return_value.get_next_instance.side_effect = service_instances

            clients = []
            for _ in range(3):
                client = UserManagementServiceClient.with_load_balancer(
                    "user-management"
                )
                clients.append(client)

            # Assert
            base_urls = [client.base_url for client in clients]
            assert len(set(base_urls)) == 3  # All different instances
