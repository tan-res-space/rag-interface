"""
Application Settings for RAG Integration Service

Configuration settings loaded from environment variables with sensible defaults.
Follows the same pattern as the Error Reporting Service for consistency.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Application settings loaded from environment variables.
    """
    
    # Application settings
    app_name: str = "RAG Integration Service"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "default-secret-key"
    access_token_expire_minutes: int = 30
    
    # ML Model settings
    ml_models: Dict[str, Any] = None
    
    # Vector Database settings
    vector_db: Dict[str, Any] = None
    
    # Redis settings
    redis: Dict[str, Any] = None
    
    # Kafka settings
    kafka: Dict[str, Any] = None
    
    # Processing settings
    processing: Dict[str, Any] = None
    
    def __init__(self):
        """Initialize settings from environment variables"""
        self.app_name = os.getenv("APP_NAME", "RAG Integration Service")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.secret_key = os.getenv("SECRET_KEY", "default-secret-key")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # ML Model configuration
        self.ml_models = {
            "default_model": os.getenv("DEFAULT_ML_MODEL", "openai"),
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": os.getenv("OPENAI_MODEL", "text-embedding-ada-002"),
                "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "8191")),
                "batch_size": int(os.getenv("OPENAI_BATCH_SIZE", "100"))
            },
            "local": {
                "model_path": os.getenv("LOCAL_MODEL_PATH", "/models/sentence-transformer"),
                "device": os.getenv("LOCAL_MODEL_DEVICE", "cpu"),
                "batch_size": int(os.getenv("LOCAL_MODEL_BATCH_SIZE", "32"))
            },
            "huggingface": {
                "model_name": os.getenv("HF_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"),
                "cache_dir": os.getenv("HF_CACHE_DIR", "/tmp/huggingface_cache"),
                "device": os.getenv("HF_DEVICE", "cpu")
            }
        }
        
        # Vector Database configuration
        self.vector_db = {
            "type": os.getenv("VECTOR_DB_TYPE", "pinecone"),
            "pinecone": {
                "api_key": os.getenv("PINECONE_API_KEY", ""),
                "environment": os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp"),
                "index_name": os.getenv("PINECONE_INDEX_NAME", "asr-embeddings"),
                "dimension": int(os.getenv("PINECONE_DIMENSION", "1536")),
                "metric": os.getenv("PINECONE_METRIC", "cosine")
            },
            "weaviate": {
                "url": os.getenv("WEAVIATE_URL", "http://localhost:8080"),
                "api_key": os.getenv("WEAVIATE_API_KEY", ""),
                "class_name": os.getenv("WEAVIATE_CLASS_NAME", "ASREmbedding"),
                "batch_size": int(os.getenv("WEAVIATE_BATCH_SIZE", "100"))
            },
            "qdrant": {
                "url": os.getenv("QDRANT_URL", "http://localhost:6333"),
                "api_key": os.getenv("QDRANT_API_KEY", ""),
                "collection_name": os.getenv("QDRANT_COLLECTION_NAME", "asr_embeddings"),
                "vector_size": int(os.getenv("QDRANT_VECTOR_SIZE", "1536"))
            }
        }
        
        # Redis configuration
        self.redis = {
            "url": os.getenv("REDIS_URL", "redis://localhost:6379/1"),  # Different DB from Error Reporting
            "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            "retry_on_timeout": os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true",
            "cache_ttl": int(os.getenv("REDIS_CACHE_TTL", "3600"))  # 1 hour default
        }
        
        # Kafka configuration
        self.kafka = {
            "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(","),
            "topic_prefix": os.getenv("KAFKA_TOPIC_PREFIX", "asr"),
            "consumer_group": os.getenv("KAFKA_CONSUMER_GROUP", "rag-integration-service"),
            "producer_config": {
                "acks": os.getenv("KAFKA_ACKS", "all"),
                "retries": int(os.getenv("KAFKA_RETRIES", "3")),
                "compression_type": os.getenv("KAFKA_COMPRESSION_TYPE", "snappy")
            },
            "consumer_config": {
                "auto_offset_reset": os.getenv("KAFKA_AUTO_OFFSET_RESET", "latest"),
                "enable_auto_commit": os.getenv("KAFKA_ENABLE_AUTO_COMMIT", "true").lower() == "true",
                "max_poll_records": int(os.getenv("KAFKA_MAX_POLL_RECORDS", "500"))
            }
        }
        
        # Processing configuration
        self.processing = {
            "batch_size": int(os.getenv("PROCESSING_BATCH_SIZE", "50")),
            "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
            "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.7")),
            "max_search_results": int(os.getenv("MAX_SEARCH_RESULTS", "100")),
            "pattern_analysis_window_days": int(os.getenv("PATTERN_ANALYSIS_WINDOW_DAYS", "30")),
            "quality_metrics_window_days": int(os.getenv("QUALITY_METRICS_WINDOW_DAYS", "7"))
        }
    
    def get_ml_model_config(self, model_name: str = None) -> Dict[str, Any]:
        """Get ML model configuration"""
        if model_name is None:
            model_name = self.ml_models["default_model"]
        return self.ml_models.get(model_name, {})
    
    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get vector database configuration"""
        db_type = self.vector_db["type"]
        return self.vector_db.get(db_type, {})
    
    def get_redis_url(self) -> str:
        """Get Redis URL"""
        return self.redis["url"]
    
    def get_kafka_bootstrap_servers(self) -> List[str]:
        """Get Kafka bootstrap servers"""
        return self.kafka["bootstrap_servers"]
    
    def get_kafka_topics(self) -> Dict[str, str]:
        """Get Kafka topic names"""
        prefix = self.kafka["topic_prefix"]
        return {
            "error_events": f"{prefix}.error.events",
            "embedding_events": f"{prefix}.embedding.events",
            "pattern_events": f"{prefix}.pattern.events",
            "quality_events": f"{prefix}.quality.events"
        }
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug
    
    def get_cache_ttl(self, cache_type: str = "default") -> int:
        """Get cache TTL for different cache types"""
        ttl_map = {
            "default": self.redis["cache_ttl"],
            "embeddings": self.redis["cache_ttl"],
            "search_results": 300,  # 5 minutes for search results
            "patterns": 1800,  # 30 minutes for patterns
            "quality_metrics": 600  # 10 minutes for quality metrics
        }
        return ttl_map.get(cache_type, self.redis["cache_ttl"])


# Global settings instance
settings = Settings()
