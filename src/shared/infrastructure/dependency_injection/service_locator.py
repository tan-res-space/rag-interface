"""
Service Locator Pattern

Provides easy access to services through the dependency injection container.
Implements the Service Locator pattern for convenient service resolution.
"""

import logging
from typing import Optional, Type, TypeVar

from .container import get_container

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceLocator:
    """
    Service Locator for easy service access.
    
    Provides a simplified interface to the dependency injection container.
    """

    @staticmethod
    async def get_service(interface: Type[T], name: Optional[str] = None) -> T:
        """
        Get a service instance.
        
        Args:
            interface: Interface type to resolve
            name: Optional service name
            
        Returns:
            Service instance
        """
        container = get_container()
        return await container.resolve(interface, name)

    @staticmethod
    def is_service_available(interface: Type[T], name: Optional[str] = None) -> bool:
        """
        Check if a service is available.
        
        Args:
            interface: Interface type to check
            name: Optional service name
            
        Returns:
            True if service is registered
        """
        container = get_container()
        return container.is_registered(interface, name)

    @staticmethod
    async def get_database_adapter():
        """Get the database adapter for the current service."""
        try:
            from error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
            from error_reporting_service.infrastructure.config.database_config import DatabaseConfig
            
            factory = await ServiceLocator.get_service(DatabaseAdapterFactory, "DatabaseAdapterFactory")
            config = await ServiceLocator.get_service(DatabaseConfig, "DatabaseConfig")
            
            return await factory.create(config)
        except Exception as e:
            logger.error(f"Failed to get database adapter: {e}")
            raise

    @staticmethod
    async def get_ml_adapter():
        """Get the ML model adapter."""
        try:
            from rag_integration_service.infrastructure.adapters.ml_models.factory import MLModelAdapterFactory
            
            factory = await ServiceLocator.get_service(MLModelAdapterFactory, "MLModelAdapterFactory")
            return await factory.create_from_env()
        except Exception as e:
            logger.error(f"Failed to get ML adapter: {e}")
            raise

    @staticmethod
    async def get_vector_storage_adapter():
        """Get the vector storage adapter."""
        try:
            from rag_integration_service.infrastructure.adapters.vector_db.factory import VectorStorageAdapterFactory
            
            factory = await ServiceLocator.get_service(VectorStorageAdapterFactory, "VectorStorageAdapterFactory")
            return await factory.create_from_env()
        except Exception as e:
            logger.error(f"Failed to get vector storage adapter: {e}")
            raise


# Convenience functions for common services
async def get_database_adapter():
    """Convenience function to get database adapter."""
    return await ServiceLocator.get_database_adapter()


async def get_ml_adapter():
    """Convenience function to get ML adapter."""
    return await ServiceLocator.get_ml_adapter()


async def get_vector_storage_adapter():
    """Convenience function to get vector storage adapter."""
    return await ServiceLocator.get_vector_storage_adapter()


class ServiceProvider:
    """
    Service provider for dependency injection in FastAPI.
    
    Provides dependency functions for FastAPI's dependency injection system.
    """

    @staticmethod
    async def get_database_adapter_dependency():
        """FastAPI dependency for database adapter."""
        return await get_database_adapter()

    @staticmethod
    async def get_ml_adapter_dependency():
        """FastAPI dependency for ML adapter."""
        return await get_ml_adapter()

    @staticmethod
    async def get_vector_storage_dependency():
        """FastAPI dependency for vector storage."""
        return await get_vector_storage_adapter()


# FastAPI dependency functions
async def database_adapter_dependency():
    """FastAPI dependency function for database adapter."""
    return await ServiceProvider.get_database_adapter_dependency()


async def ml_adapter_dependency():
    """FastAPI dependency function for ML adapter."""
    return await ServiceProvider.get_ml_adapter_dependency()


async def vector_storage_dependency():
    """FastAPI dependency function for vector storage."""
    return await ServiceProvider.get_vector_storage_dependency()
