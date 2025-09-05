# Backend Unit Test Specifications
## Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**Version:** 2.0  
**Coverage Target:** >90% for all new functionality  
**Framework:** pytest with async support

---

## Test Suite Overview

This document specifies comprehensive unit tests for all backend services and business logic related to the quality-based speaker bucket management system.

---

## 1. Enhanced Error Reporting Service Tests

### 1.1 ErrorReportService Unit Tests

#### Test Class: `TestErrorReportService`

```python
class TestErrorReportService:
    """Unit tests for enhanced error reporting service"""
    
    @pytest.fixture
    def error_report_service(self):
        return ErrorReportService(
            db_session=mock_db_session,
            vector_db=mock_vector_db,
            validation_service=mock_validation_service
        )
    
    @pytest.fixture
    def sample_enhanced_error_report(self):
        return {
            "job_id": "550e8400-e29b-41d4-a716-446655440010",
            "speaker_id": "speaker-123",
            "client_id": "client-456",
            "bucket_type": "medium_touch",
            "original_text": "The patient has severe hypertension",
            "corrected_text": "The patient has severe high blood pressure",
            "error_categories": ["medical_terminology"],
            "severity_level": "medium",
            "start_position": 20,
            "end_position": 32,
            "context_notes": "Medical terminology simplification",
            "metadata": {
                "audio_quality": "good",
                "speaker_clarity": "clear",
                "background_noise": "low",
                "number_of_speakers": "one",
                "overlapping_speech": False,
                "requires_specialized_knowledge": True,
                "additional_notes": "Complex medical terminology used"
            }
        }
```

#### Test Cases:

**TC-ER-001: Create Error Report with Enhanced Metadata**
```python
async def test_create_error_report_with_enhanced_metadata(
    self, error_report_service, sample_enhanced_error_report
):
    """Test creating error report with all enhanced metadata fields"""
    
    # Act
    result = await error_report_service.create_error_report(
        sample_enhanced_error_report
    )
    
    # Assert
    assert result.id is not None
    assert result.bucket_type == "medium_touch"
    assert result.metadata.number_of_speakers == "one"
    assert result.metadata.overlapping_speech is False
    assert result.metadata.requires_specialized_knowledge is True
    assert result.metadata.additional_notes == "Complex medical terminology used"
    assert len(result.metadata.additional_notes) <= 1000
```

**TC-ER-002: Validate Bucket Type Enum**
```python
async def test_validate_bucket_type_enum(self, error_report_service):
    """Test bucket type validation for quality-based system"""
    
    valid_buckets = ["no_touch", "low_touch", "medium_touch", "high_touch"]
    invalid_buckets = ["beginner", "intermediate", "advanced", "expert", "invalid"]
    
    # Test valid bucket types
    for bucket in valid_buckets:
        result = error_report_service.validate_bucket_type(bucket)
        assert result is True
    
    # Test invalid bucket types
    for bucket in invalid_buckets:
        with pytest.raises(ValidationError):
            error_report_service.validate_bucket_type(bucket)
```

**TC-ER-003: Validate Enhanced Metadata Fields**
```python
async def test_validate_enhanced_metadata_fields(self, error_report_service):
    """Test validation of new enhanced metadata fields"""
    
    # Test number_of_speakers validation
    valid_speaker_counts = ["one", "two", "three", "four", "five"]
    for count in valid_speaker_counts:
        assert error_report_service.validate_speaker_count(count) is True
    
    with pytest.raises(ValidationError):
        error_report_service.validate_speaker_count("six")
    
    # Test additional_notes length validation
    valid_notes = "A" * 1000  # Exactly 1000 characters
    assert error_report_service.validate_additional_notes(valid_notes) is True
    
    invalid_notes = "A" * 1001  # Over 1000 characters
    with pytest.raises(ValidationError):
        error_report_service.validate_additional_notes(invalid_notes)
```

