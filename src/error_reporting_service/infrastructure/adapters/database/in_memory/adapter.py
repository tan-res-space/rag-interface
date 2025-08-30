"""
In-Memory Database Adapter Implementation

This module contains an in-memory implementation of the IDatabaseAdapter interface
for testing and demonstration purposes.
"""

import asyncio
from copy import deepcopy
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.error_reporting_service.domain.entities.error_report import ErrorReport
from src.error_reporting_service.infrastructure.adapters.database.abstract.database_adapter import (
    IDatabaseAdapter,
)


class InMemoryDatabaseAdapter(IDatabaseAdapter):
    """
    In-memory implementation of the database adapter.

    Stores data in memory for testing and demonstration purposes.
    Not suitable for production use.
    """

    def __init__(self):
        """Initialize the in-memory adapter"""
        self._error_reports: Dict[UUID, ErrorReport] = {}
        self._transaction_data: Optional[Dict[UUID, ErrorReport]] = None

    async def save_error_report(self, error_report: ErrorReport) -> ErrorReport:
        """Save error report to in-memory storage"""
        if self._transaction_data is not None:
            # We're in a transaction
            self._transaction_data[error_report.error_id] = deepcopy(error_report)
        else:
            self._error_reports[error_report.error_id] = deepcopy(error_report)

        return deepcopy(error_report)

    async def find_error_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find error report by ID in in-memory storage"""
        storage = (
            self._transaction_data
            if self._transaction_data is not None
            else self._error_reports
        )
        error_report = storage.get(error_id)
        return deepcopy(error_report) if error_report else None

    async def find_errors_by_speaker(
        self, speaker_id: UUID, filters: Optional[Dict] = None
    ) -> List[ErrorReport]:
        """Find all error reports for a speaker in in-memory storage"""
        storage = (
            self._transaction_data
            if self._transaction_data is not None
            else self._error_reports
        )

        results = []
        for error_report in storage.values():
            if error_report.speaker_id == speaker_id:
                # Apply filters if provided
                if filters:
                    if (
                        "severity_level" in filters
                        and error_report.severity_level.value
                        != filters["severity_level"]
                    ):
                        continue
                    if (
                        "status" in filters
                        and error_report.status.value != filters["status"]
                    ):
                        continue
                    if "categories" in filters:
                        if not any(
                            cat in error_report.error_categories
                            for cat in filters["categories"]
                        ):
                            continue

                results.append(deepcopy(error_report))

        return results

    async def find_errors_by_job(
        self, job_id: UUID, filters: Optional[Dict] = None
    ) -> List[ErrorReport]:
        """Find all error reports for a job in in-memory storage"""
        storage = (
            self._transaction_data
            if self._transaction_data is not None
            else self._error_reports
        )

        results = []
        for error_report in storage.values():
            if error_report.job_id == job_id:
                # Apply filters if provided
                if filters:
                    if (
                        "severity_level" in filters
                        and error_report.severity_level.value
                        != filters["severity_level"]
                    ):
                        continue
                    if (
                        "status" in filters
                        and error_report.status.value != filters["status"]
                    ):
                        continue

                results.append(deepcopy(error_report))

        return results

    async def update_error_report(
        self, error_id: UUID, updates: Dict[str, Any]
    ) -> ErrorReport:
        """Update existing error report in in-memory storage"""
        storage = (
            self._transaction_data
            if self._transaction_data is not None
            else self._error_reports
        )

        if error_id not in storage:
            raise ValueError(f"Error report with ID {error_id} not found")

        error_report = storage[error_id]

        # Create a new error report with updates (immutable pattern)
        updated_report = ErrorReport(
            error_id=error_report.error_id,
            job_id=error_report.job_id,
            speaker_id=error_report.speaker_id,
            reported_by=error_report.reported_by,
            original_text=error_report.original_text,
            corrected_text=error_report.corrected_text,
            error_categories=error_report.error_categories,
            severity_level=error_report.severity_level,
            start_position=error_report.start_position,
            end_position=error_report.end_position,
            context_notes=updates.get("context_notes", error_report.context_notes),
            error_timestamp=error_report.error_timestamp,
            reported_at=error_report.reported_at,
            status=updates.get("status", error_report.status),
            metadata=updates.get("metadata", error_report.metadata),
        )

        storage[error_id] = updated_report
        return deepcopy(updated_report)

    async def delete_error_report(self, error_id: UUID) -> bool:
        """Delete error report from in-memory storage"""
        storage = (
            self._transaction_data
            if self._transaction_data is not None
            else self._error_reports
        )

        if error_id in storage:
            del storage[error_id]
            return True
        return False

    async def search_errors(self, query: Dict[str, Any]) -> List[ErrorReport]:
        """Search errors with complex criteria in in-memory storage"""
        storage = (
            self._transaction_data
            if self._transaction_data is not None
            else self._error_reports
        )

        results = []
        for error_report in storage.values():
            match = True

            # Apply search criteria
            if "speaker_id" in query and error_report.speaker_id != UUID(
                query["speaker_id"]
            ):
                match = False
            if "job_id" in query and error_report.job_id != UUID(query["job_id"]):
                match = False
            if (
                "severity_level" in query
                and error_report.severity_level.value != query["severity_level"]
            ):
                match = False
            if "status" in query and error_report.status.value != query["status"]:
                match = False
            if "text_search" in query:
                search_term = query["text_search"].lower()
                if (
                    search_term not in error_report.original_text.lower()
                    and search_term not in error_report.corrected_text.lower()
                ):
                    match = False

            if match:
                results.append(deepcopy(error_report))

        # Apply pagination
        if "limit" in query:
            limit = query["limit"]
            offset = query.get("offset", 0)
            results = results[offset : offset + limit]

        return results

    async def begin_transaction(self) -> Dict[UUID, ErrorReport]:
        """Begin in-memory transaction"""
        self._transaction_data = deepcopy(self._error_reports)
        return self._transaction_data

    async def commit_transaction(self, transaction: Dict[UUID, ErrorReport]) -> None:
        """Commit in-memory transaction"""
        if self._transaction_data is not None:
            self._error_reports = deepcopy(self._transaction_data)
            self._transaction_data = None

    async def rollback_transaction(self, transaction: Dict[UUID, ErrorReport]) -> None:
        """Rollback in-memory transaction"""
        self._transaction_data = None

    async def health_check(self) -> bool:
        """Check in-memory storage health (always healthy)"""
        return True

    def get_connection_info(self) -> Dict[str, Any]:
        """Get in-memory storage information"""
        return {
            "adapter_type": "in_memory",
            "total_records": len(self._error_reports),
            "in_transaction": self._transaction_data is not None,
        }

    def clear_all_data(self) -> None:
        """Clear all data (for testing)"""
        self._error_reports.clear()
        self._transaction_data = None
