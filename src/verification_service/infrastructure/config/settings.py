"""
Application Settings for Verification Service

Configuration settings loaded from environment variables with sensible defaults.
Follows the same pattern as other services for consistency.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Settings:
    """
    Application settings loaded from environment variables.
    """

    # Application settings
    app_name: str = "Verification Service"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "default-secret-key"
    access_token_expire_minutes: int = 30

    # Analytics settings
    analytics: Dict[str, Any] = None

    # Database settings
    database: Dict[str, Any] = None

    # Redis settings
    redis: Dict[str, Any] = None

    # Processing settings
    processing: Dict[str, Any] = None

    def __init__(self):
        """Initialize settings from environment variables"""
        self.app_name = os.getenv("APP_NAME", "Verification Service")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.secret_key = os.getenv("SECRET_KEY", "default-secret-key")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # Analytics configuration
        self.analytics = {
            "dashboard_refresh_interval": int(
                os.getenv("DASHBOARD_REFRESH_INTERVAL", "300")
            ),  # 5 minutes
            "metrics_retention_days": int(os.getenv("METRICS_RETENTION_DAYS", "90")),
            "aggregation_window_minutes": int(
                os.getenv("AGGREGATION_WINDOW_MINUTES", "15")
            ),
            "quality_threshold": float(os.getenv("QUALITY_THRESHOLD", "0.8")),
        }

        # Database configuration
        self.database = {
            "url": os.getenv(
                "DATABASE_URL",
                "postgresql://user:password@localhost:5432/verification_service",
            ),
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        }

        # Redis configuration
        self.redis = {
            "url": os.getenv(
                "REDIS_URL", "redis://localhost:6379/3"
            ),  # Different DB from other services
            "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            "retry_on_timeout": os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower()
            == "true",
            "cache_ttl": int(os.getenv("REDIS_CACHE_TTL", "900")),  # 15 minutes default
        }

        # Processing configuration
        self.processing = {
            "max_concurrent_verifications": int(
                os.getenv("MAX_CONCURRENT_VERIFICATIONS", "50")
            ),
            "verification_timeout_seconds": int(
                os.getenv("VERIFICATION_TIMEOUT_SECONDS", "30")
            ),
            "batch_size": int(os.getenv("PROCESSING_BATCH_SIZE", "100")),
            "analytics_batch_size": int(os.getenv("ANALYTICS_BATCH_SIZE", "1000")),
        }

    def get_database_url(self) -> str:
        """Get database URL"""
        return self.database["url"]

    def get_redis_url(self) -> str:
        """Get Redis URL"""
        return self.redis["url"]

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug

    def get_cache_ttl(self, cache_type: str = "default") -> int:
        """Get cache TTL for different cache types"""
        ttl_map = {
            "default": self.redis["cache_ttl"],
            "verification_results": self.redis["cache_ttl"],
            "analytics": 300,  # 5 minutes for analytics
            "dashboard": 180,  # 3 minutes for dashboard data
            "statistics": 600,  # 10 minutes for statistics
        }
        return ttl_map.get(cache_type, self.redis["cache_ttl"])


# Global settings instance
settings = Settings()
