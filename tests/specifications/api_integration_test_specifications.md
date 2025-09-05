# API Integration Test Specifications
## Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**Version:** 2.0  
**Framework:** pytest-asyncio with httpx for async API testing  
**Coverage Target:** 100% of API endpoints

---

## Test Suite Overview

This document specifies comprehensive integration tests for all API endpoints related to the quality-based speaker bucket management system.

---

## 1. Enhanced Error Reporting API Tests

### 1.1 POST /api/v1/errors - Enhanced Error Submission

#### Test Class: `TestEnhancedErrorReportingAPI`

**TC-API-ER-001: Submit Error Report with Enhanced Metadata**
```python
async def test_submit_error_report_enhanced_metadata(self, api_client, auth_headers):
    """Test submitting error report with all enhanced metadata fields"""
    
    # Arrange
    error_report_data = {
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
            "additional_notes": "Complex medical terminology used throughout"
        }
    }
    
    # Act
    response = await api_client.post(
        "/api/v1/errors",
        json=error_report_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["error_id"] is not None
    assert response_data["status"] == "submitted"
    assert response_data["submission_timestamp"] is not None
    assert response_data["vector_db_id"] is not None
```

**TC-API-ER-002: Validate Enhanced Metadata Fields**
```python
async def test_validate_enhanced_metadata_fields(self, api_client, auth_headers):
    """Test validation of enhanced metadata fields"""
    
    # Test invalid number_of_speakers
    invalid_data = {
        "job_id": "job-123",
        "speaker_id": "speaker-456",
        "bucket_type": "medium_touch",
        "metadata": {
            "number_of_speakers": "invalid_count",  # Invalid value
            "overlapping_speech": False,
            "requires_specialized_knowledge": True
        }
    }
    
    response = await api_client.post("/api/v1/errors", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert "number_of_speakers" in str(error_detail)
    assert "must be one of" in str(error_detail)
```

**TC-API-ER-003: Test Additional Notes Length Validation**
```python
async def test_additional_notes_length_validation(self, api_client, auth_headers):
    """Test validation of additional notes length limit"""
    
    # Test notes exceeding 1000 characters
    long_notes = "A" * 1001
    invalid_data = {
        "job_id": "job-123",
        "speaker_id": "speaker-456",
        "bucket_type": "medium_touch",
        "metadata": {
            "additional_notes": long_notes
        }
    }
    
    response = await api_client.post("/api/v1/errors", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert "additional_notes" in str(error_detail)
    assert "exceeds maximum length" in str(error_detail)
```

**TC-API-ER-004: Test Quality-Based Bucket Type Validation**
```python
async def test_quality_bucket_type_validation(self, api_client, auth_headers):
    """Test validation of quality-based bucket types"""
    
    valid_buckets = ["no_touch", "low_touch", "medium_touch", "high_touch"]
    invalid_buckets = ["beginner", "intermediate", "advanced", "expert"]
    
    # Test valid bucket types
    for bucket in valid_buckets:
        data = {
            "job_id": "job-123",
            "speaker_id": "speaker-456",
            "bucket_type": bucket,
            "original_text": "test",
            "corrected_text": "test"
        }
        response = await api_client.post("/api/v1/errors", json=data, headers=auth_headers)
        assert response.status_code == 201
    
    # Test invalid bucket types
    for bucket in invalid_buckets:
        data = {
            "job_id": "job-123",
            "speaker_id": "speaker-456",
            "bucket_type": bucket,
            "original_text": "test",
            "corrected_text": "test"
        }
        response = await api_client.post("/api/v1/errors", json=data, headers=auth_headers)
        assert response.status_code == 422
```

---

## 2. Speaker History and Performance API Tests

### 2.1 GET /api/v1/speakers/{speaker_id}/history

**TC-API-SH-001: Retrieve Complete Speaker History**
```python
async def test_retrieve_complete_speaker_history(self, api_client, auth_headers):
    """Test retrieving complete speaker history"""
    
    # Arrange
    speaker_id = "speaker-123"
    
    # Act
    response = await api_client.get(
        f"/api/v1/speakers/{speaker_id}/history",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["speaker_id"] == speaker_id
    assert "current_bucket" in data
    assert "bucket_history" in data
    assert "error_history" in data
    assert "performance_metrics" in data
    assert "metadata_analysis" in data
```

**TC-API-SH-002: Filter History by Date Range**
```python
async def test_filter_history_by_date_range(self, api_client, auth_headers):
    """Test filtering speaker history by date range"""
    
    # Arrange
    speaker_id = "speaker-123"
    start_date = "2024-12-01T00:00:00Z"
    end_date = "2024-12-19T23:59:59Z"
    
    # Act
    response = await api_client.get(
        f"/api/v1/speakers/{speaker_id}/history",
        params={"start_date": start_date, "end_date": end_date},
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify all error history entries are within date range
    for error in data["error_history"]:
        error_date = datetime.fromisoformat(error["reported_date"].replace("Z", "+00:00"))
        start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        assert start <= error_date <= end
```

