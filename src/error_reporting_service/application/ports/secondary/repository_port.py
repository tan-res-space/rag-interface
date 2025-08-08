"""
Repository Port Interface

Defines the contract for error report persistence operations.
This is a secondary port (driven adapter) that will be implemented
by infrastructure adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.error_reporting_service.domain.entities.error_report import ErrorReport


class ErrorReportRepository(ABC):
    """
    Abstract repository interface for error report persistence.
    
    This port defines the contract that infrastructure adapters must implement
    to provide error report storage capabilities.
    """
    
    @abstractmethod
    async def save(self, error_report: ErrorReport) -> ErrorReport:
        """
        Save an error report to the repository.
        
        Args:
            error_report: The error report to save
            
        Returns:
            The saved error report with any generated fields
            
        Raises:
            RepositoryError: If the save operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """
        Find an error report by its ID.
        
        Args:
            error_id: The unique identifier of the error report
            
        Returns:
            The error report if found, None otherwise
            
        Raises:
            RepositoryError: If the find operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_speaker(self, speaker_id: UUID, filters: Optional[Dict[str, Any]] = None) -> List[ErrorReport]:
        """
        Find all error reports for a specific speaker.
        
        Args:
            speaker_id: The unique identifier of the speaker
            filters: Optional filters to apply to the search
            
        Returns:
            List of error reports for the speaker
            
        Raises:
            RepositoryError: If the find operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_job(self, job_id: UUID, filters: Optional[Dict[str, Any]] = None) -> List[ErrorReport]:
        """
        Find all error reports for a specific job.
        
        Args:
            job_id: The unique identifier of the job
            filters: Optional filters to apply to the search
            
        Returns:
            List of error reports for the job
            
        Raises:
            RepositoryError: If the find operation fails
        """
        pass
    
    @abstractmethod
    async def update(self, error_id: UUID, updates: Dict[str, Any]) -> ErrorReport:
        """
        Update an existing error report.
        
        Args:
            error_id: The unique identifier of the error report
            updates: Dictionary of fields to update
            
        Returns:
            The updated error report
            
        Raises:
            RepositoryError: If the update operation fails
            NotFoundError: If the error report is not found
        """
        pass
    
    @abstractmethod
    async def delete(self, error_id: UUID) -> bool:
        """
        Delete an error report.
        
        Args:
            error_id: The unique identifier of the error report
            
        Returns:
            True if the error report was deleted, False if not found
            
        Raises:
            RepositoryError: If the delete operation fails
        """
        pass
    
    @abstractmethod
    async def search(self, criteria: Dict[str, Any], page: int = 1, limit: int = 20) -> List[ErrorReport]:
        """
        Search for error reports based on criteria.
        
        Args:
            criteria: Search criteria dictionary
            page: Page number for pagination (1-based)
            limit: Maximum number of results per page
            
        Returns:
            List of error reports matching the criteria
            
        Raises:
            RepositoryError: If the search operation fails
        """
        pass
    
    @abstractmethod
    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """
        Count error reports matching the criteria.
        
        Args:
            criteria: Optional search criteria dictionary
            
        Returns:
            Number of error reports matching the criteria
            
        Raises:
            RepositoryError: If the count operation fails
        """
        pass
