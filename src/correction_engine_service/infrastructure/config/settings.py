"""
Application Settings for Correction Engine Service

Configuration settings loaded from environment variables with sensible defaults.
Follows the same pattern as other services for consistency.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Settings:
    """
    Application settings loaded from environment variables.
    """

    # Application settings
    app_name: str = "Correction Engine Service"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "default-secret-key"
    access_token_expire_minutes: int = 30

    # Correction Model settings
    correction_models: Dict[str, Any] = None

    # Database settings
    database: Dict[str, Any] = None

    # Redis settings
    redis: Dict[str, Any] = None

    # Processing settings
    processing: Dict[str, Any] = None

    def __init__(self):
        """Initialize settings from environment variables"""
        self.app_name = os.getenv("APP_NAME", "Correction Engine Service")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.secret_key = os.getenv("SECRET_KEY", "default-secret-key")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # Correction Model configuration
        self.correction_models = {
            "default_model": os.getenv("DEFAULT_CORRECTION_MODEL", "grammar_corrector"),
            "grammar_corrector": {
                "model_path": os.getenv(
                    "GRAMMAR_MODEL_PATH", "/models/grammar-corrector"
                ),
                "confidence_threshold": float(
                    os.getenv("GRAMMAR_CONFIDENCE_THRESHOLD", "0.8")
                ),
                "max_suggestions": int(os.getenv("GRAMMAR_MAX_SUGGESTIONS", "5")),
            },
            "spell_checker": {
                "model_path": os.getenv("SPELL_MODEL_PATH", "/models/spell-checker"),
                "confidence_threshold": float(
                    os.getenv("SPELL_CONFIDENCE_THRESHOLD", "0.9")
                ),
                "max_suggestions": int(os.getenv("SPELL_MAX_SUGGESTIONS", "3")),
            },
            "style_corrector": {
                "model_path": os.getenv("STYLE_MODEL_PATH", "/models/style-corrector"),
                "confidence_threshold": float(
                    os.getenv("STYLE_CONFIDENCE_THRESHOLD", "0.7")
                ),
                "max_suggestions": int(os.getenv("STYLE_MAX_SUGGESTIONS", "3")),
            },
        }

        # Database configuration
        self.database = {
            "url": os.getenv(
                "DATABASE_URL",
                "postgresql://user:password@localhost:5432/correction_engine",
            ),
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        }

        # Redis configuration
        self.redis = {
            "url": os.getenv(
                "REDIS_URL", "redis://localhost:6379/2"
            ),  # Different DB from other services
            "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            "retry_on_timeout": os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower()
            == "true",
            "cache_ttl": int(
                os.getenv("REDIS_CACHE_TTL", "1800")
            ),  # 30 minutes default
        }

        # Processing configuration
        self.processing = {
            "max_text_length": int(os.getenv("MAX_TEXT_LENGTH", "10000")),
            "batch_size": int(os.getenv("PROCESSING_BATCH_SIZE", "50")),
            "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", "20")),
            "default_correction_mode": os.getenv("DEFAULT_CORRECTION_MODE", "balanced"),
            "max_suggestions_per_request": int(
                os.getenv("MAX_SUGGESTIONS_PER_REQUEST", "10")
            ),
        }

    def get_correction_model_config(self, model_name: str = None) -> Dict[str, Any]:
        """Get correction model configuration"""
        if model_name is None:
            model_name = self.correction_models["default_model"]
        return self.correction_models.get(model_name, {})

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
            "suggestions": self.redis["cache_ttl"],
            "corrections": 3600,  # 1 hour for applied corrections
            "statistics": 600,  # 10 minutes for statistics
        }
        return ttl_map.get(cache_type, self.redis["cache_ttl"])


# Global settings instance
settings = Settings()
