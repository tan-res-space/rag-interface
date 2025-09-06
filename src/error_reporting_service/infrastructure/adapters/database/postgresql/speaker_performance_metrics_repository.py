"""
PostgreSQL adapter for Speaker Performance Metrics repository
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from error_reporting_service.domain.entities.speaker_performance_metrics import (
    SpeakerPerformanceMetrics,
    QualityTrend,
)
from error_reporting_service.domain.entities.error_report import BucketType
from error_reporting_service.domain.ports.speaker_performance_metrics_repository import (
    SpeakerPerformanceMetricsRepository,
)
from error_reporting_service.infrastructure.adapters.database.postgresql.models import (
    SpeakerPerformanceMetricsModel,
)


class PostgreSQLSpeakerPerformanceMetricsRepository(SpeakerPerformanceMetricsRepository):
    """PostgreSQL implementation of Speaker Performance Metrics repository"""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def save_metrics(self, metrics: SpeakerPerformanceMetrics) -> SpeakerPerformanceMetrics:
        """Save speaker performance metrics to PostgreSQL database"""
        async with self._session_factory() as session:
            model = SpeakerPerformanceMetricsModel(
                metrics_id=metrics.metrics_id,
                speaker_id=metrics.speaker_id,
                current_bucket=metrics.current_bucket.value,
                total_errors_reported=metrics.total_errors_reported,
                errors_rectified=metrics.errors_rectified,
                errors_pending=metrics.errors_pending,
                rectification_rate=str(metrics.rectification_rate),
                average_audio_quality=str(metrics.average_audio_quality) if metrics.average_audio_quality else None,
                average_clarity_score=str(metrics.average_clarity_score) if metrics.average_clarity_score else None,
                specialized_knowledge_frequency=str(metrics.specialized_knowledge_frequency) if metrics.specialized_knowledge_frequency else None,
                overlapping_speech_frequency=str(metrics.overlapping_speech_frequency) if metrics.overlapping_speech_frequency else None,
                quality_trend=metrics.quality_trend.value if metrics.quality_trend else None,
                last_assessment_date=metrics.last_assessment_date,
                next_assessment_date=metrics.next_assessment_date,
                average_time_to_rectification_seconds=int(metrics.average_time_to_rectification.total_seconds()) if metrics.average_time_to_rectification else None,
                time_in_current_bucket_seconds=int(metrics.time_in_current_bucket.total_seconds()) if metrics.time_in_current_bucket else None,
                calculated_at=metrics.calculated_at,
            )

            # Use merge for upsert behavior
            await session.merge(model)
            await session.commit()

            # Refresh to get updated model
            stmt = select(SpeakerPerformanceMetricsModel).where(
                SpeakerPerformanceMetricsModel.speaker_id == metrics.speaker_id
            )
            result = await session.execute(stmt)
            updated_model = result.scalar_one()

            return self._model_to_entity(updated_model)

    async def get_metrics_by_speaker(self, speaker_id: UUID) -> Optional[SpeakerPerformanceMetrics]:
        """Get performance metrics for a specific speaker"""
        async with self._session_factory() as session:
            stmt = select(SpeakerPerformanceMetricsModel).where(
                SpeakerPerformanceMetricsModel.speaker_id == speaker_id
            )

            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

    async def get_metrics_by_bucket(self, bucket_type: BucketType) -> List[SpeakerPerformanceMetrics]:
        """Get all metrics for speakers in a specific bucket"""
        async with self._session_factory() as session:
            stmt = select(SpeakerPerformanceMetricsModel).where(
                SpeakerPerformanceMetricsModel.current_bucket == bucket_type.value
            ).order_by(desc(SpeakerPerformanceMetricsModel.rectification_rate))

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def get_speakers_needing_attention(self) -> List[SpeakerPerformanceMetrics]:
        """Get speakers that need attention based on performance"""
        async with self._session_factory() as session:
            stmt = select(SpeakerPerformanceMetricsModel).where(
                (SpeakerPerformanceMetricsModel.rectification_rate < "0.5000") |
                (SpeakerPerformanceMetricsModel.quality_trend == QualityTrend.DECLINING.value)
            ).order_by(SpeakerPerformanceMetricsModel.rectification_rate)

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def get_high_performers(self, minimum_errors: int = 10) -> List[SpeakerPerformanceMetrics]:
        """Get high-performing speakers"""
        async with self._session_factory() as session:
            stmt = select(SpeakerPerformanceMetricsModel).where(
                (SpeakerPerformanceMetricsModel.rectification_rate >= "0.8000") &
                (SpeakerPerformanceMetricsModel.total_errors_reported >= minimum_errors) &
                (SpeakerPerformanceMetricsModel.quality_trend.in_([
                    QualityTrend.IMPROVING.value, 
                    QualityTrend.STABLE.value
                ]))
            ).order_by(desc(SpeakerPerformanceMetricsModel.rectification_rate))

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def get_speakers_for_reassessment(self, days_threshold: int = 30) -> List[SpeakerPerformanceMetrics]:
        """Get speakers that should be reassessed"""
        async with self._session_factory() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
            
            stmt = select(SpeakerPerformanceMetricsModel).where(
                (SpeakerPerformanceMetricsModel.last_assessment_date < cutoff_date) |
                (SpeakerPerformanceMetricsModel.last_assessment_date.is_(None)) |
                (SpeakerPerformanceMetricsModel.quality_trend == QualityTrend.DECLINING.value)
            ).order_by(SpeakerPerformanceMetricsModel.last_assessment_date)

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def get_bucket_statistics(self) -> dict:
        """Get statistics for each bucket type"""
        async with self._session_factory() as session:
            stmt = select(
                SpeakerPerformanceMetricsModel.current_bucket,
                func.count().label('speaker_count'),
                func.avg(func.cast(SpeakerPerformanceMetricsModel.rectification_rate, func.numeric)).label('avg_rectification_rate'),
                func.avg(SpeakerPerformanceMetricsModel.total_errors_reported).label('avg_total_errors'),
                func.sum(SpeakerPerformanceMetricsModel.total_errors_reported).label('total_errors_all_speakers')
            ).group_by(SpeakerPerformanceMetricsModel.current_bucket)

            result = await session.execute(stmt)
            statistics = {}

            for row in result:
                statistics[row.current_bucket] = {
                    'speaker_count': row.speaker_count,
                    'avg_rectification_rate': float(row.avg_rectification_rate) if row.avg_rectification_rate else 0.0,
                    'avg_total_errors': float(row.avg_total_errors) if row.avg_total_errors else 0.0,
                    'total_errors_all_speakers': row.total_errors_all_speakers or 0
                }

            return statistics

    async def get_performance_trends(self, days: int = 90) -> dict:
        """Get performance trends over time"""
        async with self._session_factory() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(
                func.date_trunc('week', SpeakerPerformanceMetricsModel.calculated_at).label('week'),
                SpeakerPerformanceMetricsModel.current_bucket,
                func.avg(func.cast(SpeakerPerformanceMetricsModel.rectification_rate, func.numeric)).label('avg_rectification_rate'),
                func.count().label('speaker_count')
            ).where(
                SpeakerPerformanceMetricsModel.calculated_at >= cutoff_date
            ).group_by(
                func.date_trunc('week', SpeakerPerformanceMetricsModel.calculated_at),
                SpeakerPerformanceMetricsModel.current_bucket
            ).order_by('week')

            result = await session.execute(stmt)
            trends = {}

            for row in result:
                week_str = row.week.strftime('%Y-%m-%d')
                bucket_type = row.current_bucket

                if week_str not in trends:
                    trends[week_str] = {}
                
                trends[week_str][bucket_type] = {
                    'avg_rectification_rate': float(row.avg_rectification_rate) if row.avg_rectification_rate else 0.0,
                    'speaker_count': row.speaker_count
                }

            return trends

    def _model_to_entity(self, model: SpeakerPerformanceMetricsModel) -> SpeakerPerformanceMetrics:
        """Convert SQLAlchemy model to domain entity"""
        return SpeakerPerformanceMetrics(
            metrics_id=model.metrics_id,
            speaker_id=model.speaker_id,
            current_bucket=BucketType(model.current_bucket),
            calculated_at=model.calculated_at,
            total_errors_reported=model.total_errors_reported,
            errors_rectified=model.errors_rectified,
            errors_pending=model.errors_pending,
            rectification_rate=float(model.rectification_rate),
            average_audio_quality=float(model.average_audio_quality) if model.average_audio_quality else None,
            average_clarity_score=float(model.average_clarity_score) if model.average_clarity_score else None,
            specialized_knowledge_frequency=float(model.specialized_knowledge_frequency) if model.specialized_knowledge_frequency else None,
            overlapping_speech_frequency=float(model.overlapping_speech_frequency) if model.overlapping_speech_frequency else None,
            quality_trend=QualityTrend(model.quality_trend) if model.quality_trend else None,
            last_assessment_date=model.last_assessment_date,
            next_assessment_date=model.next_assessment_date,
            average_time_to_rectification=timedelta(seconds=model.average_time_to_rectification_seconds) if model.average_time_to_rectification_seconds else None,
            time_in_current_bucket=timedelta(seconds=model.time_in_current_bucket_seconds) if model.time_in_current_bucket_seconds else None,
            updated_at=model.updated_at,
        )
