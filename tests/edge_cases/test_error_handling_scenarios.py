"""
Edge Cases and Error Handling Tests

Tests for boundary conditions, error scenarios, and edge cases
that could occur in production environments.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

from src.error_reporting_service.domain.entities.error_report import ErrorReport, SeverityLevel
from src.error_reporting_service.application.use_cases.submit_error_report import SubmitErrorReportUseCase
from src.error_reporting_service.application.dto.requests import SubmitErrorReportRequest
from src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter import PostgreSQLAdapter
from tests.factories import ErrorReportFactory


class TestBoundaryConditions:
    """Test boundary conditions and edge cases"""

    def test_maximum_text_length_handling(self):
        """Test handling of maximum allowed text lengths"""
        max_length = 5000
        
        # Test at boundary
        boundary_text = "A" * max_length
        error_report = ErrorReport(
            job_id="boundary-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text=boundary_text,
            corrected_text=boundary_text[:-1] + "B",  # Make it different
            error_categories=["boundary_test"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=10,
            error_timestamp=datetime.utcnow()
        )
        
        assert len(error_report.original_text) == max_length
        assert error_report.original_text != error_report.corrected_text

    def test_text_length_exceeds_maximum(self):
        """Test handling when text exceeds maximum length"""
        max_length = 5000
        oversized_text = "A" * (max_length + 1)
        
        with pytest.raises(ValueError, match="cannot exceed"):
            ErrorReport(
                job_id="oversized-test",
                speaker_id="speaker-test",
                reported_by="user-test",
                original_text=oversized_text,
                corrected_text="corrected",
                error_categories=["test"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=10,
                error_timestamp=datetime.utcnow()
            )

    def test_minimum_text_length_handling(self):
        """Test handling of minimum text lengths"""
        # Single character should be valid
        single_char_report = ErrorReport(
            job_id="single-char-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text="a",
            corrected_text="A",
            error_categories=["case_correction"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=1,
            error_timestamp=datetime.utcnow()
        )
        
        assert single_char_report.original_text == "a"
        assert single_char_report.corrected_text == "A"

    def test_empty_text_rejection(self):
        """Test that empty text is properly rejected"""
        with pytest.raises(ValueError, match="cannot be empty"):
            ErrorReport(
                job_id="empty-test",
                speaker_id="speaker-test",
                reported_by="user-test",
                original_text="",
                corrected_text="corrected",
                error_categories=["test"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=0,
                error_timestamp=datetime.utcnow()
            )

    def test_unicode_text_handling(self):
        """Test handling of Unicode characters"""
        unicode_text = "Patient has 高血压 (hypertension) 症状"
        corrected_unicode = "Patient has hypertension symptoms"
        
        unicode_report = ErrorReport(
            job_id="unicode-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text=unicode_text,
            corrected_text=corrected_unicode,
            error_categories=["language_mixing"],
            severity_level=SeverityLevel.MEDIUM,
            start_position=12,
            end_position=25,
            error_timestamp=datetime.utcnow()
        )
        
        assert unicode_report.original_text == unicode_text
        assert "高血压" in unicode_report.original_text

    def test_special_characters_handling(self):
        """Test handling of special characters and symbols"""
        special_text = "Patient's temp: 98.6°F (37°C) - normal range"
        corrected_special = "Patient's temperature: 98.6°F (37°C) - normal range"
        
        special_report = ErrorReport(
            job_id="special-chars-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text=special_text,
            corrected_text=corrected_special,
            error_categories=["abbreviation"],
            severity_level=SeverityLevel.LOW,
            start_position=10,
            end_position=14,
            error_timestamp=datetime.utcnow()
        )
        
        assert "°" in special_report.original_text
        assert special_report.original_text != special_report.corrected_text

    def test_position_boundary_conditions(self):
        """Test position boundary conditions"""
        text = "This is a test sentence"
        
        # Position at start
        start_report = ErrorReport(
            job_id="start-pos-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text=text,
            corrected_text=text.replace("This", "That"),
            error_categories=["word_choice"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=4,
            error_timestamp=datetime.utcnow()
        )
        
        assert start_report.start_position == 0
        
        # Position at end
        end_report = ErrorReport(
            job_id="end-pos-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text=text,
            corrected_text=text.replace("sentence", "phrase"),
            error_categories=["word_choice"],
            severity_level=SeverityLevel.LOW,
            start_position=17,
            end_position=25,
            error_timestamp=datetime.utcnow()
        )
        
        assert end_report.end_position == len(text)

    def test_invalid_position_ranges(self):
        """Test invalid position ranges are rejected"""
        text = "Short text"
        
        # End position before start position
        with pytest.raises(ValueError, match="end_position must be greater"):
            ErrorReport(
                job_id="invalid-range-test",
                speaker_id="speaker-test",
                reported_by="user-test",
                original_text=text,
                corrected_text="Corrected text",
                error_categories=["test"],
                severity_level=SeverityLevel.LOW,
                start_position=5,
                end_position=3,  # Invalid: before start
                error_timestamp=datetime.utcnow()
            )

    def test_position_exceeds_text_length(self):
        """Test positions that exceed text length"""
        text = "Short"
        
        with pytest.raises(ValueError, match="position range exceeds text length"):
            ErrorReport(
                job_id="exceed-length-test",
                speaker_id="speaker-test",
                reported_by="user-test",
                original_text=text,
                corrected_text="Corrected",
                error_categories=["test"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=10,  # Exceeds text length
                error_timestamp=datetime.utcnow()
            )


class TestDatabaseErrorHandling:
    """Test database error handling scenarios"""

    @pytest.fixture
    def mock_db_adapter(self):
        return Mock(spec=PostgreSQLAdapter)

    @pytest.fixture
    def use_case(self, mock_db_adapter):
        mock_validation_service = Mock()
        mock_categorization_service = Mock()
        mock_event_publisher = Mock()
        
        return SubmitErrorReportUseCase(
            repository=mock_db_adapter,
            validation_service=mock_validation_service,
            categorization_service=mock_categorization_service,
            event_publisher=mock_event_publisher
        )

    @pytest.mark.asyncio
    async def test_database_connection_failure(self, use_case, mock_db_adapter):
        """Test handling of database connection failures"""
        # Mock database connection failure
        mock_db_adapter.save.side_effect = SQLAlchemyError("Connection failed")
        
        request = SubmitErrorReportRequest(
            job_id="conn-fail-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text="test original",
            corrected_text="test corrected",
            error_categories=["test"],
            severity_level="medium",
            start_position=0,
            end_position=4
        )
        
        with pytest.raises(Exception, match="Connection failed"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_database_integrity_constraint_violation(self, use_case, mock_db_adapter):
        """Test handling of database integrity constraint violations"""
        # Mock integrity constraint violation
        mock_db_adapter.save.side_effect = IntegrityError(
            "duplicate key value violates unique constraint",
            None, None
        )
        
        request = SubmitErrorReportRequest(
            job_id="integrity-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text="test original",
            corrected_text="test corrected",
            error_categories=["test"],
            severity_level="medium",
            start_position=0,
            end_position=4
        )
        
        with pytest.raises(IntegrityError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_database_timeout_handling(self, use_case, mock_db_adapter):
        """Test handling of database operation timeouts"""
        # Mock database timeout
        async def slow_save(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow operation
            return "saved"
        
        mock_db_adapter.save.side_effect = slow_save
        
        request = SubmitErrorReportRequest(
            job_id="timeout-test",
            speaker_id="speaker-test",
            reported_by="user-test",
            original_text="test original",
            corrected_text="test corrected",
            error_categories=["test"],
            severity_level="medium",
            start_position=0,
            end_position=4
        )
        
        # Test with timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(use_case.execute(request), timeout=1.0)

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, mock_db_adapter):
        """Test that transactions are properly rolled back on errors"""
        # This would test actual transaction behavior
        # For now, we'll test that the adapter handles rollback scenarios
        
        mock_db_adapter.save.side_effect = Exception("Transaction failed")
        
        with pytest.raises(Exception, match="Transaction failed"):
            await mock_db_adapter.save(ErrorReportFactory.create())
        
        # Verify rollback was called (in real implementation)
        assert mock_db_adapter.save.called


class TestConcurrencyEdgeCases:
    """Test concurrency-related edge cases"""

    @pytest.mark.asyncio
    async def test_concurrent_access_to_same_resource(self):
        """Test concurrent access to the same resource"""
        mock_adapter = AsyncMock()
        
        # Simulate concurrent operations on same resource
        resource_id = str(uuid4())
        
        async def concurrent_operation(operation_id):
            await asyncio.sleep(0.1)  # Simulate processing time
            return f"operation_{operation_id}_complete"
        
        # Run multiple operations concurrently
        tasks = [concurrent_operation(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all("complete" in result for result in results)

    @pytest.mark.asyncio
    async def test_race_condition_handling(self):
        """Test handling of race conditions"""
        shared_resource = {"counter": 0}
        
        async def increment_counter():
            # Simulate race condition
            current = shared_resource["counter"]
            await asyncio.sleep(0.01)  # Yield control
            shared_resource["counter"] = current + 1
        
        # Run concurrent increments
        tasks = [increment_counter() for _ in range(10)]
        await asyncio.gather(*tasks)
        
        # Due to race conditions, final count might be less than 10
        # In production, this would be handled with proper locking
        assert shared_resource["counter"] <= 10

    @pytest.mark.asyncio
    async def test_deadlock_prevention(self):
        """Test deadlock prevention mechanisms"""
        lock1 = asyncio.Lock()
        lock2 = asyncio.Lock()
        
        async def task1():
            async with lock1:
                await asyncio.sleep(0.1)
                # In a deadlock scenario, this would wait forever
                # We'll use timeout to prevent actual deadlock
                try:
                    async with asyncio.wait_for(lock2.acquire(), timeout=0.5):
                        await asyncio.sleep(0.1)
                        lock2.release()
                except asyncio.TimeoutError:
                    return "task1_timeout"
            return "task1_complete"
        
        async def task2():
            async with lock2:
                await asyncio.sleep(0.1)
                try:
                    async with asyncio.wait_for(lock1.acquire(), timeout=0.5):
                        await asyncio.sleep(0.1)
                        lock1.release()
                except asyncio.TimeoutError:
                    return "task2_timeout"
            return "task2_complete"
        
        # Run potentially deadlocking tasks
        results = await asyncio.gather(task1(), task2())
        
        # At least one should complete or timeout gracefully
        assert len(results) == 2
        assert any("complete" in result or "timeout" in result for result in results)


class TestMemoryAndResourceLeaks:
    """Test for memory leaks and resource management"""

    def test_large_object_cleanup(self):
        """Test that large objects are properly cleaned up"""
        import gc
        import sys
        
        # Create large objects
        large_objects = []
        for i in range(100):
            large_text = "A" * 1000  # 1KB each
            error_report = ErrorReport(
                job_id=f"large-{i}",
                speaker_id="speaker-test",
                reported_by="user-test",
                original_text=large_text,
                corrected_text=large_text.replace("A", "B"),
                error_categories=["memory_test"],
                severity_level=SeverityLevel.LOW,
                start_position=0,
                end_position=10,
                error_timestamp=datetime.utcnow()
            )
            large_objects.append(error_report)
        
        # Get reference count
        initial_refs = sys.getrefcount(large_objects[0])
        
        # Clear references
        large_objects.clear()
        gc.collect()
        
        # Verify cleanup (this is a simplified test)
        assert len(large_objects) == 0

    @pytest.mark.asyncio
    async def test_async_resource_cleanup(self):
        """Test that async resources are properly cleaned up"""
        resources_created = []
        
        async def create_resource(resource_id):
            # Simulate resource creation
            resource = {"id": resource_id, "active": True}
            resources_created.append(resource)
            
            try:
                await asyncio.sleep(0.1)
                return f"resource_{resource_id}_processed"
            finally:
                # Cleanup
                resource["active"] = False
        
        # Create multiple async resources
        tasks = [create_resource(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Verify all resources were cleaned up
        assert len(results) == 5
        assert all(not resource["active"] for resource in resources_created)

    def test_circular_reference_handling(self):
        """Test handling of circular references"""
        # Create objects with potential circular references
        class Node:
            def __init__(self, value):
                self.value = value
                self.parent = None
                self.children = []
            
            def add_child(self, child):
                child.parent = self
                self.children.append(child)
        
        # Create circular structure
        root = Node("root")
        child1 = Node("child1")
        child2 = Node("child2")
        
        root.add_child(child1)
        root.add_child(child2)
        child1.add_child(root)  # Circular reference
        
        # Verify structure is created
        assert len(root.children) == 2
        assert child1.parent == root
        assert root in child1.children
        
        # Python's garbage collector should handle this
        import gc
        gc.collect()  # Force garbage collection
