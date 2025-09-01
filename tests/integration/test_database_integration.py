"""
Integration tests for database operations.

These tests verify the integration between the application and PostgreSQL database,
including repository implementations, transactions, and data consistency.
Following TDD principles and Hexagonal Architecture patterns.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    ErrorStatus,
    SeverityLevel,
)
from src.error_reporting_service.infrastructure.adapters.database.postgresql.models import (
    Base,
    ErrorReportModel,
)
from src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter import (
    PostgreSQLAdapter,
)
from tests.factories import ErrorReportFactory, create_error_reports_batch


@pytest.mark.integration
@pytest.mark.database
class TestPostgreSQLIntegration:
    """Integration tests for PostgreSQL database operations"""

    @pytest.fixture(scope="class")
    async def test_engine(self):
        """Create test database engine"""
        # Use in-memory SQLite for fast integration tests
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        # Cleanup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    @pytest.fixture
    async def test_session(self, test_engine):
        """Create test database session"""
        async_session = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            yield session
            await session.rollback()

    @pytest.fixture
    def repository(self, test_session):
        """Create repository instance"""
        return PostgreSQLAdapter(test_session)

    @pytest.mark.asyncio
    async def test_save_error_report_success(self, repository):
        """Test successful saving of error report to database"""
        # Arrange
        error_report = ErrorReportFactory.create()

        # Act
        saved_report = await repository.save(error_report)

        # Assert
        assert saved_report is not None
        assert saved_report.error_id == error_report.error_id
        assert saved_report.original_text == error_report.original_text
        assert saved_report.corrected_text == error_report.corrected_text
        assert saved_report.severity_level == error_report.severity_level

    @pytest.mark.asyncio
    async def test_find_by_id_existing_report(self, repository):
        """Test finding existing error report by ID"""
        # Arrange
        error_report = ErrorReportFactory.create()
        saved_report = await repository.save(error_report)

        # Act
        found_report = await repository.find_by_id(saved_report.error_id)

        # Assert
        assert found_report is not None
        assert found_report.error_id == saved_report.error_id
        assert found_report.original_text == saved_report.original_text
        assert found_report.corrected_text == saved_report.corrected_text

    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent_report(self, repository):
        """Test finding non-existent error report by ID"""
        # Arrange
        nonexistent_id = uuid4()

        # Act
        found_report = await repository.find_by_id(nonexistent_id)

        # Assert
        assert found_report is None

    @pytest.mark.asyncio
    async def test_find_by_job_id_multiple_reports(self, repository):
        """Test finding multiple error reports by job ID"""
        # Arrange
        job_id = uuid4()
        error_reports = [ErrorReportFactory.create(job_id=job_id) for _ in range(3)]

        # Save all reports
        for report in error_reports:
            await repository.save(report)

        # Act
        found_reports = await repository.find_by_job_id(str(job_id))

        # Assert
        assert len(found_reports) == 3
        for report in found_reports:
            assert report.job_id == job_id

    @pytest.mark.asyncio
    async def test_find_by_speaker_id_with_pagination(self, repository):
        """Test finding error reports by speaker ID with pagination"""
        # Arrange
        speaker_id = uuid4()
        error_reports = [
            ErrorReportFactory.create(speaker_id=speaker_id) for _ in range(5)
        ]

        # Save all reports
        for report in error_reports:
            await repository.save(report)

        # Act - Get first page (2 items)
        page_1 = await repository.find_by_speaker_id(str(speaker_id), limit=2, offset=0)

        # Act - Get second page (2 items)
        page_2 = await repository.find_by_speaker_id(str(speaker_id), limit=2, offset=2)

        # Assert
        assert len(page_1) == 2
        assert len(page_2) == 2

        # Verify no overlap between pages
        page_1_ids = {report.error_id for report in page_1}
        page_2_ids = {report.error_id for report in page_2}
        assert page_1_ids.isdisjoint(page_2_ids)

    @pytest.mark.asyncio
    async def test_search_with_filters_severity(self, repository):
        """Test searching error reports with severity filter"""
        # Arrange
        high_severity_reports = [
            ErrorReportFactory.create(severity_level=SeverityLevel.HIGH)
            for _ in range(2)
        ]
        low_severity_reports = [
            ErrorReportFactory.create(severity_level=SeverityLevel.LOW)
            for _ in range(3)
        ]

        # Save all reports
        for report in high_severity_reports + low_severity_reports:
            await repository.save(report)

        # Act
        filters = {"severity_level": "high"}
        found_reports = await repository.search(filters)

        # Assert
        assert len(found_reports) == 2
        for report in found_reports:
            assert report.severity_level == SeverityLevel.HIGH

    @pytest.mark.asyncio
    async def test_search_with_filters_categories(self, repository):
        """Test searching error reports with category filter"""
        # Arrange
        medical_reports = [
            ErrorReportFactory.create(error_categories=["medical_terminology"])
            for _ in range(2)
        ]
        grammar_reports = [
            ErrorReportFactory.create(error_categories=["grammar"]) for _ in range(3)
        ]

        # Save all reports
        for report in medical_reports + grammar_reports:
            await repository.save(report)

        # Act
        filters = {"categories": ["medical_terminology"]}
        found_reports = await repository.search(filters)

        # Assert
        assert len(found_reports) == 2
        for report in found_reports:
            assert "medical_terminology" in report.error_categories

    @pytest.mark.asyncio
    async def test_search_with_date_range_filter(self, repository):
        """Test searching error reports with date range filter"""
        # Arrange
        base_date = datetime.utcnow()
        old_reports = [
            ErrorReportFactory.create(error_timestamp=base_date - timedelta(days=10))
            for _ in range(2)
        ]
        recent_reports = [
            ErrorReportFactory.create(error_timestamp=base_date - timedelta(days=2))
            for _ in range(3)
        ]

        # Save all reports
        for report in old_reports + recent_reports:
            await repository.save(report)

        # Act
        filters = {"date_from": base_date - timedelta(days=5), "date_to": base_date}
        found_reports = await repository.search(filters)

        # Assert
        assert len(found_reports) == 3
        for report in found_reports:
            assert report.error_timestamp >= filters["date_from"]
            assert report.error_timestamp <= filters["date_to"]

    @pytest.mark.asyncio
    async def test_update_error_report_success(self, repository):
        """Test successful update of error report"""
        # Arrange
        error_report = ErrorReportFactory.create(
            status=ErrorStatus.PENDING, context_notes="Original notes"
        )
        saved_report = await repository.save(error_report)

        # Modify the report
        updated_report = ErrorReport(
            error_id=saved_report.error_id,
            job_id=saved_report.job_id,
            speaker_id=saved_report.speaker_id,
            reported_by=saved_report.reported_by,
            original_text=saved_report.original_text,
            corrected_text=saved_report.corrected_text,
            error_categories=saved_report.error_categories,
            severity_level=saved_report.severity_level,
            start_position=saved_report.start_position,
            end_position=saved_report.end_position,
            context_notes="Updated notes",  # Changed
            error_timestamp=saved_report.error_timestamp,
            reported_at=saved_report.reported_at,
            status=ErrorStatus.PROCESSED,  # Changed
            metadata=saved_report.metadata,
        )

        # Act
        result = await repository.update(updated_report)

        # Assert
        assert result is not None
        assert result.status == ErrorStatus.PROCESSED
        assert result.context_notes == "Updated notes"

        # Verify in database
        found_report = await repository.find_by_id(saved_report.error_id)
        assert found_report.status == ErrorStatus.PROCESSED
        assert found_report.context_notes == "Updated notes"

    @pytest.mark.asyncio
    async def test_delete_error_report_success(self, repository):
        """Test successful deletion of error report"""
        # Arrange
        error_report = ErrorReportFactory.create()
        saved_report = await repository.save(error_report)

        # Verify report exists
        found_report = await repository.find_by_id(saved_report.error_id)
        assert found_report is not None

        # Act
        result = await repository.delete(saved_report.error_id)

        # Assert
        assert result is True

        # Verify report is deleted
        found_report = await repository.find_by_id(saved_report.error_id)
        assert found_report is None

    @pytest.mark.asyncio
    async def test_count_by_filters_accuracy(self, repository):
        """Test accuracy of count_by_filters method"""
        # Arrange
        high_severity_reports = [
            ErrorReportFactory.create(severity_level=SeverityLevel.HIGH)
            for _ in range(3)
        ]
        low_severity_reports = [
            ErrorReportFactory.create(severity_level=SeverityLevel.LOW)
            for _ in range(5)
        ]

        # Save all reports
        for report in high_severity_reports + low_severity_reports:
            await repository.save(report)

        # Act
        high_count = await repository.count_by_filters({"severity_level": "high"})
        low_count = await repository.count_by_filters({"severity_level": "low"})
        total_count = await repository.count_by_filters({})

        # Assert
        assert high_count == 3
        assert low_count == 5
        assert total_count == 8

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, repository, test_session):
        """Test transaction rollback on database error"""
        # Arrange
        error_report = ErrorReportFactory.create()

        # Act & Assert
        try:
            async with test_session.begin():
                await repository.save(error_report)
                # Simulate an error that causes rollback
                raise Exception("Simulated error")
        except Exception:
            pass

        # Verify report was not saved due to rollback
        found_report = await repository.find_by_id(error_report.error_id)
        assert found_report is None

    @pytest.mark.asyncio
    async def test_concurrent_access_handling(self, repository):
        """Test handling of concurrent access to same error report"""
        # Arrange
        error_report = ErrorReportFactory.create()
        saved_report = await repository.save(error_report)

        # Act - Simulate concurrent updates
        async def update_context_notes(notes):
            updated_report = ErrorReport(
                error_id=saved_report.error_id,
                job_id=saved_report.job_id,
                speaker_id=saved_report.speaker_id,
                reported_by=saved_report.reported_by,
                original_text=saved_report.original_text,
                corrected_text=saved_report.corrected_text,
                error_categories=saved_report.error_categories,
                severity_level=saved_report.severity_level,
                start_position=saved_report.start_position,
                end_position=saved_report.end_position,
                context_notes=notes,
                error_timestamp=saved_report.error_timestamp,
                reported_at=saved_report.reported_at,
                status=saved_report.status,
                metadata=saved_report.metadata,
            )
            return await repository.update(updated_report)

        # Execute concurrent updates
        results = await asyncio.gather(
            update_context_notes("Update 1"),
            update_context_notes("Update 2"),
            return_exceptions=True,
        )

        # Assert - At least one update should succeed
        successful_updates = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_updates) >= 1
