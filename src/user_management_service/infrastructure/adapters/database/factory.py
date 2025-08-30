"""
Database Adapter Factory

This module provides a factory for creating database adapters based on configuration.
Follows the same pattern as the Error Reporting Service.
"""

import logging
from typing import Union

from ....application.ports.user_repository_port import IUserRepositoryPort
from ...config.settings import DatabaseConfig
from .in_memory.adapter import InMemoryUserRepositoryAdapter

logger = logging.getLogger(__name__)


class DatabaseAdapterFactory:
    """
    Factory for creating database adapters.

    Supports multiple database types through configuration.
    """

    @staticmethod
    async def create(config: DatabaseConfig) -> IUserRepositoryPort:
        """
        Create a database adapter based on configuration.

        Args:
            config: Database configuration

        Returns:
            Database adapter instance

        Raises:
            ValueError: If database type is not supported
        """

        logger.info(f"Creating database adapter for type: {config.type}")

        if config.type == "in_memory":
            adapter = InMemoryUserRepositoryAdapter()
            logger.info("Created in-memory database adapter")
            return adapter

        elif config.type == "postgresql":
            # PostgreSQL adapter would be implemented here
            # For now, fall back to in-memory
            logger.warning(
                "PostgreSQL adapter not implemented, using in-memory adapter"
            )
            adapter = InMemoryUserRepositoryAdapter()
            return adapter

        else:
            raise ValueError(f"Unsupported database type: {config.type}")

    @staticmethod
    def get_supported_types() -> list:
        """Get list of supported database types"""
        return ["in_memory", "postgresql"]

    @staticmethod
    async def test_connection(config: DatabaseConfig) -> dict:
        """
        Test database connection.

        Args:
            config: Database configuration

        Returns:
            Connection test results
        """

        try:
            adapter = await DatabaseAdapterFactory.create(config)
            health_info = await adapter.health_check()
            connection_info = await adapter.get_connection_info()

            return {
                "status": "success",
                "database_type": config.type,
                "health": health_info,
                "connection": connection_info,
            }

        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return {"status": "failed", "database_type": config.type, "error": str(e)}