### 2.2 GET /api/v1/speakers/{speaker_id}/performance-trends

**TC-API-PT-001: Retrieve Performance Trends**
```python
async def test_retrieve_performance_trends(self, api_client, auth_headers):
    """Test retrieving speaker performance trends"""
    
    # Arrange
    speaker_id = "speaker-123"
    
    # Act
    response = await api_client.get(
        f"/api/v1/speakers/{speaker_id}/performance-trends",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["speaker_id"] == speaker_id
    assert "trend_period" in data
    assert "bucket_transitions" in data
    assert "improvement_indicators" in data
    
    # Validate improvement indicators structure
    indicators = data["improvement_indicators"]
    assert "error_reduction_rate" in indicators
    assert "quality_consistency" in indicators
    assert "confidence_score" in indicators
    assert 0 <= indicators["confidence_score"] <= 1
```

---

## 3. Verification Workflow API Tests

### 3.1 POST /api/v1/verification/pull-jobs

**TC-API-VF-001: Pull Jobs for Verification**
```python
async def test_pull_jobs_for_verification(self, api_client, auth_headers):
    """Test pulling jobs from InstaNote Database for verification"""
    
    # Arrange
    request_data = {
        "speaker_id": "speaker-123",
        "date_range": {
            "start_date": "2024-12-01T00:00:00Z",
            "end_date": "2024-12-19T23:59:59Z"
        },
        "error_types": ["medical_terminology", "pronunciation"],
        "max_jobs": 10
    }
    
    # Act
    response = await api_client.post(
        "/api/v1/verification/pull-jobs",
        json=request_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "jobs_found" in data
    assert "speaker_id" in data
    assert "retrieval_timestamp" in data
    assert "jobs" in data
    assert len(data["jobs"]) <= 10
    
    # Validate job structure
    for job in data["jobs"]:
        assert "job_id" in job
        assert "original_draft" in job
        assert "rag_corrected_draft" in job
        assert "corrections_applied" in job
        assert "verification_status" in job
```

**TC-API-VF-002: Handle InstaNote Database Connection Errors**
```python
async def test_handle_instanote_connection_errors(self, api_client, auth_headers, mock_instanote_error):
    """Test handling of InstaNote Database connection errors"""
    
    # Arrange
    request_data = {
        "speaker_id": "speaker-123",
        "date_range": {
            "start_date": "2024-12-01T00:00:00Z",
            "end_date": "2024-12-19T23:59:59Z"
        }
    }
    
    # Act
    response = await api_client.post(
        "/api/v1/verification/pull-jobs",
        json=request_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 503  # Service Unavailable
    error_data = response.json()
    assert error_data["error"]["code"] == "INSTANOTE_CONNECTION_ERROR"
    assert "Cannot connect to InstaNote Database" in error_data["error"]["message"]
```

### 3.2 POST /api/v1/verification/verify-correction

**TC-API-VC-001: Verify Correction Results**
```python
async def test_verify_correction_results(self, api_client, auth_headers):
    """Test verifying correction results"""
    
    # Arrange
    verification_data = {
        "verification_id": "verify-789",
        "job_id": "instanote-job-456",
        "error_id": "error-789",
        "verification_result": "rectified",
        "qa_comments": "Error successfully corrected in new draft",
        "verified_by": "qa-user-456"
    }
    
    # Act
    response = await api_client.post(
        "/api/v1/verification/verify-correction",
        json=verification_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["verification_id"] == "verify-789"
    assert data["status"] == "verified"
    assert "verification_timestamp" in data
    assert "speaker_performance_updated" in data
    assert "bucket_reassessment_triggered" in data
```

---

## 4. Dashboard Analytics API Tests

### 4.1 GET /api/v1/dashboard/bucket-overview

**TC-API-DO-001: Retrieve Bucket Distribution Overview**
```python
async def test_retrieve_bucket_distribution_overview(self, api_client, auth_headers):
    """Test retrieving bucket distribution for dashboard"""
    
    # Act
    response = await api_client.get(
        "/api/v1/dashboard/bucket-overview",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "total_speakers" in data
    assert "bucket_distribution" in data
    assert "quality_metrics" in data
    assert "generated_at" in data
    
    # Validate bucket distribution structure
    distribution = data["bucket_distribution"]
    expected_buckets = ["no_touch", "low_touch", "medium_touch", "high_touch"]
    for bucket in expected_buckets:
        assert bucket in distribution
        assert "count" in distribution[bucket]
        assert "percentage" in distribution[bucket]
        assert "trend" in distribution[bucket]
```

### 4.2 GET /api/v1/dashboard/performance-metrics

**TC-API-PM-001: Retrieve System Performance Metrics**
```python
async def test_retrieve_system_performance_metrics(self, api_client, auth_headers):
    """Test retrieving system-wide performance metrics"""
    
    # Act
    response = await api_client.get(
        "/api/v1/dashboard/performance-metrics",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "reporting_period" in data
    assert "error_reporting_metrics" in data
    assert "bucket_transition_metrics" in data
    assert "metadata_insights" in data
    assert "resource_allocation" in data
    
    # Validate metadata insights for enhanced fields
    insights = data["metadata_insights"]
    assert "specialized_knowledge_percentage" in insights
    assert "overlapping_speech_percentage" in insights
    assert "multi_speaker_percentage" in insights
```

