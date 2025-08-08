# Error Reporting Service (ERS) - System Architecture Design

**Document Version:** 1.0  
**Date:** August 7, 2025  
**Author:** Architecture Team  
**Based on:** ASR Error Reporting PRD - Error Reporting Service Component  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [ERS Hexagonal Architecture](#ers-hexagonal-architecture)
3. [Component Design](#component-design)
4. [API Specifications](#api-specifications)
5. [Data Architecture](#data-architecture)
6. [Implementation Guidelines](#implementation-guidelines)
7. [Testing Strategy](#testing-strategy)

---

## 1. Executive Summary

### 1.1 Service Overview

The Error Reporting Service (ERS) is the foundational component of the ASR Error Reporting and Correction System, responsible for capturing, validating, and processing error reports from QA personnel. Built using **Hexagonal Architecture (Ports and Adapters)** pattern with **Python + FastAPI**, ERS ensures clean separation between business logic and external dependencies while maintaining high testability and maintainability.

### 1.2 Key Responsibilities

- **Error Capture**: Accept and validate error reports from QA personnel
- **Data Validation**: Ensure data integrity and business rule compliance
- **Event Publishing**: Notify other services of error events for downstream processing
- **Audit Trail**: Maintain complete audit logs for compliance and debugging

### 1.3 Architecture Principles

1. **Hexagonal Architecture**: Clear separation between business logic (core), interfaces (ports), and external adapters
2. **Domain-Driven Design**: Business logic organized around error reporting domain concepts
3. **Event-Driven Communication**: Loose coupling through asynchronous event messaging
4. **SOLID Principles**: Maintainable, testable, and debuggable code structure
5. **Test-Driven Development**: Comprehensive test coverage with isolated unit tests

### 1.4 Technology Stack

- **Backend Framework**: Python 3.11+ with FastAPI for high-performance async API development
- **Data Validation**: Pydantic 2.0+ for robust data modeling and validation
- **Database Options** (Configurable via Adapter Pattern):
  - **PostgreSQL** 15+ with SQLAlchemy 2.0+ async ORM (Primary)
  - **SQL Server** with SQLAlchemy async support
  - **MongoDB** with Motor async driver
- **Message Queue Options** (Configurable via Adapter Pattern):
  - **Apache Kafka** with aiokafka (Primary)
  - **Azure Service Bus** with azure-servicebus
  - **AWS SQS** with aioboto3
  - **RabbitMQ** with aio-pika
- **Testing**: pytest with pytest-asyncio for comprehensive testing
- **Monitoring**: OpenTelemetry for observability and distributed tracing

---

## 2. ERS Hexagonal Architecture

### 2.1 ERS Architecture Diagram

```mermaid
graph TB
    %% External Actors
    subgraph "External Actors"
        QA[QA Personnel]
        ADMIN[System Admin]
    end

    %% External Systems
    subgraph "External Systems"
        RIS[RAG Integration Service]
        UMS[User Management Service]
        NOTIFICATION[Notification System]
    end

    %% API Gateway
    subgraph "Infrastructure Layer"
        API_GW[API Gateway<br/>Authentication<br/>Rate Limiting<br/>Request Routing]
    end

    %% Error Reporting Service - Hexagonal Architecture
    subgraph "Error Reporting Service (ERS)"
        %% Ports (Interfaces)
        subgraph "PORTS [Primary & Secondary Ports]"
            HTTP_PORT[HTTP API Port<br/>• Submit Error Report<br/>• Query Error Reports<br/>• Update Error Status]
            EVENT_PORT[Event Publishing Port<br/>• Error Reported Events<br/>• Error Updated Events<br/>• Error Deleted Events]
            VALIDATION_PORT[Validation Port<br/>• Business Rule Validation<br/>• Data Integrity Checks<br/>• Speaker/Job Validation]
            PERSISTENCE_PORT[Persistence Port<br/>• Error Storage<br/>• Audit Trail<br/>• Transaction Management]
        end
        
        %% Core Business Logic
        subgraph "CORE [Business Logic Domain]"
            DOMAIN[Error Report Domain<br/>• Error Entity<br/>• Validation Rules<br/>• Business Logic<br/>• Domain Events]
            USE_CASES[Use Cases<br/>• Submit Error Report<br/>• Validate Error Data<br/>• Process Error Context<br/>• Generate Audit Trail]
            SERVICES[Domain Services<br/>• Error Categorization<br/>• Severity Assessment<br/>• Context Processing<br/>• Quality Validation]
        end
        
        %% Adapters (External Integrations)
        subgraph "ADAPTERS [Infrastructure Adapters]"
            REST_ADAPTER[REST API Adapter<br/>FastAPI Controllers<br/>Request/Response Handling<br/>HTTP Status Management]

            subgraph "Event Bus Adapters"
                EVENT_INTERFACE[IEventBusAdapter<br/>Abstract Interface]
                KAFKA_ADAPTER[Kafka Adapter]
                AZURE_SB_ADAPTER[Azure Service Bus Adapter]
                AWS_SQS_ADAPTER[AWS SQS Adapter]
                RABBITMQ_ADAPTER[RabbitMQ Adapter]
            end

            subgraph "Database Adapters"
                DB_INTERFACE[IDatabaseAdapter<br/>Abstract Interface]
                POSTGRES_ADAPTER[PostgreSQL Adapter<br/>SQLAlchemy]
                SQLSERVER_ADAPTER[SQL Server Adapter<br/>SQLAlchemy]
                MONGODB_ADAPTER[MongoDB Adapter<br/>Motor]
            end

            EXTERNAL_ADAPTER[External Service Adapter<br/>Speaker Validation<br/>Job Verification<br/>User Authentication]
        end
    end

    %% Data Layer
    subgraph "Data Layer"
        RDB[(PostgreSQL<br/>Error Reports<br/>Audit Logs<br/>Metadata)]
        EVENT_BUS[(Kafka Event Bus<br/>Error Events<br/>Async Processing)]
        CACHE[(Redis Cache<br/>Validation Cache<br/>Session Data)]
    end

    %% Connections - External to API Gateway
    QA --> API_GW
    ADMIN --> API_GW

    %% API Gateway to Ports
    API_GW --> HTTP_PORT

    %% Port to Core connections
    HTTP_PORT --> USE_CASES
    EVENT_PORT --> USE_CASES
    VALIDATION_PORT --> USE_CASES
    PERSISTENCE_PORT --> USE_CASES

    %% Use Cases to Domain
    USE_CASES --> DOMAIN
    USE_CASES --> SERVICES

    %% Core to Adapter Interface connections
    DOMAIN --> REST_ADAPTER
    DOMAIN --> EVENT_INTERFACE
    DOMAIN --> DB_INTERFACE
    DOMAIN --> EXTERNAL_ADAPTER

    %% Abstract Interface to Concrete Adapter connections
    EVENT_INTERFACE --> KAFKA_ADAPTER
    EVENT_INTERFACE --> AZURE_SB_ADAPTER
    EVENT_INTERFACE --> AWS_SQS_ADAPTER
    EVENT_INTERFACE --> RABBITMQ_ADAPTER

    DB_INTERFACE --> POSTGRES_ADAPTER
    DB_INTERFACE --> SQLSERVER_ADAPTER
    DB_INTERFACE --> MONGODB_ADAPTER

    %% Adapter to External System connections
    REST_ADAPTER --> API_GW
    KAFKA_ADAPTER --> EVENT_BUS
    POSTGRES_ADAPTER --> RDB
    EXTERNAL_ADAPTER --> UMS
    EXTERNAL_ADAPTER --> CACHE

    %% Event Bus to External Services
    EVENT_BUS -.->|Error Reported Event| RIS
    EVENT_BUS -.->|Notification Event| NOTIFICATION

    %% Styling
    classDef coreLogic fill:#e8f5e8,stroke:#4caf50,stroke-width:3px
    classDef ports fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef adapters fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    classDef external fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px

    class CORE coreLogic
    class PORTS ports
    class ADAPTERS adapters
    class RDB,EVENT_BUS,CACHE database
    class RIS,UMS,NOTIFICATION external
```

### 2.2 Architecture Benefits

1. **Independent Development**: Business logic isolated from external dependencies
2. **High Testability**: Core domain can be tested without external systems
3. **Flexibility**: Easy to swap adapters without affecting business logic
4. **Maintainability**: Clear separation of concerns and well-defined boundaries
5. **Scalability**: Stateless design enables horizontal scaling

---

## 3. Component Design

### 3.1 Core Domain Components

#### 3.1.1 Error Report Entity
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    ARCHIVED = "archived"

class ErrorReport(BaseModel):
    """Core Error Report Entity - Domain Model"""
    error_id: UUID
    job_id: UUID
    speaker_id: UUID
    reported_by: UUID
    original_text: str = Field(..., min_length=1, max_length=5000)
    corrected_text: str = Field(..., min_length=1, max_length=5000)
    error_categories: List[str] = Field(..., min_items=1)
    severity_level: SeverityLevel
    start_position: int = Field(..., ge=0)
    end_position: int = Field(..., ge=0)
    context_notes: Optional[str] = Field(None, max_length=2000)
    error_timestamp: datetime
    reported_at: datetime
    status: ErrorStatus = ErrorStatus.PENDING
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('end_position')
    def validate_position_range(cls, v, values):
        if 'start_position' in values and v <= values['start_position']:
            raise ValueError('end_position must be greater than start_position')
        return v

    @validator('corrected_text')
    def validate_correction_differs(cls, v, values):
        if 'original_text' in values and v == values['original_text']:
            raise ValueError('corrected_text must differ from original_text')
        return v
```

#### 3.1.2 Domain Services
```python
from abc import ABC, abstractmethod

class ErrorValidationService:
    """Domain service for error validation business logic"""
    
    def validate_error_categories(self, categories: List[str]) -> bool:
        """Validate error categories against business rules"""
        valid_categories = {
            "pronunciation", "medical_terminology", "grammar", 
            "context", "speaker_specific", "audio_quality"
        }
        return all(cat in valid_categories for cat in categories)
    
    def assess_severity(self, error_report: ErrorReport) -> SeverityLevel:
        """Business logic for severity assessment"""
        if "medical_terminology" in error_report.error_categories:
            return SeverityLevel.HIGH
        if len(error_report.original_text) > 100:
            return SeverityLevel.MEDIUM
        return SeverityLevel.LOW
    
    def validate_context_integrity(self, error_report: ErrorReport) -> bool:
        """Validate error context and position integrity"""
        text_length = len(error_report.original_text)
        return (
            error_report.start_position < text_length and
            error_report.end_position <= text_length and
            error_report.start_position >= 0
        )

class ErrorCategorizationService:
    """Domain service for error categorization logic"""

    def suggest_categories(self, original_text: str, corrected_text: str) -> List[str]:
        """AI-powered category suggestion based on text analysis"""
        # Implementation would include ML-based categorization
        pass

    def validate_category_combinations(self, categories: List[str]) -> bool:
        """Validate that category combinations make business sense"""
        # Business rules for valid category combinations
        pass
```

### 3.2 Use Cases (Application Layer)

#### 3.2.1 Submit Error Report Use Case
```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class SubmitErrorReportRequest:
    job_id: str
    speaker_id: str
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: str
    start_position: int
    end_position: int
    context_notes: Optional[str]
    reported_by: str
    metadata: Dict[str, Any]

@dataclass
class SubmitErrorReportResponse:
    error_id: str
    status: str
    message: str
    validation_warnings: List[str]

class ErrorReportRepository(Protocol):
    """Repository interface for error report persistence"""
    async def save(self, error_report: ErrorReport) -> ErrorReport:
        ...

    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        ...

    async def find_by_speaker(self, speaker_id: UUID) -> List[ErrorReport]:
        ...

class EventPublisher(Protocol):
    """Event publishing interface"""
    async def publish_error_reported(self, event: ErrorReportedEvent) -> None:
        ...

class SubmitErrorReportUseCase:
    """Use case for submitting error reports"""

    def __init__(
        self,
        repository: ErrorReportRepository,
        event_publisher: EventPublisher,
        validation_service: ErrorValidationService,
        categorization_service: ErrorCategorizationService
    ):
        self._repository = repository
        self._event_publisher = event_publisher
        self._validation_service = validation_service
        self._categorization_service = categorization_service

    async def execute(self, request: SubmitErrorReportRequest) -> SubmitErrorReportResponse:
        """Execute the submit error report use case"""

        # 1. Create domain entity
        error_report = ErrorReport(
            error_id=UUID4(),
            job_id=UUID(request.job_id),
            speaker_id=UUID(request.speaker_id),
            reported_by=UUID(request.reported_by),
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            error_categories=request.error_categories,
            severity_level=SeverityLevel(request.severity_level),
            start_position=request.start_position,
            end_position=request.end_position,
            context_notes=request.context_notes,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow(),
            metadata=request.metadata
        )

        # 2. Validate business rules
        if not self._validation_service.validate_error_categories(error_report.error_categories):
            raise ValueError("Invalid error categories")

        if not self._validation_service.validate_context_integrity(error_report):
            raise ValueError("Invalid error context or position")

        # 3. Persist error report
        saved_error = await self._repository.save(error_report)

        # 4. Publish domain event
        event = ErrorReportedEvent(
            error_id=str(saved_error.error_id),
            speaker_id=str(saved_error.speaker_id),
            job_id=str(saved_error.job_id),
            original_text=saved_error.original_text,
            corrected_text=saved_error.corrected_text,
            categories=saved_error.error_categories,
            severity=saved_error.severity_level.value,
            timestamp=saved_error.reported_at
        )

        await self._event_publisher.publish_error_reported(event)

        return SubmitErrorReportResponse(
            error_id=str(saved_error.error_id),
            status="success",
            message="Error report submitted successfully",
            validation_warnings=[]
        )
```

### 3.3 Port Interfaces

#### 3.3.1 Primary Ports (Driving Adapters)
```python
from abc import ABC, abstractmethod

class ErrorReportingPort(ABC):
    """Primary port for error reporting operations"""

    @abstractmethod
    async def submit_error_report(self, request: SubmitErrorReportRequest) -> SubmitErrorReportResponse:
        """Submit a new error report"""
        pass

    @abstractmethod
    async def get_error_report(self, error_id: str) -> ErrorReport:
        """Retrieve error report by ID"""
        pass

    @abstractmethod
    async def update_error_report(self, error_id: str, updates: Dict[str, Any]) -> ErrorReport:
        """Update existing error report"""
        pass

    @abstractmethod
    async def get_errors_by_speaker(self, speaker_id: str, filters: Optional[Dict] = None) -> List[ErrorReport]:
        """Get all errors for a specific speaker"""
        pass

    @abstractmethod
    async def search_errors(self, query: Dict[str, Any]) -> List[ErrorReport]:
        """Search errors with complex criteria"""
        pass

#### 3.3.2 Secondary Ports (Driven Adapters)
class ValidationPort(ABC):
    """Secondary port for validation operations"""

    @abstractmethod
    async def validate_speaker_exists(self, speaker_id: str) -> bool:
        """Validate that speaker exists in the system"""
        pass

    @abstractmethod
    async def validate_job_exists(self, job_id: str) -> bool:
        """Validate that job exists in the system"""
        pass

    @abstractmethod
    async def validate_user_permissions(self, user_id: str, operation: str) -> bool:
        """Validate user has permissions for operation"""
        pass

class EventPublishingPort(ABC):
    """Secondary port for event publishing"""

    @abstractmethod
    async def publish_error_reported(self, event: ErrorReportedEvent) -> None:
        """Publish error reported event"""
        pass

    @abstractmethod
    async def publish_error_updated(self, event: ErrorUpdatedEvent) -> None:
        """Publish error updated event"""
        pass

### 3.4 Abstract Adapter Interfaces

#### 3.4.1 Database Adapter Interface
```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

class IDatabaseAdapter(ABC):
    """Abstract interface for database operations - technology agnostic"""

    @abstractmethod
    async def save_error_report(self, error_report: ErrorReport) -> ErrorReport:
        """Save error report to database"""
        pass

    @abstractmethod
    async def find_error_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find error report by ID"""
        pass

    @abstractmethod
    async def find_errors_by_speaker(self, speaker_id: UUID, filters: Optional[Dict] = None) -> List[ErrorReport]:
        """Find all error reports for a speaker"""
        pass

    @abstractmethod
    async def update_error_report(self, error_id: UUID, updates: Dict[str, Any]) -> ErrorReport:
        """Update existing error report"""
        pass

    @abstractmethod
    async def delete_error_report(self, error_id: UUID) -> bool:
        """Delete error report"""
        pass

    @abstractmethod
    async def search_errors(self, query: Dict[str, Any]) -> List[ErrorReport]:
        """Search errors with complex criteria"""
        pass

    @abstractmethod
    async def begin_transaction(self) -> Any:
        """Begin database transaction"""
        pass

    @abstractmethod
    async def commit_transaction(self, transaction: Any) -> None:
        """Commit database transaction"""
        pass

    @abstractmethod
    async def rollback_transaction(self, transaction: Any) -> None:
        """Rollback database transaction"""
        pass

#### 3.4.2 Event Bus Adapter Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class MessageDeliveryMode(str, Enum):
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"

class EventMetadata(BaseModel):
    correlation_id: Optional[str] = None
    delivery_mode: MessageDeliveryMode = MessageDeliveryMode.AT_LEAST_ONCE
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    headers: Dict[str, str] = Field(default_factory=dict)

class IEventBusAdapter(ABC):
    """Abstract interface for event bus operations - messaging system agnostic"""

    @abstractmethod
    async def publish_event(
        self,
        topic: str,
        event: BaseEvent,
        metadata: Optional[EventMetadata] = None
    ) -> bool:
        """Publish event to specified topic"""
        pass

    @abstractmethod
    async def subscribe_to_topic(
        self,
        topic: str,
        handler: callable,
        consumer_group: Optional[str] = None
    ) -> None:
        """Subscribe to topic with event handler"""
        pass

    @abstractmethod
    async def create_topic(self, topic: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Create topic if it doesn't exist"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if event bus is healthy"""
        pass

    @abstractmethod
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for monitoring"""
        pass

### 3.5 Concrete Database Adapter Implementations

#### 3.5.1 PostgreSQL Adapter Implementation
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any

class PostgreSQLAdapter(IDatabaseAdapter):
    """PostgreSQL implementation of database adapter"""

    def __init__(self, connection_string: str):
        self.engine = create_async_engine(connection_string)
        self.session_factory = async_sessionmaker(self.engine)

    async def save_error_report(self, error_report: ErrorReport) -> ErrorReport:
        """Save error report to PostgreSQL"""
        async with self.session_factory() as session:
            model = ErrorReportModel(
                error_id=error_report.error_id,
                job_id=error_report.job_id,
                speaker_id=error_report.speaker_id,
                reported_by=error_report.reported_by,
                original_text=error_report.original_text,
                corrected_text=error_report.corrected_text,
                error_categories=error_report.error_categories,
                severity_level=error_report.severity_level.value,
                start_position=error_report.start_position,
                end_position=error_report.end_position,
                context_notes=error_report.context_notes,
                error_timestamp=error_report.error_timestamp,
                reported_at=error_report.reported_at,
                status=error_report.status.value,
                metadata=error_report.metadata
            )

            session.add(model)
            await session.commit()
            await session.refresh(model)

            return self._model_to_entity(model)

    async def find_error_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find error report by ID in PostgreSQL"""
        async with self.session_factory() as session:
            stmt = select(ErrorReportModel).where(ErrorReportModel.error_id == error_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            return self._model_to_entity(model) if model else None

    async def begin_transaction(self) -> AsyncSession:
        """Begin PostgreSQL transaction"""
        session = self.session_factory()
        await session.begin()
        return session

    async def commit_transaction(self, transaction: AsyncSession) -> None:
        """Commit PostgreSQL transaction"""
        await transaction.commit()
        await transaction.close()

    async def rollback_transaction(self, transaction: AsyncSession) -> None:
        """Rollback PostgreSQL transaction"""
        await transaction.rollback()
        await transaction.close()

#### 3.5.2 MongoDB Adapter Implementation
```python
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

class MongoDBAdapter(IDatabaseAdapter):
    """MongoDB implementation of database adapter"""

    def __init__(self, connection_string: str, database_name: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.database: AsyncIOMotorDatabase = self.client[database_name]
        self.collection = self.database.error_reports

    async def save_error_report(self, error_report: ErrorReport) -> ErrorReport:
        """Save error report to MongoDB"""
        document = {
            "_id": str(error_report.error_id),
            "job_id": str(error_report.job_id),
            "speaker_id": str(error_report.speaker_id),
            "reported_by": str(error_report.reported_by),
            "original_text": error_report.original_text,
            "corrected_text": error_report.corrected_text,
            "error_categories": error_report.error_categories,
            "severity_level": error_report.severity_level.value,
            "start_position": error_report.start_position,
            "end_position": error_report.end_position,
            "context_notes": error_report.context_notes,
            "error_timestamp": error_report.error_timestamp,
            "reported_at": error_report.reported_at,
            "status": error_report.status.value,
            "metadata": error_report.metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await self.collection.insert_one(document)
        return error_report

    async def find_error_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find error report by ID in MongoDB"""
        document = await self.collection.find_one({"_id": str(error_id)})

        return self._document_to_entity(document) if document else None

    async def find_errors_by_speaker(self, speaker_id: UUID, filters: Optional[Dict] = None) -> List[ErrorReport]:
        """Find all error reports for a speaker in MongoDB"""
        query = {"speaker_id": str(speaker_id)}

        if filters:
            if "severity_level" in filters:
                query["severity_level"] = filters["severity_level"]
            if "status" in filters:
                query["status"] = filters["status"]
            if "categories" in filters:
                query["error_categories"] = {"$in": filters["categories"]}

        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)

        return [self._document_to_entity(doc) for doc in documents]

    async def begin_transaction(self) -> Any:
        """Begin MongoDB transaction"""
        session = await self.client.start_session()
        session.start_transaction()
        return session

    async def commit_transaction(self, transaction: Any) -> None:
        """Commit MongoDB transaction"""
        await transaction.commit_transaction()
        await transaction.end_session()

    async def rollback_transaction(self, transaction: Any) -> None:
        """Rollback MongoDB transaction"""
        await transaction.abort_transaction()
        await transaction.end_session()

    def _document_to_entity(self, document: Dict) -> ErrorReport:
        """Convert MongoDB document to domain entity"""
        return ErrorReport(
            error_id=UUID(document["_id"]),
            job_id=UUID(document["job_id"]),
            speaker_id=UUID(document["speaker_id"]),
            reported_by=UUID(document["reported_by"]),
            original_text=document["original_text"],
            corrected_text=document["corrected_text"],
            error_categories=document["error_categories"],
            severity_level=SeverityLevel(document["severity_level"]),
            start_position=document["start_position"],
            end_position=document["end_position"],
            context_notes=document.get("context_notes"),
            error_timestamp=document["error_timestamp"],
            reported_at=document["reported_at"],
            status=ErrorStatus(document["status"]),
            metadata=document.get("metadata", {})
        )

### 3.6 Concrete Event Bus Adapter Implementations

#### 3.6.1 Kafka Adapter Implementation
```python
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from typing import Dict, Any, Optional

class KafkaAdapter(IEventBusAdapter):
    """Apache Kafka implementation of event bus adapter"""

    def __init__(self, bootstrap_servers: str, client_id: str = "ers-service"):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.producer = None
        self.consumers = {}

    async def publish_event(
        self,
        topic: str,
        event: BaseEvent,
        metadata: Optional[EventMetadata] = None
    ) -> bool:
        """Publish event to Kafka topic"""
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()

        try:
            event_data = event.dict()
            if metadata:
                event_data["_metadata"] = metadata.dict()

            await self.producer.send_and_wait(topic, event_data)
            return True
        except Exception as e:
            # Log error
            return False

    async def subscribe_to_topic(
        self,
        topic: str,
        handler: callable,
        consumer_group: Optional[str] = None
    ) -> None:
        """Subscribe to Kafka topic with event handler"""
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=consumer_group or f"{self.client_id}-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        await consumer.start()
        self.consumers[topic] = consumer

        try:
            async for message in consumer:
                await handler(message.value)
        finally:
            await consumer.stop()

    async def health_check(self) -> bool:
        """Check Kafka cluster health"""
        try:
            if not self.producer:
                test_producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    client_id=f"{self.client_id}-health"
                )
                await test_producer.start()
                await test_producer.stop()
            return True
        except Exception:
            return False

#### 3.6.2 Azure Service Bus Adapter Implementation
```python
from azure.servicebus.aio import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
import json

class AzureServiceBusAdapter(IEventBusAdapter):
    """Azure Service Bus implementation of event bus adapter"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.client = ServiceBusClient.from_connection_string(connection_string)
        self.senders = {}
        self.receivers = {}

    async def publish_event(
        self,
        topic: str,
        event: BaseEvent,
        metadata: Optional[EventMetadata] = None
    ) -> bool:
        """Publish event to Service Bus topic"""
        try:
            if topic not in self.senders:
                self.senders[topic] = self.client.get_topic_sender(topic_name=topic)

            sender = self.senders[topic]

            event_data = event.dict()
            if metadata:
                event_data["_metadata"] = metadata.dict()

            message = ServiceBusMessage(
                body=json.dumps(event_data),
                content_type="application/json"
            )

            if metadata and metadata.correlation_id:
                message.correlation_id = metadata.correlation_id

            await sender.send_messages(message)
            return True
        except Exception as e:
            # Log error
            return False

    async def subscribe_to_topic(
        self,
        topic: str,
        handler: callable,
        consumer_group: Optional[str] = None
    ) -> None:
        """Subscribe to Service Bus topic with event handler"""
        subscription_name = consumer_group or "default-subscription"

        receiver = self.client.get_subscription_receiver(
            topic_name=topic,
            subscription_name=subscription_name
        )

        self.receivers[f"{topic}-{subscription_name}"] = receiver

        async with receiver:
            async for message in receiver:
                try:
                    event_data = json.loads(str(message))
                    await handler(event_data)
                    await receiver.complete_message(message)
                except Exception as e:
                    # Log error and abandon message
                    await receiver.abandon_message(message)

#### 3.6.3 AWS SQS Adapter Implementation
```python
import aioboto3
import json
from typing import Dict, Any, Optional

class AWSSQSAdapter(IEventBusAdapter):
    """AWS SQS implementation of event bus adapter"""

    def __init__(self, region_name: str, access_key_id: str, secret_access_key: str):
        self.region_name = region_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session = aioboto3.Session()
        self.queue_urls = {}

    async def publish_event(
        self,
        topic: str,
        event: BaseEvent,
        metadata: Optional[EventMetadata] = None
    ) -> bool:
        """Publish event to SQS queue"""
        try:
            async with self.session.client(
                'sqs',
                region_name=self.region_name,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key
            ) as sqs:

                if topic not in self.queue_urls:
                    response = await sqs.get_queue_url(QueueName=topic)
                    self.queue_urls[topic] = response['QueueUrl']

                event_data = event.dict()
                if metadata:
                    event_data["_metadata"] = metadata.dict()

                message_attributes = {}
                if metadata and metadata.correlation_id:
                    message_attributes['CorrelationId'] = {
                        'StringValue': metadata.correlation_id,
                        'DataType': 'String'
                    }

                await sqs.send_message(
                    QueueUrl=self.queue_urls[topic],
                    MessageBody=json.dumps(event_data),
                    MessageAttributes=message_attributes
                )
                return True
        except Exception as e:
            # Log error
            return False

    async def health_check(self) -> bool:
        """Check SQS service health"""
        try:
            async with self.session.client(
                'sqs',
                region_name=self.region_name,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key
            ) as sqs:
                await sqs.list_queues()
                return True
        except Exception:
            return False
```
```
```

---

## 4. API Specifications

### 4.1 Error Reporting API Workflow

```mermaid
sequenceDiagram
    participant QA as QA User
    participant UI as Error Reporting UI
    participant API as API Gateway
    participant ERS as Error Reporting Service
    participant DB as PostgreSQL
    participant EVENT as Event Bus
    participant RIS as RAG Integration Service

    QA->>UI: Select error text and provide correction
    UI->>UI: Validate input data locally
    UI->>API: POST /api/v1/errors/report

    API->>API: Authenticate user token
    API->>API: Rate limit check
    API->>ERS: Forward error report request

    ERS->>ERS: Validate business rules
    ERS->>DB: Validate speaker and job IDs
    DB-->>ERS: Return validation results

    alt Validation successful
        ERS->>DB: Begin transaction
        ERS->>DB: Save error report
        ERS->>DB: Create audit log entry
        ERS->>DB: Commit transaction
        DB-->>ERS: Confirm persistence

        ERS->>EVENT: Publish ErrorReportedEvent
        EVENT-->>ERS: Confirm event published

        ERS-->>API: Return 201 Created with error_id
        API-->>UI: Return success response
        UI-->>QA: Display success confirmation

        EVENT->>RIS: Process error for vector embedding
        RIS-->>EVENT: Acknowledge processing

    else Validation failed
        ERS-->>API: Return 400 Bad Request
        API-->>UI: Return validation errors
        UI-->>QA: Display error messages with corrections
    end

    Note over QA,RIS: Error successfully captured and queued for ML processing
```

### 4.2 REST API Endpoints

#### 4.2.1 Submit Error Report
```http
POST /api/v1/errors/report
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "speaker_id": "550e8400-e29b-41d4-a716-446655440001",
  "original_text": "The patient has a history of diabetis",
  "corrected_text": "The patient has a history of diabetes",
  "error_categories": ["medical_terminology", "spelling"],
  "severity_level": "high",
  "start_position": 32,
  "end_position": 40,
  "context_notes": "Common misspelling of diabetes",
  "metadata": {
    "audio_quality": "good",
    "background_noise": "low",
    "confidence_score": 0.95
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "error_id": "550e8400-e29b-41d4-a716-446655440002",
    "status": "pending",
    "message": "Error report submitted successfully"
  },
  "timestamp": "2025-08-07T10:30:00Z",
  "request_id": "req_123456789"
}
```

#### 4.2.2 Get Error Report
```http
GET /api/v1/errors/{error_id}
Authorization: Bearer {jwt_token}
```

#### 4.2.3 Update Error Report
```http
PUT /api/v1/errors/{error_id}
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "severity_level": "critical",
  "context_notes": "Updated context information"
}
```

#### 4.2.4 Search Error Reports
```http
GET /api/v1/errors/search?speaker_id={speaker_id}&category=medical_terminology&severity=high&page=1&limit=20
Authorization: Bearer {jwt_token}
```

### 4.3 Event Schema Definitions

#### 4.3.1 Error Reported Event
```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any

class ErrorReportedEvent(BaseModel):
    """Event published when a new error is reported"""
    event_id: str
    event_type: str = "error.reported"
    version: str = "1.0"
    timestamp: datetime
    source: str = "error-reporting-service"
    correlation_id: str

    # Event payload
    error_id: str
    speaker_id: str
    job_id: str
    original_text: str
    corrected_text: str
    categories: List[str]
    severity: str
    reported_by: str
    metadata: Dict[str, Any]

class ErrorUpdatedEvent(BaseModel):
    """Event published when an error is updated"""
    event_id: str
    event_type: str = "error.updated"
    version: str = "1.0"
    timestamp: datetime
    source: str = "error-reporting-service"
    correlation_id: str

    # Event payload
    error_id: str
    updated_fields: Dict[str, Any]
    updated_by: str
    previous_values: Dict[str, Any]
```

---

## 5. Data Architecture

### 5.1 Multi-Database Schema Support

The ERS system supports multiple database technologies through the adapter pattern. The same logical data model is implemented differently based on the database type while maintaining consistent business logic.

#### 5.1.1 Logical Data Model
The core entities remain consistent across all database implementations:
- **ErrorReport**: Primary entity containing error information
- **ErrorAuditLog**: Audit trail for all error report changes
- **ErrorCategory**: Reference data for error categorization
- **ErrorValidation**: Validation results and metadata

#### 5.1.2 PostgreSQL Schema (Relational Implementation)

```mermaid
erDiagram
    ERROR_REPORTS {
        uuid error_id PK
        uuid job_id FK
        uuid speaker_id FK
        uuid reported_by FK
        text original_text
        text corrected_text
        json error_categories
        string severity_level
        integer start_position
        integer end_position
        text context_notes
        timestamp error_timestamp
        timestamp reported_at
        string status
        json metadata
        timestamp created_at
        timestamp updated_at
        uuid created_by
        uuid updated_by
    }

    ERROR_AUDIT_LOGS {
        uuid audit_id PK
        uuid error_id FK
        string action_type
        json old_values
        json new_values
        uuid performed_by FK
        timestamp performed_at
        string ip_address
        string user_agent
        string reason
    }

    ERROR_CATEGORIES {
        uuid category_id PK
        string category_name
        string description
        boolean is_active
        integer sort_order
        timestamp created_at
        timestamp updated_at
    }

    ERROR_VALIDATIONS {
        uuid validation_id PK
        uuid error_id FK
        string validation_type
        boolean is_valid
        json validation_details
        timestamp validated_at
        uuid validated_by FK
    }

    %% Relationships
    ERROR_REPORTS ||--o{ ERROR_AUDIT_LOGS : "has_audit_trail"
    ERROR_REPORTS ||--o{ ERROR_VALIDATIONS : "has_validations"
    ERROR_CATEGORIES ||--o{ ERROR_REPORTS : "categorizes"
```

#### 5.1.3 MongoDB Schema (Document Implementation)

```json
{
  "error_reports": {
    "_id": "ObjectId | UUID string",
    "job_id": "UUID string",
    "speaker_id": "UUID string",
    "reported_by": "UUID string",
    "original_text": "string",
    "corrected_text": "string",
    "error_categories": ["string"],
    "severity_level": "string",
    "start_position": "number",
    "end_position": "number",
    "context_notes": "string",
    "error_timestamp": "ISODate",
    "reported_at": "ISODate",
    "status": "string",
    "metadata": {
      "audio_quality": "string",
      "background_noise": "string",
      "confidence_score": "number",
      "custom_fields": {}
    },
    "audit_trail": [
      {
        "action_type": "string",
        "old_values": {},
        "new_values": {},
        "performed_by": "UUID string",
        "performed_at": "ISODate",
        "ip_address": "string",
        "user_agent": "string",
        "reason": "string"
      }
    ],
    "validations": [
      {
        "validation_type": "string",
        "is_valid": "boolean",
        "validation_details": {},
        "validated_at": "ISODate",
        "validated_by": "UUID string"
      }
    ],
    "created_at": "ISODate",
    "updated_at": "ISODate"
  }
}
```

**MongoDB Indexes:**
```javascript
// Compound indexes for efficient querying
db.error_reports.createIndex({ "speaker_id": 1, "reported_at": -1 })
db.error_reports.createIndex({ "job_id": 1, "status": 1 })
db.error_reports.createIndex({ "error_categories": 1, "severity_level": 1 })
db.error_reports.createIndex({ "reported_by": 1, "reported_at": -1 })

// Text index for full-text search
db.error_reports.createIndex({
  "original_text": "text",
  "corrected_text": "text",
  "context_notes": "text"
})

// TTL index for automatic cleanup (optional)
db.error_reports.createIndex({ "created_at": 1 }, { expireAfterSeconds: 31536000 }) // 1 year
```

#### 5.1.4 SQL Server Schema Adaptations

For SQL Server, the schema includes specific optimizations:

```sql
-- SQL Server specific features
CREATE TABLE error_reports (
    error_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    job_id UNIQUEIDENTIFIER NOT NULL,
    speaker_id UNIQUEIDENTIFIER NOT NULL,
    reported_by UNIQUEIDENTIFIER NOT NULL,
    original_text NVARCHAR(MAX) NOT NULL,
    corrected_text NVARCHAR(MAX) NOT NULL,
    error_categories NVARCHAR(MAX) CHECK (ISJSON(error_categories) = 1),
    severity_level NVARCHAR(20) NOT NULL,
    start_position INT NOT NULL,
    end_position INT NOT NULL,
    context_notes NVARCHAR(MAX),
    error_timestamp DATETIME2 NOT NULL,
    reported_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',
    metadata NVARCHAR(MAX) CHECK (ISJSON(metadata) = 1),
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Columnstore index for analytics
CREATE NONCLUSTERED COLUMNSTORE INDEX IX_error_reports_analytics
ON error_reports (speaker_id, severity_level, reported_at, error_categories);

-- Full-text search capability
CREATE FULLTEXT CATALOG error_reports_catalog;
CREATE FULLTEXT INDEX ON error_reports (original_text, corrected_text, context_notes)
KEY INDEX PK_error_reports ON error_reports_catalog;
```
```

### 5.2 Database Adapter Implementation

#### 5.2.1 SQLAlchemy Models
```python
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class ErrorReportModel(Base):
    """SQLAlchemy model for error reports"""
    __tablename__ = "error_reports"

    error_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    speaker_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    reported_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    error_categories = Column(JSON, nullable=False)
    severity_level = Column(String(20), nullable=False, index=True)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    context_notes = Column(Text)
    error_timestamp = Column(DateTime, nullable=False)
    reported_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), nullable=False, default="pending", index=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    audit_logs = relationship("ErrorAuditLogModel", back_populates="error_report")
    validations = relationship("ErrorValidationModel", back_populates="error_report")

class ErrorAuditLogModel(Base):
    """SQLAlchemy model for error audit logs"""
    __tablename__ = "error_audit_logs"

    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    error_id = Column(UUID(as_uuid=True), ForeignKey("error_reports.error_id"), nullable=False)
    action_type = Column(String(50), nullable=False, index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    performed_by = Column(UUID(as_uuid=True), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    reason = Column(Text)

    # Relationships
    error_report = relationship("ErrorReportModel", back_populates="audit_logs")
```

#### 5.2.2 Repository Implementation
```python
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

class SQLAlchemyErrorReportRepository:
    """SQLAlchemy implementation of ErrorReportRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, error_report: ErrorReport) -> ErrorReport:
        """Save error report to database"""
        model = ErrorReportModel(
            error_id=error_report.error_id,
            job_id=error_report.job_id,
            speaker_id=error_report.speaker_id,
            reported_by=error_report.reported_by,
            original_text=error_report.original_text,
            corrected_text=error_report.corrected_text,
            error_categories=error_report.error_categories,
            severity_level=error_report.severity_level.value,
            start_position=error_report.start_position,
            end_position=error_report.end_position,
            context_notes=error_report.context_notes,
            error_timestamp=error_report.error_timestamp,
            reported_at=error_report.reported_at,
            status=error_report.status.value,
            metadata=error_report.metadata
        )

        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)

        return self._model_to_entity(model)

    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find error report by ID"""
        stmt = select(ErrorReportModel).where(ErrorReportModel.error_id == error_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_entity(model) if model else None

    async def find_by_speaker(self, speaker_id: UUID) -> List[ErrorReport]:
        """Find all error reports for a speaker"""
        stmt = select(ErrorReportModel).where(ErrorReportModel.speaker_id == speaker_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    def _model_to_entity(self, model: ErrorReportModel) -> ErrorReport:
        """Convert SQLAlchemy model to domain entity"""
        return ErrorReport(
            error_id=model.error_id,
            job_id=model.job_id,
            speaker_id=model.speaker_id,
            reported_by=model.reported_by,
            original_text=model.original_text,
            corrected_text=model.corrected_text,
            error_categories=model.error_categories,
            severity_level=SeverityLevel(model.severity_level),
            start_position=model.start_position,
            end_position=model.end_position,
            context_notes=model.context_notes,
            error_timestamp=model.error_timestamp,
            reported_at=model.reported_at,
            status=ErrorStatus(model.status),
            metadata=model.metadata
        )
```

---

## 6. Implementation Guidelines

### 6.1 Project Structure (Multi-Adapter Hexagonal Architecture)

```
src/error_reporting_service/
├── domain/                     # Business Logic Core (No external dependencies)
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── error_report.py     # ErrorReport entity
│   │   └── value_objects.py    # SeverityLevel, ErrorStatus enums
│   ├── services/
│   │   ├── __init__.py
│   │   ├── validation_service.py
│   │   └── categorization_service.py
│   └── events/
│       ├── __init__.py
│       └── domain_events.py    # ErrorReportedEvent, etc.
├── application/                # Use Cases and Application Services
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── submit_error_report.py
│   │   ├── get_error_report.py
│   │   └── update_error_report.py
│   ├── dto/
│   │   ├── __init__.py
│   │   ├── requests.py         # Pydantic request models
│   │   └── responses.py        # Pydantic response models
│   └── ports/
│       ├── __init__.py
│       ├── primary/            # Driving ports
│       │   └── error_reporting_port.py
│       └── secondary/          # Driven ports
│           ├── database_port.py        # IDatabaseAdapter interface
│           ├── event_bus_port.py       # IEventBusAdapter interface
│           └── validation_port.py
├── infrastructure/             # Adapters and External Concerns
│   ├── adapters/
│   │   ├── database/           # Database Adapter Implementations
│   │   │   ├── __init__.py
│   │   │   ├── abstract/       # Abstract interfaces
│   │   │   │   ├── __init__.py
│   │   │   │   └── database_adapter.py  # IDatabaseAdapter
│   │   │   ├── postgresql/     # PostgreSQL implementation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapter.py
│   │   │   │   ├── models.py
│   │   │   │   └── migrations/
│   │   │   ├── mongodb/        # MongoDB implementation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapter.py
│   │   │   │   └── indexes.py
│   │   │   ├── sqlserver/      # SQL Server implementation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapter.py
│   │   │   │   └── models.py
│   │   │   └── factory.py      # Database adapter factory
│   │   ├── messaging/          # Event Bus Adapter Implementations
│   │   │   ├── __init__.py
│   │   │   ├── abstract/       # Abstract interfaces
│   │   │   │   ├── __init__.py
│   │   │   │   └── event_bus_adapter.py  # IEventBusAdapter
│   │   │   ├── kafka/          # Kafka implementation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapter.py
│   │   │   │   └── config.py
│   │   │   ├── azure_servicebus/  # Azure Service Bus implementation
│   │   │   │   ├── __init__.py
│   │   │   │   └── adapter.py
│   │   │   ├── aws_sqs/        # AWS SQS implementation
│   │   │   │   ├── __init__.py
│   │   │   │   └── adapter.py
│   │   │   ├── rabbitmq/       # RabbitMQ implementation
│   │   │   │   ├── __init__.py
│   │   │   │   └── adapter.py
│   │   │   └── factory.py      # Event bus adapter factory
│   │   ├── http/
│   │   │   ├── __init__.py
│   │   │   ├── controllers.py  # FastAPI controllers
│   │   │   ├── middleware.py   # Custom middleware
│   │   │   └── dependencies.py # Dependency injection
│   │   └── external/
│   │       ├── __init__.py
│   │       ├── user_service_client.py
│   │       └── validation_client.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Pydantic Settings with adapter config
│   │   ├── database_config.py  # Database adapter configuration
│   │   └── messaging_config.py # Event bus adapter configuration
│   └── monitoring/
│       ├── __init__.py
│       ├── metrics.py          # Prometheus metrics
│       └── tracing.py          # OpenTelemetry tracing
├── tests/
│   ├── unit/                   # Unit tests (domain + application)
│   │   ├── domain/
│   │   ├── application/
│   │   └── adapters/           # Adapter-specific unit tests
│   ├── integration/            # Integration tests
│   │   ├── database/           # Database adapter integration tests
│   │   └── messaging/          # Event bus adapter integration tests
│   └── e2e/                    # End-to-end tests
├── main.py                     # FastAPI app setup with adapter factories
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Poetry configuration
└── Dockerfile                 # Container configuration
```

### 6.2 Configuration Management for Multi-Adapter Support

#### 6.2.1 Settings Configuration
```python
from pydantic import BaseSettings, Field
from typing import Optional, Dict, Any
from enum import Enum

class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    SQLSERVER = "sqlserver"
    MONGODB = "mongodb"

class EventBusType(str, Enum):
    KAFKA = "kafka"
    AZURE_SERVICEBUS = "azure_servicebus"
    AWS_SQS = "aws_sqs"
    RABBITMQ = "rabbitmq"

class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "error_reporting"
    username: str = "ers_user"
    password: str = "ers_password"
    connection_string: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

    # MongoDB specific
    replica_set: Optional[str] = None
    auth_source: Optional[str] = None

    # SQL Server specific
    driver: str = "ODBC Driver 17 for SQL Server"
    trust_server_certificate: bool = True

    class Config:
        env_prefix = "DB_"

class EventBusConfig(BaseSettings):
    """Event bus configuration settings"""
    type: EventBusType = EventBusType.KAFKA
    connection_string: str = "localhost:9092"
    client_id: str = "error-reporting-service"

    # Kafka specific
    bootstrap_servers: Optional[str] = None
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None

    # Azure Service Bus specific
    namespace: Optional[str] = None
    shared_access_key_name: Optional[str] = None
    shared_access_key: Optional[str] = None

    # AWS SQS specific
    region_name: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None

    # RabbitMQ specific
    virtual_host: str = "/"
    heartbeat: int = 600

    class Config:
        env_prefix = "EVENT_BUS_"

class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = "Error Reporting Service"
    debug: bool = False
    log_level: str = "INFO"

    # Adapter configurations
    database: DatabaseConfig = DatabaseConfig()
    event_bus: EventBusConfig = EventBusConfig()

    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
```

#### 6.2.2 Adapter Factory Pattern
```python
from typing import Protocol
from abc import ABC, abstractmethod

class AdapterFactory(ABC):
    """Abstract factory for creating adapters"""

    @abstractmethod
    async def create_database_adapter(self, config: DatabaseConfig) -> IDatabaseAdapter:
        """Create database adapter based on configuration"""
        pass

    @abstractmethod
    async def create_event_bus_adapter(self, config: EventBusConfig) -> IEventBusAdapter:
        """Create event bus adapter based on configuration"""
        pass

class DatabaseAdapterFactory:
    """Factory for creating database adapters"""

    @staticmethod
    async def create(config: DatabaseConfig) -> IDatabaseAdapter:
        """Create database adapter based on configuration"""
        if config.type == DatabaseType.POSTGRESQL:
            from infrastructure.adapters.database.postgresql.adapter import PostgreSQLAdapter
            connection_string = config.connection_string or f"postgresql+asyncpg://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            return PostgreSQLAdapter(connection_string)

        elif config.type == DatabaseType.MONGODB:
            from infrastructure.adapters.database.mongodb.adapter import MongoDBAdapter
            connection_string = config.connection_string or f"mongodb://{config.username}:{config.password}@{config.host}:{config.port}"
            return MongoDBAdapter(connection_string, config.database)

        elif config.type == DatabaseType.SQLSERVER:
            from infrastructure.adapters.database.sqlserver.adapter import SQLServerAdapter
            connection_string = config.connection_string or f"mssql+aioodbc://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}?driver={config.driver}&TrustServerCertificate={config.trust_server_certificate}"
            return SQLServerAdapter(connection_string)

        else:
            raise ValueError(f"Unsupported database type: {config.type}")

class EventBusAdapterFactory:
    """Factory for creating event bus adapters"""

    @staticmethod
    async def create(config: EventBusConfig) -> IEventBusAdapter:
        """Create event bus adapter based on configuration"""
        if config.type == EventBusType.KAFKA:
            from infrastructure.adapters.messaging.kafka.adapter import KafkaAdapter
            bootstrap_servers = config.bootstrap_servers or config.connection_string
            return KafkaAdapter(bootstrap_servers, config.client_id)

        elif config.type == EventBusType.AZURE_SERVICEBUS:
            from infrastructure.adapters.messaging.azure_servicebus.adapter import AzureServiceBusAdapter
            return AzureServiceBusAdapter(config.connection_string)

        elif config.type == EventBusType.AWS_SQS:
            from infrastructure.adapters.messaging.aws_sqs.adapter import AWSSQSAdapter
            return AWSSQSAdapter(
                region_name=config.region_name,
                access_key_id=config.access_key_id,
                secret_access_key=config.secret_access_key
            )

        elif config.type == EventBusType.RABBITMQ:
            from infrastructure.adapters.messaging.rabbitmq.adapter import RabbitMQAdapter
            return RabbitMQAdapter(config.connection_string, config.virtual_host)

        else:
            raise ValueError(f"Unsupported event bus type: {config.type}")
```

### 6.3 Multi-Adapter Dependency Injection Setup

#### 6.3.1 Adapter-Agnostic FastAPI Dependencies
```python
from fastapi import Depends
from typing import Annotated
from functools import lru_cache

# Singleton adapter instances
_database_adapter: Optional[IDatabaseAdapter] = None
_event_bus_adapter: Optional[IEventBusAdapter] = None

@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()

async def get_database_adapter() -> IDatabaseAdapter:
    """Get database adapter instance (singleton)"""
    global _database_adapter
    if _database_adapter is None:
        settings = get_settings()
        _database_adapter = await DatabaseAdapterFactory.create(settings.database)
    return _database_adapter

async def get_event_bus_adapter() -> IEventBusAdapter:
    """Get event bus adapter instance (singleton)"""
    global _event_bus_adapter
    if _event_bus_adapter is None:
        settings = get_settings()
        _event_bus_adapter = await EventBusAdapterFactory.create(settings.event_bus)
    return _event_bus_adapter

# Repository dependencies (adapter-agnostic)
def get_error_repository(
    db_adapter: Annotated[IDatabaseAdapter, Depends(get_database_adapter)]
) -> ErrorReportRepository:
    """Get error repository using configured database adapter"""
    return DatabaseAdapterRepository(db_adapter)

# Event publisher dependencies (adapter-agnostic)
def get_event_publisher(
    event_adapter: Annotated[IEventBusAdapter, Depends(get_event_bus_adapter)]
) -> EventPublisher:
    """Get event publisher using configured event bus adapter"""
    return EventBusAdapterPublisher(event_adapter)

# Service dependencies (unchanged - pure domain logic)
def get_validation_service() -> ErrorValidationService:
    return ErrorValidationService()

def get_categorization_service() -> ErrorCategorizationService:
    return ErrorCategorizationService()

# Use case dependencies (adapter-agnostic)
def get_submit_error_use_case(
    repository: Annotated[ErrorReportRepository, Depends(get_error_repository)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
    validation_service: Annotated[ErrorValidationService, Depends(get_validation_service)],
    categorization_service: Annotated[ErrorCategorizationService, Depends(get_categorization_service)]
) -> SubmitErrorReportUseCase:
    return SubmitErrorReportUseCase(
        repository, event_publisher, validation_service, categorization_service
    )

#### 6.3.2 Adapter Bridge Classes
```python
class DatabaseAdapterRepository(ErrorReportRepository):
    """Bridge between repository interface and database adapter"""

    def __init__(self, db_adapter: IDatabaseAdapter):
        self._db_adapter = db_adapter

    async def save(self, error_report: ErrorReport) -> ErrorReport:
        return await self._db_adapter.save_error_report(error_report)

    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        return await self._db_adapter.find_error_by_id(error_id)

    async def find_by_speaker(self, speaker_id: UUID) -> List[ErrorReport]:
        return await self._db_adapter.find_errors_by_speaker(speaker_id)

class EventBusAdapterPublisher(EventPublisher):
    """Bridge between event publisher interface and event bus adapter"""

    def __init__(self, event_adapter: IEventBusAdapter):
        self._event_adapter = event_adapter

    async def publish_error_reported(self, event: ErrorReportedEvent) -> None:
        await self._event_adapter.publish_event("error.reported", event)

    async def publish_error_updated(self, event: ErrorUpdatedEvent) -> None:
        await self._event_adapter.publish_event("error.updated", event)

#### 6.3.3 Environment-Based Configuration Examples

**Development Environment (.env.dev):**
```bash
# Database Configuration
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=error_reporting_dev
DB_USERNAME=dev_user
DB_PASSWORD=dev_password

# Event Bus Configuration
EVENT_BUS_TYPE=kafka
EVENT_BUS_CONNECTION_STRING=localhost:9092
EVENT_BUS_CLIENT_ID=ers-dev
```

**Production Environment (.env.prod):**
```bash
# Database Configuration
DB_TYPE=postgresql
DB_CONNECTION_STRING=postgresql+asyncpg://prod_user:prod_password@prod-db-cluster:5432/error_reporting_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Event Bus Configuration
EVENT_BUS_TYPE=azure_servicebus
EVENT_BUS_CONNECTION_STRING=Endpoint=sb://prod-servicebus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=...
EVENT_BUS_CLIENT_ID=ers-prod
```

**Cloud Environment (.env.cloud):**
```bash
# Database Configuration
DB_TYPE=mongodb
DB_CONNECTION_STRING=mongodb+srv://cloud_user:cloud_password@cluster.mongodb.net/error_reporting?retryWrites=true&w=majority
DB_DATABASE=error_reporting

# Event Bus Configuration
EVENT_BUS_TYPE=aws_sqs
EVENT_BUS_REGION_NAME=us-east-1
EVENT_BUS_ACCESS_KEY_ID=AKIA...
EVENT_BUS_SECRET_ACCESS_KEY=...
```

### 6.3 FastAPI Controller Implementation

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

router = APIRouter(prefix="/api/v1/errors", tags=["error-reporting"])

@router.post("/report", status_code=status.HTTP_201_CREATED)
async def submit_error_report(
    request: SubmitErrorReportRequest,
    use_case: Annotated[SubmitErrorReportUseCase, Depends(get_submit_error_use_case)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> SubmitErrorReportResponse:
    """Submit a new error report"""
    try:
        # Add user context to request
        request.reported_by = str(current_user.user_id)

        response = await use_case.execute(request)
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log error for monitoring
        logger.error(f"Error submitting report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{error_id}")
async def get_error_report(
    error_id: str,
    use_case: Annotated[GetErrorReportUseCase, Depends(get_get_error_use_case)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> ErrorReport:
    """Get error report by ID"""
    try:
        error_report = await use_case.execute(error_id)
        if not error_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error report not found"
            )
        return error_report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report {error_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

---

## 7. Testing Strategy

### 7.1 Multi-Adapter Test-Driven Development (TDD) Approach

#### 7.1.1 Unit Testing (70% Coverage Target)
**Framework**: pytest with pytest-asyncio for async testing

The testing strategy ensures that all adapters can be tested in isolation while maintaining consistent behavior across different implementations.

**Domain Layer Tests**:
```python
import pytest
from uuid import uuid4
from datetime import datetime
from src.domain.entities.error_report import ErrorReport, SeverityLevel, ErrorStatus
from src.domain.services.validation_service import ErrorValidationService

class TestErrorReportEntity:
    """Unit tests for ErrorReport domain entity"""

    def test_create_valid_error_report(self):
        """Test creating a valid error report"""
        error_report = ErrorReport(
            error_id=uuid4(),
            job_id=uuid4(),
            speaker_id=uuid4(),
            reported_by=uuid4(),
            original_text="The patient has diabetis",
            corrected_text="The patient has diabetes",
            error_categories=["medical_terminology"],
            severity_level=SeverityLevel.HIGH,
            start_position=16,
            end_position=24,
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        assert error_report.original_text == "The patient has diabetis"
        assert error_report.corrected_text == "The patient has diabetes"
        assert error_report.severity_level == SeverityLevel.HIGH

    def test_invalid_position_range_raises_error(self):
        """Test that invalid position range raises validation error"""
        with pytest.raises(ValueError, match="end_position must be greater than start_position"):
            ErrorReport(
                error_id=uuid4(),
                job_id=uuid4(),
                speaker_id=uuid4(),
                reported_by=uuid4(),
                original_text="Test text",
                corrected_text="Corrected text",
                error_categories=["grammar"],
                severity_level=SeverityLevel.LOW,
                start_position=10,
                end_position=5,  # Invalid: less than start_position
                error_timestamp=datetime.utcnow(),
                reported_at=datetime.utcnow()
            )

class TestErrorValidationService:
    """Unit tests for ErrorValidationService"""

    def setup_method(self):
        self.validation_service = ErrorValidationService()

    def test_validate_error_categories_valid(self):
        """Test validation of valid error categories"""
        valid_categories = ["pronunciation", "medical_terminology"]
        result = self.validation_service.validate_error_categories(valid_categories)
        assert result is True

    def test_validate_error_categories_invalid(self):
        """Test validation of invalid error categories"""
        invalid_categories = ["invalid_category", "medical_terminology"]
        result = self.validation_service.validate_error_categories(invalid_categories)
        assert result is False
```

**Application Layer Tests**:
```python
import pytest
from unittest.mock import AsyncMock, Mock
from src.application.use_cases.submit_error_report import SubmitErrorReportUseCase
from src.application.dto.requests import SubmitErrorReportRequest

class TestSubmitErrorReportUseCase:
    """Unit tests for SubmitErrorReportUseCase"""

    def setup_method(self):
        self.mock_repository = AsyncMock()
        self.mock_event_publisher = AsyncMock()
        self.mock_validation_service = Mock()
        self.mock_categorization_service = Mock()

        self.use_case = SubmitErrorReportUseCase(
            self.mock_repository,
            self.mock_event_publisher,
            self.mock_validation_service,
            self.mock_categorization_service
        )

    @pytest.mark.asyncio
    async def test_execute_valid_request_success(self):
        """Test successful execution with valid request"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="diabetis",
            corrected_text="diabetes",
            error_categories=["medical_terminology"],
            severity_level="high",
            start_position=0,
            end_position=8,
            context_notes="Common misspelling",
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={}
        )

        self.mock_validation_service.validate_error_categories.return_value = True
        self.mock_validation_service.validate_context_integrity.return_value = True
        self.mock_repository.save.return_value = Mock(error_id=uuid4())

        # Act
        response = await self.use_case.execute(request)

        # Assert
        assert response.status == "success"
        assert "successfully" in response.message
        self.mock_repository.save.assert_called_once()
        self.mock_event_publisher.publish_error_reported.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_invalid_categories_raises_error(self):
        """Test that invalid categories raise ValueError"""
        # Arrange
        request = SubmitErrorReportRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            speaker_id="550e8400-e29b-41d4-a716-446655440001",
            original_text="test",
            corrected_text="corrected",
            error_categories=["invalid_category"],
            severity_level="low",
            start_position=0,
            end_position=4,
            reported_by="550e8400-e29b-41d4-a716-446655440002",
            metadata={}
        )

        self.mock_validation_service.validate_error_categories.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid error categories"):
            await self.use_case.execute(request)

#### 7.1.3 Adapter Testing Strategy

**Abstract Adapter Interface Tests**:
```python
import pytest
from abc import ABC
from typing import Type
from uuid import uuid4

class DatabaseAdapterTestSuite:
    """Abstract test suite for database adapters - ensures consistent behavior"""

    @pytest.fixture
    def adapter(self) -> IDatabaseAdapter:
        """Override in concrete test classes"""
        raise NotImplementedError

    @pytest.mark.asyncio
    async def test_save_and_retrieve_error_report(self, adapter: IDatabaseAdapter):
        """Test saving and retrieving error report - works for all adapters"""
        # Arrange
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
            error_timestamp=datetime.utcnow(),
            reported_at=datetime.utcnow()
        )

        # Act
        saved_report = await adapter.save_error_report(error_report)
        retrieved_report = await adapter.find_error_by_id(saved_report.error_id)

        # Assert
        assert retrieved_report is not None
        assert retrieved_report.error_id == error_report.error_id
        assert retrieved_report.original_text == error_report.original_text
        assert retrieved_report.corrected_text == error_report.corrected_text

    @pytest.mark.asyncio
    async def test_find_errors_by_speaker(self, adapter: IDatabaseAdapter):
        """Test finding errors by speaker - works for all adapters"""
        # Arrange
        speaker_id = uuid4()
        error_report1 = self._create_test_error_report(speaker_id=speaker_id)
        error_report2 = self._create_test_error_report(speaker_id=speaker_id)
        other_speaker_report = self._create_test_error_report(speaker_id=uuid4())

        # Act
        await adapter.save_error_report(error_report1)
        await adapter.save_error_report(error_report2)
        await adapter.save_error_report(other_speaker_report)

        speaker_errors = await adapter.find_errors_by_speaker(speaker_id)

        # Assert
        assert len(speaker_errors) == 2
        assert all(error.speaker_id == speaker_id for error in speaker_errors)

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, adapter: IDatabaseAdapter):
        """Test transaction rollback - works for all adapters"""
        # Arrange
        error_report = self._create_test_error_report()

        # Act & Assert
        transaction = await adapter.begin_transaction()
        try:
            await adapter.save_error_report(error_report)
            # Simulate error and rollback
            await adapter.rollback_transaction(transaction)

            # Verify rollback worked
            retrieved = await adapter.find_error_by_id(error_report.error_id)
            assert retrieved is None
        except Exception:
            await adapter.rollback_transaction(transaction)
            raise

class PostgreSQLAdapterTest(DatabaseAdapterTestSuite):
    """PostgreSQL adapter specific tests"""

    @pytest.fixture
    async def adapter(self) -> PostgreSQLAdapter:
        """Create PostgreSQL adapter for testing"""
        # Use test database
        connection_string = "postgresql+asyncpg://test:test@localhost:5432/test_db"
        adapter = PostgreSQLAdapter(connection_string)

        # Setup test schema
        await self._setup_test_schema(adapter)
        yield adapter
        await self._cleanup_test_schema(adapter)

    @pytest.mark.asyncio
    async def test_postgresql_specific_features(self, adapter: PostgreSQLAdapter):
        """Test PostgreSQL-specific functionality"""
        # Test JSONB queries, full-text search, etc.
        pass

class MongoDBAdapterTest(DatabaseAdapterTestSuite):
    """MongoDB adapter specific tests"""

    @pytest.fixture
    async def adapter(self) -> MongoDBAdapter:
        """Create MongoDB adapter for testing"""
        connection_string = "mongodb://test:test@localhost:27017"
        adapter = MongoDBAdapter(connection_string, "test_db")

        # Setup test collections
        await self._setup_test_collections(adapter)
        yield adapter
        await self._cleanup_test_collections(adapter)

    @pytest.mark.asyncio
    async def test_mongodb_specific_features(self, adapter: MongoDBAdapter):
        """Test MongoDB-specific functionality"""
        # Test aggregation pipelines, text search, etc.
        pass

class EventBusAdapterTestSuite:
    """Abstract test suite for event bus adapters"""

    @pytest.fixture
    def adapter(self) -> IEventBusAdapter:
        """Override in concrete test classes"""
        raise NotImplementedError

    @pytest.mark.asyncio
    async def test_publish_and_consume_event(self, adapter: IEventBusAdapter):
        """Test publishing and consuming events - works for all adapters"""
        # Arrange
        topic = "test.topic"
        event = ErrorReportedEvent(
            event_id=str(uuid4()),
            error_id=str(uuid4()),
            speaker_id=str(uuid4()),
            job_id=str(uuid4()),
            original_text="test",
            corrected_text="corrected",
            categories=["grammar"],
            severity="low",
            reported_by=str(uuid4()),
            timestamp=datetime.utcnow(),
            metadata={}
        )

        received_events = []

        async def event_handler(event_data):
            received_events.append(event_data)

        # Act
        await adapter.create_topic(topic)
        await adapter.subscribe_to_topic(topic, event_handler)
        success = await adapter.publish_event(topic, event)

        # Wait for message processing
        await asyncio.sleep(1)

        # Assert
        assert success is True
        assert len(received_events) == 1
        assert received_events[0]["event_id"] == event.event_id

    @pytest.mark.asyncio
    async def test_health_check(self, adapter: IEventBusAdapter):
        """Test health check - works for all adapters"""
        health_status = await adapter.health_check()
        assert isinstance(health_status, bool)

class KafkaAdapterTest(EventBusAdapterTestSuite):
    """Kafka adapter specific tests"""

    @pytest.fixture
    async def adapter(self) -> KafkaAdapter:
        """Create Kafka adapter for testing"""
        adapter = KafkaAdapter("localhost:9092", "test-client")
        yield adapter
        # Cleanup if needed

    @pytest.mark.asyncio
    async def test_kafka_specific_features(self, adapter: KafkaAdapter):
        """Test Kafka-specific functionality"""
        # Test partitioning, consumer groups, etc.
        pass
```
```

#### 7.1.2 Multi-Adapter Integration Testing (20% Coverage Target)
**Framework**: pytest with httpx for API testing and testcontainers for database isolation

```python
import pytest
from httpx import AsyncClient
from testcontainers.postgres import PostgresContainer
from testcontainers.mongodb import MongoDbContainer
from testcontainers.kafka import KafkaContainer
import os

@pytest.fixture(scope="session", params=["postgresql", "mongodb"])
async def test_database_adapter(request):
    """Create test database adapter for different database types"""
    db_type = request.param

    if db_type == "postgresql":
        with PostgresContainer("postgres:15") as postgres:
            connection_string = postgres.get_connection_url().replace("postgresql://", "postgresql+asyncpg://")
            adapter = PostgreSQLAdapter(connection_string)
            yield adapter

    elif db_type == "mongodb":
        with MongoDbContainer("mongo:6") as mongodb:
            connection_string = mongodb.get_connection_url()
            adapter = MongoDBAdapter(connection_string, "test_db")
            yield adapter

@pytest.fixture(scope="session", params=["kafka", "memory"])
async def test_event_bus_adapter(request):
    """Create test event bus adapter for different messaging systems"""
    event_bus_type = request.param

    if event_bus_type == "kafka":
        with KafkaContainer() as kafka:
            bootstrap_servers = kafka.get_bootstrap_server()
            adapter = KafkaAdapter(bootstrap_servers, "test-client")
            yield adapter

    elif event_bus_type == "memory":
        # Use in-memory adapter for faster testing
        adapter = InMemoryEventBusAdapter()
        yield adapter

@pytest.mark.asyncio
async def test_submit_error_report_integration_multi_adapter(
    test_database_adapter,
    test_event_bus_adapter
):
    """Integration test that works with any database and event bus adapter"""

    # Override dependencies with test adapters
    app.dependency_overrides[get_database_adapter] = lambda: test_database_adapter
    app.dependency_overrides[get_event_bus_adapter] = lambda: test_event_bus_adapter

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange
            payload = {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "speaker_id": "550e8400-e29b-41d4-a716-446655440001",
                "original_text": "The patient has diabetis",
                "corrected_text": "The patient has diabetes",
                "error_categories": ["medical_terminology"],
                "severity_level": "high",
                "start_position": 16,
                "end_position": 24,
                "context_notes": "Common misspelling",
                "metadata": {"audio_quality": "good"}
            }

            # Act
            response = await client.post(
                "/api/v1/errors/report",
                json=payload,
                headers={"Authorization": "Bearer test_token"}
            )

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert "error_id" in data["data"]
            assert data["data"]["status"] == "pending"

            # Verify data was saved in database (adapter-agnostic)
            error_id = data["data"]["error_id"]
            saved_error = await test_database_adapter.find_error_by_id(error_id)
            assert saved_error is not None
            assert saved_error.original_text == payload["original_text"]

    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_adapter_switching_configuration():
    """Test that adapters can be switched via configuration"""

    # Test PostgreSQL configuration
    postgres_config = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        username="test",
        password="test"
    )
    postgres_adapter = await DatabaseAdapterFactory.create(postgres_config)
    assert isinstance(postgres_adapter, PostgreSQLAdapter)

    # Test MongoDB configuration
    mongodb_config = DatabaseConfig(
        type=DatabaseType.MONGODB,
        host="localhost",
        port=27017,
        database="test_db",
        username="test",
        password="test"
    )
    mongodb_adapter = await DatabaseAdapterFactory.create(mongodb_config)
    assert isinstance(mongodb_adapter, MongoDBAdapter)

    # Test Kafka configuration
    kafka_config = EventBusConfig(
        type=EventBusType.KAFKA,
        connection_string="localhost:9092",
        client_id="test-client"
    )
    kafka_adapter = await EventBusAdapterFactory.create(kafka_config)
    assert isinstance(kafka_adapter, KafkaAdapter)

@pytest.mark.asyncio
async def test_cross_adapter_data_consistency():
    """Test that data remains consistent across different adapter implementations"""

    # Create test data
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
        error_timestamp=datetime.utcnow(),
        reported_at=datetime.utcnow()
    )

    # Test with PostgreSQL
    postgres_adapter = PostgreSQLAdapter("postgresql+asyncpg://test:test@localhost:5432/test_db")
    saved_postgres = await postgres_adapter.save_error_report(error_report)
    retrieved_postgres = await postgres_adapter.find_error_by_id(saved_postgres.error_id)

    # Test with MongoDB
    mongodb_adapter = MongoDBAdapter("mongodb://test:test@localhost:27017", "test_db")
    saved_mongodb = await mongodb_adapter.save_error_report(error_report)
    retrieved_mongodb = await mongodb_adapter.find_error_by_id(saved_mongodb.error_id)

    # Assert data consistency across adapters
    assert retrieved_postgres.original_text == retrieved_mongodb.original_text
    assert retrieved_postgres.corrected_text == retrieved_mongodb.corrected_text
    assert retrieved_postgres.severity_level == retrieved_mongodb.severity_level
    assert retrieved_postgres.error_categories == retrieved_mongodb.error_categories
```

#### 7.1.3 Contract Testing (10% Coverage Target)
**Framework**: Pact Python for consumer-driven contract testing

```python
import pytest
from pact import Consumer, Provider, Like, Term
from src.infrastructure.adapters.external.user_service_client import UserServiceClient

@pytest.fixture(scope="session")
def pact():
    """Pact fixture for contract testing"""
    return Consumer("error-reporting-service").has_pact_with(
        Provider("user-management-service"),
        host_name="localhost",
        port=1234
    )

def test_validate_user_exists_contract(pact):
    """Contract test for user validation"""
    expected = {
        "user_id": Like("550e8400-e29b-41d4-a716-446655440000"),
        "exists": Like(True),
        "permissions": Like(["error_reporting"])
    }

    (pact
     .given("user exists with error reporting permissions")
     .upon_receiving("a request to validate user")
     .with_request("GET", "/api/v1/users/550e8400-e29b-41d4-a716-446655440000/validate")
     .will_respond_with(200, body=expected))

    with pact:
        client = UserServiceClient("http://localhost:1234")
        result = client.validate_user("550e8400-e29b-41d4-a716-446655440000")
        assert result["exists"] is True
```

### 7.2 Test Execution Strategy

#### 7.2.1 Local Development
```bash
# Run unit tests
pytest tests/unit/ -v --cov=src --cov-report=html

# Run integration tests
pytest tests/integration/ -v --tb=short

# Run all tests with coverage
pytest --cov=src --cov-report=html --cov-fail-under=70
```

#### 7.2.2 CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install poetry
        poetry install

    - name: Run unit tests
      run: poetry run pytest tests/unit/ --cov=src --cov-report=xml

    - name: Run integration tests
      run: poetry run pytest tests/integration/

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

**Document Status**: ✅ Complete
**Next Review Date**: August 14, 2025
**Approval Required**: Architecture Review Board, Technical Lead, Product Owner
```
```
```
```
```
