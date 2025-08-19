"""
Generate Corrections Use Case

This use case handles the generation of correction suggestions for text inputs.
It coordinates correction model operations and suggestion storage.
"""

import time
from typing import List

from ..dto.requests import CorrectionRequest
from ..dto.responses import CorrectionResponse
from ...domain.entities.correction_suggestion import CorrectionSuggestion


class GenerateCorrectionsUseCase:
    """
    Use case for generating text corrections.
    
    This use case coordinates the generation of correction suggestions by:
    1. Processing text through correction models
    2. Filtering suggestions based on correction mode
    3. Storing suggestions for tracking and analytics
    4. Returning ranked suggestions to the user
    """
    
    def __init__(self, correction_model, suggestion_repository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            correction_model: Correction model port for generating suggestions
            suggestion_repository: Repository port for storing suggestions
        """
        self._correction_model = correction_model
        self._suggestion_repository = suggestion_repository
    
    async def execute(self, request: CorrectionRequest) -> CorrectionResponse:
        """
        Execute the generate corrections use case.
        
        Args:
            request: Correction generation request
            
        Returns:
            Response containing correction suggestions
            
        Raises:
            ValueError: If request is invalid
            Exception: If correction generation fails
        """
        start_time = time.time()
        
        # 1. Generate correction suggestions using the model
        all_suggestions = await self._correction_model.generate_corrections(
            text=request.text,
            context=request.context,
            metadata=request.metadata
        )
        
        # 2. Filter suggestions based on correction mode
        filtered_suggestions = self._filter_by_correction_mode(
            all_suggestions, 
            request.correction_mode
        )
        
        # 3. Limit to max suggestions and sort by confidence
        final_suggestions = self._limit_and_sort_suggestions(
            filtered_suggestions,
            request.max_suggestions
        )
        
        # 4. Store suggestions for tracking
        await self._suggestion_repository.save_suggestions(final_suggestions)
        
        # 5. Calculate processing time and return response
        processing_time = time.time() - start_time
        return self._create_response(
            request.text,
            final_suggestions,
            processing_time,
            request.correction_mode
        )
    
    def _filter_by_correction_mode(
        self, 
        suggestions: List[CorrectionSuggestion], 
        mode
    ) -> List[CorrectionSuggestion]:
        """
        Filter suggestions based on correction mode thresholds.
        
        Args:
            suggestions: List of all suggestions
            mode: Correction mode with confidence threshold
            
        Returns:
            Filtered list of suggestions
        """
        return [
            suggestion for suggestion in suggestions
            if suggestion.should_apply_with_mode(mode)
        ]
    
    def _limit_and_sort_suggestions(
        self, 
        suggestions: List[CorrectionSuggestion], 
        max_suggestions: int
    ) -> List[CorrectionSuggestion]:
        """
        Sort suggestions by confidence and limit to max count.
        
        Args:
            suggestions: List of suggestions to sort and limit
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            Sorted and limited list of suggestions
        """
        # Sort by confidence score (highest first)
        sorted_suggestions = sorted(suggestions, reverse=True)
        
        # Limit to max suggestions
        return sorted_suggestions[:max_suggestions]
    
    def _create_response(
        self, 
        original_text: str,
        suggestions: List[CorrectionSuggestion], 
        processing_time: float,
        correction_mode
    ) -> CorrectionResponse:
        """
        Create response DTO from suggestions.
        
        Args:
            original_text: Original input text
            suggestions: List of correction suggestions
            processing_time: Time taken to process the request
            correction_mode: Correction mode used
            
        Returns:
            CorrectionResponse DTO
        """
        model_info = {
            "name": self._correction_model.get_model_name(),
            "version": self._correction_model.get_model_version()
        }
        
        return CorrectionResponse(
            original_text=original_text,
            suggestions=suggestions,
            processing_time=processing_time,
            correction_mode=correction_mode.value,
            model_info=model_info,
            status="success"
        )
