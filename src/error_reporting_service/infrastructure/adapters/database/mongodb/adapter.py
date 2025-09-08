"""
MongoDB Database Adapter

MongoDB implementation of the database repository interface.
Provides MongoDB-specific database operations for error reporting.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

try:
    import pymongo
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
    from pymongo.errors import ConnectionFailure, DuplicateKeyError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    # Create dummy classes for type hints
    AsyncIOMotorClient = None
    AsyncIOMotorDatabase = None

from error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository,
)
from error_reporting_service.domain.entities.error_report import ErrorReport

logger = logging.getLogger(__name__)


class MongoDBAdapter(ErrorReportRepository):
    """
    MongoDB adapter for error report storage.
    
    Implements the ErrorReportRepository interface using MongoDB.
    """

    def __init__(
        self,
        connection_string: str,
        database_name: str = "error_reporting",
        collection_name: str = "error_reports"
    ):
        """
        Initialize MongoDB adapter.

        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            collection_name: Name of the collection for error reports
        """
        if not MONGODB_AVAILABLE:
            raise RuntimeError("MongoDB dependencies not available. Install pymongo and motor packages.")

        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.collection = None

    async def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.database = self.client[self.database_name]
            self.collection = self.database[self.collection_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.database_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def _create_indexes(self):
        """Create necessary indexes for performance."""
        try:
            # Index on error_id for fast lookups
            await self.collection.create_index("error_id", unique=True)
            
            # Index on timestamp for time-based queries
            await self.collection.create_index("timestamp")
            
            # Index on severity for filtering
            await self.collection.create_index("severity")
            
            # Index on status for filtering
            await self.collection.create_index("status")
            
            # Compound index for common queries
            await self.collection.create_index([
                ("severity", pymongo.ASCENDING),
                ("timestamp", pymongo.DESCENDING)
            ])
            
            logger.debug("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")

    async def save(self, error_report: ErrorReport) -> bool:
        """Save an error report to MongoDB."""
        try:
            document = self._entity_to_document(error_report)
            
            # Use upsert to handle both insert and update
            result = await self.collection.replace_one(
                {"error_id": str(error_report.id)},
                document,
                upsert=True
            )
            
            success = result.acknowledged
            if success:
                logger.debug(f"Saved error report: {error_report.id}")
            
            return success
            
        except DuplicateKeyError:
            logger.warning(f"Duplicate error report ID: {error_report.id}")
            return False
        except Exception as e:
            logger.error(f"Failed to save error report {error_report.id}: {e}")
            return False

    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find an error report by ID."""
        try:
            document = await self.collection.find_one({"error_id": str(error_id)})
            
            if document:
                return self._document_to_entity(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find error report {error_id}: {e}")
            return None

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ErrorReport]:
        """Find all error reports with optional filtering."""
        try:
            query = {}
            
            # Apply filters
            if filters:
                if "severity" in filters:
                    query["severity"] = filters["severity"]
                if "status" in filters:
                    query["status"] = filters["status"]
                if "start_date" in filters:
                    query["timestamp"] = {"$gte": filters["start_date"]}
                if "end_date" in filters:
                    if "timestamp" not in query:
                        query["timestamp"] = {}
                    query["timestamp"]["$lte"] = filters["end_date"]
            
            # Execute query with pagination
            cursor = self.collection.find(query).skip(offset).limit(limit)
            
            # Sort by timestamp (newest first)
            cursor = cursor.sort("timestamp", pymongo.DESCENDING)
            
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Failed to find error reports: {e}")
            return []

    async def delete_by_id(self, error_id: UUID) -> bool:
        """Delete an error report by ID."""
        try:
            result = await self.collection.delete_one({"error_id": str(error_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.debug(f"Deleted error report: {error_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete error report {error_id}: {e}")
            return False

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count error reports with optional filtering."""
        try:
            query = {}
            
            # Apply filters (same logic as find_all)
            if filters:
                if "severity" in filters:
                    query["severity"] = filters["severity"]
                if "status" in filters:
                    query["status"] = filters["status"]
                if "start_date" in filters:
                    query["timestamp"] = {"$gte": filters["start_date"]}
                if "end_date" in filters:
                    if "timestamp" not in query:
                        query["timestamp"] = {}
                    query["timestamp"]["$lte"] = filters["end_date"]
            
            return await self.collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Failed to count error reports: {e}")
            return 0

    async def health_check(self) -> bool:
        """Check if MongoDB connection is healthy."""
        try:
            if not self.client:
                return False
            
            # Ping the database
            await self.client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False

    def _entity_to_document(self, error_report: ErrorReport) -> Dict[str, Any]:
        """Convert ErrorReport entity to MongoDB document."""
        return {
            "error_id": str(error_report.id),
            "timestamp": error_report.timestamp,
            "severity": error_report.severity.value if error_report.severity else None,
            "message": error_report.message,
            "details": error_report.details,
            "source": error_report.source,
            "user_id": str(error_report.user_id) if error_report.user_id else None,
            "session_id": error_report.session_id,
            "status": error_report.status.value if error_report.status else None,
            "tags": error_report.tags,
            "metadata": error_report.metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    def _document_to_entity(self, document: Dict[str, Any]) -> ErrorReport:
        """Convert MongoDB document to ErrorReport entity."""
        from error_reporting_service.domain.value_objects.error_severity import ErrorSeverity
        from error_reporting_service.domain.value_objects.error_status import ErrorStatus
        
        return ErrorReport(
            id=UUID(document["error_id"]),
            timestamp=document["timestamp"],
            severity=ErrorSeverity(document["severity"]) if document.get("severity") else None,
            message=document["message"],
            details=document.get("details"),
            source=document.get("source"),
            user_id=UUID(document["user_id"]) if document.get("user_id") else None,
            session_id=document.get("session_id"),
            status=ErrorStatus(document["status"]) if document.get("status") else None,
            tags=document.get("tags", []),
            metadata=document.get("metadata", {})
        )

    async def close(self):
        """Close the adapter and clean up resources."""
        await self.disconnect()
