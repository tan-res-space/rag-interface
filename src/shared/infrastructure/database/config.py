"""
Shared Database Configuration

Common database configuration classes and utilities used across all services.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DatabaseType(str, Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    SQLSERVER = "sqlserver"
    SQLITE = "sqlite"
    IN_MEMORY = "in_memory"


@dataclass
class DatabaseConfig:
    """
    Shared database configuration settings.
    
    This configuration is used across all services to ensure consistent
    database connection parameters and behavior.
    """
    
    type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "rag_interface"
    username: str = "rag_user"
    password: str = "rag_password"
    connection_string: Optional[str] = None
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # MongoDB specific
    replica_set: Optional[str] = None
    auth_source: Optional[str] = None
    
    # SQL Server specific
    driver: str = "ODBC Driver 17 for SQL Server"
    trust_server_certificate: bool = True
    
    # SQLite specific
    sqlite_file: str = ":memory:"
    
    # Additional options
    echo: bool = False  # SQL logging
    echo_pool: bool = False  # Connection pool logging
    
    def get_connection_string(self) -> str:
        """Get the appropriate connection string for the database type"""
        if self.connection_string:
            return self.connection_string
            
        if self.type == DatabaseType.POSTGRESQL:
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            
        elif self.type == DatabaseType.MONGODB:
            auth_part = f"{self.username}:{self.password}@" if self.username and self.password else ""
            replica_part = f"?replicaSet={self.replica_set}" if self.replica_set else ""
            return f"mongodb://{auth_part}{self.host}:{self.port}/{self.database}{replica_part}"
            
        elif self.type == DatabaseType.SQLSERVER:
            return (
                f"mssql+pyodbc://{self.username}:{self.password}@{self.host}:{self.port}/"
                f"{self.database}?driver={self.driver.replace(' ', '+')}"
                f"&TrustServerCertificate={'yes' if self.trust_server_certificate else 'no'}"
            )
            
        elif self.type == DatabaseType.SQLITE:
            return f"sqlite+aiosqlite:///{self.sqlite_file}"
            
        elif self.type == DatabaseType.IN_MEMORY:
            return "sqlite+aiosqlite:///:memory:"
            
        else:
            raise ValueError(f"Unsupported database type: {self.type}")
    
    def get_sync_connection_string(self) -> str:
        """Get synchronous connection string (for migrations, etc.)"""
        if self.type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.SQLITE:
            return f"sqlite:///{self.sqlite_file}"
        elif self.type == DatabaseType.IN_MEMORY:
            return "sqlite:///:memory:"
        else:
            # For other types, return async string (may need adjustment)
            return self.get_connection_string()
    
    @classmethod
    def from_env(cls, service_prefix: str = "") -> "DatabaseConfig":
        """
        Create database configuration from environment variables.
        
        Args:
            service_prefix: Optional prefix for environment variables (e.g., "ERS_", "UMS_")
        """
        import os
        
        prefix = f"{service_prefix}_" if service_prefix else ""
        
        return cls(
            type=DatabaseType(os.getenv(f"{prefix}DB_TYPE", "postgresql")),
            host=os.getenv(f"{prefix}DB_HOST", "localhost"),
            port=int(os.getenv(f"{prefix}DB_PORT", "5432")),
            database=os.getenv(f"{prefix}DB_DATABASE", "rag_interface"),
            username=os.getenv(f"{prefix}DB_USERNAME", "rag_user"),
            password=os.getenv(f"{prefix}DB_PASSWORD", "rag_password"),
            connection_string=os.getenv(f"{prefix}DB_CONNECTION_STRING"),
            pool_size=int(os.getenv(f"{prefix}DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv(f"{prefix}DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv(f"{prefix}DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv(f"{prefix}DB_POOL_RECYCLE", "3600")),
            echo=os.getenv(f"{prefix}DB_ECHO", "false").lower() == "true",
            echo_pool=os.getenv(f"{prefix}DB_ECHO_POOL", "false").lower() == "true",
        )
