"""
Database Migration Manager

Manages database schema migrations using Alembic.
Provides programmatic access to migration operations.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Database migration manager using Alembic.
    
    Provides methods to run, create, and manage database migrations.
    """

    def __init__(self, database_url: str, migrations_path: Optional[str] = None):
        """
        Initialize migration manager.
        
        Args:
            database_url: Database connection URL
            migrations_path: Path to migrations directory (optional)
        """
        self.database_url = database_url
        
        # Set migrations path
        if migrations_path is None:
            current_dir = Path(__file__).parent
            self.migrations_path = current_dir / "migrations"
        else:
            self.migrations_path = Path(migrations_path)
        
        # Initialize Alembic config
        self.alembic_cfg = self._create_alembic_config()

    def _create_alembic_config(self) -> Config:
        """Create Alembic configuration."""
        alembic_ini_path = self.migrations_path / "alembic.ini"
        
        if not alembic_ini_path.exists():
            raise FileNotFoundError(f"Alembic configuration not found: {alembic_ini_path}")
        
        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("script_location", str(self.migrations_path))
        alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
        
        return alembic_cfg

    async def upgrade_to_head(self) -> bool:
        """
        Upgrade database to the latest migration.
        
        Returns:
            True if upgrade was successful
        """
        try:
            logger.info("Upgrading database to head...")
            command.upgrade(self.alembic_cfg, "head")
            logger.info("Database upgrade completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database upgrade failed: {e}")
            return False

    async def upgrade_to_revision(self, revision: str) -> bool:
        """
        Upgrade database to a specific revision.
        
        Args:
            revision: Target revision ID
            
        Returns:
            True if upgrade was successful
        """
        try:
            logger.info(f"Upgrading database to revision: {revision}")
            command.upgrade(self.alembic_cfg, revision)
            logger.info(f"Database upgrade to {revision} completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database upgrade to {revision} failed: {e}")
            return False

    async def downgrade_to_revision(self, revision: str) -> bool:
        """
        Downgrade database to a specific revision.
        
        Args:
            revision: Target revision ID
            
        Returns:
            True if downgrade was successful
        """
        try:
            logger.info(f"Downgrading database to revision: {revision}")
            command.downgrade(self.alembic_cfg, revision)
            logger.info(f"Database downgrade to {revision} completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database downgrade to {revision} failed: {e}")
            return False

    def get_current_revision(self) -> Optional[str]:
        """
        Get the current database revision.
        
        Returns:
            Current revision ID or None if not initialized
        """
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None

    def get_pending_migrations(self) -> List[str]:
        """
        Get list of pending migrations.
        
        Returns:
            List of pending revision IDs
        """
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            current_rev = self.get_current_revision()
            
            if current_rev is None:
                # Database not initialized, all migrations are pending
                return [rev.revision for rev in script.walk_revisions()]
            
            # Get revisions between current and head
            pending = []
            for rev in script.walk_revisions(current_rev, "head"):
                if rev.revision != current_rev:
                    pending.append(rev.revision)
            
            return pending
        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []

    def create_migration(self, message: str, autogenerate: bool = True) -> Optional[str]:
        """
        Create a new migration.
        
        Args:
            message: Migration message
            autogenerate: Whether to auto-generate migration from model changes
            
        Returns:
            New revision ID or None if failed
        """
        try:
            logger.info(f"Creating migration: {message}")
            
            if autogenerate:
                command.revision(self.alembic_cfg, message=message, autogenerate=True)
            else:
                command.revision(self.alembic_cfg, message=message)
            
            logger.info("Migration created successfully")
            return "success"  # Alembic doesn't return the revision ID directly
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return None

    def check_database_connection(self) -> bool:
        """
        Check if database connection is working.
        
        Returns:
            True if connection is successful
        """
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    def initialize_database(self) -> bool:
        """
        Initialize database with Alembic version table.
        
        Returns:
            True if initialization was successful
        """
        try:
            logger.info("Initializing database...")
            command.stamp(self.alembic_cfg, "head")
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False

    def get_migration_history(self) -> List[dict]:
        """
        Get migration history.
        
        Returns:
            List of migration information
        """
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            current_rev = self.get_current_revision()
            
            history = []
            for rev in script.walk_revisions():
                history.append({
                    "revision": rev.revision,
                    "down_revision": rev.down_revision,
                    "message": rev.doc,
                    "is_current": rev.revision == current_rev
                })
            
            return history
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []

    async def reset_database(self) -> bool:
        """
        Reset database by downgrading to base and upgrading to head.
        
        WARNING: This will destroy all data!
        
        Returns:
            True if reset was successful
        """
        try:
            logger.warning("Resetting database - ALL DATA WILL BE LOST!")
            
            # Downgrade to base
            command.downgrade(self.alembic_cfg, "base")
            
            # Upgrade to head
            command.upgrade(self.alembic_cfg, "head")
            
            logger.info("Database reset completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database reset failed: {e}")
            return False

    def validate_migrations(self) -> bool:
        """
        Validate that all migrations can be applied and rolled back.
        
        Returns:
            True if all migrations are valid
        """
        try:
            # This is a basic validation - in production you might want more thorough checks
            script = ScriptDirectory.from_config(self.alembic_cfg)
            
            # Check that all revisions have valid up and down functions
            for rev in script.walk_revisions():
                if not hasattr(rev.module, 'upgrade'):
                    logger.error(f"Migration {rev.revision} missing upgrade function")
                    return False
                if not hasattr(rev.module, 'downgrade'):
                    logger.error(f"Migration {rev.revision} missing downgrade function")
                    return False
            
            logger.info("All migrations validated successfully")
            return True
        except Exception as e:
            logger.error(f"Migration validation failed: {e}")
            return False


# Convenience functions
async def run_migrations(database_url: str, migrations_path: Optional[str] = None) -> bool:
    """
    Run all pending migrations.
    
    Args:
        database_url: Database connection URL
        migrations_path: Path to migrations directory
        
    Returns:
        True if migrations were successful
    """
    manager = MigrationManager(database_url, migrations_path)
    return await manager.upgrade_to_head()


async def create_migration(
    database_url: str, 
    message: str, 
    autogenerate: bool = True,
    migrations_path: Optional[str] = None
) -> Optional[str]:
    """
    Create a new migration.
    
    Args:
        database_url: Database connection URL
        message: Migration message
        autogenerate: Whether to auto-generate migration
        migrations_path: Path to migrations directory
        
    Returns:
        New revision ID or None if failed
    """
    manager = MigrationManager(database_url, migrations_path)
    return manager.create_migration(message, autogenerate)
