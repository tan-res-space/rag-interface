"""
Configuration Settings for User Management Service

This module contains configuration settings loaded from environment variables
following the same pattern as the Error Reporting Service.
"""

import os
from typing import List

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration"""

    type: str = Field(default="in_memory")  # in_memory, postgresql
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="ums_db")
    username: str = Field(default="ums_user")
    password: str = Field(default="ums_password")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    echo: bool = Field(default=False)


class EventBusConfig(BaseModel):
    """Event bus configuration"""

    type: str = Field(default="in_memory")  # in_memory, kafka
    bootstrap_servers: str = Field(default="localhost:9092")
    topic_prefix: str = Field(default="ums")
    consumer_group: str = Field(default="ums_service")
    auto_offset_reset: str = Field(default="latest")


class AuthConfig(BaseModel):
    """Authentication configuration"""

    secret_key: str = Field(default="your-secret-key-here")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    password_hash_algorithm: str = Field(default="bcrypt")
    password_hash_rounds: int = Field(default=12)


class SecurityConfig(BaseModel):
    """Security configuration"""

    max_failed_login_attempts: int = Field(default=5)
    account_lockout_duration_minutes: int = Field(default=30)
    password_min_length: int = Field(default=12)
    password_max_length: int = Field(default=128)
    session_timeout_minutes: int = Field(default=60)
    require_password_change_days: int = Field(default=90)


class Settings(BaseModel):
    """Main settings class"""

    app_name: str = Field(default="User Management Service")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Service configuration
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    event_bus: EventBusConfig = Field(default_factory=EventBusConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # API configuration
    api_prefix: str = Field(default="/api/v1")
    cors_origins: List[str] = Field(default=["*"])

    # External service URLs
    error_reporting_service_url: str = Field(default="http://localhost:8001")
    rag_integration_service_url: str = Field(default="http://localhost:8002")
    correction_engine_service_url: str = Field(default="http://localhost:8003")
    verification_service_url: str = Field(default="http://localhost:8004")

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables"""

        # Database configuration
        db_config = DatabaseConfig(
            type=os.getenv("UMS_DB_TYPE", "in_memory"),
            host=os.getenv("UMS_DB_HOST", "localhost"),
            port=int(os.getenv("UMS_DB_PORT", "5432")),
            name=os.getenv("UMS_DB_NAME", "ums_db"),
            username=os.getenv("UMS_DB_USERNAME", "ums_user"),
            password=os.getenv("UMS_DB_PASSWORD", "ums_password"),
            pool_size=int(os.getenv("UMS_DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("UMS_DB_MAX_OVERFLOW", "20")),
            echo=os.getenv("UMS_DB_ECHO", "false").lower() == "true",
        )

        # Event bus configuration
        event_bus_config = EventBusConfig(
            type=os.getenv("UMS_EVENT_BUS_TYPE", "in_memory"),
            bootstrap_servers=os.getenv(
                "UMS_KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
            ),
            topic_prefix=os.getenv("UMS_KAFKA_TOPIC_PREFIX", "ums"),
            consumer_group=os.getenv("UMS_KAFKA_CONSUMER_GROUP", "ums_service"),
            auto_offset_reset=os.getenv("UMS_KAFKA_AUTO_OFFSET_RESET", "latest"),
        )

        # Auth configuration
        auth_config = AuthConfig(
            secret_key=os.getenv("UMS_SECRET_KEY", "your-secret-key-here"),
            algorithm=os.getenv("UMS_JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(
                os.getenv("UMS_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
            ),
            refresh_token_expire_days=int(
                os.getenv("UMS_REFRESH_TOKEN_EXPIRE_DAYS", "7")
            ),
            password_hash_algorithm=os.getenv("UMS_PASSWORD_HASH_ALGORITHM", "bcrypt"),
            password_hash_rounds=int(os.getenv("UMS_PASSWORD_HASH_ROUNDS", "12")),
        )

        # Security configuration
        security_config = SecurityConfig(
            max_failed_login_attempts=int(
                os.getenv("UMS_MAX_FAILED_LOGIN_ATTEMPTS", "5")
            ),
            account_lockout_duration_minutes=int(
                os.getenv("UMS_ACCOUNT_LOCKOUT_DURATION_MINUTES", "30")
            ),
            password_min_length=int(os.getenv("UMS_PASSWORD_MIN_LENGTH", "12")),
            password_max_length=int(os.getenv("UMS_PASSWORD_MAX_LENGTH", "128")),
            session_timeout_minutes=int(os.getenv("UMS_SESSION_TIMEOUT_MINUTES", "60")),
            require_password_change_days=int(
                os.getenv("UMS_REQUIRE_PASSWORD_CHANGE_DAYS", "90")
            ),
        )

        return cls(
            app_name=os.getenv("UMS_APP_NAME", "User Management Service"),
            debug=os.getenv("UMS_DEBUG", "false").lower() == "true",
            log_level=os.getenv("UMS_LOG_LEVEL", "INFO"),
            database=db_config,
            event_bus=event_bus_config,
            auth=auth_config,
            security=security_config,
            api_prefix=os.getenv("UMS_API_PREFIX", "/api/v1"),
            cors_origins=os.getenv("UMS_CORS_ORIGINS", "*").split(","),
            error_reporting_service_url=os.getenv(
                "ERROR_REPORTING_SERVICE_URL", "http://localhost:8001"
            ),
            rag_integration_service_url=os.getenv(
                "RAG_INTEGRATION_SERVICE_URL", "http://localhost:8002"
            ),
            correction_engine_service_url=os.getenv(
                "CORRECTION_ENGINE_SERVICE_URL", "http://localhost:8003"
            ),
            verification_service_url=os.getenv(
                "VERIFICATION_SERVICE_URL", "http://localhost:8004"
            ),
        )


# Global settings instance
settings = Settings.from_env()
