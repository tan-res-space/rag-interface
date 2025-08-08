"""
Application Settings

This module contains the main application settings class that aggregates
all configuration for the Error Reporting Service.
"""

from dataclasses import dataclass, field
from typing import List
from .database_config import DatabaseConfig
from .messaging_config import EventBusConfig


@dataclass
class Settings:
    """Main application settings"""
    app_name: str = "Error Reporting Service"
    debug: bool = False
    log_level: str = "INFO"
    
    # Adapter configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    event_bus: EventBusConfig = field(default_factory=EventBusConfig)
    
    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Create settings from environment variables"""
        import os
        from .database_config import DatabaseType
        from .messaging_config import EventBusType
        
        # Database configuration from environment
        db_config = DatabaseConfig(
            type=DatabaseType(os.getenv("DB_TYPE", "postgresql")),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_DATABASE", "error_reporting"),
            username=os.getenv("DB_USERNAME", "ers_user"),
            password=os.getenv("DB_PASSWORD", "ers_password"),
            connection_string=os.getenv("DB_CONNECTION_STRING"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30"))
        )
        
        # Event bus configuration from environment
        event_bus_config = EventBusConfig(
            type=EventBusType(os.getenv("EVENT_BUS_TYPE", "kafka")),
            connection_string=os.getenv("EVENT_BUS_CONNECTION_STRING", "localhost:9092"),
            client_id=os.getenv("EVENT_BUS_CLIENT_ID", "error-reporting-service"),
            bootstrap_servers=os.getenv("EVENT_BUS_BOOTSTRAP_SERVERS"),
            security_protocol=os.getenv("EVENT_BUS_SECURITY_PROTOCOL", "PLAINTEXT"),
            region_name=os.getenv("EVENT_BUS_REGION_NAME"),
            access_key_id=os.getenv("EVENT_BUS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("EVENT_BUS_SECRET_ACCESS_KEY")
        )
        
        return cls(
            app_name=os.getenv("APP_NAME", "Error Reporting Service"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database=db_config,
            event_bus=event_bus_config,
            api_prefix=os.getenv("API_PREFIX", "/api/v1"),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-here"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        )


# Global settings instance
settings = Settings.from_env()
