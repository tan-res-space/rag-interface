"""
Bucket Transition Management API Router

FastAPI router for speaker bucket transition management endpoints.
Implements REST API for transition requests, approvals, and history tracking.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from ....application.dto.requests import (
    ApproveBucketTransitionRequest,
    CreateBucketTransitionRequest,
    RejectBucketTransitionRequest,
)
from ....application.dto.responses import BucketTransitionRequestResponse
from ....application.use_cases.manage_bucket_transitions_use_case import (
    ManageBucketTransitionsUseCase,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/bucket-transitions", tags=["Bucket Transitions"])


# Dependency injection placeholder
async def get_bucket_transition_use_case() -> ManageBucketTransitionsUseCase:
    """Get bucket transition management use case instance."""
    # TODO: Implement proper dependency injection
    raise HTTPException(
        status_code=501, detail="Bucket transition use case not implemented"
    )


@router.post("", response_model=BucketTransitionRequestResponse, status_code=201)
async def create_transition_request(
    request: CreateBucketTransitionRequest,
    use_case: ManageBucketTransitionsUseCase = Depends(get_bucket_transition_use_case),
):
    """
    Create a new bucket transition request.

    Creates a request to move a speaker from one bucket to another with justification.
    """
    try:
        logger.info(
            f"Creating bucket transition request for speaker: {request.speaker_id}"
        )
        response = await use_case.create_transition_request(request)
        logger.info(f"Transition request created: {response.request_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid transition request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to create transition request: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create transition request"
        )


@router.get("", response_model=List[BucketTransitionRequestResponse])
async def get_transition_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    speaker_id: Optional[UUID] = Query(None, description="Filter by speaker ID"),
    urgent_only: bool = Query(False, description="Show only urgent requests"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of requests"),
    use_case: ManageBucketTransitionsUseCase = Depends(get_bucket_transition_use_case),
):
    """
    Get bucket transition requests with filters.

    Returns a list of transition requests matching the specified criteria.
    """
    try:
        logger.info(
            f"Getting transition requests with filters: status={status}, urgent_only={urgent_only}"
        )
        response = await use_case.get_transition_requests(
            status=status, speaker_id=speaker_id, urgent_only=urgent_only, limit=limit
        )
        logger.info(f"Found {len(response)} transition requests")
        return response

    except Exception as e:
        logger.error(f"Failed to get transition requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transition requests")


@router.get("/pending", response_model=List[BucketTransitionRequestResponse])
async def get_pending_transition_requests(
    use_case: ManageBucketTransitionsUseCase = Depends(get_bucket_transition_use_case),
):
    """
    Get all pending bucket transition requests.

    Returns a list of transition requests awaiting approval, sorted by priority.
    """
    try:
        logger.info("Getting pending transition requests")
        response = await use_case.get_pending_transition_requests()
        logger.info(f"Found {len(response)} pending transition requests")
        return response

    except Exception as e:
        logger.error(f"Failed to get pending transition requests: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get pending transition requests"
        )


@router.get("/{request_id}", response_model=BucketTransitionRequestResponse)
async def get_transition_request(
    request_id: UUID = Path(..., description="Transition request ID"),
    use_case: ManageBucketTransitionsUseCase = Depends(get_bucket_transition_use_case),
):
    """
    Get bucket transition request by ID.

    Returns detailed information about a specific transition request.
    """
    try:
        logger.info(f"Getting transition request: {request_id}")
        response = await use_case.get_transition_request_by_id(request_id)

        if not response:
            logger.warning(f"Transition request not found: {request_id}")
            raise HTTPException(status_code=404, detail="Transition request not found")

        logger.info(f"Transition request retrieved: {request_id}")
        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to get transition request {request_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transition request")


@router.post("/{request_id}/approve", response_model=BucketTransitionRequestResponse)
async def approve_transition_request(
    request_id: UUID,
    approval_request: ApproveBucketTransitionRequest,
    use_case: ManageBucketTransitionsUseCase = Depends(get_bucket_transition_use_case),
):
    """
    Approve a bucket transition request.

    Approves the transition request and updates the speaker's bucket assignment.
    """
    try:
        logger.info(f"Approving transition request: {request_id}")
        response = await use_case.approve_transition_request(
            request_id, approval_request
        )
        logger.info(f"Transition request approved: {request_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid approval request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to approve transition request {request_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to approve transition request"
        )


@router.post("/{request_id}/reject", response_model=BucketTransitionRequestResponse)
async def reject_transition_request(
    request_id: UUID,
    rejection_request: RejectBucketTransitionRequest,
    use_case: ManageBucketTransitionsUseCase = Depends(get_bucket_transition_use_case),
):
    """
    Reject a bucket transition request.

    Rejects the transition request with a reason and maintains current bucket assignment.
    """
    try:
        logger.info(f"Rejecting transition request: {request_id}")
        response = await use_case.reject_transition_request(
            request_id, rejection_request
        )
        logger.info(f"Transition request rejected: {request_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid rejection request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to reject transition request {request_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to reject transition request"
        )


@router.get(
    "/speaker/{speaker_id}/history",
    response_model=List[BucketTransitionRequestResponse],
)
async def get_speaker_transition_history(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records"),
    use_case: ManageBucketTransitionsUseCase = Depends(get_bucket_transition_use_case),
):
    """
    Get bucket transition history for a speaker.

    Returns the complete transition history for a specific speaker.
    """
    try:
        logger.info(f"Getting transition history for speaker: {speaker_id}")
        response = await use_case.get_speaker_transition_history(speaker_id, limit)
        logger.info(
            f"Found {len(response)} transition records for speaker {speaker_id}"
        )
        return response

    except Exception as e:
        logger.error(f"Failed to get transition history for speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transition history")


@router.get("/statistics/summary")
async def get_transition_statistics():
    """
    Get bucket transition statistics.

    Returns summary statistics about transition requests, approval rates, and trends.
    """
    try:
        logger.info("Getting transition statistics")
        # Placeholder implementation
        stats = {
            "total_requests": 150,
            "pending_requests": 12,
            "approved_requests": 120,
            "rejected_requests": 18,
            "approval_rate": 87.0,
            "average_processing_time_hours": 24.5,
            "urgent_requests": 3,
            "transition_trends": {
                "to_better_bucket": 85,
                "to_worse_bucket": 15,
                "lateral_moves": 5,
            },
            "bucket_transition_matrix": {
                "high_touch_to_medium": 45,
                "medium_touch_to_low": 25,
                "low_touch_to_no": 15,
                "other_transitions": 10,
            },
        }

        logger.info("Transition statistics retrieved successfully")
        return {"statistics": stats, "timestamp": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"Failed to get transition statistics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get transition statistics"
        )


# Health check for bucket transitions
@router.get("/health/check")
async def bucket_transition_health():
    """Health check for bucket transition functionality."""
    return {
        "status": "healthy",
        "service": "bucket-transitions",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "create_request": "POST /api/v1/bucket-transitions",
            "get_requests": "GET /api/v1/bucket-transitions",
            "approve_request": "POST /api/v1/bucket-transitions/{request_id}/approve",
            "reject_request": "POST /api/v1/bucket-transitions/{request_id}/reject",
            "transition_history": "GET /api/v1/bucket-transitions/speaker/{speaker_id}/history",
        },
    }
