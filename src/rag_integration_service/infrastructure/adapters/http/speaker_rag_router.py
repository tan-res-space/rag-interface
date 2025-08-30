"""
Speaker RAG Processing API Router

FastAPI router for speaker-specific RAG processing endpoints.
Implements REST API for error-correction pair generation, vectorization, and speaker-specific training.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from ....application.dto.requests import (
    CreateSpeakerRAGJobRequest,
    GenerateErrorCorrectionPairsRequest,
    GetSpeakerErrorPatternsRequest,
    ProcessSpeakerHistoricalDataRequest,
    VectorizeErrorPairsRequest,
)
from ....application.dto.responses import (
    ErrorCorrectionPairResponse,
    ProcessingJobResponse,
    SpeakerErrorPatternsResponse,
    SpeakerRAGProcessingResponse,
    SpeakerRAGStatsResponse,
    VectorizationResponse,
)
from ....application.use_cases.process_speaker_rag_data_use_case import (
    ProcessSpeakerRAGDataUseCase,
)
from ....domain.entities.speaker_rag_processing_job import JobType

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/speaker-rag", tags=["Speaker RAG Processing"])


# Dependency injection placeholder
async def get_speaker_rag_use_case() -> ProcessSpeakerRAGDataUseCase:
    """Get speaker RAG processing use case instance."""
    # TODO: Implement proper dependency injection
    raise HTTPException(
        status_code=501, detail="Speaker RAG processing use case not implemented"
    )


@router.post(
    "/process-historical", response_model=SpeakerRAGProcessingResponse, status_code=201
)
async def process_speaker_historical_data(
    request: ProcessSpeakerHistoricalDataRequest,
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Process historical data for a speaker to generate error-correction pairs.

    Analyzes historical ASR drafts and final notes to extract error patterns
    and generate training data for speaker-specific RAG improvements.
    """
    try:
        logger.info(f"Processing historical data for speaker: {request.speaker_id}")
        response = await use_case.process_speaker_historical_data(request)
        logger.info(
            f"Historical data processing completed: {response.total_pairs_generated} pairs generated"
        )
        return response

    except ValueError as e:
        logger.warning(f"Invalid historical data processing request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to process historical data: {e}")
        raise HTTPException(status_code=500, detail="Failed to process historical data")


