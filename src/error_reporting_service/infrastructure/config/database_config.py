"""
Database Configuration

This module contains database configuration classes and enums.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DatabaseType(str, Enum):
    """Enumeration for supported database types"""

    POSTGRESQL = "postgresql"
    SQLSERVER = "sqlserver"
    MONGODB = "mongodb"
    IN_MEMORY = "in_memory"


@dataclass
class DatabaseConfig:
    """Database configuration settings"""

    type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "error_reporting"
    username: str = "ers_user"
    password: str = "ers_password"
    connection_string: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

    # MongoDB specific
    replica_set: Optional[str] = None
    auth_source: Optional[str] = None

    # SQL Server specific
    driver: str = "ODBC Driver 17 for SQL Server"
    trust_server_certificate: bool = True

    def get_connection_string(self) -> str:
        """Get the appropriate connection string for the database type"""
        if self.connection_string:
            return self.connection_string

        if self.type == DatabaseType.POSTGRESQL:
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.MONGODB:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"
        elif self.type == DatabaseType.SQLSERVER:
            return f"mssql+aioodbc://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?driver={self.driver}&TrustServerCertificate={self.trust_server_certificate}"
        elif self.type == DatabaseType.IN_MEMORY:
            return "in-memory://localhost"
        else:
            raise ValueError(f"Unsupported database type: {self.type}")
