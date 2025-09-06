"""
Bucket Progression Service
Implements the algorithm for automatic bucket classification updates
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from ..entities.speaker_profile import SpeakerProfile, BucketProgressionRecommendation, BucketProgressionDirection
from ..value_objects.bucket_type import BucketType
from ..value_objects.speaker_metrics import SpeakerMetrics


@dataclass
class BucketProgressionCriteria:
    """Configuration for bucket progression criteria"""
    
    # Minimum requirements
    min_reports_for_promotion: int = 10
    min_reports_for_demotion: int = 5
    min_days_in_bucket: int = 7
    evaluation_window_days: int = 30
    
    # Error rate thresholds for each bucket
    high_touch_max_error_rate: float = 0.15
    medium_touch_max_error_rate: float = 0.10
    low_touch_max_error_rate: float = 0.05
    no_touch_max_error_rate: float = 0.02

    # Correction accuracy thresholds
    high_touch_min_accuracy: float = 0.60
    medium_touch_min_accuracy: float = 0.75
    low_touch_min_accuracy: float = 0.85
    no_touch_min_accuracy: float = 0.95
    
    # Consistency requirements
    min_consistency_score: float = 0.70
    min_improvement_trend: float = 0.10
    
    # Confidence thresholds
    promotion_confidence_threshold: float = 0.80
    demotion_confidence_threshold: float = 0.75
    
    # Safeguards
    max_bucket_changes_per_month: int = 2
    cooldown_period_days: int = 14


class BucketProgressionService:
    """
    Service for evaluating and recommending bucket progression
    """
    
    def __init__(self, criteria: Optional[BucketProgressionCriteria] = None):
        self.criteria = criteria or BucketProgressionCriteria()
        self.logger = logging.getLogger(__name__)
    
    def evaluate_speaker_progression(
        self, 
        speaker_profile: SpeakerProfile, 
        recent_reports: List[Dict[str, Any]]
    ) -> BucketProgressionRecommendation:
        """
        Evaluate speaker progression and recommend bucket changes
        """
        # Calculate current metrics
        metrics = SpeakerMetrics.calculate_from_reports(recent_reports)
        
        # Check if speaker meets minimum requirements for evaluation
        if not self._meets_evaluation_requirements(speaker_profile, metrics):
            return BucketProgressionRecommendation(
                speaker_id=speaker_profile.speaker_id,
                current_bucket=speaker_profile.current_bucket,
                recommended_bucket=speaker_profile.current_bucket,
                direction=BucketProgressionDirection.STABLE,
                confidence_score=0.0,
                reason="Insufficient data for evaluation",
                metrics_used=metrics,
                analysis_date=datetime.utcnow()
            )
        
        # Evaluate for promotion
        promotion_recommendation = self._evaluate_promotion(speaker_profile, metrics)
        if promotion_recommendation.confidence_score >= self.criteria.promotion_confidence_threshold:
            return promotion_recommendation
        
        # Evaluate for demotion
        demotion_recommendation = self._evaluate_demotion(speaker_profile, metrics)
        if demotion_recommendation.confidence_score >= self.criteria.demotion_confidence_threshold:
            return demotion_recommendation
        
        # No change recommended
        return BucketProgressionRecommendation(
            speaker_id=speaker_profile.speaker_id,
            current_bucket=speaker_profile.current_bucket,
            recommended_bucket=speaker_profile.current_bucket,
            direction=BucketProgressionDirection.STABLE,
            confidence_score=0.5,
            reason="Performance meets current bucket requirements",
            metrics_used=metrics,
            analysis_date=datetime.utcnow()
        )
    
    def _meets_evaluation_requirements(
        self, 
        speaker_profile: SpeakerProfile, 
        metrics: SpeakerMetrics
    ) -> bool:
        """Check if speaker meets minimum requirements for bucket evaluation"""
        
        # Check minimum time in current bucket
        if speaker_profile.days_in_current_bucket < self.criteria.min_days_in_bucket:
            return False
        
        # Check recent activity
        if metrics.reports_last_30_days < 3:
            return False
        
        # Check cooldown period
        if self._is_in_cooldown_period(speaker_profile):
            return False
        
        # Check maximum changes per month
        if self._exceeds_change_limit(speaker_profile):
            return False
        
        return True
    
    def _evaluate_promotion(
        self, 
        speaker_profile: SpeakerProfile, 
        metrics: SpeakerMetrics
    ) -> BucketProgressionRecommendation:
        """Evaluate speaker for bucket promotion"""
        
        current_bucket = speaker_profile.current_bucket
        next_bucket = self._get_next_bucket(current_bucket)
        
        if not next_bucket:
            return BucketProgressionRecommendation(
                speaker_id=speaker_profile.speaker_id,
                current_bucket=current_bucket,
                recommended_bucket=current_bucket,
                direction=BucketProgressionDirection.STABLE,
                confidence_score=0.0,
                reason="Already at highest bucket level",
                metrics_used=metrics,
                analysis_date=datetime.utcnow()
            )
        
        # Check minimum reports requirement
        if metrics.total_reports < self.criteria.min_reports_for_promotion:
            return BucketProgressionRecommendation(
                speaker_id=speaker_profile.speaker_id,
                current_bucket=current_bucket,
                recommended_bucket=current_bucket,
                direction=BucketProgressionDirection.STABLE,
                confidence_score=0.0,
                reason=f"Insufficient reports for promotion (need {self.criteria.min_reports_for_promotion})",
                metrics_used=metrics,
                analysis_date=datetime.utcnow()
            )
        
        # Calculate promotion score
        promotion_score = self._calculate_promotion_score(next_bucket, metrics)
        
        reason = self._generate_promotion_reason(next_bucket, metrics, promotion_score)
        
        return BucketProgressionRecommendation(
            speaker_id=speaker_profile.speaker_id,
            current_bucket=current_bucket,
            recommended_bucket=next_bucket if promotion_score >= self.criteria.promotion_confidence_threshold else current_bucket,
            direction=BucketProgressionDirection.PROMOTION if promotion_score >= self.criteria.promotion_confidence_threshold else BucketProgressionDirection.STABLE,
            confidence_score=promotion_score,
            reason=reason,
            metrics_used=metrics,
            analysis_date=datetime.utcnow()
        )
    
    def _evaluate_demotion(
        self, 
        speaker_profile: SpeakerProfile, 
        metrics: SpeakerMetrics
    ) -> BucketProgressionRecommendation:
        """Evaluate speaker for bucket demotion"""
        
        current_bucket = speaker_profile.current_bucket
        previous_bucket = self._get_previous_bucket(current_bucket)
        
        if not previous_bucket:
            return BucketProgressionRecommendation(
                speaker_id=speaker_profile.speaker_id,
                current_bucket=current_bucket,
                recommended_bucket=current_bucket,
                direction=BucketProgressionDirection.STABLE,
                confidence_score=0.0,
                reason="Already at lowest bucket level",
                metrics_used=metrics,
                analysis_date=datetime.utcnow()
            )
        
        # Calculate demotion score
        demotion_score = self._calculate_demotion_score(current_bucket, metrics)
        
        reason = self._generate_demotion_reason(current_bucket, metrics, demotion_score)
        
        return BucketProgressionRecommendation(
            speaker_id=speaker_profile.speaker_id,
            current_bucket=current_bucket,
            recommended_bucket=previous_bucket if demotion_score >= self.criteria.demotion_confidence_threshold else current_bucket,
            direction=BucketProgressionDirection.DEMOTION if demotion_score >= self.criteria.demotion_confidence_threshold else BucketProgressionDirection.STABLE,
            confidence_score=demotion_score,
            reason=reason,
            metrics_used=metrics,
            analysis_date=datetime.utcnow()
        )
    
    def _calculate_promotion_score(self, target_bucket: BucketType, metrics: SpeakerMetrics) -> float:
        """Calculate confidence score for promotion to target bucket"""
        score = 0.0
        
        # Error rate score (40% weight)
        error_rate_score = self._calculate_error_rate_score(target_bucket, metrics.average_error_rate)
        score += error_rate_score * 0.4
        
        # Correction accuracy score (30% weight)
        accuracy_score = self._calculate_accuracy_score(target_bucket, metrics.average_correction_accuracy)
        score += accuracy_score * 0.3
        
        # Consistency score (15% weight)
        score += metrics.consistency_score * 0.15
        
        # Improvement trend score (15% weight)
        improvement_score = max(0.0, metrics.improvement_trend)
        score += improvement_score * 0.15
        
        return min(1.0, score)
    
    def _calculate_demotion_score(self, current_bucket: BucketType, metrics: SpeakerMetrics) -> float:
        """Calculate confidence score for demotion from current bucket"""
        score = 0.0
        
        # Check if performance falls below current bucket requirements
        error_rate_threshold = self._get_error_rate_threshold(current_bucket)
        accuracy_threshold = self._get_accuracy_threshold(current_bucket)
        
        # Error rate penalty
        if metrics.average_error_rate > error_rate_threshold:
            error_penalty = (metrics.average_error_rate - error_rate_threshold) / error_rate_threshold
            score += min(0.5, error_penalty)
        
        # Accuracy penalty
        if metrics.average_correction_accuracy < accuracy_threshold:
            accuracy_penalty = (accuracy_threshold - metrics.average_correction_accuracy) / accuracy_threshold
            score += min(0.3, accuracy_penalty)
        
        # Consistency penalty
        if metrics.consistency_score < self.criteria.min_consistency_score:
            consistency_penalty = (self.criteria.min_consistency_score - metrics.consistency_score) / self.criteria.min_consistency_score
            score += min(0.2, consistency_penalty)
        
        return min(1.0, score)
    
    def _calculate_error_rate_score(self, bucket: BucketType, error_rate: float) -> float:
        """Calculate score based on error rate for target bucket"""
        threshold = self._get_error_rate_threshold(bucket)
        if error_rate <= threshold:
            return 1.0
        elif error_rate <= threshold * 1.5:
            return 1.0 - ((error_rate - threshold) / threshold)
        else:
            return 0.0
    
    def _calculate_accuracy_score(self, bucket: BucketType, accuracy: float) -> float:
        """Calculate score based on correction accuracy for target bucket"""
        threshold = self._get_accuracy_threshold(bucket)
        if accuracy >= threshold:
            return 1.0
        elif accuracy >= threshold * 0.8:
            return accuracy / threshold
        else:
            return 0.0
    
    def _get_error_rate_threshold(self, bucket: BucketType) -> float:
        """Get error rate threshold for bucket"""
        thresholds = {
            BucketType.BEGINNER: self.criteria.beginner_max_error_rate,
            BucketType.INTERMEDIATE: self.criteria.intermediate_max_error_rate,
            BucketType.ADVANCED: self.criteria.advanced_max_error_rate,
            BucketType.EXPERT: self.criteria.expert_max_error_rate
        }
        return thresholds.get(bucket, 0.1)
    
    def _get_accuracy_threshold(self, bucket: BucketType) -> float:
        """Get accuracy threshold for bucket"""
        thresholds = {
            BucketType.HIGH_TOUCH: self.criteria.high_touch_min_accuracy,
            BucketType.MEDIUM_TOUCH: self.criteria.medium_touch_min_accuracy,
            BucketType.LOW_TOUCH: self.criteria.low_touch_min_accuracy,
            BucketType.NO_TOUCH: self.criteria.no_touch_min_accuracy
        }
        return thresholds.get(bucket, 0.7)
    
    def _get_next_bucket(self, current: BucketType) -> Optional[BucketType]:
        """Get next bucket level for promotion (better quality)"""
        progression = {
            BucketType.HIGH_TOUCH: BucketType.MEDIUM_TOUCH,
            BucketType.MEDIUM_TOUCH: BucketType.LOW_TOUCH,
            BucketType.LOW_TOUCH: BucketType.NO_TOUCH,
            BucketType.NO_TOUCH: None
        }
        return progression.get(current)
    
    def _get_previous_bucket(self, current: BucketType) -> Optional[BucketType]:
        """Get previous bucket level for demotion (lower quality)"""
        regression = {
            BucketType.NO_TOUCH: BucketType.LOW_TOUCH,
            BucketType.LOW_TOUCH: BucketType.MEDIUM_TOUCH,
            BucketType.MEDIUM_TOUCH: BucketType.HIGH_TOUCH,
            BucketType.HIGH_TOUCH: None
        }
        return regression.get(current)
    
    def _is_in_cooldown_period(self, speaker_profile: SpeakerProfile) -> bool:
        """Check if speaker is in cooldown period after recent bucket change"""
        # This would need to check the last bucket change date
        # For now, return False (implement with database integration)
        return False
    
    def _exceeds_change_limit(self, speaker_profile: SpeakerProfile) -> bool:
        """Check if speaker has exceeded maximum bucket changes per month"""
        # This would need to check bucket change history
        # For now, return False (implement with database integration)
        return False
    
    def _generate_promotion_reason(self, target_bucket: BucketType, metrics: SpeakerMetrics, score: float) -> str:
        """Generate human-readable reason for promotion recommendation"""
        if score >= self.criteria.promotion_confidence_threshold:
            return f"Excellent performance qualifies for {target_bucket.value} level: " \
                   f"Error rate {metrics.average_error_rate:.1%}, " \
                   f"Accuracy {metrics.average_correction_accuracy:.1%}, " \
                   f"Consistency {metrics.consistency_score:.1%}"
        else:
            return f"Performance approaching {target_bucket.value} level but needs improvement"
    
    def _generate_demotion_reason(self, current_bucket: BucketType, metrics: SpeakerMetrics, score: float) -> str:
        """Generate human-readable reason for demotion recommendation"""
        if score >= self.criteria.demotion_confidence_threshold:
            return f"Performance below {current_bucket.value} level requirements: " \
                   f"Error rate {metrics.average_error_rate:.1%}, " \
                   f"Accuracy {metrics.average_correction_accuracy:.1%}"
        else:
            return f"Performance meets {current_bucket.value} level requirements"