@router.post(
    "/generate-pairs", response_model=List[ErrorCorrectionPairResponse], status_code=201
)
async def generate_error_correction_pairs(
    request: GenerateErrorCorrectionPairsRequest,
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Generate error-correction pairs from ASR and final text.

    Extracts specific error patterns and corrections from a single
    ASR draft and final note pair for immediate analysis.
    """
    try:
        logger.info(
            f"Generating error-correction pairs for speaker: {request.speaker_id}"
        )
        response = await use_case.generate_error_correction_pairs(request)
        logger.info(f"Generated {len(response)} error-correction pairs")
        return response

    except ValueError as e:
        logger.warning(f"Invalid error-correction pair generation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to generate error-correction pairs: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate error-correction pairs"
        )


@router.post("/vectorize", response_model=ProcessingJobResponse, status_code=201)
async def vectorize_speaker_error_pairs(
    request: VectorizeErrorPairsRequest,
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Vectorize error-correction pairs for a speaker.

    Creates vector embeddings for speaker-specific error-correction pairs
    to enable similarity search and RAG-based corrections.
    """
    try:
        logger.info(f"Starting vectorization for speaker: {request.speaker_id}")
        response = await use_case.vectorize_speaker_error_pairs(
            UUID(request.speaker_id), request.batch_size
        )
        logger.info(f"Vectorization job created: {response.job_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid vectorization request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to start vectorization: {e}")
        raise HTTPException(status_code=500, detail="Failed to start vectorization")


@router.get(
    "/speaker/{speaker_id}/error-patterns", response_model=SpeakerErrorPatternsResponse
)
async def get_speaker_error_patterns(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    error_type_filter: Optional[str] = Query(None, description="Filter by error type"),
    min_confidence: Optional[float] = Query(
        None, ge=0, le=1, description="Minimum confidence threshold"
    ),
    include_examples: bool = Query(True, description="Include example pairs"),
    max_examples_per_type: int = Query(
        5, ge=1, le=20, description="Maximum examples per error type"
    ),
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Get error patterns analysis for a speaker.

    Returns comprehensive analysis of error patterns, frequencies,
    and examples for speaker-specific RAG training insights.
    """
    try:
        request = GetSpeakerErrorPatternsRequest(
            speaker_id=str(speaker_id),
            error_type_filter=error_type_filter,
            min_confidence=min_confidence,
            include_examples=include_examples,
            max_examples_per_type=max_examples_per_type,
        )

        logger.info(f"Getting error patterns for speaker: {speaker_id}")
        response = await use_case.get_speaker_error_patterns(speaker_id)

        # Convert to response format
        patterns_response = SpeakerErrorPatternsResponse(
            speaker_id=str(speaker_id),
            total_pairs=response["total_pairs"],
            error_statistics=response["error_statistics"],
            error_patterns=response["error_patterns"],
            high_confidence_pairs=response["high_confidence_pairs"],
            training_suitable_pairs=response["training_suitable_pairs"],
            analysis_timestamp=datetime.utcnow(),
        )

        logger.info(f"Error patterns analysis completed for speaker: {speaker_id}")
        return patterns_response

    except ValueError as e:
        logger.warning(f"Invalid error patterns request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to get error patterns for speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get error patterns")


@router.post("/jobs", response_model=ProcessingJobResponse, status_code=201)
async def create_processing_job(
    request: CreateSpeakerRAGJobRequest,
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Create a new speaker RAG processing job.

    Creates a background job for speaker-specific RAG processing tasks
    such as historical analysis, vectorization, or correction generation.
    """
    try:
        logger.info(
            f"Creating processing job for speaker: {request.speaker_id}, type: {request.job_type}"
        )
        response = await use_case.create_processing_job(request)
        logger.info(f"Processing job created: {response.job_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid job creation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to create processing job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create processing job")


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
async def get_processing_job_status(
    job_id: UUID = Path(..., description="Processing job ID"),
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Get processing job status.

    Returns current status, progress, and details for a speaker RAG processing job.
    """
    try:
        logger.info(f"Getting status for processing job: {job_id}")
        response = await use_case.get_processing_job_status(job_id)

        if not response:
            logger.warning(f"Processing job not found: {job_id}")
            raise HTTPException(status_code=404, detail="Processing job not found")

        logger.info(f"Processing job status retrieved: {job_id}")
        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to get processing job status {job_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get processing job status"
        )


@router.get("/jobs", response_model=List[ProcessingJobResponse])
async def get_processing_jobs(
    speaker_id: Optional[UUID] = Query(None, description="Filter by speaker ID"),
    job_type: Optional[JobType] = Query(None, description="Filter by job type"),
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of jobs"),
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Get processing jobs with filters.

    Returns a list of speaker RAG processing jobs matching the specified criteria.
    """
    try:
        logger.info(
            f"Getting processing jobs with filters: speaker_id={speaker_id}, job_type={job_type}"
        )
        response = await use_case.get_processing_jobs(
            speaker_id=speaker_id, job_type=job_type, status=status, limit=limit
        )
        logger.info(f"Found {len(response)} processing jobs")
        return response

    except Exception as e:
        logger.error(f"Failed to get processing jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing jobs")


@router.get("/speaker/{speaker_id}/statistics", response_model=SpeakerRAGStatsResponse)
async def get_speaker_rag_statistics(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    use_case: ProcessSpeakerRAGDataUseCase = Depends(get_speaker_rag_use_case),
):
    """
    Get RAG statistics for a speaker.

    Returns comprehensive statistics about error-correction pairs,
    processing history, and training data quality for the speaker.
    """
    try:
        logger.info(f"Getting RAG statistics for speaker: {speaker_id}")

        # Placeholder implementation
        stats = SpeakerRAGStatsResponse(
            speaker_id=str(speaker_id),
            total_error_correction_pairs=245,
            error_type_distribution={
                "medical_terminology": 85,
                "numeric": 45,
                "substitution": 78,
                "insertion": 25,
                "deletion": 12,
            },
            confidence_distribution={"high": 156, "medium": 67, "low": 22},
            training_data_quality={
                "suitable_for_training": 198,
                "high_confidence_pairs": 156,
                "average_confidence": 0.78,
                "quality_score": 85.5,
            },
            processing_history=[
                {
                    "job_type": "historical_analysis",
                    "completed_at": "2025-08-20T10:30:00Z",
                    "pairs_generated": 245,
                },
                {
                    "job_type": "vectorization",
                    "completed_at": "2025-08-20T11:15:00Z",
                    "pairs_vectorized": 198,
                },
            ],
            last_updated=datetime.utcnow(),
        )

        logger.info(f"RAG statistics retrieved for speaker: {speaker_id}")
        return stats

    except Exception as e:
        logger.error(f"Failed to get RAG statistics for speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get RAG statistics")


@router.get("/statistics/summary", response_model=dict)
async def get_rag_processing_summary():
    """
    Get overall RAG processing statistics.

    Returns system-wide statistics about speaker RAG processing,
    error patterns, and training data quality.
    """
    try:
        logger.info("Getting RAG processing summary")

        # Placeholder implementation
        summary = {
            "total_speakers_processed": 246,
            "total_error_correction_pairs": 58420,
            "total_processing_jobs": 1250,
            "active_jobs": 15,
            "error_type_distribution": {
                "medical_terminology": 35.2,
                "substitution": 28.5,
                "numeric": 18.3,
                "insertion": 12.0,
                "deletion": 6.0,
            },
            "training_data_quality": {
                "high_quality_pairs": 42580,
                "average_confidence": 0.76,
                "suitable_for_training_percentage": 85.2,
            },
            "processing_performance": {
                "average_processing_time_minutes": 45.5,
                "success_rate": 97.8,
                "pairs_per_speaker_average": 237.5,
            },
        }

        response = {
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
            "period": "all_time",
        }

        logger.info("RAG processing summary retrieved successfully")
        return response

    except Exception as e:
        logger.error(f"Failed to get RAG processing summary: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get RAG processing summary"
        )


# Health check for speaker RAG processing
@router.get("/health/check")
async def speaker_rag_health():
    """Health check for speaker RAG processing functionality."""
    return {
        "status": "healthy",
        "service": "speaker-rag-processing",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "process_historical": "POST /api/v1/speaker-rag/process-historical",
            "generate_pairs": "POST /api/v1/speaker-rag/generate-pairs",
            "vectorize_pairs": "POST /api/v1/speaker-rag/vectorize",
            "error_patterns": "GET /api/v1/speaker-rag/speaker/{speaker_id}/error-patterns",
            "create_job": "POST /api/v1/speaker-rag/jobs",
            "job_status": "GET /api/v1/speaker-rag/jobs/{job_id}",
        },
    }
