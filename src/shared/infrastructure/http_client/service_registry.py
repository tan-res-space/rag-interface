"""
Service Registry

Central registry for managing HTTP clients for all services.
Provides service discovery and client management.
"""

import logging
import os
from typing import Dict, Optional

from .base_client import BaseHTTPClient
from .error_reporting_client import ErrorReportingClient
from .rag_integration_client import RAGIntegrationClient

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Central registry for service clients.
    
    Manages HTTP clients for all services in the RAG Interface system.
    """

    def __init__(self):
        self._clients: Dict[str, BaseHTTPClient] = {}
        self._service_urls: Dict[str, str] = {}
        self._auth_tokens: Dict[str, Optional[str]] = {}

    def register_service(
        self,
        service_name: str,
        base_url: str,
        auth_token: Optional[str] = None
    ):
        """
        Register a service with its URL and authentication.
        
        Args:
            service_name: Name of the service
            base_url: Base URL of the service
            auth_token: Optional authentication token
        """
        self._service_urls[service_name] = base_url
        self._auth_tokens[service_name] = auth_token
        logger.info(f"Registered service: {service_name} at {base_url}")

    def get_error_reporting_client(self) -> ErrorReportingClient:
        """
        Get Error Reporting Service client.
        
        Returns:
            Error Reporting client instance
        """
        service_name = "error_reporting"
        
        if service_name not in self._clients:
            base_url = self._service_urls.get(service_name, "http://localhost:8000")
            auth_token = self._auth_tokens.get(service_name)
            
            self._clients[service_name] = ErrorReportingClient(
                base_url=base_url,
                auth_token=auth_token
            )
        
        return self._clients[service_name]

    def get_rag_integration_client(self) -> RAGIntegrationClient:
        """
        Get RAG Integration Service client.
        
        Returns:
            RAG Integration client instance
        """
        service_name = "rag_integration"
        
        if service_name not in self._clients:
            base_url = self._service_urls.get(service_name, "http://localhost:8003")
            auth_token = self._auth_tokens.get(service_name)
            
            self._clients[service_name] = RAGIntegrationClient(
                base_url=base_url,
                auth_token=auth_token
            )
        
        return self._clients[service_name]

    def get_user_management_client(self) -> BaseHTTPClient:
        """
        Get User Management Service client.
        
        Returns:
            User Management client instance
        """
        service_name = "user_management"
        
        if service_name not in self._clients:
            base_url = self._service_urls.get(service_name, "http://localhost:8001")
            auth_token = self._auth_tokens.get(service_name)
            
            self._clients[service_name] = BaseHTTPClient(
                base_url=base_url,
                auth_token=auth_token
            )
        
        return self._clients[service_name]

    def get_verification_client(self) -> BaseHTTPClient:
        """
        Get Verification Service client.
        
        Returns:
            Verification client instance
        """
        service_name = "verification"
        
        if service_name not in self._clients:
            base_url = self._service_urls.get(service_name, "http://localhost:8004")
            auth_token = self._auth_tokens.get(service_name)
            
            self._clients[service_name] = BaseHTTPClient(
                base_url=base_url,
                auth_token=auth_token
            )
        
        return self._clients[service_name]

    def get_correction_engine_client(self) -> BaseHTTPClient:
        """
        Get Correction Engine Service client.
        
        Returns:
            Correction Engine client instance
        """
        service_name = "correction_engine"
        
        if service_name not in self._clients:
            base_url = self._service_urls.get(service_name, "http://localhost:8005")
            auth_token = self._auth_tokens.get(service_name)
            
            self._clients[service_name] = BaseHTTPClient(
                base_url=base_url,
                auth_token=auth_token
            )
        
        return self._clients[service_name]

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all registered services.
        
        Returns:
            Dictionary mapping service names to health status
        """
        health_status = {}
        
        for service_name in self._service_urls.keys():
            try:
                if service_name == "error_reporting":
                    client = self.get_error_reporting_client()
                elif service_name == "rag_integration":
                    client = self.get_rag_integration_client()
                elif service_name == "user_management":
                    client = self.get_user_management_client()
                elif service_name == "verification":
                    client = self.get_verification_client()
                elif service_name == "correction_engine":
                    client = self.get_correction_engine_client()
                else:
                    continue
                
                health_status[service_name] = await client.health_check()
                
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False
        
        return health_status

    def update_auth_token(self, service_name: str, auth_token: str):
        """
        Update authentication token for a service.
        
        Args:
            service_name: Name of the service
            auth_token: New authentication token
        """
        self._auth_tokens[service_name] = auth_token
        
        # Update existing client if it exists
        if service_name in self._clients:
            self._clients[service_name].set_auth_token(auth_token)
        
        logger.info(f"Updated auth token for service: {service_name}")

    def remove_auth_token(self, service_name: str):
        """
        Remove authentication token for a service.
        
        Args:
            service_name: Name of the service
        """
        self._auth_tokens[service_name] = None
        
        # Update existing client if it exists
        if service_name in self._clients:
            self._clients[service_name].remove_auth_token()
        
        logger.info(f"Removed auth token for service: {service_name}")

    async def close_all(self):
        """Close all service clients."""
        for service_name, client in self._clients.items():
            try:
                await client.close()
                logger.debug(f"Closed client for service: {service_name}")
            except Exception as e:
                logger.error(f"Failed to close client for {service_name}: {e}")
        
        self._clients.clear()

    def get_service_urls(self) -> Dict[str, str]:
        """Get all registered service URLs."""
        return self._service_urls.copy()

    def is_service_registered(self, service_name: str) -> bool:
        """Check if a service is registered."""
        return service_name in self._service_urls

    @classmethod
    def from_environment(cls) -> "ServiceRegistry":
        """
        Create service registry from environment variables.
        
        Environment variables:
        - ERROR_REPORTING_URL: Error Reporting Service URL
        - RAG_INTEGRATION_URL: RAG Integration Service URL
        - USER_MANAGEMENT_URL: User Management Service URL
        - VERIFICATION_URL: Verification Service URL
        - CORRECTION_ENGINE_URL: Correction Engine Service URL
        - *_AUTH_TOKEN: Authentication tokens for each service
        
        Returns:
            Configured service registry
        """
        registry = cls()
        
        # Register services from environment
        services = {
            "error_reporting": {
                "url": os.getenv("ERROR_REPORTING_URL", "http://localhost:8000"),
                "token": os.getenv("ERROR_REPORTING_AUTH_TOKEN")
            },
            "rag_integration": {
                "url": os.getenv("RAG_INTEGRATION_URL", "http://localhost:8003"),
                "token": os.getenv("RAG_INTEGRATION_AUTH_TOKEN")
            },
            "user_management": {
                "url": os.getenv("USER_MANAGEMENT_URL", "http://localhost:8001"),
                "token": os.getenv("USER_MANAGEMENT_AUTH_TOKEN")
            },
            "verification": {
                "url": os.getenv("VERIFICATION_URL", "http://localhost:8004"),
                "token": os.getenv("VERIFICATION_AUTH_TOKEN")
            },
            "correction_engine": {
                "url": os.getenv("CORRECTION_ENGINE_URL", "http://localhost:8005"),
                "token": os.getenv("CORRECTION_ENGINE_AUTH_TOKEN")
            }
        }
        
        for service_name, config in services.items():
            registry.register_service(
                service_name,
                config["url"],
                config["token"]
            )
        
        return registry


# Global service registry instance
_service_registry: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """
    Get the global service registry instance.
    
    Returns:
        Global service registry
    """
    global _service_registry
    if _service_registry is None:
        _service_registry = ServiceRegistry.from_environment()
    return _service_registry


# Convenience functions
def get_error_reporting_client() -> ErrorReportingClient:
    """Get Error Reporting Service client."""
    return get_service_registry().get_error_reporting_client()


def get_rag_integration_client() -> RAGIntegrationClient:
    """Get RAG Integration Service client."""
    return get_service_registry().get_rag_integration_client()


def get_user_management_client() -> BaseHTTPClient:
    """Get User Management Service client."""
    return get_service_registry().get_user_management_client()


def get_verification_client() -> BaseHTTPClient:
    """Get Verification Service client."""
    return get_service_registry().get_verification_client()


def get_correction_engine_client() -> BaseHTTPClient:
    """Get Correction Engine Service client."""
    return get_service_registry().get_correction_engine_client()