**TC-ER-004: Vector Database Integration with Enhanced Metadata**
```python
async def test_vector_db_integration_enhanced_metadata(
    self, error_report_service, sample_enhanced_error_report
):
    """Test vector database storage with enhanced metadata"""
    
    # Act
    result = await error_report_service.create_error_report(
        sample_enhanced_error_report
    )
    
    # Assert vector database was called with enhanced metadata
    mock_vector_db.store_error_vector.assert_called_once()
    call_args = mock_vector_db.store_error_vector.call_args[0][0]
    
    assert call_args.metadata["number_of_speakers"] == "one"
    assert call_args.metadata["overlapping_speech"] is False
    assert call_args.metadata["requires_specialized_knowledge"] is True
    assert "additional_notes" in call_args.metadata
```

---

## 2. Speaker Bucket Management Service Tests

### 2.1 SpeakerBucketService Unit Tests

#### Test Class: `TestSpeakerBucketService`

**TC-SB-001: Assign Speaker to Quality-Based Bucket**
```python
async def test_assign_speaker_to_quality_bucket(self, bucket_service):
    """Test assigning speaker to quality-based bucket"""
    
    # Arrange
    speaker_id = "speaker-123"
    bucket_type = "medium_touch"
    reason = "Initial quality assessment"
    assigned_by = "qa-user-456"
    
    # Act
    result = await bucket_service.assign_speaker_bucket(
        speaker_id=speaker_id,
        bucket_type=bucket_type,
        reason=reason,
        assigned_by=assigned_by
    )
    
    # Assert
    assert result.speaker_id == speaker_id
    assert result.bucket_type == bucket_type
    assert result.reason == reason
    assert result.assigned_by == assigned_by
    assert result.assigned_date is not None
```

**TC-SB-002: Track Bucket Transition History**
```python
async def test_track_bucket_transition_history(self, bucket_service):
    """Test tracking of bucket transitions with history"""
    
    # Arrange
    speaker_id = "speaker-123"
    
    # Act - Initial assignment
    await bucket_service.assign_speaker_bucket(
        speaker_id, "high_touch", "Initial assessment", "qa-user-456"
    )
    
    # Act - Bucket improvement
    await bucket_service.assign_speaker_bucket(
        speaker_id, "medium_touch", "Quality improvement", "qa-user-456"
    )
    
    # Assert
    history = await bucket_service.get_bucket_history(speaker_id)
    assert len(history) == 2
    assert history[0].bucket_type == "high_touch"
    assert history[1].bucket_type == "medium_touch"
    assert history[1].previous_bucket == "high_touch"
```

**TC-SB-003: Calculate Speaker Performance Metrics**
```python
async def test_calculate_speaker_performance_metrics(self, bucket_service):
    """Test calculation of speaker performance metrics"""
    
    # Arrange
    speaker_id = "speaker-123"
    mock_error_reports = [
        create_mock_error_report(speaker_id, "rectified"),
        create_mock_error_report(speaker_id, "rectified"),
        create_mock_error_report(speaker_id, "pending"),
        create_mock_error_report(speaker_id, "rectified"),
    ]
    
    # Act
    metrics = await bucket_service.calculate_performance_metrics(
        speaker_id, mock_error_reports
    )
    
    # Assert
    assert metrics.total_errors_reported == 4
    assert metrics.errors_rectified == 3
    assert metrics.rectification_rate == 0.75
    assert metrics.quality_trend == "improving"
```

---

## 3. Speaker History Service Tests

### 3.1 SpeakerHistoryService Unit Tests

**TC-SH-001: Retrieve Complete Speaker History**
```python
async def test_retrieve_complete_speaker_history(self, history_service):
    """Test retrieval of complete speaker history"""
    
    # Arrange
    speaker_id = "speaker-123"
    
    # Act
    history = await history_service.get_speaker_history(speaker_id)
    
    # Assert
    assert history.speaker_id == speaker_id
    assert history.current_bucket is not None
    assert isinstance(history.bucket_history, list)
    assert isinstance(history.error_history, list)
    assert history.performance_metrics is not None
```

