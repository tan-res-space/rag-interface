"""
Speaker Bucket Management Use Case

Handles quality-based speaker bucket assignments and history tracking.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from src.error_reporting_service.domain.entities.speaker_bucket_history import (
    SpeakerBucketHistory,
    AssignmentType,
)
from src.error_reporting_service.domain.entities.error_report import BucketType
from src.error_reporting_service.domain.ports.speaker_bucket_history_repository import (
    SpeakerBucketHistoryRepository,
)
from src.error_reporting_service.domain.ports.speaker_performance_metrics_repository import (
    SpeakerPerformanceMetricsRepository,
)
from src.error_reporting_service.application.dto.requests import (
    AssignSpeakerBucketRequest,
    GetSpeakerHistoryRequest,
)
from src.error_reporting_service.application.dto.responses import (
    SpeakerBucketHistoryResponse,
    BucketDistributionResponse,
)


class SpeakerBucketManagementUseCase:
    """Use case for managing speaker bucket assignments"""

    def __init__(
        self,
        bucket_history_repository: SpeakerBucketHistoryRepository,
        performance_metrics_repository: SpeakerPerformanceMetricsRepository,
    ):
        self._bucket_history_repository = bucket_history_repository
        self._performance_metrics_repository = performance_metrics_repository

    async def assign_speaker_bucket(
        self, request: AssignSpeakerBucketRequest
    ) -> SpeakerBucketHistoryResponse:
        """Assign a speaker to a quality-based bucket"""
        
        # Get current bucket for the speaker
        current_bucket = await self._bucket_history_repository.get_current_bucket(
            uuid.UUID(request.speaker_id)
        )
        
        # Get current performance metrics
        performance_metrics = await self._performance_metrics_repository.get_metrics_by_speaker(
            uuid.UUID(request.speaker_id)
        )
        
        # Create bucket assignment
        bucket_assignment = SpeakerBucketHistory(
            history_id=uuid.uuid4(),
            speaker_id=uuid.UUID(request.speaker_id),
            bucket_type=BucketType(request.bucket_type),
            assigned_date=datetime.utcnow(),
            assigned_by=uuid.UUID(request.assigned_by),
            assignment_reason=request.assignment_reason,
            assignment_type=AssignmentType(request.assignment_type),
            previous_bucket=current_bucket,
            error_count_at_assignment=performance_metrics.total_errors_reported if performance_metrics else 0,
            rectification_rate_at_assignment=performance_metrics.rectification_rate if performance_metrics else None,
            quality_score_at_assignment=performance_metrics.calculate_performance_score() if performance_metrics else None,
            confidence_score=0.95 if request.assignment_type == "manual" else 0.75,
        )
        
        # Save the assignment
        saved_assignment = await self._bucket_history_repository.save_bucket_assignment(
            bucket_assignment
        )
        
        # Return response
        return SpeakerBucketHistoryResponse(
            history_id=str(saved_assignment.history_id),
            speaker_id=str(saved_assignment.speaker_id),
            bucket_type=saved_assignment.bucket_type.value,
            previous_bucket=saved_assignment.previous_bucket.value if saved_assignment.previous_bucket else None,
            assigned_date=saved_assignment.assigned_date,
            assigned_by=str(saved_assignment.assigned_by),
            assignment_reason=saved_assignment.assignment_reason,
            assignment_type=saved_assignment.assignment_type.value,
            transition_description=saved_assignment.get_bucket_transition_description(),
            days_since_assignment=saved_assignment.calculate_days_since_assignment(),
            confidence_score=saved_assignment.confidence_score,
        )

    async def get_speaker_bucket_history(
        self, request: GetSpeakerHistoryRequest
    ) -> List[SpeakerBucketHistoryResponse]:
        """Get bucket history for a speaker"""
        
        history = await self._bucket_history_repository.get_bucket_transitions(
            speaker_id=uuid.UUID(request.speaker_id),
            start_date=request.start_date,
            end_date=request.end_date,
        )
        
        return [
            SpeakerBucketHistoryResponse(
                history_id=str(assignment.history_id),
                speaker_id=str(assignment.speaker_id),
                bucket_type=assignment.bucket_type.value,
                previous_bucket=assignment.previous_bucket.value if assignment.previous_bucket else None,
                assigned_date=assignment.assigned_date,
                assigned_by=str(assignment.assigned_by),
                assignment_reason=assignment.assignment_reason,
                assignment_type=assignment.assignment_type.value,
                transition_description=assignment.get_bucket_transition_description(),
                days_since_assignment=assignment.calculate_days_since_assignment(),
                confidence_score=assignment.confidence_score,
            )
            for assignment in history
        ]

    async def get_current_bucket(self, speaker_id: str) -> Optional[str]:
        """Get current bucket for a speaker"""
        
        bucket = await self._bucket_history_repository.get_current_bucket(
            uuid.UUID(speaker_id)
        )
        
        return bucket.value if bucket else None

    async def get_bucket_distribution(self) -> List[BucketDistributionResponse]:
        """Get current bucket distribution statistics"""
        
        distribution = await self._bucket_history_repository.get_bucket_distribution()
        
        return [
            BucketDistributionResponse(
                bucket_type=bucket_type,
                speaker_count=data["count"],
                percentage=data["percentage"],
                avg_rectification_rate=0.0,  # Will be calculated from performance metrics
                avg_days_in_bucket=0.0,  # Will be calculated from performance metrics
            )
            for bucket_type, data in distribution.items()
        ]

    async def recommend_bucket_reassignments(self) -> List[dict]:
        """Get speakers who should be reassessed for bucket changes"""
        
        speakers_for_reassessment = await self._performance_metrics_repository.get_speakers_for_reassessment()
        
        recommendations = []
        for metrics in speakers_for_reassessment:
            recommended_bucket = metrics.get_bucket_recommendation()
            
            if recommended_bucket != metrics.current_bucket:
                recommendations.append({
                    "speaker_id": str(metrics.speaker_id),
                    "current_bucket": metrics.current_bucket.value,
                    "recommended_bucket": recommended_bucket.value,
                    "performance_score": metrics.calculate_performance_score(),
                    "rectification_rate": metrics.rectification_rate,
                    "reason": self._get_reassignment_reason(metrics, recommended_bucket),
                    "confidence": self._calculate_reassignment_confidence(metrics),
                })
        
        return recommendations

    def _get_reassignment_reason(self, metrics, recommended_bucket) -> str:
        """Generate reason for bucket reassignment recommendation"""
        
        if metrics.quality_trend and metrics.quality_trend.value == "improving":
            return f"Performance improving - rectification rate: {metrics.rectification_rate:.2%}"
        elif metrics.quality_trend and metrics.quality_trend.value == "declining":
            return f"Performance declining - needs attention"
        elif metrics.rectification_rate >= 0.9:
            return f"Excellent performance - rectification rate: {metrics.rectification_rate:.2%}"
        elif metrics.rectification_rate < 0.5:
            return f"Low performance - rectification rate: {metrics.rectification_rate:.2%}"
        else:
            return f"Performance assessment - rectification rate: {metrics.rectification_rate:.2%}"

    def _calculate_reassignment_confidence(self, metrics) -> float:
        """Calculate confidence score for reassignment recommendation"""
        
        confidence = 0.5  # Base confidence
        
        # Higher confidence for more data
        if metrics.total_errors_reported >= 20:
            confidence += 0.2
        elif metrics.total_errors_reported >= 10:
            confidence += 0.1
        
        # Higher confidence for clear trends
        if metrics.quality_trend:
            if metrics.quality_trend.value in ["improving", "declining"]:
                confidence += 0.2
            else:
                confidence += 0.1
        
        # Higher confidence for extreme performance
        if metrics.rectification_rate >= 0.9 or metrics.rectification_rate <= 0.3:
            confidence += 0.2
        
        return min(confidence, 1.0)

    async def get_bucket_assignment_trends(self, days: int = 30) -> dict:
        """Get bucket assignment trends over time"""
        
        trends = await self._bucket_history_repository.get_assignment_trends(days)
        
        # Calculate trend statistics
        trend_stats = {
            "period_days": days,
            "daily_trends": trends,
            "summary": {
                "total_assignments": 0,
                "bucket_totals": {},
                "most_active_day": None,
                "least_active_day": None,
            }
        }
        
        # Calculate summary statistics
        daily_totals = {}
        for date, buckets in trends.items():
            daily_total = sum(buckets.values())
            daily_totals[date] = daily_total
            trend_stats["summary"]["total_assignments"] += daily_total
            
            for bucket, count in buckets.items():
                if bucket not in trend_stats["summary"]["bucket_totals"]:
                    trend_stats["summary"]["bucket_totals"][bucket] = 0
                trend_stats["summary"]["bucket_totals"][bucket] += count
        
        if daily_totals:
            trend_stats["summary"]["most_active_day"] = max(daily_totals, key=daily_totals.get)
            trend_stats["summary"]["least_active_day"] = min(daily_totals, key=daily_totals.get)
        
        return trend_stats

    async def validate_bucket_assignment(
        self, speaker_id: str, bucket_type: str, assignment_reason: str
    ) -> List[str]:
        """Validate bucket assignment and return any warnings"""
        
        warnings = []
        
        # Get current bucket
        current_bucket = await self.get_current_bucket(speaker_id)
        
        # Check if assignment is necessary
        if current_bucket == bucket_type:
            warnings.append(f"Speaker is already in {bucket_type} bucket")
        
        # Get performance metrics
        metrics = await self._performance_metrics_repository.get_metrics_by_speaker(
            uuid.UUID(speaker_id)
        )
        
        if metrics:
            recommended_bucket = metrics.get_bucket_recommendation()
            
            # Check if assignment aligns with recommendation
            if recommended_bucket.value != bucket_type:
                warnings.append(
                    f"Assignment to {bucket_type} does not align with "
                    f"performance-based recommendation: {recommended_bucket.value}"
                )
            
            # Check for insufficient data
            if not metrics.has_sufficient_data():
                warnings.append(
                    f"Limited performance data available "
                    f"({metrics.total_errors_reported} errors reported)"
                )
        else:
            warnings.append("No performance metrics available for this speaker")
        
        # Validate assignment reason
        if not assignment_reason or len(assignment_reason.strip()) < 10:
            warnings.append("Assignment reason should be more descriptive")
        
        return warnings
