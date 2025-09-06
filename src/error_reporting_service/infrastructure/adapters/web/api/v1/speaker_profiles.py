"""
Speaker Profile API Endpoints
Handles speaker profile management and bucket progression
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from error_reporting_service.infrastructure.adapters.database.in_memory.speaker_profile_adapter import InMemorySpeakerProfileAdapter
from error_reporting_service.application.use_cases.evaluate_bucket_progression_use_case import (
    EvaluateBucketProgressionUseCase,
    EvaluateBucketProgressionRequest,
    BatchEvaluateBucketProgressionUseCase,
    BatchEvaluateBucketProgressionRequest
)
from error_reporting_service.domain.services.bucket_progression_service import BucketProgressionService
from error_reporting_service.domain.value_objects.bucket_type import BucketType

# Mock authentication dependency
async def get_current_user():
    """Mock authentication - returns a test user"""
    return {
        "user_id": str(uuid.uuid4()),
        "username": "test_user",
        "email": "test@example.com"
    }

# Initialize dependencies (in production, these would be injected)
speaker_profile_adapter = InMemorySpeakerProfileAdapter()
progression_service = BucketProgressionService()
evaluate_use_case = EvaluateBucketProgressionUseCase(
    speaker_profile_repository=speaker_profile_adapter,
    error_reports_repository=None,  # Will be integrated later
    progression_service=progression_service
)
batch_evaluate_use_case = BatchEvaluateBucketProgressionUseCase(
    speaker_profile_repository=speaker_profile_adapter,
    evaluate_use_case=evaluate_use_case
)

router = APIRouter(prefix="/api/v1/speakers", tags=["Speaker Profiles"])


@router.get("/{speaker_id}/profile")
async def get_speaker_profile(
    speaker_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get speaker profile information
    """
    try:
        profile = await speaker_profile_adapter.get_by_speaker_id(speaker_id)
        
        if not profile:
            # Create new profile if it doesn't exist
            profile = await speaker_profile_adapter.create_if_not_exists(
                speaker_id, BucketType.BEGINNER
            )
        
        return {
            "speaker_id": profile.speaker_id,
            "current_bucket": profile.current_bucket.value,
            "bucket_info": {
                "label": profile.current_bucket.get_display_name(),
                "description": profile.current_bucket.get_description(),
                "color": profile.current_bucket.get_color(),
                "icon": profile.current_bucket.get_icon(),
                "level": profile.current_bucket.get_level()
            },
            "statistics": {
                "total_reports": profile.total_reports,
                "total_errors_found": profile.total_errors_found,
                "total_corrections_made": profile.total_corrections_made,
                "average_error_rate": round(profile.average_error_rate, 4),
                "average_correction_accuracy": round(profile.average_correction_accuracy, 4),
                "days_in_current_bucket": profile.days_in_current_bucket,
                "bucket_change_count": profile.bucket_change_count
            },
            "timestamps": {
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat(),
                "last_report_date": profile.last_report_date.isoformat() if profile.last_report_date else None
            },
            "metadata": profile.metadata
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving speaker profile: {str(e)}"
        )


