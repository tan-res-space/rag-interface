"""
MT Validation Repository Port

Abstract interface for MT validation data persistence operations.
Defines the contract for MT validation repository implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ...domain.entities.validation_test_session import ValidationTestSession


class ValidationTestDataItem:
    """Data class for validation test data items."""
    
    def __init__(
        self,
        id: UUID,
        speaker_id: UUID,
        original_asr_text: str,
        rag_corrected_text: str,
        final_reference_text: str,
        metadata: Dict[str, Any]
    ):
        self.id = id
        self.speaker_id = speaker_id
        self.original_asr_text = original_asr_text
        self.rag_corrected_text = rag_corrected_text
        self.final_reference_text = final_reference_text
        self.metadata = metadata


class HistoricalDataComparisonItem:
    """Data class for historical data comparison items."""
    
    def __init__(
        self,
        id: UUID,
        speaker_id: UUID,
        original_asr_text: str,
        rag_corrected_text: str,
        final_reference_text: str,
        metadata: Dict[str, Any]
    ):
        self.id = id
        self.speaker_id = speaker_id
        self.original_asr_text = original_asr_text
        self.rag_corrected_text = rag_corrected_text
        self.final_reference_text = final_reference_text
        self.metadata = metadata


class IMTValidationRepositoryPort(ABC):
    """
    Abstract interface for MT validation repository operations.
    
    This port defines the contract for MT validation data persistence,
    including session management, test data, and feedback operations.
    """
    
    # Validation Session operations
    
    @abstractmethod
    async def create_validation_session(
        self,
        session: ValidationTestSession
    ) -> ValidationTestSession:
        """
        Create a new validation session.
        
        Args:
            session: Validation session to create
            
        Returns:
            Created validation session
            
        Raises:
            RepositoryError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_validation_session_by_id(
        self,
        session_id: UUID
    ) -> Optional[ValidationTestSession]:
        """
        Get validation session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Validation session or None if not found
        """
        pass
    
    @abstractmethod
    async def update_validation_session(
        self,
        session: ValidationTestSession
    ) -> ValidationTestSession:
        """
        Update a validation session.
        
        Args:
            session: Validation session to update
            
        Returns:
            Updated validation session
            
        Raises:
            ValueError: If session not found
        """
        pass
    
    @abstractmethod
    async def get_validation_sessions_by_speaker(
        self,
        speaker_id: UUID,
        status: Optional[str] = None
    ) -> List[ValidationTestSession]:
        """
        Get validation sessions for a speaker.
        
        Args:
            speaker_id: Speaker identifier
            status: Optional status filter
            
        Returns:
            List of validation sessions
        """
        pass
    
    @abstractmethod
    async def get_validation_sessions_by_mt_user(
        self,
        mt_user_id: UUID,
        status: Optional[str] = None
    ) -> List[ValidationTestSession]:
        """
        Get validation sessions for an MT user.
        
        Args:
            mt_user_id: MT user identifier
            status: Optional status filter
            
        Returns:
            List of validation sessions
        """
        pass
    
    @abstractmethod
    async def delete_validation_session(self, session_id: UUID) -> bool:
        """
        Delete a validation session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    # Test Data operations
    
    @abstractmethod
    async def link_test_data_to_session(
        self,
        session_id: UUID,
        test_data_ids: List[UUID]
    ) -> int:
        """
        Link test data items to a validation session.
        
        Args:
            session_id: Session identifier
            test_data_ids: List of test data identifiers
            
        Returns:
            Number of items linked
        """
        pass
    
    @abstractmethod
    async def get_session_test_data(
        self,
        session_id: UUID,
        limit: Optional[int] = None
    ) -> List[ValidationTestDataItem]:
        """
        Get test data items for a validation session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of items to return
            
        Returns:
            List of validation test data items
        """
        pass
    
    @abstractmethod
    async def get_historical_data_for_comparison(
        self,
        speaker_id: UUID,
        historical_data_ids: List[UUID]
    ) -> List[HistoricalDataComparisonItem]:
        """
        Get historical data items for SER comparison.
        
        Args:
            speaker_id: Speaker identifier
            historical_data_ids: List of historical data identifiers
            
        Returns:
            List of historical data comparison items
        """
        pass
    
    # MT Feedback operations
    
    @abstractmethod
    async def create_mt_feedback(
        self,
        feedback_id: UUID,
        session_id: UUID,
        historical_data_id: UUID,
        original_asr_text: str,
        rag_corrected_text: str,
        final_reference_text: str,
        mt_feedback_rating: int,
        mt_comments: Optional[str],
        improvement_assessment: str,
        recommended_for_bucket_change: bool,
        feedback_metadata: Dict[str, Any]
    ) -> UUID:
        """
        Create MT feedback entry.
        
        Args:
            feedback_id: Feedback identifier
            session_id: Session identifier
            historical_data_id: Historical data identifier
            original_asr_text: Original ASR text
            rag_corrected_text: RAG corrected text
            final_reference_text: Final reference text
            mt_feedback_rating: MT feedback rating (1-5)
            mt_comments: Optional MT comments
            improvement_assessment: Improvement assessment
            recommended_for_bucket_change: Bucket change recommendation
            feedback_metadata: Additional metadata
            
        Returns:
            Created feedback identifier
        """
        pass
    
    @abstractmethod
    async def get_mt_feedback_by_session(
        self,
        session_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get MT feedback for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of feedback entries
        """
        pass
    
    @abstractmethod
    async def get_session_feedback_count(
        self,
        session_id: UUID
    ) -> int:
        """
        Get count of feedback entries for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of feedback entries
        """
        pass
    
    @abstractmethod
    async def get_mt_feedback_by_speaker(
        self,
        speaker_id: UUID,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get MT feedback for a speaker.
        
        Args:
            speaker_id: Speaker identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of feedback entries
        """
        pass
    
    # Statistics and analytics operations
    
    @abstractmethod
    async def get_session_statistics(
        self,
        session_id: UUID
    ) -> Dict[str, Any]:
        """
        Get statistics for a validation session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session statistics
        """
        pass
    
    @abstractmethod
    async def get_mt_user_statistics(
        self,
        mt_user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get statistics for an MT user.
        
        Args:
            mt_user_id: MT user identifier
            
        Returns:
            Dictionary with MT user statistics
        """
        pass
    
    @abstractmethod
    async def get_speaker_validation_statistics(
        self,
        speaker_id: UUID
    ) -> Dict[str, Any]:
        """
        Get validation statistics for a speaker.
        
        Args:
            speaker_id: Speaker identifier
            
        Returns:
            Dictionary with speaker validation statistics
        """
        pass
