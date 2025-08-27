"""
Integration tests for RAG processing workflow.
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.models.speaker import Speaker
from app.models.historical_asr_data import HistoricalASRData
from app.models.rag_processing_job import RAGProcessingJob
from app.domain.enums import SpeakerBucket, JobStatus
from tests.integration.conftest import create_test_speaker, create_test_historical_data


class TestRAGProcessingWorkflow:
    """Test complete RAG processing workflow."""

    async def test_speaker_specific_rag_processing(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test speaker-specific RAG processing workflow."""
        
        # Step 1: Create speaker with historical data
        speaker = await create_test_speaker(
            db_session,
            identifier="RAG_TEST_001",
            name="RAG Test Speaker"
        )
        
        historical_data = await create_test_historical_data(
            db_session,
            speaker.speaker_id,
            count=10
        )
        
        # Step 2: Start RAG processing job
        job_data = {
            "speaker_id": speaker.speaker_id,
            "processing_type": "error_correction_pairs",
            "parameters": {
                "min_error_frequency": 2,
                "similarity_threshold": 0.8,
                "max_pairs_per_speaker": 100
            }
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-speaker",
            json=job_data,
            headers=auth_headers
        )
        assert response.status_code == 202
        job_result = response.json()
        job_id = job_result["job_id"]
        
        # Verify job was created
        assert job_result["status"] == "queued"
        assert job_result["speaker_id"] == speaker.speaker_id
        
        # Step 3: Monitor job progress
        max_attempts = 30
        for attempt in range(max_attempts):
            response = await test_client.get(
                f"/api/v1/rag/jobs/{job_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            job_status = response.json()
            
            if job_status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(1)
        
        # Verify job completed successfully
        assert job_status["status"] == "completed"
        assert "processing_results" in job_status
        assert job_status["processing_results"]["pairs_generated"] > 0
        
        # Step 4: Verify error-correction pairs were created
        response = await test_client.get(
            f"/api/v1/rag/speakers/{speaker.speaker_id}/error-correction-pairs",
            headers=auth_headers
        )
        assert response.status_code == 200
        pairs = response.json()
        
        assert len(pairs["pairs"]) > 0
        for pair in pairs["pairs"]:
            assert "error_text" in pair
            assert "correction_text" in pair
            assert "frequency" in pair
            assert "confidence_score" in pair

    async def test_batch_rag_processing(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test batch RAG processing for multiple speakers."""
        
        # Create multiple speakers with data
        speakers = []
        for i in range(3):
            speaker = await create_test_speaker(
                db_session,
                identifier=f"BATCH_RAG_{i}",
                name=f"Batch RAG Speaker {i}"
            )
            await create_test_historical_data(db_session, speaker.speaker_id, count=5)
            speakers.append(speaker)
        
        # Start batch processing job
        batch_data = {
            "speaker_ids": [s.speaker_id for s in speakers],
            "processing_type": "vectorization",
            "parameters": {
                "chunk_size": 512,
                "overlap": 50,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-batch",
            json=batch_data,
            headers=auth_headers
        )
        assert response.status_code == 202
        batch_job = response.json()
        batch_job_id = batch_job["job_id"]
        
        # Monitor batch job progress
        max_attempts = 60
        for attempt in range(max_attempts):
            response = await test_client.get(
                f"/api/v1/rag/jobs/{batch_job_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            job_status = response.json()
            
            if job_status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(2)
        
        # Verify batch job completed
        assert job_status["status"] == "completed"
        assert "processing_results" in job_status
        
        # Verify all speakers were processed
        results = job_status["processing_results"]
        assert len(results["speaker_results"]) == len(speakers)
        
        for speaker_result in results["speaker_results"]:
            assert speaker_result["status"] == "completed"
            assert speaker_result["vectors_created"] > 0

    async def test_rag_similarity_search(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker]
    ):
        """Test RAG similarity search functionality."""
        
        speaker = sample_speakers[0]
        
        # Test similarity search for error patterns
        search_data = {
            "query_text": "The patient has diabetes and high blood pressure",
            "speaker_id": speaker.speaker_id,
            "search_type": "error_patterns",
            "top_k": 5,
            "similarity_threshold": 0.7
        }
        
        response = await test_client.post(
            "/api/v1/rag/similarity-search",
            json=search_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        search_results = response.json()
        
        assert "results" in search_results
        assert len(search_results["results"]) <= search_data["top_k"]
        
        for result in search_results["results"]:
            assert "text" in result
            assert "similarity_score" in result
            assert "metadata" in result
            assert result["similarity_score"] >= search_data["similarity_threshold"]

    async def test_rag_correction_generation(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        sample_speakers: List[Speaker]
    ):
        """Test RAG-based correction generation."""
        
        speaker = sample_speakers[0]
        
        # Test correction generation for ASR text
        correction_data = {
            "original_text": "The patient has diabetis and high blod pressure. He is taking metformin 500mg twice daily.",
            "speaker_id": speaker.speaker_id,
            "correction_type": "medical_terminology",
            "confidence_threshold": 0.8
        }
        
        response = await test_client.post(
            "/api/v1/rag/generate-corrections",
            json=correction_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        corrections = response.json()
        
        assert "corrected_text" in corrections
        assert "corrections_applied" in corrections
        assert "confidence_scores" in corrections
        
        # Verify corrections were applied
        assert len(corrections["corrections_applied"]) > 0
        for correction in corrections["corrections_applied"]:
            assert "original" in correction
            assert "corrected" in correction
            assert "confidence" in correction
            assert "position" in correction

    async def test_rag_performance_monitoring(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test RAG processing performance monitoring."""
        
        # Get RAG processing statistics
        response = await test_client.get(
            "/api/v1/rag/statistics",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert "total_speakers_processed" in stats
        assert "total_error_correction_pairs" in stats
        assert "processing_performance" in stats
        assert "active_jobs" in stats
        
        # Get job queue status
        response = await test_client.get(
            "/api/v1/rag/queue-status",
            headers=auth_headers
        )
        assert response.status_code == 200
        queue_status = response.json()
        
        assert "queued_jobs" in queue_status
        assert "running_jobs" in queue_status
        assert "completed_jobs" in queue_status
        assert "failed_jobs" in queue_status

    async def test_rag_error_handling(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test RAG processing error handling."""
        
        # Test processing non-existent speaker
        job_data = {
            "speaker_id": "non-existent-speaker",
            "processing_type": "error_correction_pairs"
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-speaker",
            json=job_data,
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # Test invalid processing parameters
        invalid_job_data = {
            "speaker_id": "valid-speaker-id",
            "processing_type": "invalid_type",
            "parameters": {
                "invalid_param": "invalid_value"
            }
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-speaker",
            json=invalid_job_data,
            headers=auth_headers
        )
        assert response.status_code == 422

    async def test_rag_job_management(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test RAG job management operations."""
        
        # Create speaker for job testing
        speaker = await create_test_speaker(
            db_session,
            identifier="JOB_TEST",
            name="Job Test Speaker"
        )
        
        # Start a job
        job_data = {
            "speaker_id": speaker.speaker_id,
            "processing_type": "error_correction_pairs"
        }
        
        response = await test_client.post(
            "/api/v1/rag/process-speaker",
            json=job_data,
            headers=auth_headers
        )
        assert response.status_code == 202
        job = response.json()
        job_id = job["job_id"]
        
        # Test job cancellation
        response = await test_client.post(
            f"/api/v1/rag/jobs/{job_id}/cancel",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify job was cancelled
        response = await test_client.get(
            f"/api/v1/rag/jobs/{job_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        cancelled_job = response.json()
        assert cancelled_job["status"] == "cancelled"
        
        # Test job retry
        response = await test_client.post(
            f"/api/v1/rag/jobs/{job_id}/retry",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Test job deletion
        response = await test_client.delete(
            f"/api/v1/rag/jobs/{job_id}",
            headers=auth_headers
        )
        assert response.status_code == 204

    async def test_rag_data_quality_validation(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session: AsyncSession
    ):
        """Test RAG data quality validation."""
        
        # Create speaker with mixed quality data
        speaker = await create_test_speaker(
            db_session,
            identifier="QUALITY_TEST",
            name="Quality Test Speaker"
        )
        
        # Add high-quality historical data
        high_quality_data = [
            {
                "speaker_id": speaker.speaker_id,
                "original_asr_text": "The patient has diabetes mellitus type 2.",
                "final_reference_text": "The patient has diabetes mellitus type 2.",
                "ser_score": 2.0,
                "quality_level": "high",
                "is_acceptable_quality": True
            },
            # Add low-quality data
            {
                "speaker_id": speaker.speaker_id,
                "original_asr_text": "Th patint hs diabts",
                "final_reference_text": "The patient has diabetes",
                "ser_score": 45.0,
                "quality_level": "low",
                "is_acceptable_quality": False
            }
        ]
        
        for data in high_quality_data:
            response = await test_client.post(
                f"/api/v1/speakers/{speaker.speaker_id}/historical-data",
                json=data,
                headers=auth_headers
            )
            assert response.status_code == 201
        
        # Test data quality assessment
        response = await test_client.get(
            f"/api/v1/rag/speakers/{speaker.speaker_id}/data-quality",
            headers=auth_headers
        )
        assert response.status_code == 200
        quality_report = response.json()
        
        assert "overall_quality_score" in quality_report
        assert "quality_distribution" in quality_report
        assert "recommendations" in quality_report
        assert "data_sufficiency" in quality_report

    async def test_rag_configuration_management(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test RAG configuration management."""
        
        # Get current RAG configuration
        response = await test_client.get(
            "/api/v1/rag/configuration",
            headers=auth_headers
        )
        assert response.status_code == 200
        config = response.json()
        
        assert "embedding_model" in config
        assert "similarity_threshold" in config
        assert "processing_parameters" in config
        
        # Update RAG configuration
        new_config = {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "similarity_threshold": 0.85,
            "processing_parameters": {
                "chunk_size": 256,
                "overlap": 25,
                "max_pairs_per_speaker": 150
            }
        }
        
        response = await test_client.put(
            "/api/v1/rag/configuration",
            json=new_config,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify configuration was updated
        response = await test_client.get(
            "/api/v1/rag/configuration",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_config = response.json()
        
        assert updated_config["similarity_threshold"] == new_config["similarity_threshold"]
        assert updated_config["processing_parameters"]["chunk_size"] == new_config["processing_parameters"]["chunk_size"]
