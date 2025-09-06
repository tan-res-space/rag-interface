"""
Dashboard Analytics Use Case

Provides analytics and insights for the enhanced error reporting dashboard.
"""

from datetime import datetime, timedelta
from typing import Dict, List

from error_reporting_service.domain.ports.error_report_repository import (
    ErrorReportRepository,
)
from error_reporting_service.domain.ports.speaker_bucket_history_repository import (
    SpeakerBucketHistoryRepository,
)
from error_reporting_service.domain.ports.speaker_performance_metrics_repository import (
    SpeakerPerformanceMetricsRepository,
)
from error_reporting_service.domain.ports.verification_job_repository import (
    VerificationJobRepository,
)
from error_reporting_service.application.dto.requests import (
    GetDashboardMetricsRequest,
)
from error_reporting_service.application.dto.responses import (
    DashboardMetricsResponse,
)


class DashboardAnalyticsUseCase:
    """Use case for dashboard analytics and insights"""

    def __init__(
        self,
        error_report_repository: ErrorReportRepository,
        bucket_history_repository: SpeakerBucketHistoryRepository,
        performance_metrics_repository: SpeakerPerformanceMetricsRepository,
        verification_job_repository: VerificationJobRepository,
    ):
        self._error_report_repository = error_report_repository
        self._bucket_history_repository = bucket_history_repository
        self._performance_metrics_repository = performance_metrics_repository
        self._verification_job_repository = verification_job_repository

    async def get_dashboard_metrics(
        self, request: GetDashboardMetricsRequest
    ) -> DashboardMetricsResponse:
        """Get dashboard metrics based on request type"""
        
        time_period = request.time_period or "last_30_days"
        
        if request.metric_type == "bucket_overview":
            data = await self._get_bucket_overview_metrics(time_period)
        elif request.metric_type == "performance_metrics":
            data = await self._get_performance_metrics(time_period)
        elif request.metric_type == "metadata_insights":
            data = await self._get_metadata_insights(time_period)
        elif request.metric_type == "verification_metrics":
            data = await self._get_verification_metrics(time_period)
        else:
            raise ValueError(f"Unknown metric type: {request.metric_type}")
        
        return DashboardMetricsResponse(
            metric_type=request.metric_type,
            time_period=time_period,
            data=data,
            generated_at=datetime.utcnow(),
        )

    async def _get_bucket_overview_metrics(self, time_period: str) -> Dict:
        """Get bucket overview metrics"""
        
        # Get bucket distribution
        distribution = await self._bucket_history_repository.get_bucket_distribution()
        
        # Get bucket statistics
        bucket_stats = await self._performance_metrics_repository.get_bucket_statistics()
        
        # Get assignment trends
        days = self._get_days_from_period(time_period)
        assignment_trends = await self._bucket_history_repository.get_assignment_trends(days)
        
        return {
            "bucket_distribution": distribution,
            "bucket_statistics": bucket_stats,
            "assignment_trends": assignment_trends,
            "total_speakers": sum(data["count"] for data in distribution.values()),
            "most_common_bucket": max(distribution.keys(), key=lambda k: distribution[k]["count"]) if distribution else None,
            "bucket_transition_summary": await self._get_bucket_transition_summary(days),
        }

    async def _get_performance_metrics(self, time_period: str) -> Dict:
        """Get performance metrics"""
        
        days = self._get_days_from_period(time_period)
        
        # Get performance trends
        performance_trends = await self._performance_metrics_repository.get_performance_trends(days)
        
        # Get high performers
        high_performers = await self._performance_metrics_repository.get_high_performers()
        
        # Get speakers needing attention
        speakers_needing_attention = await self._performance_metrics_repository.get_speakers_needing_attention()
        
        # Get speakers for reassessment
        speakers_for_reassessment = await self._performance_metrics_repository.get_speakers_for_reassessment()
        
        return {
            "performance_trends": performance_trends,
            "high_performers_count": len(high_performers),
            "speakers_needing_attention_count": len(speakers_needing_attention),
            "speakers_for_reassessment_count": len(speakers_for_reassessment),
            "average_performance_by_bucket": await self._calculate_average_performance_by_bucket(),
            "performance_distribution": await self._get_performance_distribution(),
        }

    async def _get_metadata_insights(self, time_period: str) -> Dict:
        """Get enhanced metadata insights"""
        
        days = self._get_days_from_period(time_period)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get error reports within time period
        filters = {
            "date_from": start_date,
            "date_to": datetime.utcnow(),
        }
        
        error_reports = await self._error_report_repository.search_errors(filters)
        
        # Analyze metadata patterns
        audio_quality_distribution = self._analyze_audio_quality(error_reports)
        speaker_clarity_distribution = self._analyze_speaker_clarity(error_reports)
        background_noise_distribution = self._analyze_background_noise(error_reports)
        speaker_count_distribution = self._analyze_speaker_count(error_reports)
        
        # Analyze correlations
        correlations = self._analyze_metadata_correlations(error_reports)
        
        return {
            "total_errors_analyzed": len(error_reports),
            "audio_quality_distribution": audio_quality_distribution,
            "speaker_clarity_distribution": speaker_clarity_distribution,
            "background_noise_distribution": background_noise_distribution,
            "speaker_count_distribution": speaker_count_distribution,
            "overlapping_speech_frequency": self._calculate_overlapping_speech_frequency(error_reports),
            "specialized_knowledge_frequency": self._calculate_specialized_knowledge_frequency(error_reports),
            "metadata_correlations": correlations,
            "complexity_score_distribution": self._analyze_complexity_scores(error_reports),
        }

    async def _get_verification_metrics(self, time_period: str) -> Dict:
        """Get verification workflow metrics"""
        
        days = self._get_days_from_period(time_period)
        
        # Get verification statistics
        verification_stats = await self._verification_job_repository.get_verification_statistics(days)
        
        return verification_stats

    def _get_days_from_period(self, time_period: str) -> int:
        """Convert time period string to number of days"""
        
        period_mapping = {
            "last_7_days": 7,
            "last_30_days": 30,
            "last_90_days": 90,
            "last_6_months": 180,
            "last_year": 365,
        }
        
        return period_mapping.get(time_period, 30)

    async def _get_bucket_transition_summary(self, days: int) -> Dict:
        """Get summary of bucket transitions"""
        
        # This would analyze bucket transitions over the period
        # For now, return a placeholder structure
        return {
            "total_transitions": 0,
            "upgrades": 0,
            "downgrades": 0,
            "lateral_moves": 0,
            "most_common_transition": None,
        }

    async def _calculate_average_performance_by_bucket(self) -> Dict:
        """Calculate average performance metrics by bucket type"""
        
        bucket_stats = await self._performance_metrics_repository.get_bucket_statistics()
        
        return {
            bucket_type: {
                "avg_rectification_rate": stats["avg_rectification_rate"],
                "avg_total_errors": stats["avg_total_errors"],
                "speaker_count": stats["speaker_count"],
            }
            for bucket_type, stats in bucket_stats.items()
        }

    async def _get_performance_distribution(self) -> Dict:
        """Get distribution of performance scores"""
        
        # This would analyze performance score distribution
        # For now, return a placeholder structure
        return {
            "excellent": 0,  # 8.5-10.0
            "good": 0,       # 7.0-8.4
            "average": 0,    # 5.0-6.9
            "poor": 0,       # 0.0-4.9
        }

    def _analyze_audio_quality(self, error_reports: List) -> Dict:
        """Analyze audio quality distribution"""
        
        quality_counts = {"good": 0, "fair": 0, "poor": 0}
        
        for report in error_reports:
            quality = report.enhanced_metadata.audio_quality.value
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        total = len(error_reports)
        return {
            quality: {
                "count": count,
                "percentage": round((count / total) * 100, 2) if total > 0 else 0
            }
            for quality, count in quality_counts.items()
        }

    def _analyze_speaker_clarity(self, error_reports: List) -> Dict:
        """Analyze speaker clarity distribution"""
        
        clarity_counts = {"clear": 0, "somewhat_clear": 0, "unclear": 0, "very_unclear": 0}
        
        for report in error_reports:
            clarity = report.enhanced_metadata.speaker_clarity.value
            clarity_counts[clarity] = clarity_counts.get(clarity, 0) + 1
        
        total = len(error_reports)
        return {
            clarity: {
                "count": count,
                "percentage": round((count / total) * 100, 2) if total > 0 else 0
            }
            for clarity, count in clarity_counts.items()
        }

    def _analyze_background_noise(self, error_reports: List) -> Dict:
        """Analyze background noise distribution"""
        
        noise_counts = {"none": 0, "low": 0, "medium": 0, "high": 0}
        
        for report in error_reports:
            noise = report.enhanced_metadata.background_noise.value
            noise_counts[noise] = noise_counts.get(noise, 0) + 1
        
        total = len(error_reports)
        return {
            noise: {
                "count": count,
                "percentage": round((count / total) * 100, 2) if total > 0 else 0
            }
            for noise, count in noise_counts.items()
        }

    def _analyze_speaker_count(self, error_reports: List) -> Dict:
        """Analyze number of speakers distribution"""
        
        speaker_counts = {"one": 0, "two": 0, "three": 0, "four": 0, "five": 0}
        
        for report in error_reports:
            count = report.enhanced_metadata.number_of_speakers.value
            speaker_counts[count] = speaker_counts.get(count, 0) + 1
        
        total = len(error_reports)
        return {
            count: {
                "count": speaker_count,
                "percentage": round((speaker_count / total) * 100, 2) if total > 0 else 0
            }
            for count, speaker_count in speaker_counts.items()
        }

    def _calculate_overlapping_speech_frequency(self, error_reports: List) -> float:
        """Calculate frequency of overlapping speech"""
        
        if not error_reports:
            return 0.0
        
        overlapping_count = sum(
            1 for report in error_reports 
            if report.enhanced_metadata.overlapping_speech
        )
        
        return round((overlapping_count / len(error_reports)) * 100, 2)

    def _calculate_specialized_knowledge_frequency(self, error_reports: List) -> float:
        """Calculate frequency of specialized knowledge requirement"""
        
        if not error_reports:
            return 0.0
        
        specialized_count = sum(
            1 for report in error_reports 
            if report.enhanced_metadata.requires_specialized_knowledge
        )
        
        return round((specialized_count / len(error_reports)) * 100, 2)

    def _analyze_metadata_correlations(self, error_reports: List) -> Dict:
        """Analyze correlations between metadata fields"""
        
        # This would perform correlation analysis
        # For now, return placeholder correlations
        return {
            "audio_quality_vs_rectification": 0.0,
            "speaker_clarity_vs_complexity": 0.0,
            "background_noise_vs_errors": 0.0,
            "overlapping_speech_vs_difficulty": 0.0,
        }

    def _analyze_complexity_scores(self, error_reports: List) -> Dict:
        """Analyze complexity score distribution"""
        
        if not error_reports:
            return {"low": 0, "medium": 0, "high": 0, "very_high": 0}
        
        complexity_counts = {"low": 0, "medium": 0, "high": 0, "very_high": 0}
        
        for report in error_reports:
            score = report.calculate_complexity_score()
            
            if score <= 2.0:
                complexity_counts["low"] += 1
            elif score <= 3.5:
                complexity_counts["medium"] += 1
            elif score <= 4.5:
                complexity_counts["high"] += 1
            else:
                complexity_counts["very_high"] += 1
        
        total = len(error_reports)
        return {
            level: {
                "count": count,
                "percentage": round((count / total) * 100, 2) if total > 0 else 0
            }
            for level, count in complexity_counts.items()
        }
