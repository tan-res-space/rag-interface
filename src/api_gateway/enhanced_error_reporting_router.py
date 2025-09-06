"""
Enhanced Error Reporting API Router

Provides API endpoints for the enhanced error reporting system with quality-based
bucket management and enhanced metadata support.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from error_reporting_service.application.use_cases.submit_error_report import (
    SubmitErrorReportUseCase,
)
from error_reporting_service.application.use_cases.speaker_bucket_management_use_case import (
    SpeakerBucketManagementUseCase,
)
from error_reporting_service.application.use_cases.dashboard_analytics_use_case import (
    DashboardAnalyticsUseCase,
)
from error_reporting_service.application.dto.requests import (
    SubmitErrorReportRequest,
    EnhancedMetadataRequest,
    AssignSpeakerBucketRequest,
    GetSpeakerHistoryRequest,
    GetDashboardMetricsRequest,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/enhanced-error-reporting",
    tags=["Enhanced Error Reporting"]
)


# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class EnhancedMetadataModel(BaseModel):
    """Enhanced metadata request model"""
    audio_quality: str = Field(..., description="Audio quality: good, fair, poor")
    speaker_clarity: str = Field(..., description="Speaker clarity: clear, somewhat_clear, unclear, very_unclear")
    background_noise: str = Field(..., description="Background noise: none, low, medium, high")
    number_of_speakers: str = Field(..., description="Number of speakers: one, two, three, four, five")
    overlapping_speech: bool = Field(..., description="Whether there is overlapping speech")
    requires_specialized_knowledge: bool = Field(..., description="Whether specialized knowledge is required")
    additional_notes: Optional[str] = Field(None, description="Additional notes (max 1000 characters)")


class SubmitErrorReportModel(BaseModel):
    """Submit error report request model"""
    job_id: str = Field(..., description="Job ID")
    speaker_id: str = Field(..., description="Speaker ID")
    client_id: str = Field(..., description="Client ID")
    original_text: str = Field(..., description="Original text with error")
    corrected_text: str = Field(..., description="Corrected text")
    error_categories: List[str] = Field(..., description="Error categories")
    severity_level: str = Field(..., description="Severity level: low, medium, high, critical")
    start_position: int = Field(..., description="Error start position")
    end_position: int = Field(..., description="Error end position")
    reported_by: str = Field(..., description="Reporter user ID")
    bucket_type: str = Field(..., description="Quality-based bucket: no_touch, low_touch, medium_touch, high_touch")
    enhanced_metadata: EnhancedMetadataModel = Field(..., description="Enhanced metadata")
    context_notes: Optional[str] = Field(None, description="Context notes")


class AssignBucketModel(BaseModel):
    """Assign speaker bucket request model"""
    speaker_id: str = Field(..., description="Speaker ID")
    bucket_type: str = Field(..., description="Bucket type: no_touch, low_touch, medium_touch, high_touch")
    assignment_reason: str = Field(..., description="Reason for assignment")
    assigned_by: str = Field(..., description="User ID of assigner")
    assignment_type: str = Field(default="manual", description="Assignment type: manual, automatic, system")


class ErrorFiltersModel(BaseModel):
    """Error report filters model"""
    speaker_id: Optional[str] = None
    client_id: Optional[str] = None
    bucket_types: Optional[List[str]] = None
    audio_quality: Optional[List[str]] = None
    requires_specialized_knowledge: Optional[bool] = None
    overlapping_speech: Optional[bool] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


# =====================================================
# DEPENDENCY INJECTION
# =====================================================

async def get_submit_error_report_use_case() -> SubmitErrorReportUseCase:
    """Get submit error report use case instance"""
    # This would be properly injected in a real implementation
    # For now, return a placeholder
    raise HTTPException(status_code=501, detail="Use case not implemented")


async def get_speaker_bucket_management_use_case() -> SpeakerBucketManagementUseCase:
    """Get speaker bucket management use case instance"""
    # This would be properly injected in a real implementation
    raise HTTPException(status_code=501, detail="Use case not implemented")


async def get_dashboard_analytics_use_case() -> DashboardAnalyticsUseCase:
    """Get dashboard analytics use case instance"""
    # This would be properly injected in a real implementation
    raise HTTPException(status_code=501, detail="Use case not implemented")


# =====================================================
# ERROR REPORTING ENDPOINTS
# =====================================================

@router.post("/error-reports", response_model=dict)
async def submit_error_report(
    request: SubmitErrorReportModel,
    use_case: SubmitErrorReportUseCase = Depends(get_submit_error_report_use_case)
):
    """
    Submit an error report with enhanced metadata.
    
    Creates a new error report with quality-based bucket assignment and
    comprehensive metadata for improved analysis and processing.
    """
    try:
        logger.info(f"Submitting error report for speaker {request.speaker_id}")
        
        # Convert API model to use case request
        enhanced_metadata_request = EnhancedMetadataRequest(
            audio_quality=request.enhanced_metadata.audio_quality,
            speaker_clarity=request.enhanced_metadata.speaker_clarity,
            background_noise=request.enhanced_metadata.background_noise,
            number_of_speakers=request.enhanced_metadata.number_of_speakers,
            overlapping_speech=request.enhanced_metadata.overlapping_speech,
            requires_specialized_knowledge=request.enhanced_metadata.requires_specialized_knowledge,
            additional_notes=request.enhanced_metadata.additional_notes,
        )
        
        use_case_request = SubmitErrorReportRequest(
            job_id=request.job_id,
            speaker_id=request.speaker_id,
            client_id=request.client_id,
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            error_categories=request.error_categories,
            severity_level=request.severity_level,
            start_position=request.start_position,
            end_position=request.end_position,
            reported_by=request.reported_by,
            bucket_type=request.bucket_type,
            enhanced_metadata=enhanced_metadata_request,
            context_notes=request.context_notes,
        )
        
        # Execute use case
        response = await use_case.execute(use_case_request)
        
        logger.info(f"Error report submitted successfully: {response.error_id}")
        return {
            "success": True,
            "error_id": response.error_id,
            "status": response.status,
            "message": response.message,
            "submission_timestamp": response.submission_timestamp,
            "vector_db_id": response.vector_db_id,
            "validation_warnings": response.validation_warnings,
        }
        
    except ValueError as e:
        logger.error(f"Validation error submitting error report: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to submit error report: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit error report")


@router.get("/error-reports", response_model=dict)
async def search_error_reports(
    filters: ErrorFiltersModel = Depends(),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Search error reports with enhanced metadata filters.
    
    Provides comprehensive filtering capabilities including bucket types,
    audio quality, specialized knowledge requirements, and more.
    """
    try:
        logger.info(f"Searching error reports with filters: {filters}")
        
        # This would use the search use case
        # For now, return a placeholder response
        return {
            "success": True,
            "error_reports": [],
            "total_count": 0,
            "page": page,
            "limit": limit,
            "has_next": False,
            "has_previous": False,
            "filters_applied": filters.dict(exclude_none=True),
        }
        
    except Exception as e:
        logger.error(f"Failed to search error reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to search error reports")


