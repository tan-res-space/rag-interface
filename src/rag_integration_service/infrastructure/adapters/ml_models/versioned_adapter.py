"""
Versioned Embedding Adapter

Embedding adapter that supports versioning and migration of embeddings.
Handles model upgrades, backward compatibility, and embedding migration.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json
import hashlib

from rag_integration_service.application.ports.secondary.ml_model_port import MLModelPort as BaseEmbeddingAdapter
from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingVersion:
    """Embedding version metadata."""
    version: str
    model_name: str
    model_version: str
    dimensions: int
    created_at: datetime
    deprecated: bool = False
    migration_path: Optional[str] = None


class VersionedEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    Versioned embedding adapter with migration support.
    
    Manages multiple embedding model versions and provides seamless
    migration between versions while maintaining backward compatibility.
    """

    def __init__(
        self,
        current_adapter: BaseEmbeddingAdapter,
        version: str = "1.0.0",
        enable_migration: bool = True,
        legacy_adapters: Optional[Dict[str, BaseEmbeddingAdapter]] = None
    ):
        """
        Initialize versioned embedding adapter.
        
        Args:
            current_adapter: Current embedding adapter
            version: Current version string
            enable_migration: Whether to enable automatic migration
            legacy_adapters: Dictionary of legacy adapters by version
        """
        self.current_adapter = current_adapter
        self.current_version = version
        self.enable_migration = enable_migration
        self.legacy_adapters = legacy_adapters or {}
        
        # Version registry
        self.versions: Dict[str, EmbeddingVersion] = {}
        self._register_current_version()
        
        logger.info(f"Initialized versioned adapter v{version}")

    def _register_current_version(self):
        """Register the current version."""
        self.versions[self.current_version] = EmbeddingVersion(
            version=self.current_version,
            model_name="current",
            model_version=self.current_version,
            dimensions=1536,  # Default OpenAI dimension
            created_at=datetime.utcnow()
        )

    async def generate_embedding(
        self,
        text: str,
        embedding_type: EmbeddingType = EmbeddingType.ERROR,
        target_version: Optional[str] = None
    ) -> List[float]:
        """
        Generate versioned embedding.
        
        Args:
            text: Text to generate embedding for
            embedding_type: Type of embedding
            target_version: Specific version to use (optional)
            
        Returns:
            Versioned embedding vector
        """
        try:
            # Use current version if no target specified
            if target_version is None:
                target_version = self.current_version
            
            # Generate embedding with specified version
            if target_version == self.current_version:
                embedding = await self.current_adapter.generate_embedding(text, embedding_type)
            elif target_version in self.legacy_adapters:
                embedding = await self.legacy_adapters[target_version].generate_embedding(text, embedding_type)
            else:
                logger.warning(f"Version {target_version} not available, using current")
                embedding = await self.current_adapter.generate_embedding(text, embedding_type)
            
            # Add version metadata
            versioned_embedding = self._add_version_metadata(embedding, target_version)
            
            logger.debug(f"Generated embedding with version {target_version}")
            return versioned_embedding
            
        except Exception as e:
            logger.error(f"Failed to generate versioned embedding: {e}")
            # Fallback to current adapter
            return await self.current_adapter.generate_embedding(text, embedding_type)

    async def generate_batch_embeddings(
        self,
        texts: List[str],
        embedding_type: EmbeddingType = EmbeddingType.ERROR,
        target_version: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate versioned embeddings for multiple texts.
        
        Args:
            texts: List of texts
            embedding_type: Type of embedding
            target_version: Specific version to use
            
        Returns:
            List of versioned embedding vectors
        """
        try:
            embeddings = []
            
            for text in texts:
                embedding = await self.generate_embedding(text, embedding_type, target_version)
                embeddings.append(embedding)
            
            logger.debug(f"Generated {len(embeddings)} versioned embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch versioned embeddings: {e}")
            # Fallback to current adapter
            return await self.current_adapter.generate_batch_embeddings(texts, embedding_type)

    async def migrate_embedding(
        self,
        embedding: List[float],
        source_version: str,
        target_version: str
    ) -> List[float]:
        """
        Migrate embedding from one version to another.
        
        Args:
            embedding: Source embedding
            source_version: Source version
            target_version: Target version
            
        Returns:
            Migrated embedding
        """
        try:
            if source_version == target_version:
                return embedding
            
            # Check if direct migration is available
            migration_key = f"{source_version}->{target_version}"
            if hasattr(self, f"_migrate_{migration_key.replace('->', '_to_').replace('.', '_')}"):
                migration_func = getattr(self, f"_migrate_{migration_key.replace('->', '_to_').replace('.', '_')}")
                return migration_func(embedding)
            
            # Use general migration strategy
            migrated_embedding = await self._general_migration(
                embedding, source_version, target_version
            )
            
            logger.debug(f"Migrated embedding from {source_version} to {target_version}")
            return migrated_embedding
            
        except Exception as e:
            logger.error(f"Failed to migrate embedding: {e}")
            return embedding

    async def _general_migration(
        self,
        embedding: List[float],
        source_version: str,
        target_version: str
    ) -> List[float]:
        """
        General migration strategy using dimension adjustment.
        
        Args:
            embedding: Source embedding
            source_version: Source version
            target_version: Target version
            
        Returns:
            Migrated embedding
        """
        try:
            source_info = self.versions.get(source_version)
            target_info = self.versions.get(target_version)
            
            if not source_info or not target_info:
                logger.warning("Version information not available for migration")
                return embedding
            
            # Remove version metadata if present
            clean_embedding = self._remove_version_metadata(embedding)
            
            # Adjust dimensions if needed
            if source_info.dimensions != target_info.dimensions:
                clean_embedding = self._adjust_dimensions(
                    clean_embedding, source_info.dimensions, target_info.dimensions
                )
            
            # Add target version metadata
            migrated_embedding = self._add_version_metadata(clean_embedding, target_version)
            
            return migrated_embedding
            
        except Exception as e:
            logger.error(f"General migration failed: {e}")
            return embedding

    def _adjust_dimensions(
        self,
        embedding: List[float],
        source_dim: int,
        target_dim: int
    ) -> List[float]:
        """
        Adjust embedding dimensions.
        
        Args:
            embedding: Source embedding
            source_dim: Source dimensions
            target_dim: Target dimensions
            
        Returns:
            Dimension-adjusted embedding
        """
        if source_dim == target_dim:
            return embedding
        
        if source_dim > target_dim:
            # Downsample using PCA-like approach (simple truncation for now)
            return embedding[:target_dim]
        else:
            # Upsample using padding with zeros
            padded = embedding.copy()
            while len(padded) < target_dim:
                padded.append(0.0)
            return padded[:target_dim]

    def _add_version_metadata(self, embedding: List[float], version: str) -> List[float]:
        """
        Add version metadata to embedding.
        
        Args:
            embedding: Base embedding
            version: Version string
            
        Returns:
            Embedding with version metadata
        """
        # For simplicity, we'll encode version as a hash and append it
        version_hash = hashlib.sha256(version.encode()).hexdigest()
        version_float = int(version_hash[:8], 16) / (16**8)  # Normalize to 0-1
        
        # Append version metadata (last element)
        versioned = embedding.copy()
        versioned.append(version_float)
        
        return versioned

    def _remove_version_metadata(self, embedding: List[float]) -> List[float]:
        """
        Remove version metadata from embedding.
        
        Args:
            embedding: Embedding with metadata
            
        Returns:
            Clean embedding without metadata
        """
        # Remove last element (version metadata)
        if len(embedding) > 1536:  # Standard dimension + metadata
            return embedding[:-1]
        return embedding

    def register_legacy_adapter(self, version: str, adapter: BaseEmbeddingAdapter):
        """
        Register a legacy adapter for a specific version.
        
        Args:
            version: Version string
            adapter: Legacy adapter
        """
        self.legacy_adapters[version] = adapter
        
        # Register version info
        self.versions[version] = EmbeddingVersion(
            version=version,
            model_name="legacy",
            model_version=version,
            dimensions=1536,  # Assume standard dimension
            created_at=datetime.utcnow(),
            deprecated=True
        )
        
        logger.info(f"Registered legacy adapter for version {version}")

    def deprecate_version(self, version: str, migration_path: Optional[str] = None):
        """
        Mark a version as deprecated.
        
        Args:
            version: Version to deprecate
            migration_path: Recommended migration path
        """
        if version in self.versions:
            self.versions[version].deprecated = True
            self.versions[version].migration_path = migration_path
            logger.info(f"Deprecated version {version}")

    def get_available_versions(self) -> List[str]:
        """Get list of available versions."""
        return list(self.versions.keys())

    def get_version_info(self, version: str) -> Optional[EmbeddingVersion]:
        """Get information about a specific version."""
        return self.versions.get(version)

    async def get_model_info(self) -> Dict[str, Any]:
        """Get versioned model information."""
        base_info = await self.current_adapter.get_model_info()
        
        versioned_info = {
            "adapter_type": "versioned",
            "current_version": self.current_version,
            "available_versions": self.get_available_versions(),
            "migration_enabled": self.enable_migration,
            "version_details": {
                version: {
                    "model_name": info.model_name,
                    "dimensions": info.dimensions,
                    "deprecated": info.deprecated,
                    "migration_path": info.migration_path
                }
                for version, info in self.versions.items()
            },
            "base_adapter": base_info
        }
        
        return versioned_info

    async def health_check(self) -> bool:
        """Check health of versioned adapter."""
        try:
            # Check current adapter
            current_healthy = await self.current_adapter.health_check()
            
            # Check legacy adapters
            legacy_health = {}
            for version, adapter in self.legacy_adapters.items():
                try:
                    legacy_health[version] = await adapter.health_check()
                except Exception as e:
                    logger.warning(f"Legacy adapter {version} health check failed: {e}")
                    legacy_health[version] = False
            
            logger.debug(f"Versioned adapter health: current={current_healthy}, legacy={legacy_health}")
            return current_healthy
            
        except Exception as e:
            logger.error(f"Versioned adapter health check failed: {e}")
            return False

    def get_migration_plan(self, source_version: str, target_version: str) -> Dict[str, Any]:
        """
        Get migration plan between versions.
        
        Args:
            source_version: Source version
            target_version: Target version
            
        Returns:
            Migration plan details
        """
        plan = {
            "source_version": source_version,
            "target_version": target_version,
            "migration_available": True,
            "steps": [],
            "estimated_time": "immediate",
            "data_loss_risk": "low"
        }
        
        # Check if versions exist
        if source_version not in self.versions or target_version not in self.versions:
            plan["migration_available"] = False
            plan["error"] = "Version not found"
            return plan
        
        source_info = self.versions[source_version]
        target_info = self.versions[target_version]
        
        # Add migration steps
        if source_info.dimensions != target_info.dimensions:
            plan["steps"].append(f"Adjust dimensions from {source_info.dimensions} to {target_info.dimensions}")
            if source_info.dimensions > target_info.dimensions:
                plan["data_loss_risk"] = "medium"
        
        plan["steps"].append("Update version metadata")

        return plan

    # Implement abstract methods by delegating to current adapter
    async def get_model_name(self) -> str:
        """Get model name."""
        return await self.current_adapter.get_model_name()

    async def get_model_version(self) -> str:
        """Get model version."""
        return self.current_version

    async def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return await self.current_adapter.get_embedding_dimension()

    async def get_max_sequence_length(self) -> int:
        """Get maximum sequence length."""
        return await self.current_adapter.get_max_sequence_length()

    async def get_max_batch_size(self) -> int:
        """Get maximum batch size."""
        return await self.current_adapter.get_max_batch_size()

    async def validate_text(self, text: str) -> bool:
        """Validate text input."""
        return await self.current_adapter.validate_text(text)

    async def preprocess_text(self, text: str) -> str:
        """Preprocess text."""
        return await self.current_adapter.preprocess_text(text)

    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count."""
        return await self.current_adapter.estimate_tokens(text)

    async def warm_up(self) -> bool:
        """Warm up the model."""
        return await self.current_adapter.warm_up()
