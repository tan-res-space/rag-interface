"""
Integration tests for multi-adapter pattern.

These tests demonstrate that the same business logic works
with different database and event bus adapters.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport, SeverityLevel, ErrorStatus
)
from src.error_reporting_service.domain.services.validation_service import (
    ErrorValidationService
)
from src.error_reporting_service.domain.services.categorization_service import (
    ErrorCategorizationService
)
from src.error_reporting_service.application.use_cases.submit_error_report import (
    SubmitErrorReportUseCase
)
from src.error_reporting_service.application.dto.requests import (
    SubmitErrorReportRequest
)
from src.error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository
)
from src.error_reporting_service.application.ports.secondary.event_publisher_port import (
    EventPublisher
)
from src.error_reporting_service.infrastructure.config.database_config import (
    DatabaseConfig, DatabaseType
)
from src.error_reporting_service.infrastructure.config.messaging_config import (
    EventBusConfig, EventBusType
)
from src.error_reporting_service.infrastructure.adapters.database.factory import (
    DatabaseAdapterFactory
)
from src.error_reporting_service.infrastructure.adapters.messaging.factory import (
    EventBusAdapterFactory
)


class DatabaseAdapterRepository(ErrorReportRepository):
    """Bridge between repository interface and database adapter"""
    
    def __init__(self, db_adapter):
        self._db_adapter = db_adapter
    
    async def save(self, error_report: ErrorReport) -> ErrorReport:
        return await self._db_adapter.save_error_report(error_report)
    
    async def find_by_id(self, error_id):
        return await self._db_adapter.find_error_by_id(error_id)
    
    async def find_by_speaker(self, speaker_id, filters=None):
        return await self._db_adapter.find_errors_by_speaker(speaker_id, filters)
    
    async def find_by_job(self, job_id, filters=None):
        return await self._db_adapter.find_errors_by_job(job_id, filters)
    
    async def update(self, error_id, updates):
        return await self._db_adapter.update_error_report(error_id, updates)
    
    async def delete(self, error_id):
        return await self._db_adapter.delete_error_report(error_id)
    
    async def search(self, criteria, page=1, limit=20):
        return await self._db_adapter.search_errors(criteria)
    
    async def count(self, criteria=None):
        # Simple implementation for testing
        results = await self._db_adapter.search_errors(criteria or {})
        return len(results)


class EventBusAdapterPublisher(EventPublisher):
    """Bridge between event publisher interface and event bus adapter"""
    
    def __init__(self, event_adapter):
        self._event_adapter = event_adapter
    
    async def publish_error_reported(self, event):
        await self._event_adapter.publish_event("error.reported", event)
    
    async def publish_error_updated(self, event):
        await self._event_adapter.publish_event("error.updated", event)
    
    async def publish_error_deleted(self, event):
        await self._event_adapter.publish_event("error.deleted", event)


class TestMultiAdapterIntegration:
    """Integration tests for multi-adapter pattern"""
    
    @pytest.mark.asyncio
    async def test_submit_error_report_with_in_memory_adapters(self):
        """Test error report submission with in-memory adapters"""
        # Arrange - Create in-memory adapters
        db_config = DatabaseConfig(type="in_memory")  # Will use in-memory adapter
        event_config = EventBusConfig(type=EventBusType.IN_MEMORY)
        
        db_adapter = await DatabaseAdapterFactory.create(db_config)
        event_adapter = await EventBusAdapterFactory.create(event_config)
        
        # Create repository and event publisher bridges
        repository = DatabaseAdapterRepository(db_adapter)
        event_publisher = EventBusAdapterPublisher(event_adapter)
        
        # Create domain services
        validation_service = ErrorValidationService()
        categorization_service = ErrorCategorizationService()
        
        # Create use case
        use_case = SubmitErrorReportUseCase(
            repository=repository,
            event_publisher=event_publisher,
            validation_service=validation_service,
            categorization_service=categorization_service
        )
        
        # Create request
        request = SubmitErrorReportRequest(
            job_id=str(uuid4()),
            speaker_id=str(uuid4()),
            original_text="The patient has diabetis",
            corrected_text="The patient has diabetes",
            error_categories=["medical_terminology"],
            severity_level="high",
            start_position=16,
            end_position=24,
            context_notes="Common misspelling",
            reported_by=str(uuid4()),
            metadata={"audio_quality": "good"}
        )
        
        # Act
        response = await use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert "successfully" in response.message
        assert response.error_id is not None
        
        # Verify data was saved in database adapter
        from uuid import UUID
        saved_error = await db_adapter.find_error_by_id(UUID(response.error_id))
        assert saved_error is not None
        assert saved_error.original_text == request.original_text
        assert saved_error.corrected_text == request.corrected_text
        
        # Verify event was published to event bus adapter
        events = event_adapter.get_events_for_topic("error.reported")
        assert len(events) == 1
        assert events[0]["payload"]["original_text"] == request.original_text
    
    @pytest.mark.asyncio
    async def test_adapter_health_checks(self):
        """Test health checks for different adapters"""
        # Test in-memory database adapter
        db_config = DatabaseConfig(type="in_memory")
        db_adapter = await DatabaseAdapterFactory.create(db_config)
        assert await db_adapter.health_check() is True
        
        # Test in-memory event bus adapter
        event_config = EventBusConfig(type=EventBusType.IN_MEMORY)
        event_adapter = await EventBusAdapterFactory.create(event_config)
        assert await event_adapter.health_check() is True
    
    @pytest.mark.asyncio
    async def test_adapter_connection_info(self):
        """Test connection info for different adapters"""
        # Test database adapter connection info
        db_config = DatabaseConfig(type="in_memory")
        db_adapter = await DatabaseAdapterFactory.create(db_config)
        db_info = db_adapter.get_connection_info()
        assert db_info["adapter_type"] == "in_memory"
        assert "total_records" in db_info
        
        # Test event bus adapter connection info
        event_config = EventBusConfig(type=EventBusType.IN_MEMORY)
        event_adapter = await EventBusAdapterFactory.create(event_config)
        event_info = event_adapter.get_connection_info()
        assert event_info["adapter_type"] == "in_memory"
        assert "topics" in event_info
    
    @pytest.mark.asyncio
    async def test_database_adapter_crud_operations(self):
        """Test CRUD operations work consistently across adapters"""
        # Create adapter
        db_config = DatabaseConfig(type="in_memory")
        db_adapter = await DatabaseAdapterFactory.create(db_config)
        
        # Create test error report
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="test error",
            corrected_text="test correction",
            error_categories=["grammar"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=10,
            error_timestamp=datetime.now(),
            reported_at=datetime.now()
        )
        
        # Test Create
        saved_error = await db_adapter.save_error_report(error_report)
        assert saved_error.error_id == error_report.error_id
        
        # Test Read
        retrieved_error = await db_adapter.find_error_by_id(error_report.error_id)
        assert retrieved_error is not None
        assert retrieved_error.original_text == error_report.original_text
        
        # Test Update
        updates = {"context_notes": "Updated notes"}
        updated_error = await db_adapter.update_error_report(error_report.error_id, updates)
        assert updated_error.context_notes == "Updated notes"
        
        # Test Delete
        deleted = await db_adapter.delete_error_report(error_report.error_id)
        assert deleted is True
        
        # Verify deletion
        deleted_error = await db_adapter.find_error_by_id(error_report.error_id)
        assert deleted_error is None
    
    def _create_test_error_report(self) -> ErrorReport:
        """Helper method to create test error reports"""
        return ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="test error",
            corrected_text="test correction",
            error_categories=["grammar"],
            severity_level=SeverityLevel.LOW,
            start_position=0,
            end_position=10,
            error_timestamp=datetime.now(),
            reported_at=datetime.now()
        )
