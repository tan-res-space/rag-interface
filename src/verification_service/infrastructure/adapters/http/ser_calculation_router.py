"""
SER Calculation API Router

FastAPI router for SER (Sentence Edit Rate) calculation endpoints.
Implements REST API for SER metrics calculation and analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

from ....application.use_cases.calculate_ser_metrics_use_case import CalculateSERMetricsUseCase
from ....application.dto.requests import (
    CalculateSERRequest,
    BatchCalculateSERRequest,
    GetSERComparisonRequest,
    GetSpeakerSERAnalysisRequest
)
from ....application.dto.responses import (
    SERCalculationResponse,
    BatchSERCalculationResponse,
    SERComparisonResponse,
    SpeakerSERAnalysisResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/ser", tags=["SER Calculation"])


# Dependency injection placeholder
async def get_ser_calculation_use_case() -> CalculateSERMetricsUseCase:
    """Get SER calculation use case instance."""
    # TODO: Implement proper dependency injection
    raise HTTPException(status_code=501, detail="SER calculation use case not implemented")


@router.post("/calculate", response_model=SERCalculationResponse, status_code=201)
async def calculate_ser_metrics(
    request: CalculateSERRequest,
    use_case: CalculateSERMetricsUseCase = Depends(get_ser_calculation_use_case)
):
    """
    Calculate SER metrics for a single text pair.
    
    Computes comprehensive SER metrics including edit distance, insertions,
    deletions, moves, and quality scores for ASR quality assessment.
    """
    try:
        logger.info(f"Calculating SER metrics for speaker: {request.speaker_id}")
        response = await use_case.execute(request)
        logger.info(f"SER calculation completed: {response.ser_metrics.ser_score}%")
        return response
    
    except ValueError as e:
        logger.warning(f"Invalid SER calculation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to calculate SER metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate SER metrics")


@router.post("/calculate/batch", response_model=BatchSERCalculationResponse, status_code=201)
async def calculate_ser_metrics_batch(
    request: BatchCalculateSERRequest,
    use_case: CalculateSERMetricsUseCase = Depends(get_ser_calculation_use_case)
):
    """
    Calculate SER metrics for multiple text pairs.
    
    Efficiently processes multiple text pairs and returns comprehensive
    SER metrics with summary statistics.
    """
    try:
        logger.info(f"Calculating SER metrics for {len(request.calculation_items)} text pairs")
        response = await use_case.execute_batch(request)
        logger.info(f"Batch SER calculation completed: {response.successful_calculations} successful")
        return response
    
    except ValueError as e:
        logger.warning(f"Invalid batch SER calculation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to calculate batch SER metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate batch SER metrics")


@router.post("/compare", response_model=SERComparisonResponse)
async def compare_ser_results(
    request: GetSERComparisonRequest,
    use_case: CalculateSERMetricsUseCase = Depends(get_ser_calculation_use_case)
):
    """
    Compare SER results between original and corrected texts.
    
    Analyzes improvement between original ASR output and RAG-corrected text
    for speaker quality assessment and bucket transition decisions.
    """
    try:
        logger.info(f"Comparing SER results for speaker: {request.speaker_id}")
        response = await use_case.get_ser_comparison(request)
        logger.info(f"SER comparison completed for {len(request.historical_data_ids)} items")
        return response
    
    except ValueError as e:
        logger.warning(f"Invalid SER comparison request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to compare SER results: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare SER results")


@router.get("/speaker/{speaker_id}/analysis", response_model=SpeakerSERAnalysisResponse)
async def get_speaker_ser_analysis(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    include_historical_trend: bool = Query(True, description="Include historical trend analysis"),
    include_quality_distribution: bool = Query(True, description="Include quality distribution"),
    include_error_pattern_analysis: bool = Query(False, description="Include error pattern analysis"),
    date_range_start: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_range_end: Optional[str] = Query(None, description="End date (ISO format)"),
    use_case: CalculateSERMetricsUseCase = Depends(get_ser_calculation_use_case)
):
    """
    Get comprehensive SER analysis for a speaker.
    
    Returns detailed SER analysis including trends, quality distribution,
    and improvement opportunities for speaker bucket management.
    """
    try:
        request = GetSpeakerSERAnalysisRequest(
            speaker_id=str(speaker_id),
            include_historical_trend=include_historical_trend,
            include_quality_distribution=include_quality_distribution,
            include_error_pattern_analysis=include_error_pattern_analysis,
            date_range_start=date_range_start,
            date_range_end=date_range_end
        )
        
        logger.info(f"Getting SER analysis for speaker: {speaker_id}")
        response = await use_case.get_speaker_ser_analysis(request)
        logger.info(f"SER analysis completed for speaker: {speaker_id}")
        return response
    
    except ValueError as e:
        logger.warning(f"Invalid SER analysis request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to get SER analysis for speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SER analysis")


@router.get("/speaker/{speaker_id}/average", response_model=dict)
async def calculate_speaker_average_ser(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    use_case: CalculateSERMetricsUseCase = Depends(get_ser_calculation_use_case)
):
    """
    Calculate average SER score for a speaker.
    
    Returns the average SER score across all processed notes for the speaker.
    """
    try:
        logger.info(f"Calculating average SER for speaker: {speaker_id}")
        # This would need to be implemented in the use case
        # For now, return a placeholder response
        average_ser = await use_case.calculate_speaker_average_ser(speaker_id, [])
        
        response = {
            "speaker_id": str(speaker_id),
            "average_ser_score": float(average_ser),
            "calculation_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Average SER calculated for speaker {speaker_id}: {average_ser}")
        return response
    
    except ValueError as e:
        logger.warning(f"Speaker not found: {speaker_id}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to calculate average SER for speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate average SER")


@router.get("/quality/distribution", response_model=dict)
async def get_quality_distribution(
    speaker_id: Optional[UUID] = Query(None, description="Speaker ID for speaker-specific distribution"),
    use_case: CalculateSERMetricsUseCase = Depends(get_ser_calculation_use_case)
):
    """
    Get quality distribution from SER metrics.
    
    Returns distribution of quality levels (high, medium, low) across
    all speakers or for a specific speaker.
    """
    try:
        logger.info(f"Getting quality distribution for speaker: {speaker_id or 'all speakers'}")
        
        # This would need to be implemented in the use case
        # For now, return a placeholder response
        distribution = {
            "high": 45,
            "medium": 35,
            "low": 20
        }
        
        response = {
            "speaker_id": str(speaker_id) if speaker_id else None,
            "quality_distribution": distribution,
            "total_samples": sum(distribution.values()),
            "calculation_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("Quality distribution calculated successfully")
        return response
    
    except Exception as e:
        logger.error(f"Failed to get quality distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quality distribution")


@router.get("/metrics/summary", response_model=dict)
async def get_ser_metrics_summary():
    """
    Get summary of SER metrics across the system.
    
    Returns overall SER statistics, trends, and quality insights
    for system-wide monitoring and reporting.
    """
    try:
        logger.info("Getting SER metrics summary")
        
        # Placeholder implementation
        summary = {
            "total_calculations": 15420,
            "average_ser_score": 18.5,
            "quality_distribution": {
                "high_quality": 35.2,
                "medium_quality": 42.8,
                "low_quality": 22.0
            },
            "improvement_trends": {
                "speakers_improving": 78,
                "speakers_stable": 156,
                "speakers_declining": 12
            },
            "bucket_recommendations": {
                "ready_for_promotion": 23,
                "maintain_current": 198,
                "needs_attention": 25
            },
            "processing_statistics": {
                "calculations_today": 342,
                "average_processing_time_ms": 125,
                "success_rate": 99.7
            }
        }
        
        response = {
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
            "period": "last_30_days"
        }
        
        logger.info("SER metrics summary retrieved successfully")
        return response
    
    except Exception as e:
        logger.error(f"Failed to get SER metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SER metrics summary")


# Health check for SER calculation
@router.get("/health/check")
async def ser_calculation_health():
    """Health check for SER calculation functionality."""
    return {
        "status": "healthy",
        "service": "ser-calculation",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "calculate_ser": "POST /api/v1/ser/calculate",
            "batch_calculate": "POST /api/v1/ser/calculate/batch",
            "compare_results": "POST /api/v1/ser/compare",
            "speaker_analysis": "GET /api/v1/ser/speaker/{speaker_id}/analysis",
            "quality_distribution": "GET /api/v1/ser/quality/distribution"
        }
    }
