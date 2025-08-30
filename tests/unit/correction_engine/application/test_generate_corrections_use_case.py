"""
Unit tests for Generate Corrections Use Case.

Following TDD principles for correction processing components.
Tests focus on use case orchestration with mocked dependencies.
"""

import asyncio
import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.correction_engine_service.application.dto.requests import CorrectionRequest
from src.correction_engine_service.application.dto.responses import CorrectionResponse
from src.correction_engine_service.application.use_cases.generate_corrections import (
    GenerateCorrectionsUseCase,
)
from src.correction_engine_service.domain.entities.correction_suggestion import (
    CorrectionSuggestion,
)
from src.correction_engine_service.domain.value_objects.confidence_score import (
    ConfidenceScore,
)
from src.correction_engine_service.domain.value_objects.correction_mode import (
    CorrectionMode,
)


class TestGenerateCorrectionsUseCase:
    """Test generate corrections use case orchestration."""

    @pytest.fixture
    def mock_correction_model(self):
        """Create mock correction model port."""
        mock = Mock()
        mock.generate_corrections = AsyncMock(
            return_value=[
                CorrectionSuggestion(
                    id=uuid4(),
                    original_text="I are going",
                    corrected_text="I am going",
                    confidence_score=ConfidenceScore(0.95),
                    correction_type="grammar",
                    model_name="test-model",
                )
            ]
        )
        mock.get_model_name.return_value = "test-correction-model"
        mock.get_model_version.return_value = "v1.0"
        return mock

    @pytest.fixture
    def mock_suggestion_repository(self):
        """Create mock suggestion repository port."""
        mock = Mock()
        mock.save_suggestions = AsyncMock(return_value=True)
        return mock

    @pytest.fixture
    def use_case(self, mock_correction_model, mock_suggestion_repository):
        """Create use case with mocked dependencies."""
        return GenerateCorrectionsUseCase(
            correction_model=mock_correction_model,
            suggestion_repository=mock_suggestion_repository,
        )

    @pytest.mark.asyncio
    async def test_generate_corrections_success(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test successful correction generation."""
        # Arrange
        request = CorrectionRequest(
            text="I are going to the store",
            correction_mode=CorrectionMode.BALANCED,
            max_suggestions=5,
            requested_by="user1",
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert isinstance(response, CorrectionResponse)
        assert response.status == "success"
        assert response.original_text == request.text
        assert len(response.suggestions) == 1
        assert response.suggestions[0].corrected_text == "I am going"
        assert response.processing_time > 0
        assert response.correction_mode == "balanced"

        # Verify interactions
        mock_correction_model.generate_corrections.assert_called_once()
        mock_suggestion_repository.save_suggestions.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_corrections_with_conservative_mode(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test correction generation with conservative mode."""
        # Arrange
        request = CorrectionRequest(
            text="Test text",
            correction_mode=CorrectionMode.CONSERVATIVE,
            max_suggestions=3,
        )

        # Mock high and low confidence suggestions
        high_confidence = CorrectionSuggestion(
            id=uuid4(),
            original_text="Test text",
            corrected_text="Test text corrected",
            confidence_score=ConfidenceScore(0.95),
            correction_type="grammar",
            model_name="test-model",
        )

        low_confidence = CorrectionSuggestion(
            id=uuid4(),
            original_text="Test text",
            corrected_text="Test text maybe corrected",
            confidence_score=ConfidenceScore(0.7),
            correction_type="style",
            model_name="test-model",
        )

        mock_correction_model.generate_corrections.return_value = [
            high_confidence,
            low_confidence,
        ]

        # Act
        response = await use_case.execute(request)

        # Assert
        # Conservative mode should only include high confidence suggestions
        assert len(response.suggestions) == 1
        assert response.suggestions[0].confidence_score.value == 0.95

    @pytest.mark.asyncio
    async def test_generate_corrections_with_aggressive_mode(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test correction generation with aggressive mode."""
        # Arrange
        request = CorrectionRequest(
            text="Test text",
            correction_mode=CorrectionMode.AGGRESSIVE,
            max_suggestions=5,
        )

        # Mock various confidence suggestions
        suggestions = [
            CorrectionSuggestion(
                id=uuid4(),
                original_text="Test text",
                corrected_text=f"Correction {i}",
                confidence_score=ConfidenceScore(0.6 + i * 0.1),
                correction_type="grammar",
                model_name="test-model",
            )
            for i in range(4)
        ]

        mock_correction_model.generate_corrections.return_value = suggestions

        # Act
        response = await use_case.execute(request)

        # Assert
        # Aggressive mode should include all suggestions above 0.6 threshold
        assert len(response.suggestions) == 4

    @pytest.mark.asyncio
    async def test_generate_corrections_respects_max_suggestions(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test that max_suggestions limit is respected."""
        # Arrange
        request = CorrectionRequest(
            text="Test text",
            correction_mode=CorrectionMode.AGGRESSIVE,
            max_suggestions=2,
        )

        # Mock more suggestions than the limit
        suggestions = [
            CorrectionSuggestion(
                id=uuid4(),
                original_text="Test text",
                corrected_text=f"Correction {i}",
                confidence_score=ConfidenceScore(0.9 - i * 0.1),
                correction_type="grammar",
                model_name="test-model",
            )
            for i in range(5)
        ]

        mock_correction_model.generate_corrections.return_value = suggestions

        # Act
        response = await use_case.execute(request)

        # Assert
        assert len(response.suggestions) == 2
        # Should return the highest confidence suggestions
        assert response.suggestions[0].confidence_score.value == 0.9
        assert response.suggestions[1].confidence_score.value == 0.8

    @pytest.mark.asyncio
    async def test_generate_corrections_model_failure(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test handling of correction model failure."""
        # Arrange
        request = CorrectionRequest(
            text="Test text", correction_mode=CorrectionMode.BALANCED
        )

        mock_correction_model.generate_corrections.side_effect = Exception(
            "Model error"
        )

        # Act & Assert
        with pytest.raises(Exception, match="Model error"):
            await use_case.execute(request)

        # Verify repository was not called due to model failure
        mock_suggestion_repository.save_suggestions.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_corrections_repository_failure(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test handling of repository failure."""
        # Arrange
        request = CorrectionRequest(
            text="Test text", correction_mode=CorrectionMode.BALANCED
        )

        mock_suggestion_repository.save_suggestions.side_effect = Exception(
            "Repository error"
        )

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await use_case.execute(request)

        # Verify model was called but repository failed
        mock_correction_model.generate_corrections.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_corrections_performance_tracking(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test that processing time is tracked correctly."""
        # Arrange
        request = CorrectionRequest(
            text="Performance test", correction_mode=CorrectionMode.BALANCED
        )

        # Simulate some processing time
        async def slow_generate_corrections(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return [
                CorrectionSuggestion(
                    id=uuid4(),
                    original_text="Performance test",
                    corrected_text="Performance test corrected",
                    confidence_score=ConfidenceScore(0.9),
                    correction_type="grammar",
                    model_name="test-model",
                )
            ]

        mock_correction_model.generate_corrections = slow_generate_corrections

        # Act
        start_time = time.time()
        response = await use_case.execute(request)
        end_time = time.time()

        # Assert
        assert response.processing_time > 0
        assert response.processing_time <= (end_time - start_time)

    @pytest.mark.asyncio
    async def test_generate_corrections_with_context(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test correction generation with context."""
        # Arrange
        request = CorrectionRequest(
            text="Test text",
            correction_mode=CorrectionMode.BALANCED,
            context="This is additional context for better corrections",
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.status == "success"
        # Verify context was passed to the model
        call_args = mock_correction_model.generate_corrections.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_generate_corrections_model_info_in_response(
        self, use_case, mock_correction_model, mock_suggestion_repository
    ):
        """Test that model information is included in response."""
        # Arrange
        request = CorrectionRequest(
            text="Model info test", correction_mode=CorrectionMode.BALANCED
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert "name" in response.model_info
        assert "version" in response.model_info
        assert response.model_info["name"] == "test-correction-model"
        assert response.model_info["version"] == "v1.0"
