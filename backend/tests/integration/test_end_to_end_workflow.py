"""
End-to-end integration tests for complete speaker bucket management workflow.
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.models.speaker import Speaker
from app.domain.enums import SpeakerBucket, QualityTrend, ImprovementAssessment, SessionStatus
from tests.integration.conftest import create_test_speaker


class TestEndToEndWorkflow:
    """Test complete end-to-end speaker bucket management workflow."""

    async def test_complete_speaker_lifecycle(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test complete speaker lifecycle from creation to bucket transition."""
        
        # Phase 1: Speaker Creation and Initial Setup
        print("Phase 1: Creating new speaker...")
        
        speaker_data = {
            "speaker_identifier": "E2E_LIFECYCLE_001",
            "speaker_name": "Dr. End-to-End Test",
            "current_bucket": "HIGH_TOUCH",
            "note_count": 0,
            "average_ser_score": 0.0,
            "quality_trend": "STABLE",
            "should_transition": False,
            "has_sufficient_data": False
        }
        
        response = await test_client.post(
            "/api/v1/speakers/",
            json=speaker_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        speaker = response.json()
        speaker_id = speaker["speaker_id"]
        
        # Phase 2: Add Historical ASR Data
        print("Phase 2: Adding historical ASR data...")
        
        historical_data_batch = []
        for i in range(25):  # Add sufficient data for processing
            data = {
                "speaker_id": speaker_id,
                "original_asr_text": f"The patient has diabetes and hypertension. Visit {i} shows improvement in glucose control.",
                "final_reference_text": f"The patient has diabetes and hypertension. Visit {i} shows improvement in glucose control.",
                "ser_score": 20.0 - (i * 0.5),  # Gradually improving scores
                "edit_distance": 10 - (i // 5),
                "insertions": 3 - (i // 10),
                "deletions": 2 - (i // 15),
                "substitutions": 4 - (i // 8),
                "moves": 1 if i % 5 == 0 else 0,
                "quality_level": "high" if i > 15 else "medium",
                "is_acceptable_quality": i > 10,
                "metadata_": {
                    "note_id": f"NOTE_E2E_{i}",
                    "visit_date": f"2024-01-{i+1:02d}",
                    "note_type": "progress_note"
                }
            }
            historical_data_batch.append(data)
        
        response = await test_client.post(
            f"/api/v1/speakers/{speaker_id}/historical-data/batch",
            json={"data": historical_data_batch},
            headers=auth_headers
        )
        assert response.status_code == 201
        
        # Phase 3: Recalculate Speaker Statistics
        print("Phase 3: Recalculating speaker statistics...")
        
        response = await test_client.post(
            f"/api/v1/speakers/{speaker_id}/recalculate-statistics",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify updated statistics
        response = await test_client.get(
            f"/api/v1/speakers/{speaker_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_speaker = response.json()
        
        assert updated_speaker["note_count"] == 25
        assert updated_speaker["has_sufficient_data"] is True
        assert updated_speaker["average_ser_score"] < 20.0  # Should show improvement
        
        # Phase 4: RAG Processing
        print("Phase 4: Starting RAG processing...")
        
        rag_job_data = {
            "speaker_id": speaker_id,
            "processing_type": "error_correction_pairs",
            "parameters": {
                "min_error_frequency": 1,
                "similarity_threshold": 0.7,
                "max_pairs_per_speaker": 50
            }
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-speaker",
            json=rag_job_data,
            headers=auth_headers
        )
        assert response.status_code == 202
        rag_job = response.json()
        rag_job_id = rag_job["job_id"]
        
        # Wait for RAG processing to complete
        max_attempts = 30
        for attempt in range(max_attempts):
            response = await test_client.get(
                f"/api/v1/rag/jobs/{rag_job_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            job_status = response.json()
            
            if job_status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(1)
        
        assert job_status["status"] == "completed"
        
        # Phase 5: Generate Validation Test Data
        print("Phase 5: Generating validation test data...")
        
        validation_generation_request = {
            "speaker_id": speaker_id,
            "count": 10,
            "priority": "high",
            "selection_criteria": {
                "min_ser_score": 5.0,
                "max_ser_score": 25.0,
                "quality_levels": ["medium", "high"],
                "require_improvements": True
            }
        }
        
        response = await test_client.post(
            "/api/v1/mt-validation/generate-test-data",
            json=validation_generation_request,
            headers=auth_headers
        )
        assert response.status_code == 201
        validation_data = response.json()
        test_data_ids = validation_data["test_data_ids"]
        
        assert len(test_data_ids) > 0
        
        # Phase 6: MT Validation Session
        print("Phase 6: Running MT validation session...")
        
        session_data = {
            "speaker_id": speaker_id,
            "session_name": "E2E Lifecycle Validation Session",
            "test_data_ids": test_data_ids,
            "mt_user_id": "e2e-test-user",
            "session_metadata": {
                "priority": "high",
                "auto_advance": True,
                "include_ser_metrics": True
            }
        }
        
        response = await test_client.post(
            "/api/v1/mt-validation/sessions",
            json=session_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        session = response.json()
        session_id = session["session_id"]
        
        # Get test data for feedback submission
        response = await test_client.get(
            f"/api/v1/mt-validation/sessions/{session_id}/test-data",
            headers=auth_headers
        )
        assert response.status_code == 200
        session_test_data = response.json()
        
        # Submit positive feedback for all items
        for i, item in enumerate(session_test_data["items"]):
            feedback_data = {
                "session_id": session_id,
                "historical_data_id": item["historical_data_id"],
                "original_asr_text": item["original_asr_text"],
                "rag_corrected_text": item["rag_corrected_text"],
                "final_reference_text": item["final_reference_text"],
                "mt_feedback_rating": 5,  # High rating
                "mt_comments": f"Excellent improvement in item {i}",
                "improvement_assessment": ImprovementAssessment.SIGNIFICANT.value,
                "recommended_for_bucket_change": i >= len(session_test_data["items"]) - 3,  # Recommend last 3
                "feedback_metadata": {
                    "review_time_seconds": 90,
                    "auto_advance": True
                }
            }
            
            response = await test_client.post(
                f"/api/v1/mt-validation/sessions/{session_id}/feedback",
                json=feedback_data,
                headers=auth_headers
            )
            assert response.status_code == 201
        
        # Complete the session
        completion_data = {
            "session_id": session_id,
            "completion_notes": "E2E test session completed with excellent results"
        }
        
        response = await test_client.post(
            f"/api/v1/mt-validation/sessions/{session_id}/complete",
            json=completion_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Phase 7: Bucket Transition Request
        print("Phase 7: Creating bucket transition request...")
        
        # Get session summary for transition justification
        response = await test_client.get(
            f"/api/v1/mt-validation/sessions/{session_id}/summary",
            headers=auth_headers
        )
        assert response.status_code == 200
        session_summary = response.json()
        
        transition_data = {
            "speaker_id": speaker_id,
            "current_bucket": "HIGH_TOUCH",
            "proposed_bucket": "MEDIUM_TOUCH",
            "justification": "Consistent high-quality validation results and significant SER improvements",
            "supporting_data": {
                "validation_session_id": session_id,
                "average_rating": session_summary["average_rating"],
                "bucket_recommendations": session_summary["bucket_change_recommendations"],
                "ser_improvement": "Significant improvement from 20.0 to sub-10.0 average"
            }
        }
        
        response = await test_client.post(
            "/api/v1/bucket-transitions/",
            json=transition_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        transition_request = response.json()
        request_id = transition_request["request_id"]
        
        # Phase 8: Approve Transition
        print("Phase 8: Approving bucket transition...")
        
        review_data = {
            "decision": "approved",
            "reviewer_comments": "E2E test shows clear quality improvement. Approved for transition.",
            "effective_date": "2024-01-31"
        }
        
        response = await test_client.post(
            f"/api/v1/bucket-transitions/{request_id}/review",
            json=review_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Phase 9: Verify Final State
        print("Phase 9: Verifying final speaker state...")
        
        response = await test_client.get(
            f"/api/v1/speakers/{speaker_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        final_speaker = response.json()
        
        # Verify successful transition
        assert final_speaker["current_bucket"] == "MEDIUM_TOUCH"
        assert final_speaker["should_transition"] is False
        assert final_speaker["quality_trend"] == "IMPROVING"
        assert final_speaker["note_count"] == 25
        assert final_speaker["has_sufficient_data"] is True
        
        print("✅ Complete speaker lifecycle test passed!")

    async def test_multi_speaker_workflow(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test workflow with multiple speakers in parallel."""
        
        print("Starting multi-speaker workflow test...")
        
        # Create multiple speakers
        speaker_count = 3
        speakers = []
        
        for i in range(speaker_count):
            speaker_data = {
                "speaker_identifier": f"MULTI_E2E_{i:03d}",
                "speaker_name": f"Dr. Multi Test {i}",
                "current_bucket": ["HIGH_TOUCH", "MEDIUM_TOUCH", "LOW_TOUCH"][i],
                "note_count": 0,
                "average_ser_score": 0.0,
                "quality_trend": "STABLE",
                "should_transition": False,
                "has_sufficient_data": False
            }
            
            response = await test_client.post(
                "/api/v1/speakers/",
                json=speaker_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            speakers.append(response.json())
        
        # Add historical data for all speakers concurrently
        async def add_speaker_data(speaker):
            historical_data = []
            for j in range(15):
                data = {
                    "speaker_id": speaker["speaker_id"],
                    "original_asr_text": f"Multi-speaker test data {j} for {speaker['speaker_name']}.",
                    "final_reference_text": f"Multi-speaker reference data {j} for {speaker['speaker_name']}.",
                    "ser_score": 15.0 - (j * 0.3),
                    "edit_distance": 8 - (j // 3),
                    "insertions": 2,
                    "deletions": 1,
                    "substitutions": 3,
                    "moves": 0,
                    "quality_level": "medium",
                    "is_acceptable_quality": j > 5,
                    "metadata_": {"multi_test": True, "speaker_index": speaker["speaker_identifier"]}
                }
                historical_data.append(data)
            
            response = await test_client.post(
                f"/api/v1/speakers/{speaker['speaker_id']}/historical-data/batch",
                json={"data": historical_data},
                headers=auth_headers
            )
            assert response.status_code == 201
            return speaker["speaker_id"]
        
        # Process all speakers concurrently
        speaker_ids = await asyncio.gather(*[add_speaker_data(speaker) for speaker in speakers])
        
        # Batch RAG processing
        batch_rag_data = {
            "speaker_ids": speaker_ids,
            "processing_type": "vectorization",
            "parameters": {
                "chunk_size": 256,
                "overlap": 25,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-batch",
            json=batch_rag_data,
            headers=auth_headers
        )
        assert response.status_code == 202
        batch_job = response.json()
        
        # Wait for batch processing
        max_attempts = 60
        for attempt in range(max_attempts):
            response = await test_client.get(
                f"/api/v1/rag/jobs/{batch_job['job_id']}",
                headers=auth_headers
            )
            assert response.status_code == 200
            job_status = response.json()
            
            if job_status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(2)
        
        assert job_status["status"] == "completed"
        
        # Verify all speakers were processed
        results = job_status["processing_results"]
        assert len(results["speaker_results"]) == speaker_count
        
        print("✅ Multi-speaker workflow test passed!")

    async def test_error_recovery_workflow(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test error recovery and resilience in the workflow."""
        
        print("Starting error recovery workflow test...")
        
        # Create speaker for error testing
        speaker = await create_test_speaker(
            db_session,
            identifier="ERROR_RECOVERY_TEST",
            name="Error Recovery Test Speaker"
        )
        
        # Test 1: Invalid data handling
        invalid_historical_data = {
            "speaker_id": speaker.speaker_id,
            "original_asr_text": "",  # Empty text
            "final_reference_text": "Valid reference text",
            "ser_score": -5.0,  # Invalid score
            "edit_distance": -1,  # Invalid distance
            "quality_level": "invalid_level"  # Invalid level
        }
        
        response = await test_client.post(
            f"/api/v1/speakers/{speaker.speaker_id}/historical-data",
            json=invalid_historical_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error
        
        # Test 2: Add valid data after error
        valid_data = {
            "speaker_id": speaker.speaker_id,
            "original_asr_text": "Valid ASR text for recovery test",
            "final_reference_text": "Valid reference text for recovery test",
            "ser_score": 12.0,
            "edit_distance": 6,
            "insertions": 2,
            "deletions": 1,
            "substitutions": 3,
            "moves": 0,
            "quality_level": "medium",
            "is_acceptable_quality": True
        }
        
        response = await test_client.post(
            f"/api/v1/speakers/{speaker.speaker_id}/historical-data",
            json=valid_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        
        # Test 3: RAG processing with insufficient data
        insufficient_rag_job = {
            "speaker_id": speaker.speaker_id,
            "processing_type": "error_correction_pairs",
            "parameters": {
                "min_error_frequency": 100,  # Too high for available data
                "similarity_threshold": 0.99  # Too strict
            }
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-speaker",
            json=insufficient_rag_job,
            headers=auth_headers
        )
        assert response.status_code == 202
        job = response.json()
        
        # Wait for job to complete (should handle gracefully)
        max_attempts = 30
        for attempt in range(max_attempts):
            response = await test_client.get(
                f"/api/v1/rag/jobs/{job['job_id']}",
                headers=auth_headers
            )
            assert response.status_code == 200
            job_status = response.json()
            
            if job_status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(1)
        
        # Job should complete but with warnings about insufficient data
        assert job_status["status"] == "completed"
        assert "warnings" in job_status.get("processing_results", {})
        
        print("✅ Error recovery workflow test passed!")

    async def test_performance_under_load(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test system performance under load."""
        
        print("Starting performance under load test...")
        
        import time
        
        # Create multiple speakers for load testing
        speaker_count = 5
        speakers = []
        
        start_time = time.time()
        
        for i in range(speaker_count):
            speaker_data = {
                "speaker_identifier": f"LOAD_TEST_{i:03d}",
                "speaker_name": f"Dr. Load Test {i}",
                "current_bucket": "MEDIUM_TOUCH",
                "note_count": 0,
                "average_ser_score": 0.0,
                "quality_trend": "STABLE",
                "should_transition": False,
                "has_sufficient_data": False
            }
            
            response = await test_client.post(
                "/api/v1/speakers/",
                json=speaker_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            speakers.append(response.json())
        
        speaker_creation_time = time.time() - start_time
        print(f"Created {speaker_count} speakers in {speaker_creation_time:.2f} seconds")
        
        # Concurrent data addition
        async def add_bulk_data(speaker):
            data_batch = []
            for j in range(20):
                data = {
                    "speaker_id": speaker["speaker_id"],
                    "original_asr_text": f"Load test data {j} with various medical terms and conditions.",
                    "final_reference_text": f"Load test reference {j} with proper medical terminology.",
                    "ser_score": 10.0 + (j % 10),
                    "edit_distance": 5 + (j % 5),
                    "insertions": 1 + (j % 3),
                    "deletions": 1,
                    "substitutions": 2,
                    "moves": 0,
                    "quality_level": "medium",
                    "is_acceptable_quality": True,
                    "metadata_": {"load_test": True}
                }
                data_batch.append(data)
            
            start = time.time()
            response = await test_client.post(
                f"/api/v1/speakers/{speaker['speaker_id']}/historical-data/batch",
                json={"data": data_batch},
                headers=auth_headers
            )
            duration = time.time() - start
            assert response.status_code == 201
            return duration
        
        # Execute concurrent data addition
        start_time = time.time()
        durations = await asyncio.gather(*[add_bulk_data(speaker) for speaker in speakers])
        total_data_time = time.time() - start_time
        
        print(f"Added bulk data for {speaker_count} speakers in {total_data_time:.2f} seconds")
        print(f"Average per-speaker data addition: {sum(durations)/len(durations):.2f} seconds")
        
        # Performance assertions
        assert speaker_creation_time < 10.0  # Should create speakers quickly
        assert total_data_time < 30.0  # Should handle concurrent data addition
        assert all(duration < 5.0 for duration in durations)  # Each speaker should be fast
        
        print("✅ Performance under load test passed!")

    async def test_data_consistency_workflow(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test data consistency across the entire workflow."""
        
        print("Starting data consistency workflow test...")
        
        # Create speaker with known data
        speaker = await create_test_speaker(
            db_session,
            identifier="CONSISTENCY_TEST",
            name="Data Consistency Test Speaker"
        )
        
        # Add precisely controlled historical data
        known_ser_scores = [15.0, 12.0, 10.0, 8.0, 6.0]
        expected_average = sum(known_ser_scores) / len(known_ser_scores)
        
        for i, score in enumerate(known_ser_scores):
            data = {
                "speaker_id": speaker.speaker_id,
                "original_asr_text": f"Consistency test text {i}",
                "final_reference_text": f"Consistency reference text {i}",
                "ser_score": score,
                "edit_distance": int(score),
                "insertions": 2,
                "deletions": 1,
                "substitutions": 3,
                "moves": 0,
                "quality_level": "high" if score < 10 else "medium",
                "is_acceptable_quality": score < 12,
                "metadata_": {"consistency_test": True, "index": i}
            }
            
            response = await test_client.post(
                f"/api/v1/speakers/{speaker.speaker_id}/historical-data",
                json=data,
                headers=auth_headers
            )
            assert response.status_code == 201
        
        # Recalculate statistics
        response = await test_client.post(
            f"/api/v1/speakers/{speaker.speaker_id}/recalculate-statistics",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify calculated statistics match expected values
        response = await test_client.get(
            f"/api/v1/speakers/{speaker.speaker_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_speaker = response.json()
        
        assert abs(updated_speaker["average_ser_score"] - expected_average) < 0.01
        assert updated_speaker["note_count"] == len(known_ser_scores)
        
        # Verify data consistency in analytics
        response = await test_client.get(
            f"/api/v1/speakers/{speaker.speaker_id}/analytics",
            headers=auth_headers
        )
        assert response.status_code == 200
        analytics = response.json()
        
        # Analytics should reflect the same statistics
        assert abs(analytics["performance_metrics"]["average_ser_score"] - expected_average) < 0.01
        assert analytics["performance_metrics"]["total_notes"] == len(known_ser_scores)
        
        print("✅ Data consistency workflow test passed!")
        
        return {
            "speaker_id": speaker.speaker_id,
            "expected_average": expected_average,
            "actual_average": updated_speaker["average_ser_score"],
            "note_count": updated_speaker["note_count"]
        }
