"""
In-memory MT Validation repository implementing IMTValidationRepositoryPort.
Suitable for development and DI examples.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ....application.ports.mt_validation_repository_port import (
    IMTValidationRepositoryPort,
    ValidationTestDataItem,
    HistoricalDataComparisonItem,
)
from ....domain.entities.validation_test_session import ValidationTestSession


class InMemoryMTValidationRepository(IMTValidationRepositoryPort):
    def __init__(self) -> None:
        self._sessions: Dict[UUID, ValidationTestSession] = {}
        self._session_test_data: Dict[UUID, List[ValidationTestDataItem]] = {}
        self._feedback: Dict[UUID, Dict[str, Any]] = {}

    async def create_validation_session(
        self, session: ValidationTestSession
    ) -> ValidationTestSession:
        self._sessions[session.id] = session
        self._session_test_data[session.id] = []
        return session

    async def get_validation_session_by_id(
        self, session_id: UUID
    ) -> Optional[ValidationTestSession]:
        return self._sessions.get(session_id)

    async def update_validation_session(
        self, session: ValidationTestSession
    ) -> ValidationTestSession:
        if session.id not in self._sessions:
            raise ValueError("Session not found")
        self._sessions[session.id] = session
        return session

    async def get_validation_sessions_by_speaker(
        self, speaker_id: UUID, status: Optional[str] = None
    ) -> List[ValidationTestSession]:
        sessions = [s for s in self._sessions.values() if s.speaker_id == speaker_id]
        if status:
            sessions = [s for s in sessions if s.status.value == status]
        return sessions

    async def get_session_test_data(
        self, session_id: UUID, limit: Optional[int] = None
    ) -> List[ValidationTestDataItem]:
        items = self._session_test_data.get(session_id, [])
        return items[:limit] if limit else items

    async def add_session_test_data(
        self, session_id: UUID, items: List[ValidationTestDataItem]
    ) -> int:
        if session_id not in self._session_test_data:
            self._session_test_data[session_id] = []
        self._session_test_data[session_id].extend(items)
        return len(items)

    async def create_mt_feedback(
        self,
        *,
        feedback_id: UUID,
        session_id: UUID,
        historical_data_id: UUID,
        original_asr_text: str,
        rag_corrected_text: str,
        final_reference_text: str,
        mt_feedback_rating: int,
        mt_comments: Optional[str],
        improvement_assessment: Optional[str],
        recommended_for_bucket_change: bool,
        feedback_metadata: Dict[str, Any],
    ) -> UUID:
        self._feedback[feedback_id] = {
            "session_id": session_id,
            "historical_data_id": historical_data_id,
            "original_asr_text": original_asr_text,
            "rag_corrected_text": rag_corrected_text,
            "final_reference_text": final_reference_text,
            "mt_feedback_rating": mt_feedback_rating,
            "mt_comments": mt_comments,
            "improvement_assessment": improvement_assessment,
            "recommended_for_bucket_change": recommended_for_bucket_change,
            "feedback_metadata": feedback_metadata,
        }
        return feedback_id

    async def get_ser_comparison_history(
        self, speaker_id: UUID, limit: int = 10
    ) -> List[HistoricalDataComparisonItem]:
        # Return empty list for example
        return []

    async def save_historical_comparison(
        self, item: HistoricalDataComparisonItem
    ) -> UUID:
        return uuid4()

