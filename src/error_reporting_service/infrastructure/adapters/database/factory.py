"""
Database Adapter Factory

This module contains the factory for creating database adapters
based on configuration.
"""

from error_reporting_service.infrastructure.adapters.database.abstract.database_adapter import (
    IDatabaseAdapter,
)
from error_reporting_service.infrastructure.config.database_config import (
    DatabaseConfig,
    DatabaseType,
)


class DatabaseAdapterFactory:
    """Factory for creating database adapters"""

    @staticmethod
    async def create(config: DatabaseConfig) -> IDatabaseAdapter:
        """
        Create database adapter based on configuration.

        Args:
            config: Database configuration

        Returns:
            Database adapter instance

        Raises:
            ValueError: If database type is not supported
        """
        if config.type == DatabaseType.POSTGRESQL:
            from .postgresql.adapter import PostgreSQLAdapter

            connection_string = config.get_connection_string()
            return PostgreSQLAdapter(connection_string)

        elif config.type == DatabaseType.MONGODB:
            try:
                from .mongodb.adapter import MongoDBAdapter

                connection_string = config.get_connection_string()
                adapter = MongoDBAdapter(connection_string, config.database)
                await adapter.connect()
                return adapter
            except ImportError as e:
                logger.error(f"MongoDB adapter not available: {e}")
                raise RuntimeError("MongoDB adapter not available. Install pymongo and motor packages.")

        elif config.type == DatabaseType.SQLSERVER:
            try:
                from .sqlserver.adapter import SQLServerAdapter

                connection_string = config.get_connection_string()
                adapter = SQLServerAdapter(connection_string)
                await adapter.connect()
                return adapter
            except ImportError as e:
                logger.error(f"SQL Server adapter not available: {e}")
                raise RuntimeError("SQL Server adapter not available. Install aioodbc package.")

        else:
            # For testing and demonstration, use in-memory adapter
            from .in_memory.adapter import InMemoryDatabaseAdapter

            return InMemoryDatabaseAdapter()

    @staticmethod
    def get_supported_types() -> list:
        """Get list of supported database types"""
        return [db_type.value for db_type in DatabaseType]
