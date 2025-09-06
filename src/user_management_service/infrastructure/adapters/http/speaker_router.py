"""
Speaker Management API Router

FastAPI router for speaker bucket management endpoints.
Implements REST API for speaker CRUD operations, bucket management, and statistics.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ....application.dto.requests import (
    CreateSpeakerRequest,
    SearchSpeakersRequest,
    UpdateSpeakerRequest,
)
from ....application.dto.responses import (
    SpeakerBucketStatsResponse,
    SpeakerListResponse,
    SpeakerResponse,
)
from ....application.use_cases.manage_speakers_use_case import ManageSpeakersUseCase
from ....domain.value_objects.speaker_bucket import SpeakerBucket

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/speakers", tags=["Speaker Management"])


# Dependency injection placeholder - in real implementation, this would be properly injected
async def get_speaker_use_case() -> ManageSpeakersUseCase:
    """Get speaker management use case instance."""
    # TODO: Implement proper dependency injection
    # For now, return a placeholder
    raise HTTPException(
        status_code=501, detail="Speaker management use case not implemented"
    )


@router.post("", response_model=SpeakerResponse, status_code=201)
async def create_speaker(
    request: CreateSpeakerRequest,
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Create a new speaker.

    Creates a new speaker with the specified identifier, name, and initial bucket.
    """
    try:
        logger.info(f"Creating speaker: {request.speaker_identifier}")
        response = await use_case.create_speaker(request)
        logger.info(f"Speaker created successfully: {response.speaker_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid speaker creation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to create speaker: {e}")
        raise HTTPException(status_code=500, detail="Failed to create speaker")


@router.get("", response_model=SpeakerListResponse)
async def search_speakers(
    name_pattern: Optional[str] = Query(
        None, description="Speaker name pattern to search for"
    ),
    bucket: Optional[SpeakerBucket] = Query(
        None, description="Filter by speaker bucket"
    ),
    min_ser_score: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum SER score filter"
    ),
    max_ser_score: Optional[float] = Query(
        None, ge=0, le=100, description="Maximum SER score filter"
    ),
    has_sufficient_data: Optional[bool] = Query(
        None, description="Filter by data sufficiency"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Search speakers with filters and pagination.

    Returns a paginated list of speakers matching the specified criteria.
    """
    try:
        request = SearchSpeakersRequest(
            name_pattern=name_pattern,
            bucket=bucket,
            min_ser_score=min_ser_score,
            max_ser_score=max_ser_score,
            has_sufficient_data=has_sufficient_data,
            page=page,
            page_size=page_size,
        )

        logger.info(
            f"Searching speakers with filters: page={page}, page_size={page_size}"
        )
        response = await use_case.search_speakers(request)
        logger.info(f"Found {len(response.speakers)} speakers")
        return response

    except ValueError as e:
        logger.warning(f"Invalid search request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to search speakers: {e}")
        raise HTTPException(status_code=500, detail="Failed to search speakers")


@router.get("/{speaker_id}", response_model=SpeakerResponse)
async def get_speaker_by_id(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Get speaker by ID.

    Returns detailed information about a specific speaker.
    """
    try:
        logger.info(f"Getting speaker: {speaker_id}")
        response = await use_case.get_speaker_by_id(speaker_id)

        if not response:
            logger.warning(f"Speaker not found: {speaker_id}")
            raise HTTPException(status_code=404, detail="Speaker not found")

        logger.info(f"Speaker retrieved successfully: {speaker_id}")
        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to get speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get speaker")


@router.get("/identifier/{speaker_identifier}", response_model=SpeakerResponse)
async def get_speaker_by_identifier(
    speaker_identifier: str = Path(..., description="Speaker identifier"),
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Get speaker by external identifier.

    Returns detailed information about a speaker using their external identifier.
    """
    try:
        logger.info(f"Getting speaker by identifier: {speaker_identifier}")
        response = await use_case.get_speaker_by_identifier(speaker_identifier)

        if not response:
            logger.warning(f"Speaker not found with identifier: {speaker_identifier}")
            raise HTTPException(status_code=404, detail="Speaker not found")

        logger.info(f"Speaker retrieved successfully: {speaker_identifier}")
        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to get speaker by identifier {speaker_identifier}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get speaker")


@router.put("/{speaker_id}", response_model=SpeakerResponse)
async def update_speaker(
    speaker_id: UUID,
    request: UpdateSpeakerRequest,
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Update an existing speaker.

    Updates speaker information including name, bucket, and metadata.
    """
    try:
        logger.info(f"Updating speaker: {speaker_id}")
        response = await use_case.update_speaker(speaker_id, request)
        logger.info(f"Speaker updated successfully: {speaker_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid speaker update request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to update speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update speaker")


@router.get("/bucket/{bucket}", response_model=List[SpeakerResponse])
async def get_speakers_by_bucket(
    bucket: SpeakerBucket = Path(..., description="Speaker bucket"),
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Get all speakers in a specific bucket.

    Returns a list of speakers currently assigned to the specified bucket.
    """
    try:
        logger.info(f"Getting speakers in bucket: {bucket}")
        response = await use_case.get_speakers_by_bucket(bucket)
        logger.info(f"Found {len(response)} speakers in bucket {bucket}")
        return response

    except Exception as e:
        logger.error(f"Failed to get speakers by bucket {bucket}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get speakers by bucket")


@router.get("/transitions/needed", response_model=List[SpeakerResponse])
async def get_speakers_needing_transition(
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Get speakers that need bucket transition.

    Returns a list of speakers whose metrics suggest they should be moved to a different bucket.
    """
    try:
        logger.info("Getting speakers needing bucket transition")
        response = await use_case.get_speakers_needing_transition()
        logger.info(f"Found {len(response)} speakers needing transition")
        return response

    except Exception as e:
        logger.error(f"Failed to get speakers needing transition: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get speakers needing transition"
        )


@router.get("/statistics/buckets", response_model=SpeakerBucketStatsResponse)
async def get_bucket_statistics(
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Get speaker bucket statistics.

    Returns comprehensive statistics about speaker distribution across buckets,
    quality metrics, and transition recommendations.
    """
    try:
        logger.info("Getting bucket statistics")
        response = await use_case.get_bucket_statistics()
        logger.info("Bucket statistics retrieved successfully")
        return response

    except Exception as e:
        logger.error(f"Failed to get bucket statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bucket statistics")


@router.post("/{speaker_id}/statistics/update", response_model=SpeakerResponse)
async def update_speaker_statistics(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    use_case: ManageSpeakersUseCase = Depends(get_speaker_use_case),
):
    """
    Update speaker statistics from historical data.

    Recalculates speaker metrics including note counts, average SER score,
    and bucket recommendations based on current historical data.
    """
    try:
        logger.info(f"Updating statistics for speaker: {speaker_id}")
        response = await use_case.update_speaker_statistics(speaker_id)
        logger.info(f"Statistics updated successfully for speaker: {speaker_id}")
        return response

    except ValueError as e:
        logger.warning(f"Speaker not found for statistics update: {speaker_id}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to update statistics for speaker {speaker_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to update speaker statistics"
        )


# Health check for speaker management
@router.get("/health/check")
async def speaker_management_health():
    """Health check for speaker management functionality."""
    return {
        "status": "healthy",
        "service": "speaker-management",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "create_speaker": "POST /api/v1/speakers",
            "search_speakers": "GET /api/v1/speakers",
            "get_speaker": "GET /api/v1/speakers/{speaker_id}",
            "update_speaker": "PUT /api/v1/speakers/{speaker_id}",
            "bucket_statistics": "GET /api/v1/speakers/statistics/buckets",
        },
    }
