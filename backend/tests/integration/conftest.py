"""
Integration test configuration and fixtures for speaker bucket management workflow.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Any, List
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

# from app.main import app
# from app.core.database import get_db
# from app.core.config import settings
# from app.models.base import Base
# from app.models.speaker import Speaker
# from app.models.historical_asr_data import HistoricalASRData
from app.models.validation_test_data import ValidationTestData
from app.models.bucket_transition_request import BucketTransitionRequest
from app.models.mt_validation_session import MTValidationSession
from app.models.mt_feedback import MTFeedback
from app.domain.enums import SpeakerBucket, QualityTrend, ImprovementAssessment
from app.services.auth_service import AuthService
from app.services.speaker_service import SpeakerService
from app.services.rag_service import RAGService
from app.services.ser_service import SERService
from app.services.mt_validation_service import MTValidationService

# Test containers
postgres_container = None
redis_container = None


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def postgres_url():
    """Start PostgreSQL container and return connection URL."""
    global postgres_container
    postgres_container = PostgresContainer("postgres:14")
    postgres_container.start()
    
    yield postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    
    postgres_container.stop()


@pytest.fixture(scope="session")
async def redis_url():
    """Start Redis container and return connection URL."""
    global redis_container
    redis_container = RedisContainer("redis:7")
    redis_container.start()
    
    yield f"redis://localhost:{redis_container.get_exposed_port(6379)}"
    
    redis_container.stop()


@pytest.fixture(scope="session")
async def test_engine(postgres_url: str):
    """Create test database engine."""
    engine = create_async_engine(
        postgres_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
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
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(test_client: AsyncClient) -> Dict[str, str]:
    """Create authentication headers for test requests."""
    # Create test user and get token
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "admin"
    }
    
    # Register user
    await test_client.post("/api/v1/auth/register", json=user_data)
    
    # Login and get token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = await test_client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def sample_speakers(db_session: AsyncSession) -> List[Speaker]:
    """Create sample speakers for testing."""
    speakers = [
        Speaker(
            speaker_identifier="SPEAKER_001",
            speaker_name="Dr. John Smith",
            current_bucket=SpeakerBucket.HIGH_TOUCH,
            note_count=150,
            average_ser_score=18.5,
            quality_trend=QualityTrend.IMPROVING,
            should_transition=True,
            has_sufficient_data=True,
        ),
        Speaker(
            speaker_identifier="SPEAKER_002",
            speaker_name="Dr. Sarah Johnson",
            current_bucket=SpeakerBucket.MEDIUM_TOUCH,
            note_count=89,
            average_ser_score=12.3,
            quality_trend=QualityTrend.STABLE,
            should_transition=False,
            has_sufficient_data=True,
        ),
        Speaker(
            speaker_identifier="SPEAKER_003",
            speaker_name="Dr. Michael Brown",
            current_bucket=SpeakerBucket.LOW_TOUCH,
            note_count=45,
            average_ser_score=8.7,
            quality_trend=QualityTrend.DECLINING,
            should_transition=True,
            has_sufficient_data=False,
        ),
    ]
    
    for speaker in speakers:
        db_session.add(speaker)
    
    await db_session.commit()
    
    for speaker in speakers:
        await db_session.refresh(speaker)
    
    return speakers


@pytest.fixture
async def sample_historical_data(
    db_session: AsyncSession, 
    sample_speakers: List[Speaker]
) -> List[HistoricalASRData]:
    """Create sample historical ASR data for testing."""
    historical_data = []
    
    for i, speaker in enumerate(sample_speakers):
        for j in range(5):  # 5 records per speaker
            data = HistoricalASRData(
                speaker_id=speaker.speaker_id,
                original_asr_text=f"Sample ASR text {i}-{j} with some errors and mistakes.",
                final_reference_text=f"Sample ASR text {i}-{j} with corrections and proper formatting.",
                ser_score=15.0 + (i * 2) + (j * 0.5),
                edit_distance=8 + i + j,
                insertions=2 + i,
                deletions=1 + j,
                substitutions=3 + i,
                moves=1,
                quality_level="medium",
                is_acceptable_quality=True,
                metadata_={"note_id": f"NOTE_{i}_{j}", "date": "2024-01-01"}
            )
            historical_data.append(data)
            db_session.add(data)
    
    await db_session.commit()
    
    for data in historical_data:
        await db_session.refresh(data)
    
    return historical_data


@pytest.fixture
async def sample_validation_data(
    db_session: AsyncSession,
    sample_speakers: List[Speaker],
    sample_historical_data: List[HistoricalASRData]
) -> List[ValidationTestData]:
    """Create sample validation test data."""
    validation_data = []
    
    for i, speaker in enumerate(sample_speakers[:2]):  # Only first 2 speakers
        for j in range(3):  # 3 validation items per speaker
            data = ValidationTestData(
                speaker_id=speaker.speaker_id,
                historical_data_id=sample_historical_data[i * 5 + j].data_id,
                original_asr_text=f"Original ASR text {i}-{j} with errors.",
                rag_corrected_text=f"RAG corrected text {i}-{j} with improvements.",
                final_reference_text=f"Final reference text {i}-{j} with perfect accuracy.",
                original_ser_metrics={
                    "ser_score": 18.5,
                    "edit_distance": 10,
                    "insertions": 3,
                    "deletions": 2,
                    "substitutions": 4,
                    "moves": 1,
                    "quality_level": "medium",
                    "is_acceptable_quality": False
                },
                corrected_ser_metrics={
                    "ser_score": 8.2,
                    "edit_distance": 4,
                    "insertions": 1,
                    "deletions": 1,
                    "substitutions": 2,
                    "moves": 0,
                    "quality_level": "high",
                    "is_acceptable_quality": True
                },
                improvement_metrics={
                    "improvement": 10.3,
                    "improvement_percentage": 55.7,
                    "is_significant_improvement": True
                },
                priority="medium",
                is_used=False,
                metadata_={"created_for_test": True}
            )
            validation_data.append(data)
            db_session.add(data)
    
    await db_session.commit()
    
    for data in validation_data:
        await db_session.refresh(data)
    
    return validation_data


@pytest.fixture
async def sample_validation_session(
    db_session: AsyncSession,
    sample_speakers: List[Speaker],
    sample_validation_data: List[ValidationTestData]
) -> MTValidationSession:
    """Create sample MT validation session."""
    session = MTValidationSession(
        speaker_id=sample_speakers[0].speaker_id,
        session_name="Test Validation Session",
        test_data_ids=[data.data_id for data in sample_validation_data[:3]],
        mt_user_id="test-user-id",
        status="active",
        progress_percentage=0.0,
        session_metadata={
            "priority": "medium",
            "auto_advance": True,
            "include_ser_metrics": True
        }
    )
    
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    
    return session


@pytest.fixture
async def services(db_session: AsyncSession):
    """Create service instances for testing."""
    return {
        "speaker_service": SpeakerService(db_session),
        "rag_service": RAGService(),
        "ser_service": SERService(),
        "mt_validation_service": MTValidationService(db_session),
    }


@pytest.fixture
def sample_asr_texts():
    """Sample ASR texts for testing."""
    return [
        {
            "original": "The patient has a history of diabetes and hypertension. He is currently taking metformin 500 mg twice daily.",
            "reference": "The patient has a history of diabetes and hypertension. He is currently taking metformin 500 mg twice daily.",
            "errors": []
        },
        {
            "original": "The patient complains of chest pain that started 2 hours ago. The pain is described as crushing and radiates to the left arm.",
            "reference": "The patient complains of chest pain that started 2 hours ago. The pain is described as crushing and radiates to the left arm.",
            "errors": []
        },
        {
            "original": "Physical examination reveals normal vital signs. Heart rate is 72 beats per minute, blood pressure is 120/80 mmHg.",
            "reference": "Physical examination reveals normal vital signs. Heart rate is 72 beats per minute, blood pressure is 120/80 mmHg.",
            "errors": []
        }
    ]


@pytest.fixture
def performance_test_data():
    """Large dataset for performance testing."""
    return {
        "speaker_count": 100,
        "historical_data_per_speaker": 50,
        "validation_data_per_speaker": 10,
        "concurrent_sessions": 5,
        "batch_size": 20
    }


# Utility functions for tests
async def create_test_speaker(
    db_session: AsyncSession,
    identifier: str = "TEST_SPEAKER",
    name: str = "Test Speaker",
    bucket: SpeakerBucket = SpeakerBucket.MEDIUM_TOUCH
) -> Speaker:
    """Create a test speaker."""
    speaker = Speaker(
        speaker_identifier=identifier,
        speaker_name=name,
        current_bucket=bucket,
        note_count=50,
        average_ser_score=15.0,
        quality_trend=QualityTrend.STABLE,
        should_transition=False,
        has_sufficient_data=True,
    )
    
    db_session.add(speaker)
    await db_session.commit()
    await db_session.refresh(speaker)
    
    return speaker


async def create_test_historical_data(
    db_session: AsyncSession,
    speaker_id: str,
    count: int = 5
) -> List[HistoricalASRData]:
    """Create test historical ASR data."""
    data_list = []
    
    for i in range(count):
        data = HistoricalASRData(
            speaker_id=speaker_id,
            original_asr_text=f"Test ASR text {i} with errors.",
            final_reference_text=f"Test reference text {i} corrected.",
            ser_score=10.0 + i,
            edit_distance=5 + i,
            insertions=1,
            deletions=1,
            substitutions=2,
            moves=0,
            quality_level="medium",
            is_acceptable_quality=True,
            metadata_={"test_data": True}
        )
        data_list.append(data)
        db_session.add(data)
    
    await db_session.commit()
    
    for data in data_list:
        await db_session.refresh(data)
    
    return data_list
