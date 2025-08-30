"""
Abstract Database Adapter Interface

Defines the contract for database operations that is technology-agnostic.
This interface can be implemented by different database technologies
while maintaining consistent behavior.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.error_reporting_service.domain.entities.error_report import ErrorReport


class IDatabaseAdapter(ABC):
    """
    Abstract interface for database operations - technology agnostic.

    This interface defines the contract that all database adapters must implement
    to provide persistence capabilities for the Error Reporting Service.
    """

    @abstractmethod
    async def save_error_report(self, error_report: ErrorReport) -> ErrorReport:
        """
        Save error report to database.

        Args:
            error_report: The error report to save

        Returns:
            The saved error report with any generated fields

        Raises:
            DatabaseError: If the save operation fails
        """
        pass

    @abstractmethod
    async def find_error_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """
        Find error report by ID.

        Args:
            error_id: The unique identifier of the error report

        Returns:
            The error report if found, None otherwise

        Raises:
            DatabaseError: If the find operation fails
        """
        pass

    @abstractmethod
    async def find_errors_by_speaker(
        self, speaker_id: UUID, filters: Optional[Dict] = None
    ) -> List[ErrorReport]:
        """
        Find all error reports for a speaker.

        Args:
            speaker_id: The unique identifier of the speaker
            filters: Optional filters to apply to the search

        Returns:
            List of error reports for the speaker

        Raises:
            DatabaseError: If the find operation fails
        """
        pass

    @abstractmethod
    async def find_errors_by_job(
        self, job_id: UUID, filters: Optional[Dict] = None
    ) -> List[ErrorReport]:
        """
        Find all error reports for a job.

        Args:
            job_id: The unique identifier of the job
            filters: Optional filters to apply to the search

        Returns:
            List of error reports for the job

        Raises:
            DatabaseError: If the find operation fails
        """
        pass

    @abstractmethod
    async def update_error_report(
        self, error_id: UUID, updates: Dict[str, Any]
    ) -> ErrorReport:
        """
        Update existing error report.

        Args:
            error_id: The unique identifier of the error report
            updates: Dictionary of fields to update

        Returns:
            The updated error report

        Raises:
            DatabaseError: If the update operation fails
            NotFoundError: If the error report is not found
        """
        pass

    @abstractmethod
    async def delete_error_report(self, error_id: UUID) -> bool:
        """
        Delete error report.

        Args:
            error_id: The unique identifier of the error report

        Returns:
            True if the error report was deleted, False if not found

        Raises:
            DatabaseError: If the delete operation fails
        """
        pass

    @abstractmethod
    async def search_errors(self, query: Dict[str, Any]) -> List[ErrorReport]:
        """
        Search errors with complex criteria.

        Args:
            query: Search criteria dictionary

        Returns:
            List of error reports matching the criteria

        Raises:
            DatabaseError: If the search operation fails
        """
        pass

    @abstractmethod
    async def begin_transaction(self) -> Any:
        """
        Begin database transaction.

        Returns:
            Transaction object (implementation-specific)

        Raises:
            DatabaseError: If transaction creation fails
        """
        pass

    @abstractmethod
    async def commit_transaction(self, transaction: Any) -> None:
        """
        Commit database transaction.

        Args:
            transaction: Transaction object to commit

        Raises:
            DatabaseError: If commit fails
        """
        pass

    @abstractmethod
    async def rollback_transaction(self, transaction: Any) -> None:
        """
        Rollback database transaction.

        Args:
            transaction: Transaction object to rollback

        Raises:
            DatabaseError: If rollback fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if database is healthy and accessible.

        Returns:
            True if database is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get database connection information for monitoring.

        Returns:
            Dictionary containing connection information
        """
        pass
