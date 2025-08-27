"""
MT Validation Workflow Use Case

Application use case for medical transcriptionist validation workflow.
Orchestrates the complete MT validation process for speaker bucket evaluation.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from decimal import Decimal

from ...domain.entities.validation_test_session import ValidationTestSession, SessionStatus
from ...domain.services.ser_calculation_service import SERCalculationService
from ...domain.value_objects.ser_metrics import SERMetrics
from ..ports.mt_validation_repository_port import IMTValidationRepositoryPort
from ..dto.requests import (
    StartValidationSessionRequest,
    SubmitMTFeedbackRequest,
    CompleteValidationSessionRequest,
    GetSERComparisonRequest
)
from ..dto.responses import (
    ValidationSessionResponse,
    MTFeedbackResponse,
    SERComparisonResponse,
    ValidationTestDataResponse
)


class MTValidationWorkflowUseCase:
    """
    Use case for managing the medical transcriptionist validation workflow.
    
    This use case orchestrates the complete MT validation process including
    session management, test data preparation, feedback collection, and SER analysis.
    """
    
    def __init__(
        self,
        mt_validation_repository: IMTValidationRepositoryPort,
        ser_calculation_service: SERCalculationService
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            mt_validation_repository: Repository for MT validation data
            ser_calculation_service: Service for SER calculations
        """
        self._mt_repo = mt_validation_repository
        self._ser_service = ser_calculation_service
    
    async def start_validation_session(
        self,
        request: StartValidationSessionRequest
    ) -> ValidationSessionResponse:
        """
        Start a new MT validation session.
        
        Args:
            request: Session start request
            
        Returns:
            Created validation session response
            
        Raises:
            ValueError: If validation fails
        """
        # Validate that test data exists
        test_data_count = len(request.test_data_ids)
        if test_data_count == 0:
            raise ValueError("No test data provided for validation session")
        
        # Create validation session
        session = ValidationTestSession(
            id=uuid4(),
            speaker_id=request.speaker_id,
            session_name=request.session_name,
            test_data_count=test_data_count,
            session_metadata=request.session_metadata or {}
        )
        
        # Save session
        created_session = await self._mt_repo.create_validation_session(session)
        
        # Start the session
        created_session.start_session(request.mt_user_id)
        updated_session = await self._mt_repo.update_validation_session(created_session)
        
        # Prepare test data for the session
        await self._prepare_session_test_data(updated_session.id, request.test_data_ids)
        
        return self._session_to_response(updated_session, 0)  # 0 completed items initially
    
    async def get_validation_test_data(
        self,
        session_id: UUID,
        limit: Optional[int] = None
    ) -> List[ValidationTestDataResponse]:
        """
        Get test data for MT validation session.
        
        Args:
            session_id: Validation session ID
            limit: Maximum number of items to return
            
        Returns:
            List of validation test data items
            
        Raises:
            ValueError: If session not found
        """
        # Verify session exists and is active
        session = await self._mt_repo.get_validation_session_by_id(session_id)
        if not session:
            raise ValueError(f"Validation session {session_id} not found")
        
        if not session.is_in_progress():
            raise ValueError(f"Session {session_id} is not in progress")
        
        # Get test data for the session
        test_data_items = await self._mt_repo.get_session_test_data(session_id, limit)
        
        # Convert to response DTOs with SER calculations
        responses = []
        for item in test_data_items:
            # Calculate SER metrics for original and corrected texts
            original_ser = self._ser_service.calculate_ser(
                item.original_asr_text,
                item.final_reference_text
            )
            
            corrected_ser = self._ser_service.calculate_ser(
                item.rag_corrected_text,
                item.final_reference_text
            )
            
            # Calculate improvement metrics
            improvement_metrics = self._ser_service.compare_ser_metrics(
                original_ser,
                corrected_ser
            )
            
            response = ValidationTestDataResponse(
                data_id=item.id,
                speaker_id=item.speaker_id,
                original_asr_text=item.original_asr_text,
                rag_corrected_text=item.rag_corrected_text,
                final_reference_text=item.final_reference_text,
                original_ser_metrics=original_ser,
                corrected_ser_metrics=corrected_ser,
                improvement_metrics=improvement_metrics,
                metadata=item.metadata
            )
            responses.append(response)
        
        return responses
    
    async def submit_mt_feedback(
        self,
        request: SubmitMTFeedbackRequest
    ) -> MTFeedbackResponse:
        """
        Submit MT feedback for a validation item.
        
        Args:
            request: MT feedback request
            
        Returns:
            MT feedback response
            
        Raises:
            ValueError: If validation fails
        """
        # Verify session exists and is active
        session = await self._mt_repo.get_validation_session_by_id(request.session_id)
        if not session:
            raise ValueError(f"Validation session {request.session_id} not found")
        
        if not session.is_in_progress():
            raise ValueError(f"Session {request.session_id} is not in progress")
        
        # Calculate SER comparison for the feedback
        original_ser = self._ser_service.calculate_ser(
            request.original_asr_text,
            request.final_reference_text
        )
        
        corrected_ser = self._ser_service.calculate_ser(
            request.rag_corrected_text,
            request.final_reference_text
        )
        
        ser_comparison = self._ser_service.compare_ser_metrics(original_ser, corrected_ser)
        
        # Create feedback entity
        feedback_id = uuid4()
        
        # Save feedback
        await self._mt_repo.create_mt_feedback(
            feedback_id=feedback_id,
            session_id=request.session_id,
            historical_data_id=request.historical_data_id,
            original_asr_text=request.original_asr_text,
            rag_corrected_text=request.rag_corrected_text,
            final_reference_text=request.final_reference_text,
            mt_feedback_rating=request.mt_feedback_rating,
            mt_comments=request.mt_comments,
            improvement_assessment=request.improvement_assessment,
            recommended_for_bucket_change=request.recommended_for_bucket_change,
            feedback_metadata=request.feedback_metadata or {}
        )
        
        return MTFeedbackResponse(
            feedback_id=feedback_id,
            session_id=request.session_id,
            historical_data_id=request.historical_data_id,
            mt_feedback_rating=request.mt_feedback_rating,
            improvement_assessment=request.improvement_assessment,
            recommended_for_bucket_change=request.recommended_for_bucket_change,
            ser_comparison=ser_comparison
        )
    
    async def complete_validation_session(
        self,
        request: CompleteValidationSessionRequest
    ) -> ValidationSessionResponse:
        """
        Complete a validation session.
        
        Args:
            request: Session completion request
            
        Returns:
            Completed session response
            
        Raises:
            ValueError: If session cannot be completed
        """
        # Get session
        session = await self._mt_repo.get_validation_session_by_id(request.session_id)
        if not session:
            raise ValueError(f"Validation session {request.session_id} not found")
        
        if not session.can_be_completed():
            raise ValueError(f"Session {request.session_id} cannot be completed from status: {session.status}")
        
        # Add completion metadata
        if request.completion_notes:
            session.add_metadata("completion_notes", request.completion_notes)
        
        if request.session_summary:
            session.add_metadata("session_summary", request.session_summary)
        
        # Complete the session
        session.complete_session()
        updated_session = await self._mt_repo.update_validation_session(session)
        
        # Get completion statistics
        completed_items = await self._mt_repo.get_session_feedback_count(request.session_id)
        
        return self._session_to_response(updated_session, completed_items)
    
    async def get_ser_comparison(
        self,
        request: GetSERComparisonRequest
    ) -> SERComparisonResponse:
        """
        Get SER comparison results for a speaker.
        
        Args:
            request: SER comparison request
            
        Returns:
            SER comparison response
        """
        # Get historical data for the speaker
        historical_data_items = await self._mt_repo.get_historical_data_for_comparison(
            request.speaker_id,
            request.historical_data_ids
        )
        
        if not historical_data_items:
            raise ValueError(f"No historical data found for speaker {request.speaker_id}")
        
        # Calculate SER metrics for each item
        individual_comparisons = []
        original_ser_scores = []
        corrected_ser_scores = []
        
        for item in historical_data_items:
            original_ser = self._ser_service.calculate_ser(
                item.original_asr_text,
                item.final_reference_text
            )
            
            corrected_ser = self._ser_service.calculate_ser(
                item.rag_corrected_text,
                item.final_reference_text
            )
            
            comparison = self._ser_service.compare_ser_metrics(original_ser, corrected_ser)
            
            if request.include_individual_metrics:
                individual_comparisons.append({
                    "historical_data_id": str(item.id),
                    "original_ser": comparison["original_ser"],
                    "corrected_ser": comparison["corrected_ser"],
                    "improvement": comparison["improvement"],
                    "improvement_percentage": comparison["improvement_percentage"],
                    "is_significant_improvement": comparison["is_significant_improvement"]
                })
            
            original_ser_scores.append(original_ser.ser_score)
            corrected_ser_scores.append(corrected_ser.ser_score)
        
        # Calculate overall improvement
        avg_original_ser = sum(original_ser_scores) / len(original_ser_scores)
        avg_corrected_ser = sum(corrected_ser_scores) / len(corrected_ser_scores)
        overall_improvement = float(avg_original_ser - avg_corrected_ser)
        improvement_percentage = (overall_improvement / float(avg_original_ser)) * 100 if avg_original_ser > 0 else 0
        
        # Generate recommendation
        recommendation = self._generate_bucket_recommendation(
            avg_original_ser,
            avg_corrected_ser,
            improvement_percentage
        )
        
        # Create summary
        comparison_summary = {
            "total_items": len(historical_data_items),
            "average_original_ser": float(avg_original_ser),
            "average_corrected_ser": float(avg_corrected_ser),
            "overall_improvement": overall_improvement,
            "improvement_percentage": improvement_percentage,
            "significant_improvements": len([c for c in individual_comparisons if c.get("is_significant_improvement", False)])
        } if request.include_summary_statistics else {}
        
        return SERComparisonResponse(
            speaker_id=request.speaker_id,
            comparison_summary=comparison_summary,
            individual_comparisons=individual_comparisons,
            overall_improvement={
                "improvement": overall_improvement,
                "improvement_percentage": improvement_percentage,
                "is_significant": improvement_percentage >= 10.0
            },
            recommendation=recommendation
        )
    
    async def _prepare_session_test_data(
        self,
        session_id: UUID,
        test_data_ids: List[UUID]
    ) -> None:
        """
        Prepare test data for a validation session.
        
        Args:
            session_id: Session identifier
            test_data_ids: List of test data identifiers
        """
        # Link test data to session
        await self._mt_repo.link_test_data_to_session(session_id, test_data_ids)
    
    def _generate_bucket_recommendation(
        self,
        avg_original_ser: Decimal,
        avg_corrected_ser: Decimal,
        improvement_percentage: float
    ) -> Dict[str, Any]:
        """
        Generate bucket transition recommendation based on SER improvement.
        
        Args:
            avg_original_ser: Average original SER score
            avg_corrected_ser: Average corrected SER score
            improvement_percentage: Improvement percentage
            
        Returns:
            Recommendation dictionary
        """
        # Simple recommendation logic
        if improvement_percentage >= 20:
            recommendation = "strong_improvement"
            suggested_action = "Consider transitioning to better bucket"
        elif improvement_percentage >= 10:
            recommendation = "moderate_improvement"
            suggested_action = "Monitor for continued improvement"
        elif improvement_percentage >= 5:
            recommendation = "slight_improvement"
            suggested_action = "Continue current bucket with monitoring"
        else:
            recommendation = "minimal_improvement"
            suggested_action = "Maintain current bucket"
        
        return {
            "recommendation": recommendation,
            "suggested_action": suggested_action,
            "confidence": "high" if improvement_percentage >= 15 else "medium" if improvement_percentage >= 5 else "low"
        }
    
    def _session_to_response(
        self,
        session: ValidationTestSession,
        completed_items: int
    ) -> ValidationSessionResponse:
        """
        Convert validation session to response DTO.
        
        Args:
            session: Validation session entity
            completed_items: Number of completed items
            
        Returns:
            Validation session response
        """
        progress_percentage = session.get_progress_percentage(completed_items)
        duration_minutes = session.get_duration_minutes()
        
        return ValidationSessionResponse(
            session_id=session.id,
            speaker_id=session.speaker_id,
            session_name=session.session_name,
            test_data_count=session.test_data_count,
            status=session.status.value,
            mt_user_id=session.mt_user_id,
            progress_percentage=progress_percentage,
            started_at=session.started_at,
            completed_at=session.completed_at,
            duration_minutes=duration_minutes,
            session_metadata=session.session_metadata,
            created_at=session.created_at
        )