---

## 5. Authentication and Authorization Tests

### 5.1 Authentication Tests

**TC-API-AUTH-001: Test JWT Token Validation**
```python
async def test_jwt_token_validation(self, api_client):
    """Test JWT token validation for API access"""
    
    # Test without token
    response = await api_client.get("/api/v1/speakers/speaker-123/history")
    assert response.status_code == 401
    
    # Test with invalid token
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    response = await api_client.get(
        "/api/v1/speakers/speaker-123/history",
        headers=invalid_headers
    )
    assert response.status_code == 401
    
    # Test with expired token
    expired_headers = {"Authorization": f"Bearer {create_expired_token()}"}
    response = await api_client.get(
        "/api/v1/speakers/speaker-123/history",
        headers=expired_headers
    )
    assert response.status_code == 401
```

**TC-API-AUTH-002: Test Role-Based Access Control**
```python
async def test_role_based_access_control(self, api_client):
    """Test role-based access control for different user types"""
    
    # QA user should have full access
    qa_headers = {"Authorization": f"Bearer {create_qa_token()}"}
    response = await api_client.get(
        "/api/v1/speakers/speaker-123/history",
        headers=qa_headers
    )
    assert response.status_code == 200
    
    # MT user should have limited access
    mt_headers = {"Authorization": f"Bearer {create_mt_token()}"}
    response = await api_client.post(
        "/api/v1/verification/pull-jobs",
        json={"speaker_id": "speaker-123"},
        headers=mt_headers
    )
    assert response.status_code == 403  # Forbidden
```

---

## 6. Error Handling and Edge Cases

### 6.1 Error Response Format Tests

**TC-API-ERR-001: Test Standard Error Response Format**
```python
async def test_standard_error_response_format(self, api_client, auth_headers):
    """Test standard error response format across all endpoints"""
    
    # Test validation error
    invalid_data = {"invalid": "data"}
    response = await api_client.post("/api/v1/errors", json=invalid_data, headers=auth_headers)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "error" in error_data
    assert "code" in error_data["error"]
    assert "message" in error_data["error"]
    assert "details" in error_data["error"]
    assert "timestamp" in error_data["error"]
```

**TC-API-ERR-002: Test Rate Limiting**
```python
async def test_rate_limiting(self, api_client, auth_headers):
    """Test API rate limiting functionality"""
    
    # Make multiple rapid requests
    responses = []
    for i in range(100):
        response = await api_client.get(
            "/api/v1/speakers/speaker-123/history",
            headers=auth_headers
        )
        responses.append(response)
    
    # Check if rate limiting is triggered
    rate_limited_responses = [r for r in responses if r.status_code == 429]
    assert len(rate_limited_responses) > 0
    
    # Validate rate limit error response
    rate_limit_response = rate_limited_responses[0]
    error_data = rate_limit_response.json()
    assert error_data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
```

---

## Test Configuration and Setup

### API Client Setup
```python
# conftest.py
@pytest.fixture
async def api_client():
    """Setup async HTTP client for API testing"""
    async with httpx.AsyncClient(
        app=app,
        base_url="http://testserver"
    ) as client:
        yield client

@pytest.fixture
def auth_headers():
    """Provide authentication headers for API requests"""
    token = create_test_jwt_token(user_id="test-user", role="qa")
    return {"Authorization": f"Bearer {token}"}
```

### Test Data Setup
```python
@pytest.fixture
async def setup_test_data(db_session):
    """Setup test data for API integration tests"""
    # Create test speakers
    test_speakers = [
        create_test_speaker("speaker-123", "medium_touch"),
        create_test_speaker("speaker-456", "high_touch"),
    ]
    
    # Create test error reports
    test_errors = [
        create_test_error_report("speaker-123", enhanced_metadata=True),
        create_test_error_report("speaker-456", enhanced_metadata=True),
    ]
    
    db_session.add_all(test_speakers + test_errors)
    await db_session.commit()
```

### Performance Testing
```python
@pytest.mark.performance
async def test_api_response_times(self, api_client, auth_headers):
    """Test API response times meet performance requirements"""
    
    endpoints = [
        "/api/v1/speakers/speaker-123/history",
        "/api/v1/dashboard/bucket-overview",
        "/api/v1/dashboard/performance-metrics"
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        response = await api_client.get(endpoint, headers=auth_headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 0.5  # 500ms requirement
```

### Test Execution
```bash
# Run all API integration tests
pytest tests/integration/api/ -v

# Run with performance tests
pytest tests/integration/api/ -v -m "not performance"
pytest tests/integration/api/ -v -m "performance"

# Run specific API test suites
pytest tests/integration/api/test_error_reporting_api.py -v
pytest tests/integration/api/test_speaker_history_api.py -v
pytest tests/integration/api/test_verification_api.py -v
```
