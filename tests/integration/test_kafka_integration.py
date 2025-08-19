"""
Integration tests for Kafka message queue operations.

These tests verify the integration between the application and Kafka,
including event publishing, serialization, and error handling.
Following TDD principles and Hexagonal Architecture patterns.
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any

from src.error_reporting_service.infrastructure.adapters.messaging.kafka_producer import (
    KafkaErrorEventPublisher
)
from src.error_reporting_service.domain.events.domain_events import (
    ErrorReportedEvent, ErrorUpdatedEvent, ErrorDeletedEvent
)
from src.error_reporting_service.infrastructure.config.settings import Settings
from tests.factories import ErrorReportedEventFactory


@pytest.mark.integration
@pytest.mark.kafka
class TestKafkaIntegration:
    """Integration tests for Kafka message queue operations"""
    
    @pytest.fixture
    def kafka_settings(self):
        """Create Kafka settings for testing"""
        return {
            "bootstrap_servers": ["localhost:9092"],
            "topic_prefix": "test_asr",
            "producer_config": {
                "acks": "all",
                "retries": 3,
                "compression_type": "snappy",
                "max_in_flight_requests_per_connection": 1
            }
        }
    
    @pytest.fixture
    def mock_kafka_producer(self):
        """Create mock Kafka producer"""
        producer = AsyncMock()
        producer.send = AsyncMock()
        producer.flush = AsyncMock()
        producer.close = AsyncMock()
        return producer
    
    @pytest.fixture
    def event_publisher(self, mock_kafka_producer, kafka_settings):
        """Create Kafka event publisher with mock producer"""
        return KafkaErrorEventPublisher(
            producer=mock_kafka_producer,
            settings=kafka_settings
        )
    
    @pytest.mark.asyncio
    async def test_publish_error_reported_event_success(self, event_publisher, mock_kafka_producer):
        """Test successful publishing of error reported event"""
        # Arrange
        event = ErrorReportedEventFactory.create()
        
        # Mock successful send
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        await event_publisher.publish_error_reported(event)
        
        # Assert
        mock_kafka_producer.send.assert_called_once()
        call_args = mock_kafka_producer.send.call_args
        
        # Verify topic
        assert call_args[0][0] == "test_asr.error.reported"
        
        # Verify message structure
        message = call_args[1]["value"]
        assert message["event_id"] == event.event_id
        assert message["event_type"] == "error.reported"
        assert message["data"]["error_id"] == event.error_id
        assert message["data"]["original_text"] == event.original_text
        assert message["data"]["corrected_text"] == event.corrected_text
    
    @pytest.mark.asyncio
    async def test_publish_error_updated_event_success(self, event_publisher, mock_kafka_producer):
        """Test successful publishing of error updated event"""
        # Arrange
        event = ErrorUpdatedEvent(
            event_id=str(uuid4()),
            correlation_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            error_id=str(uuid4()),
            changes={"status": "processed", "context_notes": "Updated notes"},
            updated_by=str(uuid4())
        )
        
        # Mock successful send
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        await event_publisher.publish_error_updated(event)
        
        # Assert
        mock_kafka_producer.send.assert_called_once()
        call_args = mock_kafka_producer.send.call_args
        
        # Verify topic
        assert call_args[0][0] == "test_asr.error.updated"
        
        # Verify message structure
        message = call_args[1]["value"]
        assert message["event_type"] == "error.updated"
        assert message["data"]["error_id"] == event.error_id
        assert message["data"]["changes"] == event.changes
    
    @pytest.mark.asyncio
    async def test_publish_error_deleted_event_success(self, event_publisher, mock_kafka_producer):
        """Test successful publishing of error deleted event"""
        # Arrange
        event = ErrorDeletedEvent(
            event_id=str(uuid4()),
            correlation_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            error_id=str(uuid4()),
            deleted_by=str(uuid4())
        )
        
        # Mock successful send
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        await event_publisher.publish_error_deleted(event)
        
        # Assert
        mock_kafka_producer.send.assert_called_once()
        call_args = mock_kafka_producer.send.call_args
        
        # Verify topic
        assert call_args[0][0] == "test_asr.error.deleted"
        
        # Verify message structure
        message = call_args[1]["value"]
        assert message["event_type"] == "error.deleted"
        assert message["data"]["error_id"] == event.error_id
        assert message["data"]["deleted_by"] == event.deleted_by
    
    @pytest.mark.asyncio
    async def test_publish_event_with_retry_on_failure(self, event_publisher, mock_kafka_producer):
        """Test event publishing with retry on failure"""
        # Arrange
        event = ErrorReportedEventFactory.create()
        
        # Mock initial failure then success
        mock_kafka_producer.send.side_effect = [
            Exception("Connection failed"),
            Exception("Timeout"),
            AsyncMock()  # Success on third try
        ]
        
        # Act
        await event_publisher.publish_error_reported(event)
        
        # Assert
        assert mock_kafka_producer.send.call_count == 3
    
    @pytest.mark.asyncio
    async def test_publish_event_max_retries_exceeded(self, event_publisher, mock_kafka_producer):
        """Test event publishing when max retries are exceeded"""
        # Arrange
        event = ErrorReportedEventFactory.create()
        
        # Mock persistent failure
        mock_kafka_producer.send.side_effect = Exception("Persistent connection failure")
        
        # Act & Assert
        with pytest.raises(Exception, match="Persistent connection failure"):
            await event_publisher.publish_error_reported(event)
        
        # Verify retry attempts
        assert mock_kafka_producer.send.call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_event_serialization_with_complex_metadata(self, event_publisher, mock_kafka_producer):
        """Test event serialization with complex metadata"""
        # Arrange
        complex_metadata = {
            "audio_quality": "excellent",
            "nested_data": {
                "recording_device": "microphone_a",
                "room_acoustics": "poor"
            },
            "technical_issues": ["static", "echo"],
            "timestamps": {
                "recording_start": "2023-01-01T10:00:00Z",
                "error_detected": "2023-01-01T10:05:30Z"
            }
        }
        
        event = ErrorReportedEventFactory.create(metadata=complex_metadata)
        
        # Mock successful send
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        await event_publisher.publish_error_reported(event)
        
        # Assert
        call_args = mock_kafka_producer.send.call_args
        message = call_args[1]["value"]
        
        # Verify complex metadata is properly serialized
        assert message["data"]["metadata"]["nested_data"]["recording_device"] == "microphone_a"
        assert len(message["data"]["metadata"]["technical_issues"]) == 2
        assert "recording_start" in message["data"]["metadata"]["timestamps"]
    
    @pytest.mark.asyncio
    async def test_event_ordering_with_partition_key(self, event_publisher, mock_kafka_producer):
        """Test event ordering using partition keys"""
        # Arrange
        speaker_id = str(uuid4())
        events = [
            ErrorReportedEventFactory.create(speaker_id=speaker_id)
            for _ in range(3)
        ]
        
        # Mock successful sends
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        for event in events:
            await event_publisher.publish_error_reported(event)
        
        # Assert
        assert mock_kafka_producer.send.call_count == 3
        
        # Verify all events use the same partition key (speaker_id)
        for call in mock_kafka_producer.send.call_args_list:
            partition_key = call[1].get("key")
            assert partition_key == speaker_id
    
    @pytest.mark.asyncio
    async def test_event_headers_and_metadata(self, event_publisher, mock_kafka_producer):
        """Test event headers and metadata are properly set"""
        # Arrange
        event = ErrorReportedEventFactory.create()
        
        # Mock successful send
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        await event_publisher.publish_error_reported(event)
        
        # Assert
        call_args = mock_kafka_producer.send.call_args
        headers = call_args[1].get("headers", {})
        
        # Verify standard headers
        assert "content-type" in headers
        assert headers["content-type"] == "application/json"
        assert "event-type" in headers
        assert headers["event-type"] == "error.reported"
        assert "event-version" in headers
        assert "correlation-id" in headers
    
    @pytest.mark.asyncio
    async def test_batch_event_publishing(self, event_publisher, mock_kafka_producer):
        """Test batch publishing of multiple events"""
        # Arrange
        events = ErrorReportedEventFactory.create_batch(5)
        
        # Mock successful sends
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        await event_publisher.publish_batch(events)
        
        # Assert
        assert mock_kafka_producer.send.call_count == 5
        mock_kafka_producer.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_event_compression_and_size_limits(self, event_publisher, mock_kafka_producer):
        """Test event compression and size limit handling"""
        # Arrange
        large_text = "x" * 50000  # Large text content
        event = ErrorReportedEventFactory.create(
            original_text=large_text,
            corrected_text=large_text.replace("x", "X", 1)
        )
        
        # Mock successful send
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        await event_publisher.publish_error_reported(event)
        
        # Assert
        call_args = mock_kafka_producer.send.call_args
        message = call_args[1]["value"]
        
        # Verify message was sent (compression should handle large size)
        assert len(message["data"]["original_text"]) == 50000
        mock_kafka_producer.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_producer_health_check(self, event_publisher, mock_kafka_producer):
        """Test Kafka producer health check functionality"""
        # Arrange
        mock_kafka_producer.list_topics = AsyncMock(return_value={"test_asr.error.reported"})
        
        # Act
        is_healthy = await event_publisher.health_check()
        
        # Assert
        assert is_healthy is True
        mock_kafka_producer.list_topics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_producer_health_check_failure(self, event_publisher, mock_kafka_producer):
        """Test Kafka producer health check failure"""
        # Arrange
        mock_kafka_producer.list_topics = AsyncMock(side_effect=Exception("Kafka unavailable"))
        
        # Act
        is_healthy = await event_publisher.health_check()
        
        # Assert
        assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, event_publisher, mock_kafka_producer):
        """Test graceful shutdown of Kafka producer"""
        # Arrange
        events = ErrorReportedEventFactory.create_batch(3)
        
        # Mock pending sends
        pending_futures = [AsyncMock() for _ in range(3)]
        mock_kafka_producer.send.side_effect = pending_futures
        
        # Act
        # Start publishing events
        publish_tasks = [
            event_publisher.publish_error_reported(event)
            for event in events
        ]
        
        # Initiate shutdown
        await event_publisher.shutdown()
        
        # Assert
        mock_kafka_producer.flush.assert_called()
        mock_kafka_producer.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_event_deduplication(self, event_publisher, mock_kafka_producer):
        """Test event deduplication based on event ID"""
        # Arrange
        event = ErrorReportedEventFactory.create()
        
        # Mock successful sends
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act - Publish same event twice
        await event_publisher.publish_error_reported(event)
        await event_publisher.publish_error_reported(event)
        
        # Assert - Should only send once due to deduplication
        assert mock_kafka_producer.send.call_count == 1
    
    @pytest.mark.asyncio
    async def test_topic_auto_creation_configuration(self, kafka_settings):
        """Test topic auto-creation configuration"""
        # Arrange
        kafka_settings["auto_create_topics"] = True
        
        with patch('aiokafka.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer
            
            # Act
            event_publisher = KafkaErrorEventPublisher(
                producer=mock_producer,
                settings=kafka_settings
            )
            
            # Assert
            # Verify producer was configured with auto-creation enabled
            assert event_publisher.auto_create_topics is True
    
    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self, event_publisher, mock_kafka_producer):
        """Test performance metrics collection during event publishing"""
        # Arrange
        events = ErrorReportedEventFactory.create_batch(10)
        
        # Mock successful sends with varying latencies
        mock_kafka_producer.send.return_value = AsyncMock()
        
        # Act
        start_time = datetime.utcnow()
        for event in events:
            await event_publisher.publish_error_reported(event)
        end_time = datetime.utcnow()
        
        # Assert
        total_time = (end_time - start_time).total_seconds()
        assert total_time < 5.0  # Should complete within 5 seconds
        
        # Verify metrics are collected
        metrics = event_publisher.get_metrics()
        assert metrics["events_published"] == 10
        assert metrics["average_latency"] > 0
        assert metrics["success_rate"] == 1.0