@router.get("/{speaker_id}/bucket-history")
async def get_bucket_change_history(
    speaker_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get bucket change history for a speaker
    """
    try:
        change_history = await speaker_profile_adapter.get_bucket_change_history(
            speaker_id, limit
        )
        
        history_items = []
        for change in change_history:
            history_items.append({
                "change_id": change.change_id,
                "old_bucket": {
                    "type": change.old_bucket.value,
                    "label": change.old_bucket.get_display_name(),
                    "level": change.old_bucket.get_level()
                },
                "new_bucket": {
                    "type": change.new_bucket.value,
                    "label": change.new_bucket.get_display_name(),
                    "level": change.new_bucket.get_level()
                },
                "change_reason": change.change_reason,
                "changed_at": change.changed_at.isoformat(),
                "metrics_at_change": change.metrics_at_change.to_dict(),
                "metadata": change.metadata
            })
        
        return {
            "speaker_id": speaker_id,
            "total_changes": len(history_items),
            "history": history_items
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving bucket history: {str(e)}"
        )


@router.post("/{speaker_id}/evaluate-progression")
async def evaluate_speaker_progression(
    speaker_id: str,
    force_evaluation: bool = Query(False),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Trigger bucket progression evaluation for a speaker
    """
    try:
        request = EvaluateBucketProgressionRequest(
            speaker_id=speaker_id,
            trigger_event="manual_evaluation",
            force_evaluation=force_evaluation
        )
        
        response = await evaluate_use_case.execute(request)
        
        return {
            "speaker_id": response.speaker_id,
            "evaluation_performed": response.evaluation_performed,
            "bucket_changed": response.bucket_changed,
            "old_bucket": response.old_bucket.value if response.old_bucket else None,
            "new_bucket": response.new_bucket.value if response.new_bucket else None,
            "change_reason": response.change_reason,
            "recommendation": {
                "recommended_bucket": response.recommendation.recommended_bucket.value if response.recommendation and response.recommendation.recommended_bucket else None,
                "direction": response.recommendation.direction.value if response.recommendation else None,
                "confidence_score": response.recommendation.confidence_score if response.recommendation else 0.0,
                "reason": response.recommendation.reason if response.recommendation else None
            } if response.recommendation else None,
            "evaluation_timestamp": response.evaluation_timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating speaker progression: {str(e)}"
        )


@router.post("/batch-evaluate")
async def batch_evaluate_progression(
    max_profiles: int = Query(100, ge=1, le=500),
    force_evaluation: bool = Query(False),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Trigger batch bucket progression evaluation
    """
    try:
        request = BatchEvaluateBucketProgressionRequest(
            max_profiles=max_profiles,
            force_evaluation=force_evaluation
        )
        
        response = await batch_evaluate_use_case.execute(request)
        
        # Summarize results
        evaluation_summary = []
        for result in response.evaluation_results:
            evaluation_summary.append({
                "speaker_id": result.speaker_id,
                "bucket_changed": result.bucket_changed,
                "old_bucket": result.old_bucket.value if result.old_bucket else None,
                "new_bucket": result.new_bucket.value if result.new_bucket else None,
                "confidence_score": result.recommendation.confidence_score if result.recommendation else 0.0
            })
        
        return {
            "total_profiles_evaluated": response.total_profiles_evaluated,
            "bucket_changes_applied": response.bucket_changes_applied,
            "evaluation_timestamp": response.evaluation_timestamp.isoformat(),
            "results_summary": evaluation_summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during batch evaluation: {str(e)}"
        )


@router.get("/bucket-statistics")
async def get_bucket_statistics(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get overall bucket distribution statistics
    """
    try:
        stats = await speaker_profile_adapter.get_bucket_statistics()
        
        # Add bucket type information
        bucket_info = BucketType.get_bucket_info()
        enhanced_distribution = {}
        
        for bucket_type, count in stats["bucket_distribution"].items():
            enhanced_distribution[bucket_type] = {
                "count": count,
                "percentage": stats["bucket_percentages"][bucket_type],
                "info": bucket_info[bucket_type]
            }
        
        return {
            "total_profiles": stats["total_profiles"],
            "bucket_distribution": enhanced_distribution,
            "change_statistics": {
                "total_bucket_changes": stats["total_bucket_changes"],
                "recent_bucket_changes": stats["recent_bucket_changes"],
                "average_changes_per_profile": stats["average_changes_per_profile"]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving bucket statistics: {str(e)}"
        )


@router.get("/bucket-types")
async def get_bucket_types() -> dict:
    """
    Get information about all bucket types
    """
    bucket_info = BucketType.get_bucket_info()
    progression_order = BucketType.get_progression_order()
    
    return {
        "bucket_types": bucket_info,
        "progression_order": [bucket.value for bucket in progression_order],
        "total_levels": len(progression_order)
    }
