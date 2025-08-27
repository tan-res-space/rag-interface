"""
Integration tests for speaker management workflow.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.models.speaker import Speaker
from app.models.historical_asr_data import HistoricalASRData
from app.domain.enums import SpeakerBucket, QualityTrend
from tests.integration.conftest import create_test_speaker, create_test_historical_data


class TestSpeakerManagementWorkflow:
    """Test complete speaker management workflow."""

    async def test_create_speaker_workflow(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test complete speaker creation workflow."""
        
        # Step 1: Create new speaker
        speaker_data = {
            "speaker_identifier": "WORKFLOW_001",
            "speaker_name": "Dr. Workflow Test",
            "current_bucket": "MEDIUM_TOUCH",
            "note_count": 25,
            "average_ser_score": 15.5,
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
        created_speaker = response.json()
        speaker_id = created_speaker["speaker_id"]
        
        # Verify speaker was created correctly
        assert created_speaker["speaker_identifier"] == speaker_data["speaker_identifier"]
        assert created_speaker["current_bucket"] == speaker_data["current_bucket"]
        
        # Step 2: Add historical ASR data
        historical_data = []
        for i in range(10):
            data = {
                "speaker_id": speaker_id,
                "original_asr_text": f"Sample ASR text {i} with some errors.",
                "final_reference_text": f"Sample reference text {i} corrected.",
                "ser_score": 12.0 + i * 0.5,
                "edit_distance": 6 + i,
                "insertions": 2,
                "deletions": 1,
                "substitutions": 3,
                "moves": 0,
                "quality_level": "medium",
                "is_acceptable_quality": True,
                "metadata_": {"note_id": f"NOTE_{i}"}
            }
            historical_data.append(data)
        
        response = await test_client.post(
            f"/api/v1/speakers/{speaker_id}/historical-data/batch",
            json={"data": historical_data},
            headers=auth_headers
        )
        assert response.status_code == 201
        
        # Step 3: Verify speaker statistics updated
        response = await test_client.get(
            f"/api/v1/speakers/{speaker_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_speaker = response.json()
        
        # Should have updated statistics
        assert updated_speaker["note_count"] >= 10
        assert updated_speaker["has_sufficient_data"] is True
        
        # Step 4: Get speaker recommendations
        response = await test_client.get(
            f"/api/v1/speakers/{speaker_id}/recommendations",
            headers=auth_headers
        )
        assert response.status_code == 200
        recommendations = response.json()
        
        assert "bucket_recommendation" in recommendations
        assert "confidence_score" in recommendations
        assert "reasoning" in recommendations

    async def test_speaker_search_and_filtering(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker]
    ):
        """Test speaker search and filtering functionality."""
        
        # Test search by name
        response = await test_client.get(
            "/api/v1/speakers/search",
            params={"query": "John"},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()
        assert len(results["speakers"]) >= 1
        assert any("John" in speaker["speaker_name"] for speaker in results["speakers"])
        
        # Test filter by bucket
        response = await test_client.get(
            "/api/v1/speakers/",
            params={"bucket": "HIGH_TOUCH"},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()
        assert all(speaker["current_bucket"] == "HIGH_TOUCH" for speaker in results["speakers"])
        
        # Test filter by quality trend
        response = await test_client.get(
            "/api/v1/speakers/",
            params={"quality_trend": "IMPROVING"},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()
        assert all(speaker["quality_trend"] == "IMPROVING" for speaker in results["speakers"])
        
        # Test filter by transition eligibility
        response = await test_client.get(
            "/api/v1/speakers/",
            params={"should_transition": True},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()
        assert all(speaker["should_transition"] is True for speaker in results["speakers"])

    async def test_speaker_statistics_calculation(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test speaker statistics calculation workflow."""
        
        # Create speaker with known data
        speaker = await create_test_speaker(
            db_session,
            identifier="STATS_TEST",
            name="Statistics Test Speaker"
        )
        
        # Add historical data with known SER scores
        ser_scores = [10.0, 12.0, 8.0, 15.0, 11.0]
        for i, score in enumerate(ser_scores):
            data = HistoricalASRData(
                speaker_id=speaker.speaker_id,
                original_asr_text=f"Test text {i}",
                final_reference_text=f"Reference text {i}",
                ser_score=score,
                edit_distance=int(score),
                insertions=2,
                deletions=1,
                substitutions=3,
                moves=0,
                quality_level="medium",
                is_acceptable_quality=score < 12.0,
                metadata_={"test": True}
            )
            db_session.add(data)
        
        await db_session.commit()
        
        # Trigger statistics recalculation
        response = await test_client.post(
            f"/api/v1/speakers/{speaker.speaker_id}/recalculate-statistics",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify calculated statistics
        response = await test_client.get(
            f"/api/v1/speakers/{speaker.speaker_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_speaker = response.json()
        
        expected_average = sum(ser_scores) / len(ser_scores)
        assert abs(updated_speaker["average_ser_score"] - expected_average) < 0.1
        assert updated_speaker["note_count"] == len(ser_scores)

    async def test_bucket_transition_workflow(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker]
    ):
        """Test complete bucket transition workflow."""
        
        speaker = sample_speakers[0]  # Should have should_transition=True
        original_bucket = speaker.current_bucket
        
        # Step 1: Create transition request
        transition_data = {
            "speaker_id": speaker.speaker_id,
            "current_bucket": original_bucket.value,
            "proposed_bucket": "MEDIUM_TOUCH",
            "justification": "Improved SER scores over recent period",
            "supporting_data": {
                "average_ser_improvement": 5.2,
                "recent_note_count": 25,
                "quality_trend": "improving"
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
        
        # Verify request was created
        assert transition_request["status"] == "pending"
        assert transition_request["speaker_id"] == speaker.speaker_id
        
        # Step 2: Review and approve transition
        review_data = {
            "decision": "approved",
            "reviewer_comments": "Statistics support the transition",
            "effective_date": "2024-01-15"
        }
        
        response = await test_client.post(
            f"/api/v1/bucket-transitions/{request_id}/review",
            json=review_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 3: Verify speaker bucket was updated
        response = await test_client.get(
            f"/api/v1/speakers/{speaker.speaker_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_speaker = response.json()
        
        assert updated_speaker["current_bucket"] == "MEDIUM_TOUCH"
        assert updated_speaker["should_transition"] is False  # Should be reset

    async def test_bulk_operations(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test bulk operations on speakers."""
        
        # Create multiple speakers for bulk operations
        speaker_ids = []
        for i in range(5):
            speaker = await create_test_speaker(
                db_session,
                identifier=f"BULK_{i}",
                name=f"Bulk Test Speaker {i}",
                bucket=SpeakerBucket.HIGH_TOUCH
            )
            speaker_ids.append(speaker.speaker_id)
        
        # Test bulk statistics recalculation
        response = await test_client.post(
            "/api/v1/speakers/bulk/recalculate-statistics",
            json={"speaker_ids": speaker_ids},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()
        assert len(results["results"]) == len(speaker_ids)
        assert all(result["success"] for result in results["results"])
        
        # Test bulk bucket update
        response = await test_client.post(
            "/api/v1/speakers/bulk/update-bucket",
            json={
                "speaker_ids": speaker_ids[:3],
                "new_bucket": "MEDIUM_TOUCH",
                "reason": "Bulk update for testing"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify updates
        for speaker_id in speaker_ids[:3]:
            response = await test_client.get(
                f"/api/v1/speakers/{speaker_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            speaker = response.json()
            assert speaker["current_bucket"] == "MEDIUM_TOUCH"

    async def test_speaker_analytics_workflow(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker],
        sample_historical_data: List[HistoricalASRData]
    ):
        """Test speaker analytics and reporting workflow."""
        
        # Test speaker performance analytics
        response = await test_client.get(
            f"/api/v1/speakers/{sample_speakers[0].speaker_id}/analytics",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "include_trends": True
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        analytics = response.json()
        
        assert "performance_metrics" in analytics
        assert "quality_trends" in analytics
        assert "ser_distribution" in analytics
        assert "improvement_analysis" in analytics
        
        # Test bucket distribution analytics
        response = await test_client.get(
            "/api/v1/speakers/analytics/bucket-distribution",
            headers=auth_headers
        )
        assert response.status_code == 200
        distribution = response.json()
        
        assert "bucket_counts" in distribution
        assert "quality_metrics" in distribution
        assert "transition_statistics" in distribution
        
        # Test quality improvement report
        response = await test_client.get(
            "/api/v1/speakers/analytics/quality-improvement",
            params={"period": "last_30_days"},
            headers=auth_headers
        )
        assert response.status_code == 200
        report = response.json()
        
        assert "improvement_summary" in report
        assert "top_improvers" in report
        assert "recommendations" in report

    async def test_error_handling_and_validation(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test error handling and input validation."""
        
        # Test invalid speaker creation
        invalid_speaker_data = {
            "speaker_identifier": "",  # Empty identifier
            "speaker_name": "Test Speaker",
            "current_bucket": "INVALID_BUCKET",  # Invalid bucket
            "average_ser_score": -5.0  # Invalid score
        }
        
        response = await test_client.post(
            "/api/v1/speakers/",
            json=invalid_speaker_data,
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # Test non-existent speaker access
        response = await test_client.get(
            "/api/v1/speakers/non-existent-id",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # Test invalid search parameters
        response = await test_client.get(
            "/api/v1/speakers/search",
            params={"query": ""},  # Empty query
            headers=auth_headers
        )
        assert response.status_code == 400
        
        # Test unauthorized access
        response = await test_client.get("/api/v1/speakers/")
        assert response.status_code == 401

    async def test_concurrent_operations(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test concurrent operations on speakers."""
        import asyncio
        
        # Create a speaker for concurrent testing
        speaker = await create_test_speaker(
            db_session,
            identifier="CONCURRENT_TEST",
            name="Concurrent Test Speaker"
        )
        
        # Define concurrent operations
        async def update_speaker_stats():
            return await test_client.post(
                f"/api/v1/speakers/{speaker.speaker_id}/recalculate-statistics",
                headers=auth_headers
            )
        
        async def add_historical_data():
            data = {
                "speaker_id": speaker.speaker_id,
                "original_asr_text": "Concurrent test data",
                "final_reference_text": "Concurrent reference",
                "ser_score": 10.0,
                "edit_distance": 5,
                "insertions": 1,
                "deletions": 1,
                "substitutions": 2,
                "moves": 0,
                "quality_level": "medium",
                "is_acceptable_quality": True
            }
            return await test_client.post(
                f"/api/v1/speakers/{speaker.speaker_id}/historical-data",
                json=data,
                headers=auth_headers
            )
        
        # Execute concurrent operations
        tasks = [
            update_speaker_stats(),
            add_historical_data(),
            update_speaker_stats(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify no exceptions occurred
        for result in results:
            assert not isinstance(result, Exception)
            assert result.status_code in [200, 201]
