"""
Shared Logging Configuration

Common logging setup and utilities used across all services.
"""

import logging
import logging.config
import os
import sys
from typing import Optional


class LoggingConfig:
    """
    Shared logging configuration for all services.
    
    Provides consistent logging format, levels, and handlers across the system.
    """
    
    @staticmethod
    def setup_logging(
        service_name: str,
        log_level: str = "INFO",
        log_format: Optional[str] = None,
        enable_json_logging: bool = False,
        log_file: Optional[str] = None
    ) -> None:
        """
        Set up logging configuration for a service.
        
        Args:
            service_name: Name of the service for log identification
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Custom log format string
            enable_json_logging: Whether to use JSON format for structured logging
            log_file: Optional file path for file logging
        """
        
        # Default log format
        if log_format is None:
            if enable_json_logging:
                log_format = '{"timestamp": "%(asctime)s", "service": "' + service_name + '", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            else:
                log_format = f"%(asctime)s - {service_name} - %(name)s - %(levelname)s - %(message)s"
        
        # Configure logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "standard",
                    "stream": sys.stdout
                }
            },
            "loggers": {
                "": {  # Root logger
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False
                },
                "sqlalchemy.engine": {
                    "handlers": ["console"],
                    "level": "WARNING",  # Reduce SQL noise unless debugging
                    "propagate": False
                }
            }
        }
        
        # Add file handler if log_file is specified
        if log_file:
            logging_config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "standard",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
            # Add file handler to all loggers
            for logger_config in logging_config["loggers"].values():
                logger_config["handlers"].append("file")
        
        # Apply configuration
        logging.config.dictConfig(logging_config)
        
        # Log startup message
        logger = logging.getLogger(service_name)
        logger.info(f"{service_name} logging initialized at {log_level} level")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    @staticmethod
    def set_sql_logging(enabled: bool) -> None:
        """
        Enable or disable SQL query logging.
        
        Args:
            enabled: Whether to enable SQL logging
        """
        sql_logger = logging.getLogger("sqlalchemy.engine")
        if enabled:
            sql_logger.setLevel(logging.INFO)
        else:
            sql_logger.setLevel(logging.WARNING)
    
    @staticmethod
    def configure_from_env(service_name: str, env_prefix: str = "") -> None:
        """
        Configure logging from environment variables.
        
        Args:
            service_name: Name of the service
            env_prefix: Optional prefix for environment variables
        """
        prefix = f"{env_prefix}_" if env_prefix else ""
        
        log_level = os.getenv(f"{prefix}LOG_LEVEL", "INFO").upper()
        enable_json = os.getenv(f"{prefix}LOG_JSON", "false").lower() == "true"
        log_file = os.getenv(f"{prefix}LOG_FILE")
        
        LoggingConfig.setup_logging(
            service_name=service_name,
            log_level=log_level,
            enable_json_logging=enable_json,
            log_file=log_file
        )


def get_correlation_id() -> str:
    """
    Get or generate a correlation ID for request tracing.
    
    Returns:
        Correlation ID string
    """
    import uuid
    # In a real implementation, this would check for existing correlation ID
    # from request context, headers, etc.
    return str(uuid.uuid4())


class CorrelationFilter(logging.Filter):
    """
    Logging filter that adds correlation ID to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log record"""
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = get_correlation_id()
        return True
