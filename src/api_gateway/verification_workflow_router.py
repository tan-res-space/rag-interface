"""
Verification Workflow API Router

Provides API endpoints for the verification workflow including InstaNote Database
integration and RAG system correction verification.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from error_reporting_service.application.use_cases.verification_workflow_use_case import (
    VerificationWorkflowUseCase,
)
from error_reporting_service.application.dto.requests import (
    PullVerificationJobsRequest,
    VerifyCorrectionRequest,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/verification-workflow",
    tags=["Verification Workflow"]
)


# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class PullJobsModel(BaseModel):
    """Pull verification jobs request model"""
    speaker_id: str = Field(..., description="Speaker ID")
    start_date: str = Field(..., description="Start date (ISO format)")
    end_date: str = Field(..., description="End date (ISO format)")
    error_types: Optional[List[str]] = Field(None, description="Filter by error types")
    max_jobs: int = Field(default=10, ge=1, le=50, description="Maximum jobs to pull")


class VerifyResultModel(BaseModel):
    """Verify correction result request model"""
    verification_id: str = Field(..., description="Verification job ID")
    job_id: str = Field(..., description="InstaNote job ID")
    error_id: str = Field(..., description="Related error report ID")
    verification_result: str = Field(..., description="Result: rectified, not_rectified, partially_rectified, not_applicable")
    qa_comments: Optional[str] = Field(None, description="QA comments")
    verified_by: str = Field(..., description="User ID of verifier")


class BatchProcessModel(BaseModel):
    """Batch process verification jobs request model"""
    speaker_ids: List[str] = Field(..., description="List of speaker IDs")
    max_jobs_per_speaker: int = Field(default=5, ge=1, le=20, description="Max jobs per speaker")


# =====================================================
# DEPENDENCY INJECTION
# =====================================================

async def get_verification_workflow_use_case() -> VerificationWorkflowUseCase:
    """Get verification workflow use case instance"""
    # This would be properly injected in a real implementation
    # For now, return a placeholder
    raise HTTPException(status_code=501, detail="Use case not implemented")


# =====================================================
# VERIFICATION JOB MANAGEMENT ENDPOINTS
# =====================================================

@router.post("/jobs/pull", response_model=dict)
async def pull_verification_jobs(
    request: PullJobsModel,
    use_case: VerificationWorkflowUseCase = Depends(get_verification_workflow_use_case)
):
    """
    Pull jobs from InstaNote Database for verification.
    
    Retrieves jobs for a specific speaker within a date range and creates
    verification job entries for processing.
    """
    try:
        logger.info(f"Pulling verification jobs for speaker {request.speaker_id}")
        
        # Convert to use case request
        use_case_request = PullVerificationJobsRequest(
            speaker_id=request.speaker_id,
            date_range={
                "start_date": request.start_date,
                "end_date": request.end_date,
            },
            error_types=request.error_types,
            max_jobs=request.max_jobs,
            requested_by="api_user",  # Would be extracted from auth context
        )
        
        # Execute use case
        jobs = await use_case.pull_verification_jobs(use_case_request)
        
        logger.info(f"Pulled {len(jobs)} verification jobs")
        return {
            "success": True,
            "jobs_pulled": len(jobs),
            "jobs": [
                {
                    "verification_id": job.verification_id,
                    "job_id": job.job_id,
                    "speaker_id": job.speaker_id,
                    "verification_status": job.verification_status,
                    "corrections_count": job.corrections_count,
                    "needs_manual_review": job.needs_manual_review,
                }
                for job in jobs
            ],
            "pulled_at": datetime.utcnow().isoformat(),
        }
        
    except ValueError as e:
        logger.error(f"Validation error pulling jobs: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to pull verification jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to pull verification jobs")


@router.post("/jobs/{verification_id}/apply-corrections", response_model=dict)
async def apply_rag_corrections(
    verification_id: UUID,
    use_case: VerificationWorkflowUseCase = Depends(get_verification_workflow_use_case)
):
    """
    Apply RAG system corrections to a verification job.
    
    Processes the original draft through the RAG system and applies
    corrections based on learned error patterns.
    """
    try:
        logger.info(f"Applying RAG corrections to verification job: {verification_id}")
        
        # Execute use case
        job = await use_case.apply_rag_corrections(str(verification_id))
        
        logger.info(f"Applied {job.corrections_count} corrections")
        return {
            "success": True,
            "verification_id": job.verification_id,
            "job_id": job.job_id,
            "corrections_applied": job.corrections_count,
            "average_confidence": job.average_confidence,
            "needs_manual_review": job.needs_manual_review,
            "verification_status": job.verification_status,
            "processed_at": datetime.utcnow().isoformat(),
        }
        
    except ValueError as e:
        logger.error(f"Validation error applying corrections: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to apply RAG corrections: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply RAG corrections")


@router.post("/jobs/verify-result", response_model=dict)
async def verify_correction_result(
    request: VerifyResultModel,
    use_case: VerificationWorkflowUseCase = Depends(get_verification_workflow_use_case)
):
    """
    Verify the result of error correction.
    
    Records the verification result and updates the status of the
    verification job and related error report.
    """
    try:
        logger.info(f"Verifying correction result for job: {request.verification_id}")
        
        # Convert to use case request
        use_case_request = VerifyCorrectionRequest(
            verification_id=request.verification_id,
            job_id=request.job_id,
            error_id=request.error_id,
            verification_result=request.verification_result,
            qa_comments=request.qa_comments,
            verified_by=request.verified_by,
        )
        
        # Execute use case
        job = await use_case.verify_correction_result(use_case_request)
        
        logger.info(f"Verification result recorded: {job.verification_result}")
        return {
            "success": True,
            "verification_id": job.verification_id,
            "job_id": job.job_id,
            "verification_result": job.verification_result,
            "verified_by": job.verified_by,
            "verified_at": job.verified_at.isoformat() if job.verified_at else None,
            "has_qa_comments": job.has_qa_comments,
        }
        
    except ValueError as e:
        logger.error(f"Validation error verifying result: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to verify correction result: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify correction result")


@router.get("/jobs/review", response_model=dict)
async def get_jobs_for_review(
    speaker_id: Optional[str] = Query(None, description="Filter by speaker ID"),
    use_case: VerificationWorkflowUseCase = Depends(get_verification_workflow_use_case)
):
    """
    Get verification jobs that need manual review.
    
    Returns jobs that require human verification due to low confidence
    scores, complex corrections, or other quality indicators.
    """
    try:
        logger.info(f"Getting jobs for review (speaker_id: {speaker_id})")
        
        # Execute use case
        jobs = await use_case.get_verification_jobs_for_review(speaker_id)
        
        logger.info(f"Found {len(jobs)} jobs needing review")
        return {
            "success": True,
            "jobs_needing_review": len(jobs),
            "jobs": [
                {
                    "verification_id": job.verification_id,
                    "job_id": job.job_id,
                    "speaker_id": job.speaker_id,
                    "verification_status": job.verification_status,
                    "corrections_count": job.corrections_count,
                    "average_confidence": job.average_confidence,
                    "needs_manual_review": job.needs_manual_review,
                    "has_qa_comments": job.has_qa_comments,
                }
                for job in jobs
            ],
            "retrieved_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Failed to get jobs for review: {e}")
        raise HTTPException(status_code=500, detail="Failed to get jobs for review")


# =====================================================
# BATCH PROCESSING ENDPOINTS
# =====================================================

@router.post("/jobs/batch-process", response_model=dict)
async def batch_process_verification_jobs(
    request: BatchProcessModel,
    use_case: VerificationWorkflowUseCase = Depends(get_verification_workflow_use_case)
):
    """
    Batch process verification jobs for multiple speakers.
    
    Pulls jobs and applies RAG corrections for multiple speakers
    in a single operation for efficiency.
    """
    try:
        logger.info(f"Batch processing verification jobs for {len(request.speaker_ids)} speakers")
        
        # Execute use case
        results = await use_case.batch_process_verification_jobs(
            speaker_ids=request.speaker_ids,
            max_jobs_per_speaker=request.max_jobs_per_speaker
        )
        
        logger.info(f"Batch processing completed: {results['processed_speakers']} speakers processed")
        return {
            "success": True,
            "batch_results": results,
            "processed_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Failed to batch process verification jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to batch process verification jobs")


# =====================================================
# STATISTICS AND MONITORING ENDPOINTS
# =====================================================

@router.get("/statistics", response_model=dict)
async def get_verification_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    use_case: VerificationWorkflowUseCase = Depends(get_verification_workflow_use_case)
):
    """
    Get verification workflow statistics.
    
    Provides comprehensive statistics about verification jobs,
    rectification rates, and system performance.
    """
    try:
        logger.info(f"Getting verification statistics for {days} days")
        
        # Execute use case
        stats = await use_case.get_verification_statistics(days)
        
        return {
            "success": True,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Failed to get verification statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get verification statistics")


@router.get("/jobs/{verification_id}", response_model=dict)
async def get_verification_job_details(
    verification_id: UUID,
):
    """
    Get detailed information about a specific verification job.
    
    Returns comprehensive details including corrections applied,
    verification status, and related metadata.
    """
    try:
        logger.info(f"Getting verification job details: {verification_id}")
        
        # This would use a get verification job use case
        # For now, return a placeholder response
        return {
            "success": True,
            "verification_job": {
                "verification_id": str(verification_id),
                "job_id": "instanote_job_123",
                "speaker_id": "speaker_456",
                "verification_status": "verified",
                "verification_result": "rectified",
                "corrections_applied": [
                    {
                        "correction_type": "medical_terminology",
                        "original_text": "hypertension",
                        "corrected_text": "high blood pressure",
                        "confidence": 0.95,
                        "position_start": 45,
                        "position_end": 57,
                    }
                ],
                "average_confidence": 0.95,
                "needs_manual_review": False,
                "verified_by": "qa_user_789",
                "verified_at": datetime.utcnow().isoformat(),
                "qa_comments": "Correction applied successfully",
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get verification job details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get verification job details")


# =====================================================
# HEALTH CHECK ENDPOINTS
# =====================================================

@router.get("/health", response_model=dict)
async def health_check():
    """
    Health check for verification workflow service.
    """
    return {
        "status": "healthy",
        "service": "verification-workflow",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "features": [
            "instanote_integration",
            "rag_corrections",
            "verification_tracking",
            "batch_processing",
        ]
    }
