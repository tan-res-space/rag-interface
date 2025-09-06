"""
PostgreSQL Database Adapter Implementation

This module contains the PostgreSQL implementation of the IDatabaseAdapter interface
using SQLAlchemy with async support.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    ErrorStatus,
    SeverityLevel,
    BucketType,
    AudioQuality,
    SpeakerClarity,
    BackgroundNoise,
    NumberOfSpeakers,
    EnhancedMetadata,
)
from error_reporting_service.infrastructure.adapters.database.abstract.database_adapter import (
    IDatabaseAdapter,
)

from .models import Base, ErrorReportModel


class PostgreSQLAdapter(IDatabaseAdapter):
    """
    PostgreSQL implementation of the database adapter.

    Uses SQLAlchemy with async support to provide database operations
    for the Error Reporting Service.
    """

    def __init__(self, connection_string: str):
        """
        Initialize the PostgreSQL adapter.

        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.engine = create_async_engine(
            connection_string,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
        )
        self._session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def save_error_report(self, error_report: ErrorReport) -> ErrorReport:
        """Save error report with enhanced metadata to PostgreSQL database"""
        async with self._session_factory() as session:
            model = ErrorReportModel(
                error_id=error_report.error_id,
                job_id=error_report.job_id,
                speaker_id=error_report.speaker_id,
                client_id=error_report.client_id,
                reported_by=error_report.reported_by,
                original_text=error_report.original_text,
                corrected_text=error_report.corrected_text,
                error_categories=error_report.error_categories,
                severity_level=error_report.severity_level.value,
                start_position=error_report.start_position,
                end_position=error_report.end_position,
                context_notes=error_report.context_notes,
                error_timestamp=error_report.error_timestamp,
                reported_at=error_report.reported_at,

                # Quality-based bucket management
                bucket_type=error_report.bucket_type.value,

                # Enhanced metadata fields
                audio_quality=error_report.enhanced_metadata.audio_quality.value,
                speaker_clarity=error_report.enhanced_metadata.speaker_clarity.value,
                background_noise=error_report.enhanced_metadata.background_noise.value,
                number_of_speakers=error_report.enhanced_metadata.number_of_speakers.value,
                overlapping_speech=error_report.enhanced_metadata.overlapping_speech,
                requires_specialized_knowledge=error_report.enhanced_metadata.requires_specialized_knowledge,
                additional_notes=error_report.enhanced_metadata.additional_notes,

                # System fields
                status=error_report.status.value,
                vector_db_id=error_report.vector_db_id,
                error_metadata=error_report.metadata,
            )

            session.add(model)
            await session.commit()
            await session.refresh(model)

            return self._model_to_entity(model)

    async def find_error_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find error report by ID in PostgreSQL database"""
        async with self._session_factory() as session:
            stmt = select(ErrorReportModel).where(ErrorReportModel.error_id == error_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            return self._model_to_entity(model) if model else None

    async def find_errors_by_speaker(
        self, speaker_id: UUID, filters: Optional[Dict] = None
    ) -> List[ErrorReport]:
        """Find all error reports for a speaker in PostgreSQL database"""
        async with self._session_factory() as session:
            stmt = select(ErrorReportModel).where(
                ErrorReportModel.speaker_id == speaker_id
            )

            # Apply filters if provided
            if filters:
                if "severity_level" in filters:
                    stmt = stmt.where(
                        ErrorReportModel.severity_level == filters["severity_level"]
                    )
                if "status" in filters:
                    stmt = stmt.where(ErrorReportModel.status == filters["status"])
                if "bucket_type" in filters:
                    stmt = stmt.where(ErrorReportModel.bucket_type == filters["bucket_type"])
                if "audio_quality" in filters:
                    stmt = stmt.where(ErrorReportModel.audio_quality == filters["audio_quality"])
                if "requires_specialized_knowledge" in filters:
                    stmt = stmt.where(
                        ErrorReportModel.requires_specialized_knowledge == filters["requires_specialized_knowledge"]
                    )
                if "overlapping_speech" in filters:
                    stmt = stmt.where(
                        ErrorReportModel.overlapping_speech == filters["overlapping_speech"]
                    )
                if "number_of_speakers" in filters:
                    stmt = stmt.where(
                        ErrorReportModel.number_of_speakers == filters["number_of_speakers"]
                    )
                if "categories" in filters:
                    # PostgreSQL JSONB contains operation
                    for category in filters["categories"]:
                        stmt = stmt.where(
                            ErrorReportModel.error_categories.contains([category])
                        )

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def find_errors_by_job(
        self, job_id: UUID, filters: Optional[Dict] = None
    ) -> List[ErrorReport]:
        """Find all error reports for a job in PostgreSQL database"""
        async with self._session_factory() as session:
            stmt = select(ErrorReportModel).where(ErrorReportModel.job_id == job_id)

            # Apply filters if provided
            if filters:
                if "severity_level" in filters:
                    stmt = stmt.where(
                        ErrorReportModel.severity_level == filters["severity_level"]
                    )
                if "status" in filters:
                    stmt = stmt.where(ErrorReportModel.status == filters["status"])

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def update_error_report(
        self, error_id: UUID, updates: Dict[str, Any]
    ) -> ErrorReport:
        """Update existing error report in PostgreSQL database"""
        async with self._session_factory() as session:
            stmt = (
                update(ErrorReportModel)
                .where(ErrorReportModel.error_id == error_id)
                .values(**updates)
                .returning(ErrorReportModel)
            )

            result = await session.execute(stmt)
            await session.commit()

            model = result.scalar_one()
            return self._model_to_entity(model)

    async def delete_error_report(self, error_id: UUID) -> bool:
        """Delete error report from PostgreSQL database"""
        async with self._session_factory() as session:
            stmt = delete(ErrorReportModel).where(ErrorReportModel.error_id == error_id)
            result = await session.execute(stmt)
            await session.commit()

            return result.rowcount > 0

    async def search_errors(self, query: Dict[str, Any]) -> List[ErrorReport]:
        """Search errors with complex criteria in PostgreSQL database"""
        async with self._session_factory() as session:
            stmt = select(ErrorReportModel)

            # Build dynamic query based on search criteria
            if "speaker_id" in query:
                stmt = stmt.where(
                    ErrorReportModel.speaker_id == UUID(query["speaker_id"])
                )
            if "job_id" in query:
                stmt = stmt.where(ErrorReportModel.job_id == UUID(query["job_id"]))
            if "severity_level" in query:
                stmt = stmt.where(
                    ErrorReportModel.severity_level == query["severity_level"]
                )
            if "status" in query:
                stmt = stmt.where(ErrorReportModel.status == query["status"])
            if "text_search" in query:
                # Full-text search on original and corrected text
                search_term = f"%{query['text_search']}%"
                stmt = stmt.where(
                    ErrorReportModel.original_text.ilike(search_term)
                    | ErrorReportModel.corrected_text.ilike(search_term)
                )

            # Add pagination if specified
            if "limit" in query:
                stmt = stmt.limit(query["limit"])
            if "offset" in query:
                stmt = stmt.offset(query["offset"])

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def begin_transaction(self) -> AsyncSession:
        """Begin PostgreSQL transaction"""
        session = self._session_factory()
        await session.begin()
        return session

    async def commit_transaction(self, transaction: AsyncSession) -> None:
        """Commit PostgreSQL transaction"""
        await transaction.commit()
        await transaction.close()

    async def rollback_transaction(self, transaction: AsyncSession) -> None:
        """Rollback PostgreSQL transaction"""
        await transaction.rollback()
        await transaction.close()

    async def health_check(self) -> bool:
        """Check PostgreSQL database health"""
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception:
            return False

    def get_connection_info(self) -> Dict[str, Any]:
        """Get PostgreSQL connection information"""
        return {
            "adapter_type": "postgresql",
            "connection_string": self.connection_string,
            "engine_info": {
                "pool_size": self.engine.pool.size(),
                "checked_in": self.engine.pool.checkedin(),
                "checked_out": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow(),
                "invalid": self.engine.pool.invalid(),
            },
        }

    def _model_to_entity(self, model: ErrorReportModel) -> ErrorReport:
        """Convert SQLAlchemy model to domain entity with enhanced metadata"""
        # Create enhanced metadata object
        enhanced_metadata = EnhancedMetadata(
            audio_quality=AudioQuality(model.audio_quality),
            speaker_clarity=SpeakerClarity(model.speaker_clarity),
            background_noise=BackgroundNoise(model.background_noise),
            number_of_speakers=NumberOfSpeakers(model.number_of_speakers),
            overlapping_speech=model.overlapping_speech,
            requires_specialized_knowledge=model.requires_specialized_knowledge,
            additional_notes=model.additional_notes,
        )

        return ErrorReport(
            error_id=model.error_id,
            job_id=model.job_id,
            speaker_id=model.speaker_id,
            client_id=model.client_id,
            reported_by=model.reported_by,
            original_text=model.original_text,
            corrected_text=model.corrected_text,
            error_categories=model.error_categories,
            severity_level=SeverityLevel(model.severity_level),
            start_position=model.start_position,
            end_position=model.end_position,
            context_notes=model.context_notes,
            error_timestamp=model.error_timestamp,
            reported_at=model.reported_at,
            bucket_type=BucketType(model.bucket_type),
            enhanced_metadata=enhanced_metadata,
            status=ErrorStatus(model.status),
            vector_db_id=model.vector_db_id,
            metadata=model.error_metadata or {},
        )

    async def create_tables(self) -> None:
        """Create database tables (for testing/setup)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop database tables (for testing/cleanup)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
