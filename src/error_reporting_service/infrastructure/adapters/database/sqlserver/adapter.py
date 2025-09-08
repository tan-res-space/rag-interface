"""
SQL Server Database Adapter

SQL Server implementation of the database repository interface.
Provides SQL Server-specific database operations for error reporting.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

try:
    import aioodbc
    from aioodbc import Connection, Cursor
    SQLSERVER_AVAILABLE = True
except ImportError:
    SQLSERVER_AVAILABLE = False
    # Create dummy classes for type hints
    Connection = None
    Cursor = None

from error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository,
)
from error_reporting_service.domain.entities.error_report import ErrorReport

logger = logging.getLogger(__name__)


class SQLServerAdapter(ErrorReportRepository):
    """
    SQL Server adapter for error report storage.
    
    Implements the ErrorReportRepository interface using SQL Server.
    """

    def __init__(
        self,
        connection_string: str,
        table_name: str = "error_reports"
    ):
        """
        Initialize SQL Server adapter.

        Args:
            connection_string: SQL Server connection string
            table_name: Name of the table for error reports
        """
        if not SQLSERVER_AVAILABLE:
            raise RuntimeError("SQL Server dependencies not available. Install aioodbc package.")

        self.connection_string = connection_string
        self.table_name = table_name
        self.connection: Optional[Connection] = None

    async def connect(self):
        """Establish connection to SQL Server."""
        try:
            self.connection = await aioodbc.connect(dsn=self.connection_string)
            logger.info("Connected to SQL Server")
            
            # Create table if it doesn't exist
            await self._create_table()
            
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            raise

    async def disconnect(self):
        """Close SQL Server connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from SQL Server")

    async def _create_table(self):
        """Create error reports table if it doesn't exist."""
        try:
            create_table_sql = f"""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.table_name}' AND xtype='U')
            CREATE TABLE {self.table_name} (
                error_id UNIQUEIDENTIFIER PRIMARY KEY,
                timestamp DATETIME2 NOT NULL,
                severity NVARCHAR(50),
                message NVARCHAR(MAX) NOT NULL,
                details NVARCHAR(MAX),
                source NVARCHAR(255),
                user_id UNIQUEIDENTIFIER,
                session_id NVARCHAR(255),
                status NVARCHAR(50),
                tags NVARCHAR(MAX),
                metadata NVARCHAR(MAX),
                created_at DATETIME2 DEFAULT GETUTCDATE(),
                updated_at DATETIME2 DEFAULT GETUTCDATE()
            )
            """
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(create_table_sql)
                await self.connection.commit()
            
            # Create indexes
            await self._create_indexes()
            
            logger.debug("SQL Server table and indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create table: {e}")

    async def _create_indexes(self):
        """Create necessary indexes for performance."""
        try:
            indexes = [
                f"CREATE INDEX IF NOT EXISTS IX_{self.table_name}_timestamp ON {self.table_name} (timestamp DESC)",
                f"CREATE INDEX IF NOT EXISTS IX_{self.table_name}_severity ON {self.table_name} (severity)",
                f"CREATE INDEX IF NOT EXISTS IX_{self.table_name}_status ON {self.table_name} (status)",
                f"CREATE INDEX IF NOT EXISTS IX_{self.table_name}_user_id ON {self.table_name} (user_id)",
            ]
            
            async with self.connection.cursor() as cursor:
                for index_sql in indexes:
                    try:
                        await cursor.execute(index_sql)
                    except Exception as e:
                        # Index might already exist, continue
                        logger.debug(f"Index creation skipped: {e}")
                
                await self.connection.commit()
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")

    async def save(self, error_report: ErrorReport) -> bool:
        """Save an error report to SQL Server."""
        try:
            # Use MERGE for upsert operation
            merge_sql = f"""
            MERGE {self.table_name} AS target
            USING (SELECT ? AS error_id) AS source
            ON target.error_id = source.error_id
            WHEN MATCHED THEN
                UPDATE SET
                    timestamp = ?,
                    severity = ?,
                    message = ?,
                    details = ?,
                    source = ?,
                    user_id = ?,
                    session_id = ?,
                    status = ?,
                    tags = ?,
                    metadata = ?,
                    updated_at = GETUTCDATE()
            WHEN NOT MATCHED THEN
                INSERT (error_id, timestamp, severity, message, details, source, 
                       user_id, session_id, status, tags, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE());
            """
            
            params = [
                str(error_report.id),  # For MERGE condition
                error_report.timestamp,
                error_report.severity.value if error_report.severity else None,
                error_report.message,
                error_report.details,
                error_report.source,
                str(error_report.user_id) if error_report.user_id else None,
                error_report.session_id,
                error_report.status.value if error_report.status else None,
                ",".join(error_report.tags) if error_report.tags else None,
                str(error_report.metadata) if error_report.metadata else None,
                # Repeat for INSERT clause
                str(error_report.id),
                error_report.timestamp,
                error_report.severity.value if error_report.severity else None,
                error_report.message,
                error_report.details,
                error_report.source,
                str(error_report.user_id) if error_report.user_id else None,
                error_report.session_id,
                error_report.status.value if error_report.status else None,
                ",".join(error_report.tags) if error_report.tags else None,
                str(error_report.metadata) if error_report.metadata else None,
            ]
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(merge_sql, params)
                await self.connection.commit()
            
            logger.debug(f"Saved error report: {error_report.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save error report {error_report.id}: {e}")
            return False

    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find an error report by ID."""
        try:
            select_sql = f"""
            SELECT error_id, timestamp, severity, message, details, source,
                   user_id, session_id, status, tags, metadata
            FROM {self.table_name}
            WHERE error_id = ?
            """
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(select_sql, [str(error_id)])
                row = await cursor.fetchone()
                
                if row:
                    return self._row_to_entity(row)
                
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
            where_clauses = []
            params = []
            
            # Apply filters
            if filters:
                if "severity" in filters:
                    where_clauses.append("severity = ?")
                    params.append(filters["severity"])
                if "status" in filters:
                    where_clauses.append("status = ?")
                    params.append(filters["status"])
                if "start_date" in filters:
                    where_clauses.append("timestamp >= ?")
                    params.append(filters["start_date"])
                if "end_date" in filters:
                    where_clauses.append("timestamp <= ?")
                    params.append(filters["end_date"])
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            select_sql = f"""
            SELECT error_id, timestamp, severity, message, details, source,
                   user_id, session_id, status, tags, metadata
            FROM {self.table_name}
            {where_clause}
            ORDER BY timestamp DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            
            params.extend([offset, limit])
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(select_sql, params)
                rows = await cursor.fetchall()
                
                return [self._row_to_entity(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to find error reports: {e}")
            return []

    async def delete_by_id(self, error_id: UUID) -> bool:
        """Delete an error report by ID."""
        try:
            delete_sql = f"DELETE FROM {self.table_name} WHERE error_id = ?"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(delete_sql, [str(error_id)])
                await self.connection.commit()
                
                success = cursor.rowcount > 0
                if success:
                    logger.debug(f"Deleted error report: {error_id}")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to delete error report {error_id}: {e}")
            return False

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count error reports with optional filtering."""
        try:
            where_clauses = []
            params = []
            
            # Apply filters (same logic as find_all)
            if filters:
                if "severity" in filters:
                    where_clauses.append("severity = ?")
                    params.append(filters["severity"])
                if "status" in filters:
                    where_clauses.append("status = ?")
                    params.append(filters["status"])
                if "start_date" in filters:
                    where_clauses.append("timestamp >= ?")
                    params.append(filters["start_date"])
                if "end_date" in filters:
                    where_clauses.append("timestamp <= ?")
                    params.append(filters["end_date"])
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            count_sql = f"SELECT COUNT(*) FROM {self.table_name} {where_clause}"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(count_sql, params)
                row = await cursor.fetchone()
                
                return row[0] if row else 0
                
        except Exception as e:
            logger.error(f"Failed to count error reports: {e}")
            return 0

    async def health_check(self) -> bool:
        """Check if SQL Server connection is healthy."""
        try:
            if not self.connection:
                return False
            
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                await cursor.fetchone()
                
            return True
            
        except Exception as e:
            logger.error(f"SQL Server health check failed: {e}")
            return False

    def _row_to_entity(self, row) -> ErrorReport:
        """Convert database row to ErrorReport entity."""
        from error_reporting_service.domain.value_objects.error_severity import ErrorSeverity
        from error_reporting_service.domain.value_objects.error_status import ErrorStatus
        
        return ErrorReport(
            id=UUID(row[0]),
            timestamp=row[1],
            severity=ErrorSeverity(row[2]) if row[2] else None,
            message=row[3],
            details=row[4],
            source=row[5],
            user_id=UUID(row[6]) if row[6] else None,
            session_id=row[7],
            status=ErrorStatus(row[8]) if row[8] else None,
            tags=row[9].split(",") if row[9] else [],
            metadata=eval(row[10]) if row[10] else {}  # Note: In production, use proper JSON parsing
        )

    async def close(self):
        """Close the adapter and clean up resources."""
        await self.disconnect()
