"""
Evaluate Bucket Progression Use Case
Handles automatic bucket progression evaluation when new reports are submitted
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from error_reporting_service.domain.entities.speaker_profile import SpeakerProfile, BucketProgressionRecommendation
from error_reporting_service.domain.repositories.speaker_profile_repository import SpeakerProfileRepository
from error_reporting_service.domain.services.bucket_progression_service import BucketProgressionService, BucketProgressionCriteria
from error_reporting_service.domain.value_objects.bucket_type import BucketType
from error_reporting_service.domain.value_objects.speaker_metrics import SpeakerMetrics


@dataclass
class EvaluateBucketProgressionRequest:
    """Request for bucket progression evaluation"""
    speaker_id: str
    trigger_event: str = "new_report_submitted"
    force_evaluation: bool = False


@dataclass
class EvaluateBucketProgressionResponse:
    """Response from bucket progression evaluation"""
    speaker_id: str
    evaluation_performed: bool
    recommendation: Optional[BucketProgressionRecommendation]
    bucket_changed: bool
    old_bucket: Optional[BucketType]
    new_bucket: Optional[BucketType]
    change_reason: Optional[str]
    evaluation_timestamp: datetime


class EvaluateBucketProgressionUseCase:
    """
    Use case for evaluating and applying bucket progression
    """
    
    def __init__(
        self,
        speaker_profile_repository: SpeakerProfileRepository,
        error_reports_repository,  # Will be injected
        progression_service: Optional[BucketProgressionService] = None,
        criteria: Optional[BucketProgressionCriteria] = None
    ):
        self.speaker_profile_repository = speaker_profile_repository
        self.error_reports_repository = error_reports_repository
        self.progression_service = progression_service or BucketProgressionService(criteria)
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, request: EvaluateBucketProgressionRequest) -> EvaluateBucketProgressionResponse:
        """
        Execute bucket progression evaluation
        """
        try:
            self.logger.info(f"Starting bucket progression evaluation for speaker {request.speaker_id}")
            
            # Get or create speaker profile
            speaker_profile = await self._get_or_create_speaker_profile(request.speaker_id)
            
            # Check if evaluation should be performed
            if not request.force_evaluation and not await self._should_evaluate(speaker_profile):
                return EvaluateBucketProgressionResponse(
                    speaker_id=request.speaker_id,
                    evaluation_performed=False,
                    recommendation=None,
                    bucket_changed=False,
                    old_bucket=speaker_profile.current_bucket,
                    new_bucket=speaker_profile.current_bucket,
                    change_reason="Evaluation criteria not met",
                    evaluation_timestamp=datetime.utcnow()
                )
            
            # Get recent error reports for the speaker
            recent_reports = await self._get_recent_reports(request.speaker_id)
            
            # Update speaker metrics
            await self._update_speaker_metrics(speaker_profile, recent_reports)
            
            # Evaluate progression
            recommendation = self.progression_service.evaluate_speaker_progression(
                speaker_profile, recent_reports
            )
            
            # Apply bucket change if recommended
            bucket_changed = False
            old_bucket = speaker_profile.current_bucket
            new_bucket = speaker_profile.current_bucket
            change_reason = None
            
            if recommendation.should_change_bucket():
                bucket_changed = await self._apply_bucket_change(
                    speaker_profile, recommendation
                )
                if bucket_changed:
                    new_bucket = recommendation.recommended_bucket
                    change_reason = recommendation.reason
            
            self.logger.info(
                f"Bucket progression evaluation completed for speaker {request.speaker_id}: "
                f"bucket_changed={bucket_changed}, old={old_bucket.value}, new={new_bucket.value}"
            )
            
            return EvaluateBucketProgressionResponse(
                speaker_id=request.speaker_id,
                evaluation_performed=True,
                recommendation=recommendation,
                bucket_changed=bucket_changed,
                old_bucket=old_bucket,
                new_bucket=new_bucket,
                change_reason=change_reason,
                evaluation_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error during bucket progression evaluation: {str(e)}")
            raise
    
    async def _get_or_create_speaker_profile(self, speaker_id: str) -> SpeakerProfile:
        """Get existing speaker profile or create new one"""
        profile = await self.speaker_profile_repository.get_by_speaker_id(speaker_id)
        
        if profile is None:
            # Create new profile with beginner bucket
            profile = await self.speaker_profile_repository.create_if_not_exists(
                speaker_id, BucketType.BEGINNER
            )
            self.logger.info(f"Created new speaker profile for {speaker_id} with beginner bucket")
        
        return profile
    
    async def _should_evaluate(self, speaker_profile: SpeakerProfile) -> bool:
        """Determine if speaker should be evaluated for bucket progression"""
        
        # Check minimum time in current bucket
        if speaker_profile.days_in_current_bucket < 7:
            return False
        
        # Check if speaker has recent activity
        if not speaker_profile.last_report_date:
            return False
        
        # Check if speaker has minimum number of reports
        if speaker_profile.total_reports < 3:
            return False
        
        # Check cooldown period (no recent bucket changes)
        recent_changes = await self.speaker_profile_repository.get_recent_bucket_changes(
            speaker_profile.speaker_id, days=14
        )
        if recent_changes:
            return False
        
        return True
    
    async def _get_recent_reports(self, speaker_id: str) -> List[Dict[str, Any]]:
        """Get recent error reports for the speaker"""
        # This would integrate with the error reports repository
        # For now, return empty list (will be implemented with actual repository)
        try:
            # Placeholder for actual implementation
            # reports = await self.error_reports_repository.get_by_speaker_id(
            #     speaker_id, limit=50, days=30
            # )
            reports = []
            return reports
        except Exception as e:
            self.logger.warning(f"Could not retrieve recent reports for {speaker_id}: {str(e)}")
            return []
    
    async def _update_speaker_metrics(
        self, 
        speaker_profile: SpeakerProfile, 
        recent_reports: List[Dict[str, Any]]
    ) -> None:
        """Update speaker profile with latest metrics"""
        
        # Calculate metrics from reports
        metrics = SpeakerMetrics.calculate_from_reports(recent_reports)
        
        # Update profile metrics
        speaker_profile.update_metrics(metrics)
        
        # Update days in current bucket
        if speaker_profile.created_at:
            days_since_creation = (datetime.utcnow() - speaker_profile.created_at).days
            speaker_profile.days_in_current_bucket = days_since_creation
        
        # Save updated profile
        await self.speaker_profile_repository.save(speaker_profile)
    
    async def _apply_bucket_change(
        self, 
        speaker_profile: SpeakerProfile, 
        recommendation: BucketProgressionRecommendation
    ) -> bool:
        """Apply bucket change based on recommendation"""
        
        if not recommendation.recommended_bucket:
            return False
        
        try:
            # Create bucket change log
            change_log = speaker_profile.change_bucket(
                recommendation.recommended_bucket,
                recommendation.reason
            )
            
            # Save change log
            await self.speaker_profile_repository.save_bucket_change_log(change_log)
            
            # Save updated profile
            await self.speaker_profile_repository.save(speaker_profile)
            
            self.logger.info(
                f"Applied bucket change for speaker {speaker_profile.speaker_id}: "
                f"{change_log.old_bucket.value} -> {change_log.new_bucket.value}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply bucket change: {str(e)}")
            return False


@dataclass
class BatchEvaluateBucketProgressionRequest:
    """Request for batch bucket progression evaluation"""
    max_profiles: int = 100
    force_evaluation: bool = False


@dataclass
class BatchEvaluateBucketProgressionResponse:
    """Response from batch bucket progression evaluation"""
    total_profiles_evaluated: int
    bucket_changes_applied: int
    evaluation_results: List[EvaluateBucketProgressionResponse]
    evaluation_timestamp: datetime


class BatchEvaluateBucketProgressionUseCase:
    """
    Use case for batch evaluation of bucket progression
    """
    
    def __init__(
        self,
        speaker_profile_repository: SpeakerProfileRepository,
        evaluate_use_case: EvaluateBucketProgressionUseCase
    ):
        self.speaker_profile_repository = speaker_profile_repository
        self.evaluate_use_case = evaluate_use_case
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, request: BatchEvaluateBucketProgressionRequest) -> BatchEvaluateBucketProgressionResponse:
        """
        Execute batch bucket progression evaluation
        """
        self.logger.info(f"Starting batch bucket progression evaluation for up to {request.max_profiles} profiles")
        
        # Get profiles eligible for evaluation
        eligible_profiles = await self.speaker_profile_repository.get_profiles_for_evaluation()
        
        # Limit to max profiles
        profiles_to_evaluate = eligible_profiles[:request.max_profiles]
        
        evaluation_results = []
        bucket_changes_applied = 0
        
        for profile in profiles_to_evaluate:
            try:
                # Evaluate individual profile
                eval_request = EvaluateBucketProgressionRequest(
                    speaker_id=profile.speaker_id,
                    trigger_event="batch_evaluation",
                    force_evaluation=request.force_evaluation
                )
                
                result = await self.evaluate_use_case.execute(eval_request)
                evaluation_results.append(result)
                
                if result.bucket_changed:
                    bucket_changes_applied += 1
                    
            except Exception as e:
                self.logger.error(f"Error evaluating profile {profile.speaker_id}: {str(e)}")
                continue
        
        self.logger.info(
            f"Batch evaluation completed: {len(evaluation_results)} profiles evaluated, "
            f"{bucket_changes_applied} bucket changes applied"
        )
        
        return BatchEvaluateBucketProgressionResponse(
            total_profiles_evaluated=len(evaluation_results),
            bucket_changes_applied=bucket_changes_applied,
            evaluation_results=evaluation_results,
            evaluation_timestamp=datetime.utcnow()
        )
