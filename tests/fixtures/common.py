"""
Common Test Fixtures

Shared test data and fixtures used across multiple test suites.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytest

from src.shared.domain.value_objects import BucketType, SeverityLevel, ErrorStatus


@pytest.fixture
def sample_uuid() -> str:
    """Generate a sample UUID for testing"""
    return str(uuid.uuid4())


@pytest.fixture
def sample_timestamp() -> datetime:
    """Generate a sample timestamp for testing"""
    return datetime.utcnow()


@pytest.fixture
def past_timestamp() -> datetime:
    """Generate a timestamp in the past for testing"""
    return datetime.utcnow() - timedelta(days=1)


@pytest.fixture
def future_timestamp() -> datetime:
    """Generate a timestamp in the future for testing"""
    return datetime.utcnow() + timedelta(days=1)


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """Generate sample metadata for testing"""
    return {
        "source": "test",
        "version": "1.0.0",
        "created_by": "test_user",
        "environment": "testing"
    }


@pytest.fixture
def bucket_types() -> List[BucketType]:
    """Get all bucket types for testing"""
    return [BucketType.NO_TOUCH, BucketType.LOW_TOUCH, BucketType.MEDIUM_TOUCH, BucketType.HIGH_TOUCH]


@pytest.fixture
def severity_levels() -> List[SeverityLevel]:
    """Get all severity levels for testing"""
    return [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]


@pytest.fixture
def error_statuses() -> List[ErrorStatus]:
    """Get all error statuses for testing"""
    return [ErrorStatus.SUBMITTED, ErrorStatus.PROCESSING, ErrorStatus.RECTIFIED, ErrorStatus.VERIFIED, ErrorStatus.REJECTED]


@pytest.fixture
def sample_speaker_id() -> str:
    """Generate a sample speaker ID for testing"""
    return f"speaker_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_job_id() -> str:
    """Generate a sample job ID for testing"""
    return f"job_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_user_id() -> str:
    """Generate a sample user ID for testing"""
    return f"user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_error_text() -> str:
    """Generate sample error text for testing"""
    return "The patient has a history of diabetes and hypertension."


@pytest.fixture
def sample_corrected_text() -> str:
    """Generate sample corrected text for testing"""
    return "The patient has a history of diabetes and hypertension, as well as chronic kidney disease."


@pytest.fixture
def sample_context_notes() -> str:
    """Generate sample context notes for testing"""
    return "Medical terminology correction needed. Speaker has slight accent."


class TestDataFactory:
    """Factory class for generating test data"""
    
    @staticmethod
    def create_error_report_data(
        speaker_id: str = None,
        job_id: str = None,
        severity: SeverityLevel = SeverityLevel.MEDIUM,
        status: ErrorStatus = ErrorStatus.SUBMITTED,
        bucket_type: BucketType = BucketType.MEDIUM_TOUCH
    ) -> Dict[str, Any]:
        """Create error report test data"""
        return {
            "id": str(uuid.uuid4()),
            "speaker_id": speaker_id or f"speaker_{uuid.uuid4().hex[:8]}",
            "job_id": job_id or f"job_{uuid.uuid4().hex[:8]}",
            "original_text": "The patient has diabetes",
            "corrected_text": "The patient has diabetes mellitus",
            "error_categories": ["medical_terminology"],
            "severity_level": severity.value,
            "status": status.value,
            "bucket_type": bucket_type.value,
            "start_position": 17,
            "end_position": 25,
            "context_notes": "Medical terminology needs clarification",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "audio_quality": "good",
                "speaker_clarity": "clear",
                "background_noise": "low"
            }
        }
    
    @staticmethod
    def create_user_data(
        user_id: str = None,
        role: str = "QA_ANALYST"
    ) -> Dict[str, Any]:
        """Create user test data"""
        return {
            "id": user_id or str(uuid.uuid4()),
            "username": f"test_user_{uuid.uuid4().hex[:6]}",
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
            "role": role,
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_speaker_data(
        speaker_id: str = None,
        bucket_type: BucketType = BucketType.MEDIUM_TOUCH
    ) -> Dict[str, Any]:
        """Create speaker test data"""
        return {
            "id": speaker_id or f"speaker_{uuid.uuid4().hex[:8]}",
            "name": f"Dr. Test Speaker {uuid.uuid4().hex[:6]}",
            "bucket_type": bucket_type.value,
            "total_errors": 5,
            "rectified_errors": 3,
            "rectification_rate": 0.6,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
