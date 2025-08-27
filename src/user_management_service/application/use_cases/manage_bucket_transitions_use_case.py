"""
Manage Bucket Transitions Use Case

Application use case for managing speaker bucket transition requests.
Orchestrates transition request creation, approval workflow, and history tracking.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from ...domain.entities.bucket_transition_request import BucketTransitionRequest
from ...domain.entities.speaker import Speaker
from ...domain.value_objects.speaker_bucket import SpeakerBucket
from ..ports.speaker_repository_port import ISpeakerRepositoryPort
from ..dto.requests import (
    CreateBucketTransitionRequest,
    ApproveBucketTransitionRequest,
    RejectBucketTransitionRequest
)
from ..dto.responses import (
    BucketTransitionRequestResponse
)


class ManageBucketTransitionsUseCase:
    """
    Use case for managing speaker bucket transition requests.
    
    This use case orchestrates the complete bucket transition workflow including
    request creation, approval process, speaker updates, and history tracking.
    """
    
    def __init__(self, speaker_repository: ISpeakerRepositoryPort):
        """
        Initialize the use case with required repositories.
        
        Args:
            speaker_repository: Repository for speaker and transition data operations
        """
        self._speaker_repo = speaker_repository
    
    async def create_transition_request(
        self,
        request: CreateBucketTransitionRequest
    ) -> BucketTransitionRequestResponse:
        """
        Create a new bucket transition request.
        
        Args:
            request: Transition request creation data
            
        Returns:
            Created transition request response
            
        Raises:
            ValueError: If validation fails
        """
        # Verify speaker exists
        speaker = await self._speaker_repo.get_speaker_by_id(request.speaker_id)
        if not speaker:
            raise ValueError(f"Speaker with ID {request.speaker_id} not found")
        
        # Validate transition is allowed
        if not speaker.can_transition_to_bucket(request.to_bucket):
            raise ValueError(
                f"Invalid transition from {request.from_bucket} to {request.to_bucket}"
            )
        
        # Create transition request entity
        transition_request = BucketTransitionRequest(
            id=uuid4(),
            speaker_id=request.speaker_id,
            from_bucket=request.from_bucket,
            to_bucket=request.to_bucket,
            transition_reason=request.transition_reason,
            ser_improvement=request.ser_improvement,
            requested_by=request.requested_by
        )
        
        # Save transition request
        created_request = await self._speaker_repo.create_bucket_transition_request(transition_request)
        
        return self._transition_request_to_response(created_request)
    
    async def get_transition_request_by_id(
        self,
        request_id: UUID
    ) -> Optional[BucketTransitionRequestResponse]:
        """
        Get transition request by ID.
        
        Args:
            request_id: Transition request identifier
            
        Returns:
            Transition request response or None if not found
        """
        transition_request = await self._speaker_repo.get_bucket_transition_request_by_id(request_id)
        if not transition_request:
            return None
        
        return self._transition_request_to_response(transition_request)
    
    async def get_pending_transition_requests(self) -> List[BucketTransitionRequestResponse]:
        """
        Get all pending transition requests.
        
        Returns:
            List of pending transition requests sorted by priority
        """
        pending_requests = await self._speaker_repo.get_pending_transition_requests()
        
        # Sort by priority (lower score = higher priority)
        sorted_requests = sorted(pending_requests, key=lambda r: r.get_priority_score())
        
        return [self._transition_request_to_response(req) for req in sorted_requests]
    
    async def approve_transition_request(
        self,
        request_id: UUID,
        approval_request: ApproveBucketTransitionRequest
    ) -> BucketTransitionRequestResponse:
        """
        Approve a bucket transition request.
        
        Args:
            request_id: Transition request identifier
            approval_request: Approval details
            
        Returns:
            Updated transition request response
            
        Raises:
            ValueError: If request cannot be approved
        """
        # Get transition request
        transition_request = await self._speaker_repo.get_bucket_transition_request_by_id(request_id)
        if not transition_request:
            raise ValueError(f"Transition request {request_id} not found")
        
        # Approve the request
        transition_request.approve(
            approved_by=approval_request.approved_by,
            approval_notes=approval_request.approval_notes
        )
        
        # Update transition request
        updated_request = await self._speaker_repo.update_bucket_transition_request(transition_request)
        
        # Update speaker bucket
        speaker = await self._speaker_repo.get_speaker_by_id(transition_request.speaker_id)
        if speaker:
            speaker.transition_bucket(transition_request.to_bucket)
            await self._speaker_repo.update_speaker(speaker)
        
        return self._transition_request_to_response(updated_request)
    
    async def reject_transition_request(
        self,
        request_id: UUID,
        rejection_request: RejectBucketTransitionRequest
    ) -> BucketTransitionRequestResponse:
        """
        Reject a bucket transition request.
        
        Args:
            request_id: Transition request identifier
            rejection_request: Rejection details
            
        Returns:
            Updated transition request response
            
        Raises:
            ValueError: If request cannot be rejected
        """
        # Get transition request
        transition_request = await self._speaker_repo.get_bucket_transition_request_by_id(request_id)
        if not transition_request:
            raise ValueError(f"Transition request {request_id} not found")
        
        # Reject the request
        transition_request.reject(
            rejected_by=rejection_request.rejected_by,
            rejection_reason=rejection_request.rejection_reason
        )
        
        # Update transition request
        updated_request = await self._speaker_repo.update_bucket_transition_request(transition_request)
        
        return self._transition_request_to_response(updated_request)
    
    async def get_speaker_transition_history(
        self,
        speaker_id: UUID,
        limit: int = 50
    ) -> List[BucketTransitionRequestResponse]:
        """
        Get transition history for a speaker.
        
        Args:
            speaker_id: Speaker identifier
            limit: Maximum number of records to return
            
        Returns:
            List of transition requests for the speaker
        """
        transition_history = await self._speaker_repo.get_transition_history_for_speaker(speaker_id)
        
        # Sort by creation date (most recent first)
        sorted_history = sorted(
            transition_history,
            key=lambda r: r.created_at,
            reverse=True
        )[:limit]
        
        return [self._transition_request_to_response(req) for req in sorted_history]
    
    async def get_transition_requests(
        self,
        status: Optional[str] = None,
        speaker_id: Optional[UUID] = None,
        urgent_only: bool = False,
        limit: int = 100
    ) -> List[BucketTransitionRequestResponse]:
        """
        Get transition requests with filters.
        
        Args:
            status: Filter by status
            speaker_id: Filter by speaker ID
            urgent_only: Show only urgent requests
            limit: Maximum number of requests
            
        Returns:
            List of filtered transition requests
        """
        # This would need to be implemented in the repository
        # For now, get all pending requests and filter
        if status == "pending" or status is None:
            requests = await self._speaker_repo.get_pending_transition_requests()
        else:
            # Would need repository method to get by status
            requests = []
        
        # Apply filters
        if speaker_id:
            requests = [req for req in requests if req.speaker_id == speaker_id]
        
        if urgent_only:
            requests = [req for req in requests if req.is_urgent()]
        
        # Sort by priority and limit
        sorted_requests = sorted(requests, key=lambda r: r.get_priority_score())[:limit]
        
        return [self._transition_request_to_response(req) for req in sorted_requests]
    
    async def auto_generate_transition_requests(self) -> List[BucketTransitionRequestResponse]:
        """
        Auto-generate transition requests for speakers needing bucket changes.
        
        Returns:
            List of auto-generated transition requests
        """
        # Get speakers needing transition
        speakers_needing_transition = await self._speaker_repo.get_speakers_needing_transition()
        
        generated_requests = []
        
        for speaker in speakers_needing_transition:
            # Check if there's already a pending request for this speaker
            existing_requests = await self._speaker_repo.get_transition_history_for_speaker(speaker.id)
            has_pending = any(req.is_pending() for req in existing_requests)
            
            if not has_pending:
                # Generate automatic transition request
                recommended_bucket = speaker.get_recommended_bucket()
                
                transition_request = BucketTransitionRequest(
                    id=uuid4(),
                    speaker_id=speaker.id,
                    from_bucket=speaker.current_bucket,
                    to_bucket=recommended_bucket,
                    transition_reason=f"Automatic recommendation based on SER improvement. "
                                    f"Current trend: {speaker.get_quality_trend()}",
                    ser_improvement=speaker.average_ser_score,
                    requested_by=None  # System-generated
                )
                
                # Save the request
                created_request = await self._speaker_repo.create_bucket_transition_request(
                    transition_request
                )
                generated_requests.append(self._transition_request_to_response(created_request))
        
        return generated_requests
    
    def _transition_request_to_response(
        self,
        transition_request: BucketTransitionRequest
    ) -> BucketTransitionRequestResponse:
        """
        Convert transition request entity to response DTO.
        
        Args:
            transition_request: Transition request entity
            
        Returns:
            Transition request response DTO
        """
        summary = transition_request.get_request_summary()
        
        return BucketTransitionRequestResponse(
            request_id=summary["id"],
            speaker_id=summary["speaker_id"],
            from_bucket=summary["from_bucket"],
            to_bucket=summary["to_bucket"],
            transition_type=summary["transition_type"],
            transition_reason=summary["transition_reason"],
            ser_improvement=summary["ser_improvement"],
            status=summary["status"],
            requested_by=summary["requested_by"],
            approved_by=summary["approved_by"],
            approval_notes=summary["approval_notes"],
            is_urgent=summary["is_urgent"],
            priority_score=summary["priority_score"],
            processing_time_hours=summary["processing_time_hours"],
            created_at=transition_request.created_at,
            approved_at=transition_request.approved_at
        )
