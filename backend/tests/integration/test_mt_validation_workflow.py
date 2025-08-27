"""
Integration tests for MT validation workflow.
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.models.speaker import Speaker
from app.models.validation_test_data import ValidationTestData
from app.models.mt_validation_session import MTValidationSession
from app.models.mt_feedback import MTFeedback
from app.domain.enums import SessionStatus, ImprovementAssessment
from tests.integration.conftest import create_test_speaker


class TestMTValidationWorkflow:
    """Test complete MT validation workflow."""

    async def test_complete_validation_session_workflow(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker],
        sample_validation_data: List[ValidationTestData]
    ):
        """Test complete MT validation session workflow from start to finish."""
        
        speaker = sample_speakers[0]
        
        # Step 1: Start validation session
        session_data = {
            "speaker_id": speaker.speaker_id,
            "session_name": "Complete Workflow Test Session",
            "test_data_ids": [data.data_id for data in sample_validation_data[:3]],
            "mt_user_id": "test-mt-user",
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
        
        # Verify session was created correctly
        assert session["status"] == "active"
        assert session["progress_percentage"] == 0.0
        assert len(session["test_data_ids"]) == 3
        
        # Step 2: Get validation test data for session
        response = await test_client.get(
            f"/api/v1/mt-validation/sessions/{session_id}/test-data",
            headers=auth_headers
        )
        assert response.status_code == 200
        test_data = response.json()
        
        assert len(test_data["items"]) == 3
        assert test_data["current_index"] == 0
        
        # Step 3: Submit feedback for each validation item
        feedback_items = []
        for i, item in enumerate(test_data["items"]):
            feedback_data = {
                "session_id": session_id,
                "historical_data_id": item["historical_data_id"],
                "original_asr_text": item["original_asr_text"],
                "rag_corrected_text": item["rag_corrected_text"],
                "final_reference_text": item["final_reference_text"],
                "mt_feedback_rating": 4 + (i % 2),  # Alternate between 4 and 5
                "mt_comments": f"Test feedback for item {i}",
                "improvement_assessment": ImprovementAssessment.MODERATE.value if i % 2 == 0 else ImprovementAssessment.SIGNIFICANT.value,
                "recommended_for_bucket_change": i == 2,  # Only last item
                "feedback_metadata": {
                    "review_time_seconds": 120 + i * 30,
                    "auto_advance": True
                }
            }
            
            response = await test_client.post(
                f"/api/v1/mt-validation/sessions/{session_id}/feedback",
                json=feedback_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            feedback = response.json()
            feedback_items.append(feedback)
            
            # Verify feedback was recorded
            assert feedback["mt_feedback_rating"] == feedback_data["mt_feedback_rating"]
            assert feedback["improvement_assessment"] == feedback_data["improvement_assessment"]
        
        # Step 4: Complete the session
        completion_data = {
            "session_id": session_id,
            "completion_notes": "Session completed successfully during integration test"
        }
        
        response = await test_client.post(
            f"/api/v1/mt-validation/sessions/{session_id}/complete",
            json=completion_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        completed_session = response.json()
        
        # Verify session completion
        assert completed_session["status"] == "completed"
        assert completed_session["progress_percentage"] == 100.0
        assert completed_session["completion_date"] is not None
        
        # Step 5: Get session summary
        response = await test_client.get(
            f"/api/v1/mt-validation/sessions/{session_id}/summary",
            headers=auth_headers
        )
        assert response.status_code == 200
        summary = response.json()
        
        assert summary["total_feedback_items"] == 3
        assert summary["average_rating"] > 0
        assert "improvement_distribution" in summary
        assert summary["bucket_change_recommendations"] == 1

    async def test_validation_session_management(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker],
        sample_validation_data: List[ValidationTestData]
    ):
        """Test validation session management operations."""
        
        speaker = sample_speakers[0]
        
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_data = {
                "speaker_id": speaker.speaker_id,
                "session_name": f"Management Test Session {i}",
                "test_data_ids": [sample_validation_data[i].data_id],
                "mt_user_id": "test-mt-user"
            }
            
            response = await test_client.post(
                "/api/v1/mt-validation/sessions",
                json=session_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            session_ids.append(response.json()["session_id"])
        
        # Test session listing with filters
        response = await test_client.get(
            "/api/v1/mt-validation/sessions",
            params={"status": "active", "mt_user_id": "test-mt-user"},
            headers=auth_headers
        )
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions["sessions"]) == 3
        
        # Test session pause
        response = await test_client.post(
            f"/api/v1/mt-validation/sessions/{session_ids[0]}/pause",
            headers=auth_headers
        )
        assert response.status_code == 200
        paused_session = response.json()
        assert paused_session["status"] == "paused"
        
        # Test session resume
        response = await test_client.post(
            f"/api/v1/mt-validation/sessions/{session_ids[0]}/resume",
            headers=auth_headers
        )
        assert response.status_code == 200
        resumed_session = response.json()
        assert resumed_session["status"] == "active"
        
        # Test session cancellation
        response = await test_client.post(
            f"/api/v1/mt-validation/sessions/{session_ids[1]}/cancel",
            json={"reason": "Test cancellation"},
            headers=auth_headers
        )
        assert response.status_code == 200
        cancelled_session = response.json()
        assert cancelled_session["status"] == "cancelled"

    async def test_validation_data_generation(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test validation test data generation workflow."""
        
        # Create speaker with sufficient historical data
        speaker = await create_test_speaker(
            db_session,
            identifier="VALIDATION_GEN_TEST",
            name="Validation Generation Test Speaker"
        )
        
        # Add historical data for validation generation
        historical_data = []
        for i in range(20):
            data = {
                "speaker_id": speaker.speaker_id,
                "original_asr_text": f"Original ASR text {i} with various errors and mistakes.",
                "final_reference_text": f"Final reference text {i} with proper corrections.",
                "ser_score": 10.0 + (i % 10),
                "edit_distance": 5 + (i % 5),
                "insertions": 1 + (i % 3),
                "deletions": 1,
                "substitutions": 2 + (i % 2),
                "moves": 0,
                "quality_level": "medium" if i % 2 == 0 else "high",
                "is_acceptable_quality": i % 3 != 0,
                "metadata_": {"note_id": f"NOTE_{i}"}
            }
            
            response = await test_client.post(
                f"/api/v1/speakers/{speaker.speaker_id}/historical-data",
                json=data,
                headers=auth_headers
            )
            assert response.status_code == 201
        
        # Generate validation test data
        generation_request = {
            "speaker_id": speaker.speaker_id,
            "count": 10,
            "priority": "medium",
            "selection_criteria": {
                "min_ser_score": 5.0,
                "max_ser_score": 20.0,
                "quality_levels": ["medium", "high"],
                "require_improvements": True
            }
        }
        
        response = await test_client.post(
            "/api/v1/mt-validation/generate-test-data",
            json=generation_request,
            headers=auth_headers
        )
        assert response.status_code == 201
        generation_result = response.json()
        
        assert generation_result["generated_count"] > 0
        assert len(generation_result["test_data_ids"]) == generation_result["generated_count"]
        
        # Verify generated test data
        for test_data_id in generation_result["test_data_ids"]:
            response = await test_client.get(
                f"/api/v1/mt-validation/test-data/{test_data_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            test_data = response.json()
            
            assert test_data["speaker_id"] == speaker.speaker_id
            assert "original_ser_metrics" in test_data
            assert "corrected_ser_metrics" in test_data
            assert "improvement_metrics" in test_data

    async def test_feedback_analytics_and_reporting(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_validation_session: MTValidationSession,
        sample_validation_data: List[ValidationTestData]
    ):
        """Test feedback analytics and reporting functionality."""
        
        session_id = sample_validation_session.session_id
        
        # Submit diverse feedback for analytics
        feedback_scenarios = [
            {
                "rating": 5,
                "assessment": ImprovementAssessment.SIGNIFICANT,
                "bucket_change": True,
                "comments": "Excellent improvement in medical terminology"
            },
            {
                "rating": 3,
                "assessment": ImprovementAssessment.MINIMAL,
                "bucket_change": False,
                "comments": "Some improvement but still has issues"
            },
            {
                "rating": 4,
                "assessment": ImprovementAssessment.MODERATE,
                "bucket_change": False,
                "comments": "Good improvement in overall accuracy"
            }
        ]
        
        for i, scenario in enumerate(feedback_scenarios):
            feedback_data = {
                "session_id": session_id,
                "historical_data_id": sample_validation_data[i].historical_data_id,
                "original_asr_text": sample_validation_data[i].original_asr_text,
                "rag_corrected_text": sample_validation_data[i].rag_corrected_text,
                "final_reference_text": sample_validation_data[i].final_reference_text,
                "mt_feedback_rating": scenario["rating"],
                "mt_comments": scenario["comments"],
                "improvement_assessment": scenario["assessment"].value,
                "recommended_for_bucket_change": scenario["bucket_change"]
            }
            
            response = await test_client.post(
                f"/api/v1/mt-validation/sessions/{session_id}/feedback",
                json=feedback_data,
                headers=auth_headers
            )
            assert response.status_code == 201
        
        # Test MT user statistics
        response = await test_client.get(
            "/api/v1/mt-validation/users/test-user-id/statistics",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        user_stats = response.json()
        
        assert "total_sessions" in user_stats
        assert "total_feedback_items" in user_stats
        assert "average_rating" in user_stats
        assert "productivity_metrics" in user_stats
        
        # Test feedback quality analysis
        response = await test_client.get(
            f"/api/v1/mt-validation/sessions/{session_id}/feedback-analysis",
            headers=auth_headers
        )
        assert response.status_code == 200
        analysis = response.json()
        
        assert "rating_distribution" in analysis
        assert "improvement_assessment_distribution" in analysis
        assert "quality_insights" in analysis
        assert "recommendations" in analysis

    async def test_validation_workflow_performance(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession,
        performance_test_data: Dict
    ):
        """Test validation workflow performance with larger datasets."""
        
        # Create speaker for performance testing
        speaker = await create_test_speaker(
            db_session,
            identifier="PERF_TEST_SPEAKER",
            name="Performance Test Speaker"
        )
        
        # Generate large validation dataset
        validation_data_ids = []
        batch_size = performance_test_data["batch_size"]
        total_items = performance_test_data["validation_data_per_speaker"]
        
        for batch_start in range(0, total_items, batch_size):
            batch_end = min(batch_start + batch_size, total_items)
            batch_data = []
            
            for i in range(batch_start, batch_end):
                data = {
                    "speaker_id": speaker.speaker_id,
                    "original_asr_text": f"Performance test ASR text {i} with errors.",
                    "rag_corrected_text": f"Performance test corrected text {i}.",
                    "final_reference_text": f"Performance test reference text {i}.",
                    "original_ser_metrics": {
                        "ser_score": 15.0 + (i % 10),
                        "edit_distance": 8,
                        "quality_level": "medium"
                    },
                    "corrected_ser_metrics": {
                        "ser_score": 8.0 + (i % 5),
                        "edit_distance": 4,
                        "quality_level": "high"
                    },
                    "improvement_metrics": {
                        "improvement": 7.0,
                        "improvement_percentage": 46.7,
                        "is_significant_improvement": True
                    },
                    "priority": "medium"
                }
                batch_data.append(data)
            
            # Create batch of validation data
            response = await test_client.post(
                "/api/v1/mt-validation/test-data/batch",
                json={"test_data": batch_data},
                headers=auth_headers
            )
            assert response.status_code == 201
            batch_result = response.json()
            validation_data_ids.extend(batch_result["created_ids"])
        
        # Create large validation session
        import time
        start_time = time.time()
        
        session_data = {
            "speaker_id": speaker.speaker_id,
            "session_name": "Performance Test Session",
            "test_data_ids": validation_data_ids,
            "mt_user_id": "perf-test-user"
        }
        
        response = await test_client.post(
            "/api/v1/mt-validation/sessions",
            json=session_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        session = response.json()
        session_creation_time = time.time() - start_time
        
        # Verify performance metrics
        assert session_creation_time < 5.0  # Should create session in under 5 seconds
        assert len(session["test_data_ids"]) == total_items
        
        # Test batch feedback submission performance
        start_time = time.time()
        
        # Submit feedback for first 10 items to test performance
        for i in range(min(10, len(validation_data_ids))):
            feedback_data = {
                "session_id": session["session_id"],
                "historical_data_id": f"hist-{i}",
                "original_asr_text": f"Test text {i}",
                "rag_corrected_text": f"Corrected text {i}",
                "final_reference_text": f"Reference text {i}",
                "mt_feedback_rating": 4,
                "improvement_assessment": ImprovementAssessment.MODERATE.value,
                "recommended_for_bucket_change": False
            }
            
            response = await test_client.post(
                f"/api/v1/mt-validation/sessions/{session['session_id']}/feedback",
                json=feedback_data,
                headers=auth_headers
            )
            assert response.status_code == 201
        
        feedback_submission_time = time.time() - start_time
        avg_feedback_time = feedback_submission_time / 10
        
        # Verify feedback submission performance
        assert avg_feedback_time < 1.0  # Should submit feedback in under 1 second per item

    async def test_concurrent_validation_sessions(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker],
        sample_validation_data: List[ValidationTestData]
    ):
        """Test concurrent validation sessions."""
        
        # Create multiple concurrent sessions
        async def create_and_run_session(speaker_index: int):
            speaker = sample_speakers[speaker_index % len(sample_speakers)]
            
            session_data = {
                "speaker_id": speaker.speaker_id,
                "session_name": f"Concurrent Session {speaker_index}",
                "test_data_ids": [sample_validation_data[speaker_index].data_id],
                "mt_user_id": f"concurrent-user-{speaker_index}"
            }
            
            # Create session
            response = await test_client.post(
                "/api/v1/mt-validation/sessions",
                json=session_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            session = response.json()
            
            # Submit feedback
            feedback_data = {
                "session_id": session["session_id"],
                "historical_data_id": sample_validation_data[speaker_index].historical_data_id,
                "original_asr_text": sample_validation_data[speaker_index].original_asr_text,
                "rag_corrected_text": sample_validation_data[speaker_index].rag_corrected_text,
                "final_reference_text": sample_validation_data[speaker_index].final_reference_text,
                "mt_feedback_rating": 4,
                "improvement_assessment": ImprovementAssessment.MODERATE.value,
                "recommended_for_bucket_change": False
            }
            
            response = await test_client.post(
                f"/api/v1/mt-validation/sessions/{session['session_id']}/feedback",
                json=feedback_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            
            return session["session_id"]
        
        # Run concurrent sessions
        concurrent_count = 5
        tasks = [create_and_run_session(i) for i in range(concurrent_count)]
        session_ids = await asyncio.gather(*tasks)
        
        # Verify all sessions were created and processed successfully
        assert len(session_ids) == concurrent_count
        
        for session_id in session_ids:
            response = await test_client.get(
                f"/api/v1/mt-validation/sessions/{session_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            session = response.json()
            assert session["status"] in ["active", "completed"]
