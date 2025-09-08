"""
In-memory ErrorReport repository for development/testing.
Implements the ErrorReportRepository port with an in-memory store.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository,
)
from error_reporting_service.domain.entities.error_report import ErrorReport


class InMemoryErrorReportRepository(ErrorReportRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ErrorReport] = {}

    async def save(self, error_report: ErrorReport) -> ErrorReport:
        self._store[error_report.error_id] = error_report
        return error_report

    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        return self._store.get(error_id)

    async def find_by_speaker(
        self, speaker_id: UUID, filters: Optional[Dict[str, Any]] = None
    ) -> List[ErrorReport]:
        results = [e for e in self._store.values() if e.speaker_id == speaker_id]
        return results

    async def find_by_job(
        self, job_id: UUID, filters: Optional[Dict[str, Any]] = None
    ) -> List[ErrorReport]:
        return [e for e in self._store.values() if e.job_id == job_id]

    async def update(self, error_id: UUID, updates: Dict[str, Any]) -> ErrorReport:
        if error_id not in self._store:
            raise KeyError("Error report not found")
        current = self._store[error_id]
        data = {**current.__dict__, **updates}
        # Recreate entity immutably
        updated = ErrorReport(
            error_id=current.error_id,
            job_id=current.job_id,
            speaker_id=current.speaker_id,
            client_id=current.client_id,
            reported_by=current.reported_by,
            original_text=data.get("original_text", current.original_text),
            corrected_text=data.get("corrected_text", current.corrected_text),
            error_categories=data.get("error_categories", current.error_categories),
            severity_level=current.severity_level,
            start_position=current.start_position,
            end_position=current.end_position,
            error_timestamp=current.error_timestamp,
            reported_at=current.reported_at,
            bucket_type=current.bucket_type,
            enhanced_metadata=current.enhanced_metadata,
            context_notes=data.get("context_notes", current.context_notes),
            status=current.status,
            vector_db_id=data.get("vector_db_id", current.vector_db_id),
            metadata=data.get("metadata", current.metadata),
        )
        self._store[error_id] = updated
        return updated

    async def delete(self, error_id: UUID) -> bool:
        return self._store.pop(error_id, None) is not None

    async def search(
        self, criteria: Dict[str, Any], page: int = 1, limit: int = 20
    ) -> List[ErrorReport]:
        # Very basic filter implementation for example purposes
        results = list(self._store.values())
        speaker_id = criteria.get("speaker_id")
        if speaker_id:
            results = [e for e in results if str(e.speaker_id) == str(speaker_id)]
        start = (page - 1) * limit
        end = start + limit
        return results[start:end]

    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        return len(self._store)

