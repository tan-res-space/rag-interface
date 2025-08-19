"""
End-to-end tests for complete Error Reporting Service workflows.

These tests verify complete business scenarios from start to finish,
including multi-step processes, event propagation, and system integration.
Following TDD principles and testing real-world usage patterns.
"""

import pytest
import asyncio
import json
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Dict, Any, List

from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.error_reporting_service.main import app
from tests.factories import SubmitErrorReportRequestFactory


@pytest.mark.e2e
@pytest.mark.workflows
class TestCompleteErrorReportingWorkflows:
    """End-to-end tests for complete error reporting workflows"""
    
    @pytest.fixture
    def client(self):
        """Create FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """Create async HTTP client"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    def qa_user_headers(self):
        """Create QA user authentication headers"""
        return {
            "Authorization": "Bearer qa.user.token",
            "Content-Type": "application/json",
            "X-User-Role": "qa_personnel",
            "X-Organization-Id": str(uuid4())
        }
    
    @pytest.fixture
    def admin_user_headers(self):
        """Create admin user authentication headers"""
        return {
            "Authorization": "Bearer admin.user.token",
            "Content-Type": "application/json",
            "X-User-Role": "admin",
            "X-Organization-Id": str(uuid4())
        }
    
    def test_complete_error_submission_workflow(self, client, qa_user_headers):
        """Test complete error submission workflow from QA perspective"""
        # Step 1: QA user submits error report
        error_data = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "original_text": "The patient has diabetis and hypertention",
            "corrected_text": "The patient has diabetes and hypertension",
            "error_categories": ["medical_terminology", "spelling"],
            "severity_level": "high",
            "start_position": 16,
            "end_position": 41,
            "context_notes": "Multiple medical terminology errors",
            "metadata": {
                "audio_quality": "good",
                "confidence_score": 0.92,
                "review_priority": "high"
            }
        }
        
        # Act - Submit error report
        submit_response = client.post(
            "/api/v1/errors",
            json=error_data,
            headers=qa_user_headers
        )
        
        # Assert - Submission successful
        assert submit_response.status_code == 201
        submit_data = submit_response.json()
        assert submit_data["status"] == "success"
        error_id = submit_data["error_id"]
        
        # Step 2: Verify error report can be retrieved
        get_response = client.get(
            f"/api/v1/errors/{error_id}",
            headers=qa_user_headers
        )
        
        # Assert - Retrieval successful
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["id"] == error_id
        assert get_data["original_text"] == error_data["original_text"]
        assert get_data["corrected_text"] == error_data["corrected_text"]
        assert get_data["status"] == "pending"
        
        # Step 3: Search for the submitted error
        search_response = client.get(
            "/api/v1/errors",
            headers=qa_user_headers,
            params={
                "severity_level": "high",
                "categories": "medical_terminology",
                "page": 1,
                "size": 10
            }
        )
        
        # Assert - Search finds the error
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["total"] >= 1
        
        # Verify our error is in the results
        error_ids = [item["id"] for item in search_data["items"]]
        assert error_id in error_ids
    
    def test_error_review_and_approval_workflow(self, client, qa_user_headers, admin_user_headers):
        """Test error review and approval workflow"""
        # Step 1: QA user submits error report
        error_data = SubmitErrorReportRequestFactory.create(
            severity_level="critical",
            error_categories=["patient_safety"]
        ).__dict__
        
        submit_response = client.post(
            "/api/v1/errors",
            json=error_data,
            headers=qa_user_headers
        )
        error_id = submit_response.json()["error_id"]
        
        # Step 2: Admin reviews the error report
        get_response = client.get(
            f"/api/v1/errors/{error_id}",
            headers=admin_user_headers
        )
        
        assert get_response.status_code == 200
        error_details = get_response.json()
        assert error_details["severity_level"] == "critical"
        assert "patient_safety" in error_details["error_categories"]
        
        # Step 3: Admin approves the error report
        approval_data = {
            "status": "approved",
            "context_notes": "Approved after review - critical patient safety issue",
            "metadata": {
                "reviewed_by": "admin_user_123",
                "review_date": datetime.utcnow().isoformat(),
                "approval_reason": "Valid critical error requiring immediate attention"
            }
        }
        
        update_response = client.put(
            f"/api/v1/errors/{error_id}",
            json=approval_data,
            headers=admin_user_headers
        )
        
        # Assert - Update successful
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["status"] == "approved"
        assert "Approved after review" in updated_data["context_notes"]
        
        # Step 4: Verify the approval is reflected in search results
        search_response = client.get(
            "/api/v1/errors",
            headers=admin_user_headers,
            params={"status": "approved", "severity_level": "critical"}
        )
        
        assert search_response.status_code == 200
        search_data = search_response.json()
        approved_error_ids = [item["id"] for item in search_data["items"]]
        assert error_id in approved_error_ids
    
    def test_bulk_error_processing_workflow(self, client, qa_user_headers):
        """Test bulk error processing workflow"""
        # Step 1: Submit multiple error reports
        job_id = str(uuid4())
        speaker_id = str(uuid4())
        error_ids = []
        
        error_reports = [
            {
                "job_id": job_id,
                "speaker_id": speaker_id,
                "original_text": f"Error text {i}",
                "corrected_text": f"Corrected text {i}",
                "error_categories": ["grammar"],
                "severity_level": "medium",
                "start_position": 0,
                "end_position": 10,
                "context_notes": f"Error {i} in batch processing",
                "metadata": {"batch_id": "batch_001", "sequence": i}
            }
            for i in range(5)
        ]
        
        for error_data in error_reports:
            response = client.post(
                "/api/v1/errors",
                json=error_data,
                headers=qa_user_headers
            )
            assert response.status_code == 201
            error_ids.append(response.json()["error_id"])
        
        # Step 2: Search for all errors in the batch
        search_response = client.get(
            "/api/v1/errors",
            headers=qa_user_headers,
            params={"job_id": job_id, "page": 1, "size": 10}
        )
        
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["total"] == 5
        
        # Verify all submitted errors are found
        found_error_ids = [item["id"] for item in search_data["items"]]
        for error_id in error_ids:
            assert error_id in found_error_ids
        
        # Step 3: Bulk update all errors in the batch
        for error_id in error_ids:
            update_data = {
                "status": "processed",
                "metadata": {"batch_processed": True, "processing_date": datetime.utcnow().isoformat()}
            }
            
            update_response = client.put(
                f"/api/v1/errors/{error_id}",
                json=update_data,
                headers=qa_user_headers
            )
            assert update_response.status_code == 200
        
        # Step 4: Verify all errors are marked as processed
        processed_search = client.get(
            "/api/v1/errors",
            headers=qa_user_headers,
            params={"job_id": job_id, "status": "processed"}
        )
        
        assert processed_search.status_code == 200
        processed_data = processed_search.json()
        assert processed_data["total"] == 5
    
    def test_error_correction_feedback_loop(self, client, qa_user_headers):
        """Test error correction feedback loop workflow"""
        # Step 1: Submit initial error report
        initial_error = {
            "job_id": str(uuid4()),
            "speaker_id": str(uuid4()),
            "original_text": "The patient has diabetis",
            "corrected_text": "The patient has diabetes",
            "error_categories": ["medical_terminology"],
            "severity_level": "high",
            "start_position": 16,
            "end_position": 24,
            "context_notes": "Initial correction attempt",
            "metadata": {"correction_attempt": 1}
        }
        
        submit_response = client.post(
            "/api/v1/errors",
            json=initial_error,
            headers=qa_user_headers
        )
        error_id = submit_response.json()["error_id"]
        
        # Step 2: Review reveals additional correction needed
        review_update = {
            "corrected_text": "The patient has diabetes mellitus",  # More specific correction
            "context_notes": "Updated to include full medical term",
            "metadata": {
                "correction_attempt": 2,
                "review_feedback": "Correction should be more specific",
                "updated_by": "senior_qa_reviewer"
            }
        }
        
        update_response = client.put(
            f"/api/v1/errors/{error_id}",
            json=review_update,
            headers=qa_user_headers
        )
        
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["corrected_text"] == "The patient has diabetes mellitus"
        assert updated_data["metadata"]["correction_attempt"] == 2
        
        # Step 3: Final approval after correction refinement
        final_approval = {
            "status": "approved",
            "context_notes": "Final correction approved - specific medical terminology used",
            "metadata": {
                "correction_attempt": 2,
                "final_approval": True,
                "approved_by": "medical_terminology_expert"
            }
        }
        
        final_response = client.put(
            f"/api/v1/errors/{error_id}",
            json=final_approval,
            headers=qa_user_headers
        )
        
        assert final_response.status_code == 200
        final_data = final_response.json()
        assert final_data["status"] == "approved"
        assert final_data["metadata"]["final_approval"] is True
    
    def test_error_analytics_workflow(self, client, qa_user_headers):
        """Test error analytics and reporting workflow"""
        # Step 1: Submit errors with various characteristics for analytics
        speaker_id = str(uuid4())
        analytics_errors = [
            {
                "job_id": str(uuid4()),
                "speaker_id": speaker_id,
                "original_text": "diabetis",
                "corrected_text": "diabetes",
                "error_categories": ["medical_terminology"],
                "severity_level": "high",
                "start_position": 0,
                "end_position": 8,
                "metadata": {"error_type": "medical_term"}
            },
            {
                "job_id": str(uuid4()),
                "speaker_id": speaker_id,
                "original_text": "hypertention",
                "corrected_text": "hypertension",
                "error_categories": ["medical_terminology"],
                "severity_level": "high",
                "start_position": 0,
                "end_position": 12,
                "metadata": {"error_type": "medical_term"}
            },
            {
                "job_id": str(uuid4()),
                "speaker_id": speaker_id,
                "original_text": "there house",
                "corrected_text": "their house",
                "error_categories": ["grammar"],
                "severity_level": "low",
                "start_position": 0,
                "end_position": 5,
                "metadata": {"error_type": "grammar"}
            }
        ]
        
        error_ids = []
        for error_data in analytics_errors:
            response = client.post(
                "/api/v1/errors",
                json=error_data,
                headers=qa_user_headers
            )
            assert response.status_code == 201
            error_ids.append(response.json()["error_id"])
        
        # Step 2: Analyze medical terminology errors
        medical_search = client.get(
            "/api/v1/errors",
            headers=qa_user_headers,
            params={
                "categories": "medical_terminology",
                "speaker_id": speaker_id,
                "severity_level": "high"
            }
        )
        
        assert medical_search.status_code == 200
        medical_data = medical_search.json()
        assert medical_data["total"] == 2  # Two medical terminology errors
        
        # Step 3: Analyze grammar errors
        grammar_search = client.get(
            "/api/v1/errors",
            headers=qa_user_headers,
            params={
                "categories": "grammar",
                "speaker_id": speaker_id
            }
        )
        
        assert grammar_search.status_code == 200
        grammar_data = grammar_search.json()
        assert grammar_data["total"] == 1  # One grammar error
        
        # Step 4: Get speaker-specific error patterns
        speaker_search = client.get(
            "/api/v1/errors",
            headers=qa_user_headers,
            params={"speaker_id": speaker_id}
        )
        
        assert speaker_search.status_code == 200
        speaker_data = speaker_search.json()
        assert speaker_data["total"] == 3  # All errors for this speaker
        
        # Verify error distribution
        categories = []
        severities = []
        for item in speaker_data["items"]:
            categories.extend(item["error_categories"])
            severities.append(item["severity_level"])
        
        assert categories.count("medical_terminology") == 2
        assert categories.count("grammar") == 1
        assert severities.count("high") == 2
        assert severities.count("low") == 1
    
    @pytest.mark.asyncio
    async def test_concurrent_error_submission_workflow(self, async_client, qa_user_headers):
        """Test concurrent error submission workflow"""
        # Arrange
        concurrent_errors = [
            SubmitErrorReportRequestFactory.create().__dict__
            for _ in range(10)
        ]
        
        # Act - Submit errors concurrently
        async def submit_error(error_data):
            response = await async_client.post(
                "/api/v1/errors",
                json=error_data,
                headers=qa_user_headers
            )
            return response.status_code, response.json()
        
        results = await asyncio.gather(
            *[submit_error(error_data) for error_data in concurrent_errors],
            return_exceptions=True
        )
        
        # Assert - All submissions successful
        successful_submissions = [
            result for result in results 
            if not isinstance(result, Exception) and result[0] == 201
        ]
        
        assert len(successful_submissions) == 10
        
        # Verify all error IDs are unique
        error_ids = [result[1]["error_id"] for result in successful_submissions]
        assert len(set(error_ids)) == 10
    
    def test_error_lifecycle_complete_workflow(self, client, qa_user_headers, admin_user_headers):
        """Test complete error lifecycle from submission to archival"""
        # Step 1: Submit error report
        error_data = SubmitErrorReportRequestFactory.create(
            severity_level="medium",
            error_categories=["pronunciation"]
        ).__dict__
        
        submit_response = client.post(
            "/api/v1/errors",
            json=error_data,
            headers=qa_user_headers
        )
        error_id = submit_response.json()["error_id"]
        
        # Step 2: Review (pending -> under_review)
        review_update = {
            "status": "under_review",
            "context_notes": "Under review by QA team",
            "metadata": {"reviewer_id": "qa_reviewer_456", "review_started": datetime.utcnow().isoformat()}
        }
        
        client.put(f"/api/v1/errors/{error_id}", json=review_update, headers=qa_user_headers)
        
        # Step 3: Process (under_review -> processed)
        process_update = {
            "status": "processed",
            "context_notes": "Processed and correction validated",
            "metadata": {"processed_by": "qa_processor_789", "processing_completed": datetime.utcnow().isoformat()}
        }
        
        client.put(f"/api/v1/errors/{error_id}", json=process_update, headers=qa_user_headers)
        
        # Step 4: Archive (processed -> archived)
        archive_update = {
            "status": "archived",
            "context_notes": "Archived after successful processing",
            "metadata": {"archived_by": "system_admin", "archive_date": datetime.utcnow().isoformat()}
        }
        
        archive_response = client.put(
            f"/api/v1/errors/{error_id}",
            json=archive_update,
            headers=admin_user_headers
        )
        
        # Assert - Final state verification
        assert archive_response.status_code == 200
        final_data = archive_response.json()
        assert final_data["status"] == "archived"
        assert "Archived after successful processing" in final_data["context_notes"]
        
        # Verify archived error can still be retrieved
        get_response = client.get(f"/api/v1/errors/{error_id}", headers=admin_user_headers)
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "archived"
