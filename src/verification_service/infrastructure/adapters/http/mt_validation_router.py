"""
MT Validation Workflow API Router

FastAPI router for medical transcriptionist validation workflow endpoints.
Implements REST API for MT validation sessions, feedback collection, and analysis.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ....application.dto.requests import (
    CompleteValidationSessionRequest,
    GetSERComparisonRequest,
    StartValidationSessionRequest,
    SubmitMTFeedbackRequest,
)
from ....application.dto.responses import (
    MTFeedbackResponse,
    SERComparisonResponse,
    ValidationSessionResponse,
    ValidationTestDataResponse,
)
from ....application.use_cases.mt_validation_workflow_use_case import (
    MTValidationWorkflowUseCase,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/mt-validation", tags=["MT Validation"])


# Dependency injection placeholder
async def get_mt_validation_use_case() -> MTValidationWorkflowUseCase:
    """Get MT validation workflow use case instance."""
    # TODO: Implement proper dependency injection
    raise HTTPException(
        status_code=501, detail="MT validation use case not implemented"
    )


@router.post("/sessions", response_model=ValidationSessionResponse, status_code=201)
async def start_validation_session(
    request: StartValidationSessionRequest,
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Start a new MT validation session.

    Creates and starts a validation session for a medical transcriptionist
    to review RAG-corrected ASR drafts for a specific speaker.
    """
    try:
        logger.info(f"Starting validation session for speaker: {request.speaker_id}")
        response = await use_case.start_validation_session(request)
        logger.info(f"Validation session started: {response.session_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid validation session request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to start validation session: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to start validation session"
        )