**TC-SH-002: Filter History by Date Range**
```python
async def test_filter_history_by_date_range(self, history_service):
    """Test filtering speaker history by date range"""
    
    # Arrange
    speaker_id = "speaker-123"
    start_date = datetime(2024, 12, 1)
    end_date = datetime(2024, 12, 19)
    
    # Act
    history = await history_service.get_speaker_history(
        speaker_id, start_date=start_date, end_date=end_date
    )
    
    # Assert
    for error in history.error_history:
        assert start_date <= error.reported_date <= end_date
```

**TC-SH-003: Calculate Performance Trends**
```python
async def test_calculate_performance_trends(self, history_service):
    """Test calculation of speaker performance trends"""
    
    # Arrange
    speaker_id = "speaker-123"
    
    # Act
    trends = await history_service.get_performance_trends(speaker_id)
    
    # Assert
    assert trends.speaker_id == speaker_id
    assert trends.trend_period is not None
    assert isinstance(trends.bucket_transitions, list)
    assert trends.improvement_indicators is not None
    assert 0 <= trends.improvement_indicators.confidence_score <= 1
```

---

## 4. Verification Service Tests

### 4.1 VerificationService Unit Tests

**TC-VS-001: Pull Jobs from InstaNote Database**
```python
async def test_pull_jobs_from_instanote_db(self, verification_service):
    """Test pulling jobs from InstaNote Database"""
    
    # Arrange
    speaker_id = "speaker-123"
    date_range = DateRange(
        start_date=datetime(2024, 12, 1),
        end_date=datetime(2024, 12, 19)
    )
    
    # Act
    jobs = await verification_service.pull_jobs_for_verification(
        speaker_id=speaker_id,
        date_range=date_range,
        max_jobs=10
    )
    
    # Assert
    assert isinstance(jobs, list)
    assert len(jobs) <= 10
    for job in jobs:
        assert job.speaker_id == speaker_id
        assert job.original_draft is not None
        assert job.job_metadata is not None
```

**TC-VS-002: Apply RAG Corrections to Drafts**
```python
async def test_apply_rag_corrections_to_drafts(self, verification_service):
    """Test applying RAG-based corrections to draft text"""
    
    # Arrange
    original_draft = "The patient has severe hypertension and diabetes"
    speaker_id = "speaker-123"
    error_patterns = [
        {"original": "hypertension", "corrected": "high blood pressure", "confidence": 0.95}
    ]
    
    # Act
    corrected_draft = await verification_service.apply_rag_corrections(
        original_draft=original_draft,
        speaker_id=speaker_id,
        error_patterns=error_patterns
    )
    
    # Assert
    assert "high blood pressure" in corrected_draft.corrected_text
    assert corrected_draft.corrections_applied is not None
    assert len(corrected_draft.corrections_applied) > 0
```

**TC-VS-003: Process Verification Results**
```python
async def test_process_verification_results(self, verification_service):
    """Test processing of verification results"""
    
    # Arrange
    verification_result = VerificationResult(
        job_id="job-456",
        error_id="error-789",
        verification_result="rectified",
        qa_comments="Error successfully corrected",
        verified_by="qa-user-456"
    )
    
    # Act
    result = await verification_service.process_verification_result(
        verification_result
    )
    
    # Assert
    assert result.status == "verified"
    assert result.verification_timestamp is not None
    assert result.speaker_performance_updated is True
```

---

## 5. Enhanced Metadata Validation Tests

### 5.1 MetadataValidationService Unit Tests

**TC-MV-001: Validate All Enhanced Metadata Fields**
```python
async def test_validate_all_enhanced_metadata_fields(self, validation_service):
    """Test validation of all enhanced metadata fields"""
    
    # Arrange
    metadata = {
        "audio_quality": "good",
        "speaker_clarity": "clear",
        "background_noise": "low",
        "number_of_speakers": "one",
        "overlapping_speech": False,
        "requires_specialized_knowledge": True,
        "additional_notes": "Valid notes within limit"
    }
    
    # Act
    result = validation_service.validate_enhanced_metadata(metadata)
    
    # Assert
    assert result.is_valid is True
    assert len(result.errors) == 0
```

