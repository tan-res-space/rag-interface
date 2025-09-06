"""
Calculate SER Metrics Use Case

Application use case for calculating SER metrics for speaker bucket management.
Orchestrates SER calculation workflow and data persistence.
"""

from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from ...domain.services.ser_calculation_service import SERCalculationService
from ...domain.value_objects.ser_metrics import SERMetrics
from ..dto.requests import BatchCalculateSERRequest, CalculateSERRequest
from ..dto.responses import BatchSERCalculationResponse, SERCalculationResponse


class CalculateSERMetricsUseCase:
    """
    Use case for calculating SER metrics for speaker quality assessment.

    This use case orchestrates the SER calculation process, including
    validation, computation, and result formatting for the speaker bucket management system.
    """

    def __init__(self, ser_calculation_service: SERCalculationService):
        """
        Initialize the use case with required services.

        Args:
            ser_calculation_service: Domain service for SER calculations
        """
        self._ser_service = ser_calculation_service

    def execute(self, request: CalculateSERRequest) -> SERCalculationResponse:
        """
        Execute SER calculation for a single text pair.

        Args:
            request: SER calculation request

        Returns:
            SER calculation response

        Raises:
            ValueError: If request validation fails
        """
        # Validate request
        self._validate_single_request(request)

        # Calculate SER metrics
        ser_metrics = self._ser_service.calculate_ser(
            asr_text=request.asr_text, reference_text=request.reference_text
        )

        # Create response
        return SERCalculationResponse(
            speaker_id=request.speaker_id,
            historical_data_id=request.historical_data_id,
            calculation_type=request.calculation_type,
            ser_metrics=ser_metrics,
            metadata=request.metadata or {},
        )

    def execute_batch(
        self, request: BatchCalculateSERRequest
    ) -> BatchSERCalculationResponse:
        """
        Execute SER calculation for multiple text pairs.

        Args:
            request: Batch SER calculation request

        Returns:
            Batch SER calculation response

        Raises:
            ValueError: If request validation fails
        """
        # Validate request
        self._validate_batch_request(request)

        # Prepare text pairs
        text_pairs = [
            (item.asr_text, item.reference_text) for item in request.calculation_items
        ]

        # Calculate SER metrics for all pairs
        ser_metrics_list = self._ser_service.calculate_batch_ser(text_pairs)

        # Create individual responses
        responses = []
        for i, (item, ser_metrics) in enumerate(
            zip(request.calculation_items, ser_metrics_list)
        ):
            response = SERCalculationResponse(
                speaker_id=item.speaker_id,
                historical_data_id=item.historical_data_id,
                calculation_type=item.calculation_type,
                ser_metrics=ser_metrics,
                metadata=item.metadata or {},
            )
            responses.append(response)

        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(ser_metrics_list)

        return BatchSERCalculationResponse(
            total_calculations=len(responses),
            successful_calculations=len(
                responses
            ),  # All successful in this implementation
            failed_calculations=0,
            results=responses,
            summary_statistics=summary_stats,
        )

    def compare_ser_results(
        self, original_ser: SERMetrics, corrected_ser: SERMetrics
    ) -> Dict[str, Any]:
        """
        Compare two SER results to assess improvement.

        Args:
            original_ser: Original ASR SER metrics
            corrected_ser: RAG-corrected SER metrics

        Returns:
            Comparison results
        """
        return self._ser_service.compare_ser_metrics(original_ser, corrected_ser)

    def calculate_speaker_average_ser(
        self, speaker_id: UUID, ser_metrics_list: List[SERMetrics]
    ) -> Decimal:
        """
        Calculate average SER score for a speaker.

        Args:
            speaker_id: Speaker identifier
            ser_metrics_list: List of SER metrics for the speaker

        Returns:
            Average SER score
        """
        if not ser_metrics_list:
            raise ValueError("Cannot calculate average from empty metrics list")

        return self._ser_service.calculate_speaker_average_ser(ser_metrics_list)

    def get_quality_distribution(
        self, ser_metrics_list: List[SERMetrics]
    ) -> Dict[str, int]:
        """
        Get quality distribution from SER metrics.

        Args:
            ser_metrics_list: List of SER metrics

        Returns:
            Quality distribution
        """
        return self._ser_service.get_quality_distribution(ser_metrics_list)

    def _validate_single_request(self, request: CalculateSERRequest) -> None:
        """
        Validate single SER calculation request.

        Args:
            request: Request to validate

        Raises:
            ValueError: If validation fails
        """
        if not request.asr_text or not request.asr_text.strip():
            raise ValueError("asr_text cannot be empty")

        if not request.reference_text or not request.reference_text.strip():
            raise ValueError("reference_text cannot be empty")

        if request.asr_text.strip() == request.reference_text.strip():
            raise ValueError("asr_text and reference_text cannot be identical")

        if request.calculation_type not in ["original", "rag_corrected"]:
            raise ValueError("calculation_type must be 'original' or 'rag_corrected'")

    def _validate_batch_request(self, request: BatchCalculateSERRequest) -> None:
        """
        Validate batch SER calculation request.

        Args:
            request: Request to validate

        Raises:
            ValueError: If validation fails
        """
        if not request.calculation_items:
            raise ValueError("calculation_items cannot be empty")

        if len(request.calculation_items) > 1000:  # Reasonable batch size limit
            raise ValueError("Batch size exceeds maximum allowed (1000)")

        # Validate each item
        for i, item in enumerate(request.calculation_items):
            try:
                self._validate_single_request(item)
            except ValueError as e:
                raise ValueError(f"Validation failed for item {i}: {e}")

    def _calculate_summary_statistics(
        self, ser_metrics_list: List[SERMetrics]
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics for a batch of SER metrics.

        Args:
            ser_metrics_list: List of SER metrics

        Returns:
            Summary statistics
        """
        if not ser_metrics_list:
            return {}

        ser_scores = [float(metrics.ser_score) for metrics in ser_metrics_list]
        quality_distribution = self.get_quality_distribution(ser_metrics_list)

        return {
            "total_items": len(ser_metrics_list),
            "average_ser": sum(ser_scores) / len(ser_scores),
            "min_ser": min(ser_scores),
            "max_ser": max(ser_scores),
            "quality_distribution": quality_distribution,
            "high_quality_percentage": (
                quality_distribution.get("high", 0) / len(ser_metrics_list)
            )
            * 100,
            "medium_quality_percentage": (
                quality_distribution.get("medium", 0) / len(ser_metrics_list)
            )
            * 100,
            "low_quality_percentage": (
                quality_distribution.get("low", 0) / len(ser_metrics_list)
            )
            * 100,
        }
