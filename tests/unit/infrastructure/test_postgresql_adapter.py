"""
Unit tests for PostgreSQL Database Adapter.

Following TDD principles - tests define the expected behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    ErrorStatus,
    SeverityLevel,
)
from src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter import (
    PostgreSQLAdapter,
)


class TestPostgreSQLAdapter:
    """Test suite for PostgreSQL database adapter"""

    def setup_method(self):
        """Set up test fixtures"""
        self.connection_string = "postgresql+asyncpg://test:test@localhost:5432/test_db"

        # Mock the SQLAlchemy engine and session
        with patch(
            "src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter.create_async_engine"
        ):
            with patch(
                "src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter.async_sessionmaker"
            ):
                self.adapter = PostgreSQLAdapter(self.connection_string)

    @pytest.mark.asyncio
    async def test_save_error_report_success(self):
        """Test successful error report save operation"""
        # Arrange
        error_report = self._create_test_error_report()

        # Mock session and model
        mock_session = AsyncMock()
        mock_model = Mock()

        # Mock the async context manager
        mock_session_factory = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__.return_value = None

        with patch.object(self.adapter, "_session_factory", mock_session_factory):
            with patch(
                "src.error_reporting_service.infrastructure.adapters.database.postgresql.models.ErrorReportModel",
                return_value=mock_model,
            ):
                with patch.object(
                    self.adapter, "_model_to_entity", return_value=error_report
                ):

                    # Act
                    result = await self.adapter.save_error_report(error_report)

                    # Assert
                    assert result == error_report
                    mock_session.add.assert_called_once_with(mock_model)
                    mock_session.commit.assert_called_once()
                    mock_session.refresh.assert_called_once_with(mock_model)

    @pytest.mark.asyncio
    async def test_find_error_by_id_found(self):
        """Test finding error report by ID when it exists"""
        # Arrange
        error_id = uuid4()
        error_report = self._create_test_error_report(error_id=error_id)

        # Mock session and query result
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_model = Mock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        with patch.object(self.adapter, "_session_factory", return_value=mock_session):
            with patch.object(
                self.adapter, "_model_to_entity", return_value=error_report
            ):

                # Act
                result = await self.adapter.find_error_by_id(error_id)

                # Assert
                assert result == error_report
                mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_error_by_id_not_found(self):
        """Test finding error report by ID when it doesn't exist"""
        # Arrange
        error_id = uuid4()

        # Mock session and query result
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with patch.object(self.adapter, "_session_factory", return_value=mock_session):

            # Act
            result = await self.adapter.find_error_by_id(error_id)

            # Assert
            assert result is None
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_errors_by_speaker(self):
        """Test finding error reports by speaker ID"""
        # Arrange
        speaker_id = uuid4()
        error_reports = [
            self._create_test_error_report(speaker_id=speaker_id),
            self._create_test_error_report(speaker_id=speaker_id),
        ]

        # Mock session and query result
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_models = [Mock(), Mock()]
        mock_result.scalars.return_value.all.return_value = mock_models
        mock_session.execute.return_value = mock_result

        with patch.object(self.adapter, "_session_factory", return_value=mock_session):
            with patch.object(
                self.adapter, "_model_to_entity", side_effect=error_reports
            ):

                # Act
                result = await self.adapter.find_errors_by_speaker(speaker_id)

                # Assert
                assert len(result) == 2
                assert result == error_reports
                mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        # Arrange
        mock_session = AsyncMock()

        with patch.object(self.adapter, "_session_factory", return_value=mock_session):

            # Act
            result = await self.adapter.health_check()

            # Assert
            assert result is True
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure"""
        # Arrange
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database connection failed")

        with patch.object(self.adapter, "_session_factory", return_value=mock_session):

            # Act
            result = await self.adapter.health_check()

            # Assert
            assert result is False

    @pytest.mark.asyncio
    async def test_begin_transaction(self):
        """Test beginning a transaction"""
        # Arrange
        mock_session = AsyncMock()

        with patch.object(self.adapter, "_session_factory", return_value=mock_session):

            # Act
            result = await self.adapter.begin_transaction()

            # Assert
            assert result == mock_session
            mock_session.begin.assert_called_once()

    @pytest.mark.asyncio
    async def test_commit_transaction(self):
        """Test committing a transaction"""
        # Arrange
        mock_transaction = AsyncMock()

        # Act
        await self.adapter.commit_transaction(mock_transaction)

        # Assert
        mock_transaction.commit.assert_called_once()
        mock_transaction.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_rollback_transaction(self):
        """Test rolling back a transaction"""
        # Arrange
        mock_transaction = AsyncMock()

        # Act
        await self.adapter.rollback_transaction(mock_transaction)

        # Assert
        mock_transaction.rollback.assert_called_once()
        mock_transaction.close.assert_called_once()

    def test_get_connection_info(self):
        """Test getting connection information"""
        # Act
        result = self.adapter.get_connection_info()

        # Assert
        assert isinstance(result, dict)
        assert "adapter_type" in result
        assert result["adapter_type"] == "postgresql"
        assert "connection_string" in result

    def _create_test_error_report(self, error_id=None, speaker_id=None) -> ErrorReport:
        """Helper method to create test error reports"""
        return ErrorReport(
            error_id=error_id or uuid4(),
            job_id=uuid4(),
            speaker_id=speaker_id or uuid4(),
            reported_by=uuid4(),
            original_text="test error",
            corrected_text="test correction",
            error_categories=["grammar"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=10,
            error_timestamp=datetime.now(),
            reported_at=datetime.now(),
        )
