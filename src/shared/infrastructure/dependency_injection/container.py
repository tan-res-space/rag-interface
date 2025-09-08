"""
Dependency Injection Container

Centralized dependency injection container for the RAG Interface system.
Implements the Dependency Inversion Principle from Hexagonal Architecture.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DIContainer:
    """
    Dependency Injection Container.
    
    Manages service registration, resolution, and lifecycle.
    Supports singleton and transient service lifetimes.
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._lifecycle: Dict[str, str] = {}  # 'singleton' or 'transient'

    def register_singleton(self, interface: Type[T], implementation: Type[T], name: Optional[str] = None):
        """
        Register a service as singleton.
        
        Args:
            interface: Interface type
            implementation: Implementation type
            name: Optional service name (defaults to interface name)
        """
        service_name = name or interface.__name__
        self._factories[service_name] = implementation
        self._lifecycle[service_name] = 'singleton'
        logger.debug(f"Registered singleton: {service_name}")

    def register_transient(self, interface: Type[T], implementation: Type[T], name: Optional[str] = None):
        """
        Register a service as transient (new instance each time).
        
        Args:
            interface: Interface type
            implementation: Implementation type
            name: Optional service name (defaults to interface name)
        """
        service_name = name or interface.__name__
        self._factories[service_name] = implementation
        self._lifecycle[service_name] = 'transient'
        logger.debug(f"Registered transient: {service_name}")

    def register_instance(self, interface: Type[T], instance: T, name: Optional[str] = None):
        """
        Register a specific instance.
        
        Args:
            interface: Interface type
            instance: Instance to register
            name: Optional service name (defaults to interface name)
        """
        service_name = name or interface.__name__
        self._singletons[service_name] = instance
        self._lifecycle[service_name] = 'singleton'
        logger.debug(f"Registered instance: {service_name}")

    def register_factory(self, interface: Type[T], factory: Callable[[], T], name: Optional[str] = None):
        """
        Register a factory function.
        
        Args:
            interface: Interface type
            factory: Factory function that creates instances
            name: Optional service name (defaults to interface name)
        """
        service_name = name or interface.__name__
        self._factories[service_name] = factory
        self._lifecycle[service_name] = 'transient'
        logger.debug(f"Registered factory: {service_name}")

    async def resolve(self, interface: Type[T], name: Optional[str] = None) -> T:
        """
        Resolve a service instance.
        
        Args:
            interface: Interface type to resolve
            name: Optional service name (defaults to interface name)
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        service_name = name or interface.__name__
        
        # Check if already instantiated as singleton
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # Check if factory exists
        if service_name not in self._factories:
            raise ValueError(f"Service not registered: {service_name}")
        
        factory = self._factories[service_name]
        lifecycle = self._lifecycle.get(service_name, 'transient')
        
        # Create instance
        if callable(factory):
            if asyncio.iscoroutinefunction(factory):
                instance = await factory()
            else:
                instance = factory()
        else:
            # Assume it's a class
            instance = factory()
        
        # Store as singleton if needed
        if lifecycle == 'singleton':
            self._singletons[service_name] = instance
        
        logger.debug(f"Resolved service: {service_name}")
        return instance

    def is_registered(self, interface: Type[T], name: Optional[str] = None) -> bool:
        """Check if a service is registered."""
        service_name = name or interface.__name__
        return service_name in self._factories or service_name in self._singletons

    def get_registered_services(self) -> list[str]:
        """Get list of all registered service names."""
        return list(set(self._factories.keys()) | set(self._singletons.keys()))

    async def dispose(self):
        """Dispose of all services and clean up resources."""
        logger.info("Disposing DI container...")
        
        # Dispose singletons that have dispose methods
        for service_name, instance in self._singletons.items():
            try:
                if hasattr(instance, 'dispose'):
                    if asyncio.iscoroutinefunction(instance.dispose):
                        await instance.dispose()
                    else:
                        instance.dispose()
                elif hasattr(instance, 'close'):
                    if asyncio.iscoroutinefunction(instance.close):
                        await instance.close()
                    else:
                        instance.close()
            except Exception as e:
                logger.error(f"Error disposing service {service_name}: {e}")
        
        # Clear all registrations
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._lifecycle.clear()
        
        logger.info("DI container disposed")


class ServiceRegistry:
    """
    Service registry for managing service configurations.
    
    Provides a higher-level interface for service registration.
    """

    def __init__(self, container: DIContainer):
        self.container = container

    async def register_database_services(self, config: Dict[str, Any]):
        """Register database-related services."""
        from error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
        from error_reporting_service.infrastructure.config.database_config import DatabaseConfig
        
        # Register database adapter factory
        self.container.register_factory(
            DatabaseAdapterFactory,
            lambda: DatabaseAdapterFactory(),
            "DatabaseAdapterFactory"
        )
        
        # Register database config
        db_config = DatabaseConfig.from_dict(config.get('database', {}))
        self.container.register_instance(DatabaseConfig, db_config, "DatabaseConfig")

    async def register_ml_services(self, config: Dict[str, Any]):
        """Register ML-related services."""
        from rag_integration_service.infrastructure.adapters.ml_models.factory import MLModelAdapterFactory
        
        # Register ML model adapter factory
        self.container.register_factory(
            MLModelAdapterFactory,
            lambda: MLModelAdapterFactory(),
            "MLModelAdapterFactory"
        )

    async def register_vector_storage_services(self, config: Dict[str, Any]):
        """Register vector storage services."""
        from rag_integration_service.infrastructure.adapters.vector_db.factory import VectorStorageAdapterFactory
        
        # Register vector storage adapter factory
        self.container.register_factory(
            VectorStorageAdapterFactory,
            lambda: VectorStorageAdapterFactory(),
            "VectorStorageAdapterFactory"
        )

    async def register_messaging_services(self, config: Dict[str, Any]):
        """Register messaging services."""
        # This would register message bus adapters
        pass

    async def register_all_services(self, config: Dict[str, Any]):
        """Register all services based on configuration."""
        await self.register_database_services(config)
        await self.register_ml_services(config)
        await self.register_vector_storage_services(config)
        await self.register_messaging_services(config)


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get the global DI container instance."""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


async def initialize_container(config: Dict[str, Any]) -> DIContainer:
    """Initialize the global DI container with services."""
    container = get_container()
    registry = ServiceRegistry(container)
    await registry.register_all_services(config)
    return container


async def dispose_container():
    """Dispose of the global DI container."""
    global _container
    if _container is not None:
        await _container.dispose()
        _container = None
