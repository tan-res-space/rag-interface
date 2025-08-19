"""
Request DTOs for the Correction Engine Service application layer.

These DTOs define the structure of requests to use cases and API endpoints.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from src.correction_engine_service.domain.value_objects.correction_mode import CorrectionMode


@dataclass(frozen=True)
class CorrectionRequest:
    """
    Request DTO for text correction.
    """
    
    text: str
    correction_mode: CorrectionMode = CorrectionMode.BALANCED
    max_suggestions: int = 5
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    requested_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.text or not self.text.strip():
            raise ValueError("text cannot be empty")
        
        if len(self.text) > 10000:
            raise ValueError("text cannot exceed 10000 characters")
        
        if self.max_suggestions <= 0 or self.max_suggestions > 20:
            raise ValueError("max_suggestions must be between 1 and 20")
        
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class BatchCorrectionRequest:
    """
    Request DTO for batch text correction.
    """
    
    texts: List[str]
    correction_mode: CorrectionMode = CorrectionMode.BALANCED
    max_suggestions_per_text: int = 5
    metadata: Optional[Dict[str, Any]] = None
    requested_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.texts:
            raise ValueError("texts list cannot be empty")
        
        if len(self.texts) > 50:
            raise ValueError("batch size cannot exceed 50 texts")
        
        for i, text in enumerate(self.texts):
            if not text or not text.strip():
                raise ValueError(f"text at index {i} cannot be empty")
            
            if len(text) > 10000:
                raise ValueError(f"text at index {i} cannot exceed 10000 characters")
        
        if self.max_suggestions_per_text <= 0 or self.max_suggestions_per_text > 10:
            raise ValueError("max_suggestions_per_text must be between 1 and 10")
        
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class ApplyCorrectionRequest:
    """
    Request DTO for applying a specific correction.
    """
    
    suggestion_id: str
    user_feedback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    requested_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.suggestion_id or not self.suggestion_id.strip():
            raise ValueError("suggestion_id cannot be empty")
        
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class RejectCorrectionRequest:
    """
    Request DTO for rejecting a correction suggestion.
    """
    
    suggestion_id: str
    rejection_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    requested_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.suggestion_id or not self.suggestion_id.strip():
            raise ValueError("suggestion_id cannot be empty")
        
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