@router.get("/sessions/{session_id}", response_model=ValidationSessionResponse)
async def get_validation_session(
    session_id: UUID = Path(..., description="Validation session ID"),
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Get validation session details.

    Returns detailed information about a specific validation session
    including progress, status, and metadata.
    """
    try:
        logger.info(f"Getting validation session: {session_id}")
        response = await use_case.get_validation_session(session_id)

        if not response:
            logger.warning(f"Validation session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Validation session not found")

        logger.info(f"Validation session retrieved: {session_id}")
        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to get validation session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get validation session")


@router.get(
    "/sessions/{session_id}/test-data", response_model=List[ValidationTestDataResponse]
)
async def get_validation_test_data(
    session_id: UUID = Path(..., description="Validation session ID"),
    limit: Optional[int] = Query(
        None, ge=1, le=100, description="Maximum number of items"
    ),
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Get test data for MT validation session.

    Returns test data items for the validation session with SER metrics
    and improvement analysis for MT review.
    """
    try:
        logger.info(f"Getting test data for session: {session_id}")
        response = await use_case.get_validation_test_data(session_id, limit)
        logger.info(
            f"Retrieved {len(response)} test data items for session {session_id}"
        )
        return response

    except ValueError as e:
        logger.warning(f"Invalid test data request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to get test data for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get test data")


@router.post(
    "/sessions/{session_id}/feedback",
    response_model=MTFeedbackResponse,
    status_code=201,
)
async def submit_mt_feedback(
    session_id: UUID,
    request: SubmitMTFeedbackRequest,
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Submit MT feedback for a validation item.

    Records medical transcriptionist feedback on RAG correction quality
    including ratings, comments, and bucket change recommendations.
    """
    try:
        # Ensure session_id matches request
        request.session_id = session_id

        logger.info(f"Submitting MT feedback for session: {session_id}")
        response = await use_case.submit_mt_feedback(request)
        logger.info(f"MT feedback submitted: {response.feedback_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid MT feedback request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to submit MT feedback for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit MT feedback")


@router.post(
    "/sessions/{session_id}/complete", response_model=ValidationSessionResponse
)
async def complete_validation_session(
    session_id: UUID,
    request: CompleteValidationSessionRequest,
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Complete a validation session.

    Marks the validation session as complete and generates final
    summary statistics and recommendations.
    """
    try:
        # Ensure session_id matches request
        request.session_id = session_id

        logger.info(f"Completing validation session: {session_id}")
        response = await use_case.complete_validation_session(request)
        logger.info(f"Validation session completed: {session_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid session completion request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to complete validation session {session_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to complete validation session"
        )


@router.get("/sessions", response_model=List[ValidationSessionResponse])
async def get_validation_sessions(
    speaker_id: Optional[UUID] = Query(None, description="Filter by speaker ID"),
    mt_user_id: Optional[UUID] = Query(None, description="Filter by MT user ID"),
    status: Optional[str] = Query(None, description="Filter by session status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of sessions"),
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Get validation sessions with filters.

    Returns a list of validation sessions matching the specified criteria.
    """
    try:
        logger.info(
            f"Getting validation sessions with filters: speaker_id={speaker_id}, status={status}"
        )
        response = await use_case.get_validation_sessions(
            speaker_id=speaker_id, mt_user_id=mt_user_id, status=status, limit=limit
        )
        logger.info(f"Found {len(response)} validation sessions")
        return response

    except Exception as e:
        logger.error(f"Failed to get validation sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get validation sessions")


@router.post("/ser-comparison", response_model=SERComparisonResponse)
async def get_ser_comparison(
    request: GetSERComparisonRequest,
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Get SER comparison results for speaker validation.

    Analyzes SER improvement between original and RAG-corrected texts
    to support bucket transition decisions.
    """
    try:
        logger.info(f"Getting SER comparison for speaker: {request.speaker_id}")
        response = await use_case.get_ser_comparison(request)
        logger.info(f"SER comparison completed for speaker: {request.speaker_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid SER comparison request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to get SER comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SER comparison")


@router.get("/sessions/{session_id}/feedback", response_model=List[dict])
async def get_session_feedback(
    session_id: UUID = Path(..., description="Validation session ID"),
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Get all feedback for a validation session.

    Returns all MT feedback entries for the specified validation session.
    """
    try:
        logger.info(f"Getting feedback for session: {session_id}")
        response = await use_case.get_session_feedback(session_id)
        logger.info(
            f"Retrieved {len(response)} feedback entries for session {session_id}"
        )
        return response

    except Exception as e:
        logger.error(f"Failed to get session feedback for {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session feedback")


@router.get("/statistics/mt-user/{mt_user_id}", response_model=dict)
async def get_mt_user_statistics(
    mt_user_id: UUID = Path(..., description="MT user ID"),
    use_case: MTValidationWorkflowUseCase = Depends(get_mt_validation_use_case),
):
    """
    Get statistics for an MT user.

    Returns performance and activity statistics for a medical transcriptionist.
    """
    try:
        logger.info(f"Getting statistics for MT user: {mt_user_id}")

        # Placeholder implementation
        stats = {
            "mt_user_id": str(mt_user_id),
            "total_sessions": 45,
            "completed_sessions": 42,
            "total_feedback_items": 1250,
            "average_session_duration_minutes": 85.5,
            "feedback_quality_score": 4.2,
            "bucket_change_recommendations": 23,
            "accuracy_score": 94.5,
            "productivity_score": 87.2,
        }

        response = {
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "period": "last_30_days",
        }

        logger.info(f"Statistics retrieved for MT user: {mt_user_id}")
        return response

    except Exception as e:
        logger.error(f"Failed to get MT user statistics for {mt_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get MT user statistics")


@router.get("/statistics/summary", response_model=dict)
async def get_validation_statistics():
    """
    Get overall validation statistics.

    Returns system-wide MT validation statistics and performance metrics.
    """
    try:
        logger.info("Getting validation statistics summary")

        # Placeholder implementation
        stats = {
            "total_sessions": 1250,
            "active_sessions": 15,
            "completed_sessions": 1180,
            "cancelled_sessions": 55,
            "total_feedback_items": 35420,
            "average_session_duration_minutes": 78.5,
            "mt_user_count": 25,
            "speakers_validated": 246,
            "bucket_transitions_recommended": 89,
            "quality_improvement_rate": 76.5,
            "mt_satisfaction_score": 4.1,
        }

        response = {
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "period": "last_30_days",
        }

        logger.info("Validation statistics summary retrieved successfully")
        return response

    except Exception as e:
        logger.error(f"Failed to get validation statistics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get validation statistics"
        )


# Health check for MT validation
@router.get("/health/check")
async def mt_validation_health():
    """Health check for MT validation functionality."""
    return {
        "status": "healthy",
        "service": "mt-validation",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "start_session": "POST /api/v1/mt-validation/sessions",
            "get_test_data": "GET /api/v1/mt-validation/sessions/{session_id}/test-data",
            "submit_feedback": "POST /api/v1/mt-validation/sessions/{session_id}/feedback",
            "complete_session": "POST /api/v1/mt-validation/sessions/{session_id}/complete",
            "ser_comparison": "POST /api/v1/mt-validation/ser-comparison",
        },
    }