**TC-MV-002: Validate Field Constraints**
```python
async def test_validate_field_constraints(self, validation_service):
    """Test validation of field constraints and limits"""
    
    # Test invalid number_of_speakers
    with pytest.raises(ValidationError) as exc_info:
        validation_service.validate_speaker_count("invalid")
    assert "must be one of" in str(exc_info.value)
    
    # Test additional_notes length limit
    with pytest.raises(ValidationError) as exc_info:
        validation_service.validate_additional_notes("A" * 1001)
    assert "exceeds maximum length" in str(exc_info.value)
    
    # Test boolean field validation
    assert validation_service.validate_boolean_field(True) is True
    assert validation_service.validate_boolean_field(False) is True
    with pytest.raises(ValidationError):
        validation_service.validate_boolean_field("invalid")
```

---

## 6. Database Integration Tests

### 6.1 Enhanced Error Reports Repository Tests

**TC-DB-001: Store Error Report with Enhanced Metadata**
```python
async def test_store_error_report_enhanced_metadata(self, db_session):
    """Test storing error report with enhanced metadata in database"""
    
    # Arrange
    error_report = ErrorReport(
        job_id="job-123",
        speaker_id="speaker-456",
        bucket_type="medium_touch",
        number_of_speakers="one",
        overlapping_speech=False,
        requires_specialized_knowledge=True,
        additional_notes="Test notes"
    )
    
    # Act
    repository = ErrorReportRepository(db_session)
    saved_report = await repository.save(error_report)
    
    # Assert
    assert saved_report.id is not None
    assert saved_report.number_of_speakers == "one"
    assert saved_report.overlapping_speech is False
    assert saved_report.requires_specialized_knowledge is True
    assert saved_report.additional_notes == "Test notes"
```

**TC-DB-002: Query Error Reports with Enhanced Filters**
```python
async def test_query_error_reports_enhanced_filters(self, db_session):
    """Test querying error reports with enhanced metadata filters"""
    
    # Arrange
    repository = ErrorReportRepository(db_session)
    filters = {
        "bucket_type": "medium_touch",
        "requires_specialized_knowledge": True,
        "number_of_speakers": "one"
    }
    
    # Act
    results = await repository.find_by_filters(filters)
    
    # Assert
    assert isinstance(results, list)
    for report in results:
        assert report.bucket_type == "medium_touch"
        assert report.requires_specialized_knowledge is True
        assert report.number_of_speakers == "one"
```

---

## Test Configuration and Setup

### Test Environment Setup
```python
# conftest.py
@pytest.fixture(scope="session")
async def test_db():
    """Setup test database with enhanced schema"""
    engine = create_async_engine("postgresql://test:test@localhost/test_db")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_db):
    """Provide database session for tests"""
    async with AsyncSession(test_db) as session:
        yield session
        await session.rollback()
```

### Test Data Factories
```python
# test_factories.py
class ErrorReportFactory:
    @staticmethod
    def create_enhanced_error_report(**kwargs):
        defaults = {
            "job_id": "job-123",
            "speaker_id": "speaker-456",
            "bucket_type": "medium_touch",
            "number_of_speakers": "one",
            "overlapping_speech": False,
            "requires_specialized_knowledge": True,
            "additional_notes": "Test notes"
        }
        defaults.update(kwargs)
        return ErrorReport(**defaults)
```

### Coverage Requirements
- **Minimum Coverage**: 90% for all new functionality
- **Critical Path Coverage**: 100% for error reporting and bucket management
- **Integration Coverage**: 85% for external service integrations
- **Edge Case Coverage**: All validation and error handling paths

### Test Execution
```bash
# Run all unit tests with coverage
pytest tests/unit/ --cov=src --cov-report=html --cov-fail-under=90

# Run specific test suites
pytest tests/unit/test_error_reporting_service.py -v
pytest tests/unit/test_speaker_bucket_service.py -v
pytest tests/unit/test_verification_service.py -v
```
