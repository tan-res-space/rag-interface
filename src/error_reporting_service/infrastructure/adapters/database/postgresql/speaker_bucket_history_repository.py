"""
PostgreSQL adapter for Speaker Bucket History repository
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from error_reporting_service.domain.entities.speaker_bucket_history import (
    SpeakerBucketHistory,
    AssignmentType,
)
from error_reporting_service.domain.entities.error_report import BucketType
from error_reporting_service.domain.ports.speaker_bucket_history_repository import (
    SpeakerBucketHistoryRepository,
)
from error_reporting_service.infrastructure.adapters.database.postgresql.models import (
    SpeakerBucketHistoryModel,
)


class PostgreSQLSpeakerBucketHistoryRepository(SpeakerBucketHistoryRepository):
    """PostgreSQL implementation of Speaker Bucket History repository"""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def save_bucket_assignment(self, bucket_history: SpeakerBucketHistory) -> SpeakerBucketHistory:
        """Save bucket assignment to PostgreSQL database"""
        async with self._session_factory() as session:
            model = SpeakerBucketHistoryModel(
                history_id=bucket_history.history_id,
                speaker_id=bucket_history.speaker_id,
                bucket_type=bucket_history.bucket_type.value,
                previous_bucket=bucket_history.previous_bucket.value if bucket_history.previous_bucket else None,
                assigned_date=bucket_history.assigned_date,
                assigned_by=bucket_history.assigned_by,
                assignment_reason=bucket_history.assignment_reason,
                assignment_type=bucket_history.assignment_type.value,
                error_count_at_assignment=bucket_history.error_count_at_assignment,
                rectification_rate_at_assignment=str(bucket_history.rectification_rate_at_assignment) if bucket_history.rectification_rate_at_assignment else None,
                quality_score_at_assignment=str(bucket_history.quality_score_at_assignment) if bucket_history.quality_score_at_assignment else None,
                confidence_score=str(bucket_history.confidence_score) if bucket_history.confidence_score else None,
            )

            session.add(model)
            await session.commit()
            await session.refresh(model)

            return self._model_to_entity(model)

    async def get_speaker_bucket_history(
        self, 
        speaker_id: UUID, 
        limit: Optional[int] = None
    ) -> List[SpeakerBucketHistory]:
        """Get bucket history for a speaker"""
        async with self._session_factory() as session:
            stmt = select(SpeakerBucketHistoryModel).where(
                SpeakerBucketHistoryModel.speaker_id == speaker_id
            ).order_by(desc(SpeakerBucketHistoryModel.assigned_date))

            if limit:
                stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def get_current_bucket(self, speaker_id: UUID) -> Optional[BucketType]:
        """Get current bucket for a speaker"""
        async with self._session_factory() as session:
            stmt = select(SpeakerBucketHistoryModel).where(
                SpeakerBucketHistoryModel.speaker_id == speaker_id
            ).order_by(desc(SpeakerBucketHistoryModel.assigned_date)).limit(1)

            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return BucketType(model.bucket_type)
            return None

    async def get_bucket_transitions(
        self, 
        speaker_id: UUID, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SpeakerBucketHistory]:
        """Get bucket transitions for a speaker within date range"""
        async with self._session_factory() as session:
            stmt = select(SpeakerBucketHistoryModel).where(
                SpeakerBucketHistoryModel.speaker_id == speaker_id
            )

            if start_date:
                stmt = stmt.where(SpeakerBucketHistoryModel.assigned_date >= start_date)
            if end_date:
                stmt = stmt.where(SpeakerBucketHistoryModel.assigned_date <= end_date)

            stmt = stmt.order_by(SpeakerBucketHistoryModel.assigned_date)

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def get_recent_assignments(
        self, 
        assignment_type: Optional[AssignmentType] = None,
        days: int = 7
    ) -> List[SpeakerBucketHistory]:
        """Get recent bucket assignments"""
        async with self._session_factory() as session:
            cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
            
            stmt = select(SpeakerBucketHistoryModel).where(
                SpeakerBucketHistoryModel.assigned_date >= cutoff_date
            )

            if assignment_type:
                stmt = stmt.where(SpeakerBucketHistoryModel.assignment_type == assignment_type.value)

            stmt = stmt.order_by(desc(SpeakerBucketHistoryModel.assigned_date))

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

    async def count_bucket_assignments(
        self, 
        bucket_type: BucketType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count bucket assignments by type and date range"""
        async with self._session_factory() as session:
            stmt = select(SpeakerBucketHistoryModel).where(
                SpeakerBucketHistoryModel.bucket_type == bucket_type.value
            )

            if start_date:
                stmt = stmt.where(SpeakerBucketHistoryModel.assigned_date >= start_date)
            if end_date:
                stmt = stmt.where(SpeakerBucketHistoryModel.assigned_date <= end_date)

            result = await session.execute(stmt)
            return len(result.scalars().all())

    def _model_to_entity(self, model: SpeakerBucketHistoryModel) -> SpeakerBucketHistory:
        """Convert SQLAlchemy model to domain entity"""
        return SpeakerBucketHistory(
            history_id=model.history_id,
            speaker_id=model.speaker_id,
            bucket_type=BucketType(model.bucket_type),
            assigned_date=model.assigned_date,
            assigned_by=model.assigned_by,
            assignment_reason=model.assignment_reason,
            assignment_type=AssignmentType(model.assignment_type),
            previous_bucket=BucketType(model.previous_bucket) if model.previous_bucket else None,
            error_count_at_assignment=model.error_count_at_assignment,
            rectification_rate_at_assignment=float(model.rectification_rate_at_assignment) if model.rectification_rate_at_assignment else None,
            quality_score_at_assignment=float(model.quality_score_at_assignment) if model.quality_score_at_assignment else None,
            confidence_score=float(model.confidence_score) if model.confidence_score else None,
        )

    async def get_bucket_distribution(self) -> dict:
        """Get current bucket distribution statistics"""
        async with self._session_factory() as session:
            # Get latest assignment for each speaker
            subquery = select(
                SpeakerBucketHistoryModel.speaker_id,
                SpeakerBucketHistoryModel.bucket_type,
                SpeakerBucketHistoryModel.assigned_date
            ).distinct(SpeakerBucketHistoryModel.speaker_id).order_by(
                SpeakerBucketHistoryModel.speaker_id,
                desc(SpeakerBucketHistoryModel.assigned_date)
            ).subquery()

            # Count by bucket type
            stmt = select(
                subquery.c.bucket_type,
                func.count().label('count')
            ).group_by(subquery.c.bucket_type)

            result = await session.execute(stmt)
            distribution = {}
            total = 0

            for row in result:
                bucket_type = row.bucket_type
                count = row.count
                distribution[bucket_type] = count
                total += count

            # Calculate percentages
            for bucket_type in distribution:
                distribution[bucket_type] = {
                    'count': distribution[bucket_type],
                    'percentage': round((distribution[bucket_type] / total) * 100, 2) if total > 0 else 0
                }

            return distribution

    async def get_assignment_trends(self, days: int = 30) -> dict:
        """Get bucket assignment trends over time"""
        async with self._session_factory() as session:
            cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
            
            stmt = select(
                func.date_trunc('day', SpeakerBucketHistoryModel.assigned_date).label('date'),
                SpeakerBucketHistoryModel.bucket_type,
                func.count().label('count')
            ).where(
                SpeakerBucketHistoryModel.assigned_date >= cutoff_date
            ).group_by(
                func.date_trunc('day', SpeakerBucketHistoryModel.assigned_date),
                SpeakerBucketHistoryModel.bucket_type
            ).order_by('date')

            result = await session.execute(stmt)
            trends = {}

            for row in result:
                date_str = row.date.strftime('%Y-%m-%d')
                bucket_type = row.bucket_type
                count = row.count

                if date_str not in trends:
                    trends[date_str] = {}
                trends[date_str][bucket_type] = count

            return trends
