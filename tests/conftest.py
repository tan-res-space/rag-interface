"""
Global test configuration and fixtures for Error Reporting Service.

This module provides shared fixtures and configuration for all tests,
following TDD principles and the design specification requirements.
"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, Generator
from unittest.mock import AsyncMock, Mock

import pytest

# Test database imports
import sqlalchemy as sa

# FastAPI testing imports
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    ErrorStatus,
    SeverityLevel,
)
from src.error_reporting_service.infrastructure.adapters.database.postgresql.models import (
    Base,
)
from src.error_reporting_service.infrastructure.config.settings import Settings

# Application imports
from src.error_reporting_service.main import app

# Test Configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_REDIS_URL = "redis://localhost:6379/15"  # Use test database
TEST_KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
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
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings configuration."""
    return Settings(
        app_name="Error Reporting Service - Test",
        debug=True,
        log_level="DEBUG",
        database={"url": TEST_DATABASE_URL},
        redis={"url": TEST_REDIS_URL},
        kafka={"bootstrap_servers": TEST_KAFKA_BOOTSTRAP_SERVERS},
        secret_key="test-secret-key",
        access_token_expire_minutes=30,
    )


@pytest.fixture
def client() -> TestClient:
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Domain Entity Fixtures
@pytest.fixture
def sample_error_id() -> uuid.UUID:
    """Generate a sample error ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_job_id() -> uuid.UUID:
    """Generate a sample job ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_speaker_id() -> uuid.UUID:
    """Generate a sample speaker ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_user_id() -> uuid.UUID:
    """Generate a sample user ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_error_report(
    sample_error_id: uuid.UUID,
    sample_job_id: uuid.UUID,
    sample_speaker_id: uuid.UUID,
    sample_user_id: uuid.UUID,
) -> ErrorReport:
    """Create a sample error report for testing."""
    return ErrorReport(
        error_id=sample_error_id,
        job_id=sample_job_id,
        speaker_id=sample_speaker_id,
        reported_by=sample_user_id,
        original_text="The patient has diabetis",
        corrected_text="The patient has diabetes",
        error_categories=["medical_terminology", "spelling"],
        severity_level=SeverityLevel.HIGH,
        start_position=16,
        end_position=24,
        context_notes="Common misspelling in medical terminology",
        error_timestamp=datetime.utcnow(),
        reported_at=datetime.utcnow(),
        status=ErrorStatus.PENDING,
        metadata={"audio_quality": "good", "confidence_score": 0.95},
    )


# Mock Fixtures
@pytest.fixture
def mock_error_repository():
    """Create mock error repository."""
    return AsyncMock()


@pytest.fixture
def mock_event_publisher():
    """Create mock event publisher."""
    return AsyncMock()


@pytest.fixture
def mock_validation_service():
    """Create mock validation service."""
    return Mock()


@pytest.fixture
def mock_categorization_service():
    """Create mock categorization service."""
    return Mock()


@pytest.fixture
def mock_redis_client():
    """Create mock Redis client."""
    return AsyncMock()


@pytest.fixture
def mock_kafka_producer():
    """Create mock Kafka producer."""
    return AsyncMock()


# Authentication Fixtures
@pytest.fixture
def valid_jwt_token() -> str:
    """Generate a valid JWT token for testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"


@pytest.fixture
def test_user() -> Dict[str, Any]:
    """Create test user data."""
    return {
        "user_id": str(uuid.uuid4()),
        "username": "test_user",
        "email": "test@example.com",
        "roles": ["qa_personnel"],
        "organization_id": str(uuid.uuid4()),
    }


# Test Data Fixtures
@pytest.fixture
def valid_error_report_data() -> Dict[str, Any]:
    """Create valid error report request data."""
    return {
        "job_id": str(uuid.uuid4()),
        "speaker_id": str(uuid.uuid4()),
        "original_text": "The patient has diabetis",
        "corrected_text": "The patient has diabetes",
        "error_categories": ["medical_terminology"],
        "severity_level": "high",
        "start_position": 16,
        "end_position": 24,
        "context_notes": "Common misspelling",
        "metadata": {"audio_quality": "good"},
    }


@pytest.fixture
def invalid_error_report_data() -> Dict[str, Any]:
    """Create invalid error report request data for testing validation."""
    return {
        "job_id": "invalid-uuid",
        "speaker_id": "",
        "original_text": "",
        "corrected_text": "",
        "error_categories": [],
        "severity_level": "invalid",
        "start_position": -1,
        "end_position": 0,
        "context_notes": "x" * 1001,  # Exceeds max length
        "metadata": {},
    }


# Environment Setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["REDIS_URL"] = TEST_REDIS_URL
    os.environ["LOG_LEVEL"] = "DEBUG"
    yield
    # Cleanup is handled by pytest automatically


# Async Test Utilities
@pytest.fixture
def anyio_backend():
    """Configure anyio backend for async tests."""
    return "asyncio"
