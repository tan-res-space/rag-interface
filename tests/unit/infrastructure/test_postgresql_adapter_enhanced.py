"""
Enhanced unit tests for PostgreSQL adapter to improve coverage.

These tests focus on testing the PostgreSQL adapter implementation
to increase infrastructure layer test coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter import (
    PostgreSQLAdapter,
)
from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    ErrorStatus,
    SeverityLevel,
)


class TestPostgreSQLAdapterEnhanced:
    """Enhanced tests for PostgreSQL adapter to improve coverage."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def adapter(self, mock_session):
        """Create adapter instance with mocked session factory."""
        with patch('src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter.create_async_engine'), \
             patch('src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter.async_sessionmaker') as mock_sessionmaker:

            # Mock the session factory to return our mock session
            mock_sessionmaker.return_value = lambda: mock_session

            adapter = PostgreSQLAdapter("postgresql://test:test@localhost/test")
            adapter._session_factory = lambda: mock_session
            return adapter

    @pytest.fixture
    def sample_error_report(self):
        """Create a sample error report for testing."""
        return ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="This is the original text with an error.",
            corrected_text="This is the corrected text without error.",
            error_categories=["grammar"],
            severity_level=SeverityLevel.MEDIUM,
            start_position=25,
            end_position=30,
            error_timestamp=datetime.now(),
            reported_at=datetime.now(),
            status=ErrorStatus.PENDING,
            metadata={"confidence": 0.85}
        )

    @pytest.mark.asyncio
    async def test_save_success(self, adapter, mock_session, sample_error_report):
        """Test successful save operation."""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await adapter.save_error_report(sample_error_report)

        # Assert
        assert result == sample_error_report
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_database_error(self, adapter, mock_session, sample_error_report):
        """Test save operation with database error."""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=SQLAlchemyError("Database error"))
        mock_session.rollback = AsyncMock()

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await adapter.save_error_report(sample_error_report)

        assert "Database error" in str(exc_info.value)
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_id_success(self, adapter, mock_session):
        """Test successful find by ID operation."""
        # Arrange
        error_id = uuid4()
        # Create a mock model with proper attributes
        mock_model = MagicMock()
        mock_model.error_id = error_id
        mock_model.job_id = uuid4()
        mock_model.speaker_id = uuid4()
        mock_model.original_text = "Original text"
        mock_model.corrected_text = "Corrected text"
        mock_model.start_position = 0
        mock_model.end_position = 5
        mock_model.severity_level = "medium"
        mock_model.error_categories = ["grammar"]
        mock_model.reported_by = uuid4()
        mock_model.error_timestamp = datetime.now()
        mock_model.reported_at = datetime.now()
        mock_model.status = "pending"
        mock_model.error_metadata = {}

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await adapter.find_error_by_id(error_id)

        # Assert
        assert result is not None
        assert result.error_id == error_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, adapter, mock_session):
        """Test find by ID when record not found."""
        # Arrange
        error_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await adapter.find_error_by_id(error_id)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_speaker_success(self, adapter, mock_session):
        """Test successful find by speaker operation."""
        # Arrange
        speaker_id = uuid4()
        mock_model = MagicMock()
        mock_model.error_id = uuid4()
        mock_model.job_id = uuid4()
        mock_model.speaker_id = speaker_id
        mock_model.original_text = "Text 1"
        mock_model.corrected_text = "Corrected 1"
        mock_model.start_position = 0
        mock_model.end_position = 5
        mock_model.severity_level = "high"
        mock_model.error_categories = ["grammar"]
        mock_model.reported_by = uuid4()
        mock_model.error_timestamp = datetime.now()
        mock_model.reported_at = datetime.now()
        mock_model.status = "pending"
        mock_model.error_metadata = {}

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        results = await adapter.find_errors_by_speaker(speaker_id)

        # Assert
        assert len(results) == 1
        assert results[0].speaker_id == speaker_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_success(self, adapter, mock_session):
        """Test successful delete operation."""
        # Arrange
        error_id = uuid4()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        # Act
        result = await adapter.delete_error_report(error_id)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_success(self, adapter, mock_session):
        """Test successful health check operation."""
        # Arrange
        mock_session.execute = AsyncMock()

        # Act
        result = await adapter.health_check()

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
