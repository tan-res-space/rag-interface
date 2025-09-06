"""
Tests for Shared Database Configuration

Unit tests for database configuration classes and utilities.
"""

import os
import pytest
from unittest.mock import patch

from src.shared.infrastructure.database import DatabaseConfig, DatabaseType


class TestDatabaseConfig:
    """Test cases for DatabaseConfig"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = DatabaseConfig()
        
        assert config.type == DatabaseType.POSTGRESQL
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "rag_interface"
        assert config.username == "rag_user"
        assert config.password == "rag_password"
        assert config.pool_size == 10
        assert config.max_overflow == 20
        assert config.pool_timeout == 30
        assert config.echo is False
    
    def test_postgresql_connection_string(self):
        """Test PostgreSQL connection string generation"""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        expected = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"
        assert config.get_connection_string() == expected
    
    def test_sqlite_connection_string(self):
        """Test SQLite connection string generation"""
        config = DatabaseConfig(
            type=DatabaseType.SQLITE,
            sqlite_file="/path/to/db.sqlite"
        )
        
        expected = "sqlite+aiosqlite:///path/to/db.sqlite"
        assert config.get_connection_string() == expected
    
    def test_in_memory_connection_string(self):
        """Test in-memory database connection string"""
        config = DatabaseConfig(type=DatabaseType.IN_MEMORY)
        
        expected = "sqlite+aiosqlite:///:memory:"
        assert config.get_connection_string() == expected
    
    def test_custom_connection_string(self):
        """Test using custom connection string"""
        custom_string = "postgresql://custom:string@host:1234/db"
        config = DatabaseConfig(connection_string=custom_string)
        
        assert config.get_connection_string() == custom_string
    
    def test_sync_connection_string(self):
        """Test synchronous connection string generation"""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        expected = "postgresql://test_user:test_pass@localhost:5432/test_db"
        assert config.get_sync_connection_string() == expected
    
    @patch.dict(os.environ, {
        "TEST_DB_TYPE": "postgresql",
        "TEST_DB_HOST": "test-host",
        "TEST_DB_PORT": "5433",
        "TEST_DB_DATABASE": "test-db",
        "TEST_DB_USERNAME": "test-user",
        "TEST_DB_PASSWORD": "test-password",
        "TEST_DB_POOL_SIZE": "15",
        "TEST_DB_ECHO": "true"
    })
    def test_from_env_with_prefix(self):
        """Test creating configuration from environment variables with prefix"""
        config = DatabaseConfig.from_env("TEST")
        
        assert config.type == DatabaseType.POSTGRESQL
        assert config.host == "test-host"
        assert config.port == 5433
        assert config.database == "test-db"
        assert config.username == "test-user"
        assert config.password == "test-password"
        assert config.pool_size == 15
        assert config.echo is True
    
    @patch.dict(os.environ, {
        "DB_TYPE": "sqlite",
        "DB_HOST": "env-host"
    })
    def test_from_env_without_prefix(self):
        """Test creating configuration from environment variables without prefix"""
        config = DatabaseConfig.from_env()
        
        assert config.type == DatabaseType.SQLITE
        assert config.host == "env-host"
        # Other values should be defaults
        assert config.port == 5432
        assert config.database == "rag_interface"
    
    def test_unsupported_database_type(self):
        """Test error handling for unsupported database types"""
        # Create a config with an invalid type by bypassing enum validation
        config = DatabaseConfig()
        config.type = "unsupported"
        
        with pytest.raises(ValueError, match="Unsupported database type"):
            config.get_connection_string()


class TestDatabaseType:
    """Test cases for DatabaseType enum"""
    
    def test_database_type_values(self):
        """Test that all database type values are correct"""
        assert DatabaseType.POSTGRESQL.value == "postgresql"
        assert DatabaseType.MONGODB.value == "mongodb"
        assert DatabaseType.SQLSERVER.value == "sqlserver"
        assert DatabaseType.SQLITE.value == "sqlite"
        assert DatabaseType.IN_MEMORY.value == "in_memory"
