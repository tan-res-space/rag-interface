"""
Enhanced RAG System Service

Provides integration with the enhanced RAG system for applying learned
corrections and improving transcription quality.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

import aiohttp
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RAGSystemConfig(BaseModel):
    """Configuration for RAG system service"""
    
    base_url: str = Field(..., description="Base URL for RAG system API")
    api_key: str = Field(..., description="API key for authentication")
    vector_db_url: str = Field(..., description="Vector database URL")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    confidence_threshold: float = Field(default=0.7, description="Minimum confidence for corrections")
    max_corrections_per_job: int = Field(default=20, description="Maximum corrections per job")


class CorrectionCandidate(BaseModel):
    """RAG correction candidate model"""
    
    correction_type: str = Field(..., description="Type of correction")
    original_text: str = Field(..., description="Original text to be corrected")
    corrected_text: str = Field(..., description="Suggested correction")
    confidence: float = Field(..., description="Confidence score (0-1)")
    position_start: Optional[int] = Field(None, description="Start position in text")
    position_end: Optional[int] = Field(None, description="End position in text")
    context: Optional[str] = Field(None, description="Surrounding context")
    reasoning: Optional[str] = Field(None, description="Explanation for correction")
    similar_cases: List[str] = Field(default_factory=list, description="Similar error cases")


class RAGCorrectionResult(BaseModel):
    """RAG correction result model"""
    
    original_text: str = Field(..., description="Original input text")
    corrected_text: str = Field(..., description="Text with corrections applied")
    corrections: List[CorrectionCandidate] = Field(..., description="List of corrections applied")
    overall_confidence: float = Field(..., description="Overall confidence score")
    processing_time: float = Field(..., description="Processing time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EnhancedRAGService:
    """Service for integrating with enhanced RAG system"""

    def __init__(self, config: RAGSystemConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()

    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "RAG-Interface-ErrorReporting/2.0"
            }
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )

    async def _close_session(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        await self._ensure_session()
        
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.config.max_retries):
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status >= 500:
                        # Server error, retry
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    
                    response.raise_for_status()
                    
            except aiohttp.ClientError as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
        
        raise Exception(f"Failed to complete request after {self.config.max_retries} attempts")

    async def apply_corrections(
        self,
        original_text: str,
        speaker_id: str,
        job_metadata: Optional[Dict[str, Any]] = None
    ) -> RAGCorrectionResult:
        """
        Apply RAG corrections to original text.
        
        Args:
            original_text: Original transcription text
            speaker_id: Speaker identifier for context
            job_metadata: Optional job metadata for context
            
        Returns:
            RAG correction result with applied corrections
        """
        logger.info(f"Applying RAG corrections for speaker {speaker_id}")
        
        start_time = datetime.utcnow()
        
        data = {
            "text": original_text,
            "speaker_id": speaker_id,
            "confidence_threshold": self.config.confidence_threshold,
            "max_corrections": self.config.max_corrections_per_job,
            "metadata": job_metadata or {}
        }
        
        try:
            response = await self._make_request("POST", "/api/v1/corrections/apply", data=data)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Parse corrections
            corrections = []
            for correction_data in response.get("corrections", []):
                try:
                    correction = CorrectionCandidate(**correction_data)
                    corrections.append(correction)
                except Exception as e:
                    logger.error(f"Failed to parse correction: {e}")
                    continue
            
            result = RAGCorrectionResult(
                original_text=original_text,
                corrected_text=response.get("corrected_text", original_text),
                corrections=corrections,
                overall_confidence=response.get("overall_confidence", 0.0),
                processing_time=processing_time,
                metadata=response.get("metadata", {})
            )
            
            logger.info(f"Applied {len(corrections)} corrections with confidence {result.overall_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to apply RAG corrections: {e}")
            raise

    async def learn_from_error_report(
        self,
        original_text: str,
        corrected_text: str,
        error_categories: List[str],
        speaker_id: str,
        enhanced_metadata: Dict[str, Any]
    ) -> bool:
        """
        Learn from an error report to improve future corrections.
        
        Args:
            original_text: Original text with error
            corrected_text: Corrected text
            error_categories: Categories of errors
            speaker_id: Speaker identifier
            enhanced_metadata: Enhanced metadata for context
            
        Returns:
            True if learning was successful
        """
        logger.info(f"Learning from error report for speaker {speaker_id}")
        
        data = {
            "original_text": original_text,
            "corrected_text": corrected_text,
            "error_categories": error_categories,
            "speaker_id": speaker_id,
            "enhanced_metadata": enhanced_metadata
        }
        
        try:
            await self._make_request("POST", "/api/v1/learning/error-report", data=data)
            logger.info("Successfully learned from error report")
            return True
            
        except Exception as e:
            logger.error(f"Failed to learn from error report: {e}")
            return False

    async def get_similar_errors(
        self,
        text: str,
        error_categories: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get similar errors from the vector database.
        
        Args:
            text: Text to find similar errors for
            error_categories: Error categories to filter by
            limit: Maximum number of similar errors to return
            
        Returns:
            List of similar error cases
        """
        logger.info(f"Finding similar errors for text: {text[:50]}...")
        
        data = {
            "text": text,
            "error_categories": error_categories,
            "limit": limit
        }
        
        try:
            response = await self._make_request("POST", "/api/v1/similarity/errors", data=data)
            
            similar_errors = response.get("similar_errors", [])
            logger.info(f"Found {len(similar_errors)} similar errors")
            return similar_errors
            
        except Exception as e:
            logger.error(f"Failed to find similar errors: {e}")
            return []

    async def update_speaker_profile(
        self,
        speaker_id: str,
        performance_metrics: Dict[str, Any],
        bucket_type: str
    ) -> bool:
        """
        Update speaker profile in RAG system for personalized corrections.
        
        Args:
            speaker_id: Speaker identifier
            performance_metrics: Performance metrics
            bucket_type: Current bucket type
            
        Returns:
            True if update was successful
        """
        logger.info(f"Updating speaker profile for {speaker_id}")
        
        data = {
            "speaker_id": speaker_id,
            "performance_metrics": performance_metrics,
            "bucket_type": bucket_type
        }
        
        try:
            await self._make_request("PUT", f"/api/v1/speakers/{speaker_id}/profile", data=data)
            logger.info(f"Successfully updated speaker profile for {speaker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update speaker profile: {e}")
            return False

    async def get_correction_suggestions(
        self,
        text: str,
        context: Optional[str] = None,
        speaker_id: Optional[str] = None
    ) -> List[CorrectionCandidate]:
        """
        Get correction suggestions for a text snippet.
        
        Args:
            text: Text to get suggestions for
            context: Optional context around the text
            speaker_id: Optional speaker identifier for personalization
            
        Returns:
            List of correction candidates
        """
        logger.info(f"Getting correction suggestions for text: {text[:50]}...")
        
        data = {
            "text": text,
            "context": context,
            "speaker_id": speaker_id,
            "confidence_threshold": self.config.confidence_threshold
        }
        
        try:
            response = await self._make_request("POST", "/api/v1/corrections/suggest", data=data)
            
            suggestions = []
            for suggestion_data in response.get("suggestions", []):
                try:
                    suggestion = CorrectionCandidate(**suggestion_data)
                    suggestions.append(suggestion)
                except Exception as e:
                    logger.error(f"Failed to parse suggestion: {e}")
                    continue
            
            logger.info(f"Generated {len(suggestions)} correction suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get correction suggestions: {e}")
            return []

    async def analyze_text_complexity(
        self,
        text: str,
        enhanced_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze text complexity using enhanced metadata.
        
        Args:
            text: Text to analyze
            enhanced_metadata: Enhanced metadata for context
            
        Returns:
            Dictionary containing complexity analysis
        """
        logger.info(f"Analyzing text complexity for text: {text[:50]}...")
        
        data = {
            "text": text,
            "enhanced_metadata": enhanced_metadata
        }
        
        try:
            response = await self._make_request("POST", "/api/v1/analysis/complexity", data=data)
            
            analysis = {
                "complexity_score": response.get("complexity_score", 0.0),
                "difficulty_factors": response.get("difficulty_factors", []),
                "recommended_bucket": response.get("recommended_bucket", "medium_touch"),
                "confidence": response.get("confidence", 0.0),
                "analysis_details": response.get("analysis_details", {})
            }
            
            logger.info(f"Complexity analysis completed with score {analysis['complexity_score']:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze text complexity: {e}")
            return {"complexity_score": 0.0, "difficulty_factors": [], "recommended_bucket": "medium_touch"}

    async def get_system_statistics(self) -> Dict[str, Any]:
        """
        Get RAG system statistics and performance metrics.
        
        Returns:
            Dictionary containing system statistics
        """
        logger.info("Fetching RAG system statistics")
        
        try:
            response = await self._make_request("GET", "/api/v1/statistics")
            
            statistics = {
                "total_corrections_applied": response.get("total_corrections_applied", 0),
                "average_confidence": response.get("average_confidence", 0.0),
                "correction_types": response.get("correction_types", {}),
                "speaker_profiles": response.get("speaker_profiles", 0),
                "vector_db_size": response.get("vector_db_size", 0),
                "learning_rate": response.get("learning_rate", 0.0),
                "system_health": response.get("system_health", "unknown")
            }
            
            logger.info("Retrieved RAG system statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get system statistics: {e}")
            return {}

    async def health_check(self) -> bool:
        """
        Check if RAG system is healthy.
        
        Returns:
            True if system is healthy
        """
        try:
            response = await self._make_request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