@router.get("/error-reports/{error_id}", response_model=dict)
async def get_error_report(
    error_id: UUID,
    include_metadata: bool = Query(True, description="Include enhanced metadata"),
):
    """
    Get a specific error report by ID.
    
    Returns detailed error report information including enhanced metadata
    and quality-based bucket information.
    """
    try:
        logger.info(f"Getting error report: {error_id}")
        
        # This would use the get error report use case
        # For now, return a placeholder response
        return {
            "success": True,
            "error_report": {
                "error_id": str(error_id),
                "status": "submitted",
                "bucket_type": "medium_touch",
                "enhanced_metadata": {
                    "audio_quality": "good",
                    "speaker_clarity": "clear",
                    "background_noise": "low",
                    "number_of_speakers": "one",
                    "overlapping_speech": False,
                    "requires_specialized_knowledge": True,
                },
                "complexity_score": 3.2,
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get error report {error_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get error report")


# =====================================================
# SPEAKER BUCKET MANAGEMENT ENDPOINTS
# =====================================================

@router.post("/speakers/assign-bucket", response_model=dict)
async def assign_speaker_bucket(
    request: AssignBucketModel,
    use_case: SpeakerBucketManagementUseCase = Depends(get_speaker_bucket_management_use_case)
):
    """
    Assign a speaker to a quality-based bucket.
    
    Creates a bucket assignment with tracking and validation.
    """
    try:
        logger.info(f"Assigning speaker {request.speaker_id} to bucket {request.bucket_type}")
        
        # Convert to use case request
        use_case_request = AssignSpeakerBucketRequest(
            speaker_id=request.speaker_id,
            bucket_type=request.bucket_type,
            assignment_reason=request.assignment_reason,
            assigned_by=request.assigned_by,
            assignment_type=request.assignment_type,
        )
        
        # Execute use case
        response = await use_case.assign_speaker_bucket(use_case_request)
        
        logger.info(f"Speaker bucket assigned successfully: {response.history_id}")
        return {
            "success": True,
            "assignment": {
                "history_id": response.history_id,
                "speaker_id": response.speaker_id,
                "bucket_type": response.bucket_type,
                "previous_bucket": response.previous_bucket,
                "assigned_date": response.assigned_date.isoformat(),
                "transition_description": response.transition_description,
                "confidence_score": response.confidence_score,
            }
        }
        
    except ValueError as e:
        logger.error(f"Validation error assigning bucket: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to assign speaker bucket: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign speaker bucket")


@router.get("/speakers/{speaker_id}/bucket-history", response_model=dict)
async def get_speaker_bucket_history(
    speaker_id: UUID,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit results"),
    use_case: SpeakerBucketManagementUseCase = Depends(get_speaker_bucket_management_use_case)
):
    """
    Get bucket history for a speaker.
    
    Returns the complete bucket assignment history with transitions and reasons.
    """
    try:
        logger.info(f"Getting bucket history for speaker: {speaker_id}")
        
        # Convert dates if provided
        start_datetime = datetime.fromisoformat(start_date) if start_date else None
        end_datetime = datetime.fromisoformat(end_date) if end_date else None
        
        # Create use case request
        use_case_request = GetSpeakerHistoryRequest(
            speaker_id=str(speaker_id),
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit,
        )
        
        # Execute use case
        history = await use_case.get_speaker_bucket_history(use_case_request)
        
        logger.info(f"Retrieved {len(history)} bucket history entries")
        return {
            "success": True,
            "speaker_id": str(speaker_id),
            "history": [
                {
                    "history_id": entry.history_id,
                    "bucket_type": entry.bucket_type,
                    "previous_bucket": entry.previous_bucket,
                    "assigned_date": entry.assigned_date.isoformat(),
                    "assignment_reason": entry.assignment_reason,
                    "assignment_type": entry.assignment_type,
                    "transition_description": entry.transition_description,
                    "days_since_assignment": entry.days_since_assignment,
                    "confidence_score": entry.confidence_score,
                }
                for entry in history
            ],
            "total_entries": len(history),
        }
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    except Exception as e:
        logger.error(f"Failed to get speaker bucket history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get speaker bucket history")


@router.get("/buckets/distribution", response_model=dict)
async def get_bucket_distribution(
    use_case: SpeakerBucketManagementUseCase = Depends(get_speaker_bucket_management_use_case)
):
    """
    Get current bucket distribution statistics.
    
    Returns the distribution of speakers across quality-based buckets.
    """
    try:
        logger.info("Getting bucket distribution")
        
        distribution = await use_case.get_bucket_distribution()
        
        return {
            "success": True,
            "distribution": [
                {
                    "bucket_type": entry.bucket_type,
                    "speaker_count": entry.speaker_count,
                    "percentage": entry.percentage,
                    "avg_rectification_rate": entry.avg_rectification_rate,
                    "avg_days_in_bucket": entry.avg_days_in_bucket,
                }
                for entry in distribution
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Failed to get bucket distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bucket distribution")


# =====================================================
# DASHBOARD ANALYTICS ENDPOINTS
# =====================================================

@router.get("/dashboard/metrics/{metric_type}", response_model=dict)
async def get_dashboard_metrics(
    metric_type: str,
    time_period: Optional[str] = Query("last_30_days", description="Time period for metrics"),
    use_case: DashboardAnalyticsUseCase = Depends(get_dashboard_analytics_use_case)
):
    """
    Get dashboard metrics by type.
    
    Provides comprehensive analytics for the enhanced error reporting dashboard.
    """
    try:
        logger.info(f"Getting dashboard metrics: {metric_type}")
        
        # Create use case request
        use_case_request = GetDashboardMetricsRequest(
            metric_type=metric_type,
            time_period=time_period,
        )
        
        # Execute use case
        response = await use_case.get_dashboard_metrics(use_case_request)
        
        return {
            "success": True,
            "metric_type": response.metric_type,
            "time_period": response.time_period,
            "data": response.data,
            "generated_at": response.generated_at.isoformat(),
        }
        
    except ValueError as e:
        logger.error(f"Invalid metric type: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard metrics")


# =====================================================
# HEALTH CHECK ENDPOINTS
# =====================================================

@router.get("/health", response_model=dict)
async def health_check():
    """
    Health check for enhanced error reporting service.
    """
    return {
        "status": "healthy",
        "service": "enhanced-error-reporting",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "features": [
            "quality_based_buckets",
            "enhanced_metadata",
            "speaker_history_tracking",
            "dashboard_analytics",
        ]
    }
