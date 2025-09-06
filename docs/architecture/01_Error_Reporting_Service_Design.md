# Error Reporting Service (ERS) - Detailed Architecture Design

**Document Version:** 1.2
**Date:** August 19, 2025
**Service:** Error Reporting Service (ERS)
**Technology Stack:** Python + FastAPI + PostgreSQL + Redis + Kafka
**Design Principles:** SOLID Principles + Hexagonal Architecture + Test-Driven Development (TDD)
**Development Methodology:** TDD Mandatory for All Components

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Test-Driven Development (TDD) Requirements](#test-driven-development-tdd-requirements)
3. [SOLID Principles Implementation](#solid-principles-implementation)
4. [Hexagonal Architecture Design](#hexagonal-architecture-design)
5. [API Specifications](#api-specifications)
6. [Database Schema Design](#database-schema-design)
7. [Integration Points](#integration-points)
8. [Error Handling Strategy](#error-handling-strategy)
9. [Technology Implementation](#technology-implementation)
10. [Directory Structure](#directory-structure)
11. [Key Classes and Interfaces](#key-classes-and-interfaces)
12. [Configuration Management](#configuration-management)
13. [Dependency Management](#dependency-management)
14. [User Stories](#user-stories)

---

## 1. Service Overview

### 1.1 Service Responsibilities

The Error Reporting Service (ERS) is the primary entry point for the ASR Error Reporting System. It handles:

- **Error Submission**: Accept and validate error reports from QA personnel
- **Error Categorization**: Classify errors by type, severity, and context (including custom categories)
- **Data Validation**: Ensure error report completeness and accuracy
- **Event Publishing**: Notify other services of error events for processing
- **Error Management**: CRUD operations for error reports
- **Search and Filtering**: Query capabilities for error analysis

### 1.2 Service Boundaries

**Inputs:**
- Error reports from QA personnel via REST API
- Update requests for existing error reports
- Search and filter queries

**Outputs:**
- Validated error reports stored in database
- Error events published to message queue
- API responses with error data and metadata

**Dependencies:**
- User Management Service (authentication/authorization)
- PostgreSQL database (data persistence)
- Redis cache (performance optimization)
- Kafka message queue (event publishing)

### 1.3 Core Capabilities

- Sub-second error report validation
- Real-time event publishing
- Comprehensive error categorization
- Advanced search and filtering
- Audit trail maintenance
- Data consistency guarantees

---

## 2. Test-Driven Development (TDD) Requirements

### 2.1 TDD Workflow for Error Reporting Service

All development in the Error Reporting Service must follow the Red-Green-Refactor cycle:

**Red Phase - Write Failing Tests:**
```python
# Example: Testing error report submission
class TestSubmitErrorReportUseCase:
    def test_submit_valid_error_report_returns_id(self):
        # Red: This test will fail until implementation exists
        use_case = SubmitErrorReportUseCase(
            mock_repository, mock_validator, mock_publisher
        )
        error_report = create_valid_error_report()

        error_id = await use_case.execute(error_report)

        assert error_id is not None
        assert isinstance(error_id, str)
        assert len(error_id) > 0
```

**Green Phase - Minimal Implementation:**
```python
# Green: Minimal code to make test pass
class SubmitErrorReportUseCase:
    def __init__(self, repository, validator, publisher):
        self._repository = repository
        self._validator = validator
        self._publisher = publisher

    async def execute(self, error_report: ErrorReport) -> str:
        # Minimal implementation to pass test
        return "test-id-123"
```

**Refactor Phase - Improve Design:**
```python
# Refactor: Add proper implementation while keeping tests green
class SubmitErrorReportUseCase:
    def __init__(
        self,
        repository: ErrorRepositoryPort,
        validator: ErrorValidatorPort,
        publisher: EventPublishingPort
    ):
        self._repository = repository
        self._validator = validator
        self._publisher = publisher

    async def execute(self, error_report: ErrorReport) -> str:
        validation_result = await self._validator.validate(error_report)
        if not validation_result.is_valid:
            raise ValidationError(validation_result.errors)

        error_id = await self._repository.save(error_report)
        await self._publisher.publish_error_created(error_report)

        return error_id
```

### 2.2 TDD Requirements for ERS Components

**Domain Logic Testing (70% of tests):**
- All business rules must be tested before implementation
- Error validation logic tested with comprehensive edge cases
- Error categorization algorithms tested with various inputs
- Severity calculation logic tested with boundary conditions

**Integration Testing (20% of tests):**
- Database operations tested with test database
- Event publishing tested with test message queue
- Cache operations tested with test cache
- External service integrations tested with mocks

**End-to-End Testing (10% of tests):**
- Complete error submission workflow tested
- API endpoint integration tested
- Cross-service communication tested
- User authentication flow tested

### 2.3 TDD Testing Framework Configuration

**pytest Configuration for ERS:**
```python
# pytest.ini for Error Reporting Service
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=src/error_reporting_service
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=70
    --asyncio-mode=auto
    -v

markers =
    unit: Unit tests for business logic
    integration: Integration tests for external dependencies
    e2e: End-to-end tests for complete workflows
    slow: Tests that take longer than 1 second
```

**Required Testing Dependencies:**
```python
# requirements-test.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
httpx>=0.24.0
factory-boy>=3.2.0
freezegun>=1.2.0
responses>=0.23.0
```

### 2.4 TDD Definition of Done for ERS

**Code Completion Criteria:**
- [ ] All tests written before implementation (Red phase)
- [ ] All tests passing (Green phase)
- [ ] Code refactored for quality (Refactor phase)
- [ ] Unit test coverage ≥ 70%
- [ ] Integration test coverage ≥ 20%
- [ ] E2E test coverage ≥ 10%
- [ ] All edge cases and error conditions tested
- [ ] Mock usage validates dependency abstractions
- [ ] Test names clearly describe business scenarios

**Code Review Criteria:**
- [ ] Evidence of TDD workflow in commit history
- [ ] Test quality meets standards (clear, focused, maintainable)
- [ ] SOLID principles validated through test design
- [ ] Appropriate use of mocks for dependency isolation
- [ ] Test documentation explains business requirements
- [ ] No production code without corresponding tests

### 2.5 ERS-Specific TDD Patterns

**Testing Error Validation:**
```python
class TestErrorReportValidator:
    def test_validates_required_job_id(self):
        validator = ErrorReportValidator()
        error_report = ErrorReport(job_id="", speaker_id="123")

        result = validator.validate(error_report)

        assert not result.is_valid
        assert "job_id is required" in result.errors

    def test_validates_text_length_limits(self):
        validator = ErrorReportValidator()
        long_text = "x" * 10001  # Exceeds 10000 character limit
        error_report = ErrorReport(original_text=long_text)

        result = validator.validate(error_report)

        assert not result.is_valid
        assert "text exceeds maximum length" in result.errors
```

**Testing Repository Operations:**
```python
class TestErrorReportRepository:
    async def test_save_returns_valid_id(self):
        repository = PostgreSQLErrorRepository(test_db_connection)
        error_report = ErrorReportFactory.create()

        error_id = await repository.save(error_report)

        assert error_id is not None
        assert isinstance(error_id, str)
        assert len(error_id) > 0

    async def test_get_by_id_returns_saved_report(self):
        repository = PostgreSQLErrorRepository(test_db_connection)
        error_report = ErrorReportFactory.create()

        error_id = await repository.save(error_report)
        retrieved_report = await repository.get_by_id(error_id)

        assert retrieved_report.original_text == error_report.original_text
        assert retrieved_report.corrected_text == error_report.corrected_text
```

**Testing Event Publishing:**
```python
class TestErrorEventPublisher:
    async def test_publishes_error_created_event(self):
        mock_kafka_producer = Mock()
        publisher = KafkaErrorEventPublisher(mock_kafka_producer)
        error_report = ErrorReportFactory.create()

        await publisher.publish_error_created(error_report)

        mock_kafka_producer.send.assert_called_once()
        call_args = mock_kafka_producer.send.call_args
        assert call_args[0][0] == "error-created"  # Topic
        assert "error_id" in call_args[1]["value"]  # Event payload
```

---

## 3. SOLID Principles Implementation

### 2.1 Single Responsibility Principle (SRP)

The Error Reporting Service strictly adheres to SRP at multiple levels:

**Service Level:**
- **Primary Responsibility**: Error submission, validation, and management only
- **Clear Boundaries**: Does not handle user authentication (delegated to UMS), vector processing (delegated to RIS), or real-time corrections (delegated to CES)

**Class Level:**
- `ErrorReportDomain`: Contains only business logic for error validation and categorization
- `ErrorReportUseCase`: Contains only application workflow logic for error processing
- `ErrorReportController`: Contains only HTTP request/response handling
- `ErrorReportRepository`: Contains only data persistence operations
- `ErrorValidationService`: Contains only validation logic

**Method Level:**
- Each method has a single, well-defined purpose
- Validation methods only validate
- Persistence methods only persist
- Event publishing methods only publish events

### 2.2 Open/Closed Principle (OCP)

The service is designed for extension without modification:

**Extension Points:**
- **Error Categories**: New error types can be added through configuration without code changes
- **Validation Rules**: New validation logic can be added via strategy pattern
- **Event Publishers**: New event destinations can be added through publisher interfaces
- **Data Formats**: New input/output formats can be supported via adapter pattern

**Implementation Strategy:**
```python
# Abstract base for extensible validation
class ErrorValidationStrategy(ABC):
    @abstractmethod
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        pass

# Concrete implementations can be added without modifying existing code
class SeverityValidationStrategy(ErrorValidationStrategy):
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        # Implementation for severity validation
        pass

class ContextValidationStrategy(ErrorValidationStrategy):
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        # Implementation for context validation
        pass
```

### 2.3 Liskov Substitution Principle (LSP)

All implementations are fully substitutable:

**Database Adapters:**
- PostgreSQL and MongoDB adapters implement the same `ErrorRepositoryPort`
- Both provide identical behavior and honor the same contracts
- Switching between implementations requires no code changes

**Event Publishers:**
- Kafka, RabbitMQ, and in-memory publishers are interchangeable
- All implement the same `EventPublishingPort` interface
- Behavior is consistent across all implementations

**Cache Providers:**
- Redis, Memcached, and in-memory cache implementations are substitutable
- All honor the same caching contracts and timeouts

### 2.4 Interface Segregation Principle (ISP)

Interfaces are focused and client-specific:

**Segregated Interfaces:**
```python
# Read-only operations
class ErrorReaderPort(ABC):
    @abstractmethod
    async def get_by_id(self, error_id: str) -> Optional[ErrorReport]:
        pass

    @abstractmethod
    async def search(self, filters: ErrorFilters) -> List[ErrorReport]:
        pass

# Write-only operations
class ErrorWriterPort(ABC):
    @abstractmethod
    async def create(self, error_report: ErrorReport) -> str:
        pass

    @abstractmethod
    async def update(self, error_id: str, updates: ErrorReportUpdate) -> None:
        pass

# Validation-specific operations
class ErrorValidatorPort(ABC):
    @abstractmethod
    async def validate_error_report(self, error_report: ErrorReport) -> ValidationResult:
        pass

# Event-specific operations
class ErrorEventPort(ABC):
    @abstractmethod
    async def publish_error_created(self, error_report: ErrorReport) -> None:
        pass
```

**Benefits:**
- Controllers only depend on the interfaces they actually use
- Read-only services don't have access to write operations
- Validation services are isolated from persistence concerns

### 2.5 Dependency Inversion Principle (DIP)

High-level modules depend only on abstractions:

**Dependency Structure:**
```python
# High-level module (Use Case) depends on abstraction
class SubmitErrorReportUseCase:
    def __init__(
        self,
        error_repository: ErrorRepositoryPort,  # Abstraction
        event_publisher: EventPublishingPort,   # Abstraction
        validator: ErrorValidatorPort           # Abstraction
    ):
        self._error_repository = error_repository
        self._event_publisher = event_publisher
        self._validator = validator

# Low-level modules implement abstractions
class PostgreSQLErrorRepository(ErrorRepositoryPort):
    # Implementation details
    pass

class KafkaEventPublisher(EventPublishingPort):
    # Implementation details
    pass
```

**Dependency Injection:**
- All dependencies are injected at runtime
- Configuration determines concrete implementations
- Business logic is completely independent of infrastructure

---

## 3. Hexagonal Architecture Design

### 3.1 Architecture Overview (SOLID-Compliant)

```mermaid
graph TB
    subgraph "External Actors"
        QA[QA Personnel]
        API_GW[API Gateway]
    end

    subgraph "Error Reporting Service"
        subgraph "Ports (Interfaces)"
            HTTP_PORT[HTTP API Port<br/>ErrorReportingPort]
            EVENT_PORT[Event Publishing Port<br/>EventPublishingPort]
            VALIDATION_PORT[Validation Port<br/>ValidationPort]
            SEARCH_PORT[Search Port<br/>SearchPort]
        end
        
        subgraph "Core Domain (Business Logic)"
            DOMAIN[Error Report Domain<br/>• Error Validation Rules<br/>• Business Logic<br/>• Error Categorization<br/>• Severity Assessment]
            USE_CASES[Use Cases<br/>• Submit Error Report<br/>• Validate Error Data<br/>• Process Error Context<br/>• Search Errors<br/>• Update Error Status]
        end
        
        subgraph "Adapters (Infrastructure)"
            REST_ADAPTER[REST API Adapter<br/>FastAPI Controllers]
            EVENT_ADAPTER[Event Bus Adapter<br/>Kafka Producer]
            DB_ADAPTER[Database Adapter<br/>SQLAlchemy Repository]
            CACHE_ADAPTER[Cache Adapter<br/>Redis Client]
            AUTH_ADAPTER[Auth Adapter<br/>JWT Validation]
        end
    end

    subgraph "External Systems"
        UMS[User Management Service]
        POSTGRES[(PostgreSQL Database)]
        REDIS[(Redis Cache)]
        KAFKA[(Kafka Message Queue)]
    end

    %% External to Ports
    QA --> API_GW
    API_GW --> HTTP_PORT

    %% Ports to Core
    HTTP_PORT --> USE_CASES
    EVENT_PORT --> USE_CASES
    VALIDATION_PORT --> USE_CASES
    SEARCH_PORT --> USE_CASES
    USE_CASES --> DOMAIN

    %% Core to Adapters
    DOMAIN --> REST_ADAPTER
    DOMAIN --> EVENT_ADAPTER
    DOMAIN --> DB_ADAPTER
    DOMAIN --> CACHE_ADAPTER
    DOMAIN --> AUTH_ADAPTER

    %% Adapters to External Systems
    AUTH_ADAPTER --> UMS
    DB_ADAPTER --> POSTGRES
    CACHE_ADAPTER --> REDIS
    EVENT_ADAPTER --> KAFKA

    %% Styling
    classDef coreLogic fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef ports fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef adapters fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef external fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px

    class DOMAIN,USE_CASES coreLogic
    class HTTP_PORT,EVENT_PORT,VALIDATION_PORT,SEARCH_PORT ports
    class REST_ADAPTER,EVENT_ADAPTER,DB_ADAPTER,CACHE_ADAPTER,AUTH_ADAPTER adapters
    class UMS,POSTGRES,REDIS,KAFKA external
```

### 3.2 Port Definitions (SOLID-Aligned)

**Primary Ports (Driving) - Following ISP:**
- `ErrorReportingPort`: Main API interface for error operations (focused on core error operations)
- `ErrorSearchPort`: Advanced search and filtering capabilities (separated from main operations)
- `ErrorValidationPort`: Error validation and business rules (single responsibility for validation)

**Secondary Ports (Driven) - Following DIP:**
- `EventPublishingPort`: Async event publishing interface (abstraction for event systems)
- `ErrorRepositoryPort`: Data persistence interface (abstraction for data storage)
- `CachePort`: Caching operations interface (abstraction for caching systems)
- `AuthenticationPort`: User authentication interface (abstraction for auth systems)

**SOLID Benefits:**
- **ISP**: Clients depend only on the interfaces they use
- **DIP**: Core logic depends on abstractions, not concrete implementations
- **SRP**: Each port has a single, well-defined responsibility
- **OCP**: New ports can be added without modifying existing ones

---

## 4. API Specifications (SOLID-Compliant)

### 4.1 REST API Endpoints (Following SRP and ISP)

**Design Principles Applied:**
- **SRP**: Each endpoint has a single responsibility
- **ISP**: Endpoints are focused and don't force clients to depend on unused functionality
- **OCP**: New endpoints can be added without modifying existing ones
- **DIP**: Controllers depend on use case abstractions, not concrete implementations

#### 4.1.1 Error Report Management (SRP-Compliant)

```python
# POST /api/v1/errors
@router.post("/errors", response_model=ErrorReportResponse)
async def submit_error_report(
    request: ErrorReportRequest,
    current_user: User = Depends(get_current_user)
) -> ErrorReportResponse:
    """Submit a new error report"""

# GET /api/v1/errors/{error_id}
@router.get("/errors/{error_id}", response_model=ErrorReportResponse)
async def get_error_report(
    error_id: str,
    current_user: User = Depends(get_current_user)
) -> ErrorReportResponse:
    """Retrieve a specific error report"""

# PUT /api/v1/errors/{error_id}
@router.put("/errors/{error_id}", response_model=ErrorReportResponse)
async def update_error_report(
    error_id: str,
    updates: ErrorReportUpdateRequest,
    current_user: User = Depends(get_current_user)
) -> ErrorReportResponse:
    """Update an existing error report"""

# DELETE /api/v1/errors/{error_id}
@router.delete("/errors/{error_id}", status_code=204)
async def delete_error_report(
    error_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete an error report"""
```

#### 4.1.2 Search and Filtering (ISP-Compliant)

```python
# GET /api/v1/errors
@router.get("/errors", response_model=PaginatedErrorReports)
async def search_errors(
    filters: ErrorFilters = Depends(),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user)
) -> PaginatedErrorReports:
    """Search and filter error reports"""

# GET /api/v1/errors/by-job/{job_id}
@router.get("/errors/by-job/{job_id}", response_model=PaginatedErrorReports)
async def get_errors_by_job(
    job_id: str,
    filters: ErrorFilters = Depends(),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user)
) -> PaginatedErrorReports:
    """Get errors for a specific job"""

# GET /api/v1/errors/by-speaker/{speaker_id}
@router.get("/errors/by-speaker/{speaker_id}", response_model=PaginatedErrorReports)
async def get_errors_by_speaker(
    speaker_id: str,
    filters: ErrorFilters = Depends(),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user)
) -> PaginatedErrorReports:
    """Get errors for a specific speaker"""
```

### 4.2 Data Models (SOLID-Designed)

#### 3.2.1 Request Models

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
from datetime import datetime

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    SUBSTITUTION = "substitution"
    INSERTION = "insertion"
    DELETION = "deletion"
    PRONUNCIATION = "pronunciation"
    GRAMMAR = "grammar"
    CONTEXT = "context"

class ErrorMetadata(BaseModel):
    audio_quality: Optional[str] = None
    background_noise: Optional[bool] = None
    speaker_accent: Optional[str] = None
    technical_issues: Optional[List[str]] = None

class ErrorReportRequest(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    speaker_id: str = Field(..., description="Speaker identifier")
    original_text: str = Field(..., min_length=1, max_length=10000)
    corrected_text: str = Field(..., min_length=1, max_length=10000)
    error_categories: List[ErrorCategory] = Field(..., min_items=1)
    severity_level: SeverityLevel
    start_position: int = Field(..., ge=0)
    end_position: int = Field(..., ge=0)
    context_notes: Optional[str] = Field(None, max_length=1000)
    metadata: ErrorMetadata

    @validator('end_position')
    def validate_positions(cls, v, values):
        if 'start_position' in values and v <= values['start_position']:
            raise ValueError('end_position must be greater than start_position')
        return v
```

#### 3.2.2 Response Models

```python
class ErrorReportResponse(BaseModel):
    id: str
    job_id: str
    speaker_id: str
    original_text: str
    corrected_text: str
    error_categories: List[ErrorCategory]
    severity_level: SeverityLevel
    start_position: int
    end_position: int
    context_notes: Optional[str]
    metadata: ErrorMetadata
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    version: int

class PaginatedErrorReports(BaseModel):
    items: List[ErrorReportResponse]
    total: int
    page: int
    size: int
    pages: int
```

---

## 4. Database Schema Design

### 4.1 Entity Relationship Diagram

```mermaid
erDiagram
    ERROR_REPORTS {
        uuid id PK
        string job_id
        string speaker_id
        text original_text
        text corrected_text
        integer start_position
        integer end_position
        string severity_level
        text context_notes
        jsonb metadata
        string status
        timestamp created_at
        timestamp updated_at
        string created_by
        integer version
    }

    ERROR_CATEGORIES {
        uuid id PK
        uuid error_report_id FK
        string category_type
        timestamp created_at
    }

    ERROR_AUDIT_LOG {
        uuid id PK
        uuid error_report_id FK
        string action
        jsonb old_values
        jsonb new_values
        string user_id
        timestamp created_at
    }

    ERROR_REPORTS ||--o{ ERROR_CATEGORIES : has
    ERROR_REPORTS ||--o{ ERROR_AUDIT_LOG : tracks
```

### 4.2 Table Definitions

#### 4.2.1 error_reports Table

```sql
CREATE TABLE error_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) NOT NULL,
    speaker_id VARCHAR(255) NOT NULL,
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    start_position INTEGER NOT NULL CHECK (start_position >= 0),
    end_position INTEGER NOT NULL CHECK (end_position > start_position),
    severity_level VARCHAR(20) NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    context_notes TEXT,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1
);

-- Indexes for performance
CREATE INDEX idx_error_reports_job_id ON error_reports(job_id);
CREATE INDEX idx_error_reports_speaker_id ON error_reports(speaker_id);
CREATE INDEX idx_error_reports_created_at ON error_reports(created_at);
CREATE INDEX idx_error_reports_severity ON error_reports(severity_level);
CREATE INDEX idx_error_reports_status ON error_reports(status);
CREATE INDEX idx_error_reports_metadata ON error_reports USING GIN(metadata);
```

#### 4.2.2 error_categories Table

```sql
CREATE TABLE error_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    error_report_id UUID NOT NULL REFERENCES error_reports(id) ON DELETE CASCADE,
    category_type VARCHAR(50) NOT NULL CHECK (category_type IN (
        'substitution', 'insertion', 'deletion', 'pronunciation', 'grammar', 'context'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_error_categories_report_id ON error_categories(error_report_id);
CREATE INDEX idx_error_categories_type ON error_categories(category_type);
```

#### 4.2.3 error_audit_log Table

```sql
CREATE TABLE error_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    error_report_id UUID NOT NULL REFERENCES error_reports(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL CHECK (action IN ('created', 'updated', 'deleted')),
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_error_audit_log_report_id ON error_audit_log(error_report_id);
CREATE INDEX idx_error_audit_log_user_id ON error_audit_log(user_id);
CREATE INDEX idx_error_audit_log_created_at ON error_audit_log(created_at);
```

---

## 5. Integration Points

### 5.1 Event Publishing

#### 5.1.1 Event Schemas

```python
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class BaseEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    version: str = "1.0"
    source: str = "error-reporting-service"
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ErrorReportedEventData(BaseModel):
    error_id: str
    job_id: str
    speaker_id: str
    original_text: str
    corrected_text: str
    categories: List[str]
    severity: str
    start_position: int
    end_position: int
    context_notes: Optional[str]
    metadata: Dict[str, Any]
    created_by: str

class ErrorReportedEvent(BaseEvent):
    event_type: str = "error.reported"
    data: ErrorReportedEventData

class ErrorUpdatedEventData(BaseModel):
    error_id: str
    changes: Dict[str, Any]
    updated_by: str

class ErrorUpdatedEvent(BaseEvent):
    event_type: str = "error.updated"
    data: ErrorUpdatedEventData

class ErrorDeletedEventData(BaseModel):
    error_id: str
    deleted_by: str

class ErrorDeletedEvent(BaseEvent):
    event_type: str = "error.deleted"
    data: ErrorDeletedEventData
```

#### 5.1.2 Kafka Topics

```yaml
# Kafka topic configuration
topics:
  error-events:
    partitions: 6
    replication_factor: 3
    config:
      retention.ms: 604800000  # 7 days
      compression.type: snappy
      cleanup.policy: delete
```

### 5.2 Service Dependencies

#### 5.2.1 User Management Service Integration

```python
class AuthenticationAdapter:
    async def validate_token(self, token: str) -> TokenValidationResult:
        """Validate JWT token with User Management Service"""

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions for authorization"""
```

#### 5.2.2 External System Integrations

```mermaid
sequenceDiagram
    participant QA as QA Personnel
    participant ERS as Error Reporting Service
    participant UMS as User Management Service
    participant DB as PostgreSQL
    participant KAFKA as Kafka
    participant RIS as RAG Integration Service

    QA->>ERS: Submit Error Report
    ERS->>UMS: Validate Token
    UMS-->>ERS: User Info
    ERS->>ERS: Validate Error Data
    ERS->>DB: Store Error Report
    DB-->>ERS: Confirmation
    ERS->>KAFKA: Publish Error Event
    KAFKA-->>RIS: Error Reported Event
    ERS-->>QA: Success Response
```

---

## 6. Error Handling Strategy

### 6.1 Error Categories

```python
from enum import Enum

class ErrorCode(str, Enum):
    # Validation Errors (400)
    INVALID_REQUEST = "INVALID_REQUEST"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"
    INVALID_POSITION_RANGE = "INVALID_POSITION_RANGE"

    # Authentication/Authorization Errors (401/403)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TOKEN = "INVALID_TOKEN"

    # Resource Errors (404)
    ERROR_REPORT_NOT_FOUND = "ERROR_REPORT_NOT_FOUND"

    # Conflict Errors (409)
    DUPLICATE_ERROR_REPORT = "DUPLICATE_ERROR_REPORT"
    VERSION_CONFLICT = "VERSION_CONFLICT"

    # Server Errors (500)
    DATABASE_ERROR = "DATABASE_ERROR"
    EVENT_PUBLISHING_ERROR = "EVENT_PUBLISHING_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
```

### 6.2 Error Response Format

```python
class ErrorDetail(BaseModel):
    field: str
    message: str
    code: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorInfo
    timestamp: datetime
    request_id: str
    version: str = "1.0"

class ErrorInfo(BaseModel):
    code: ErrorCode
    message: str
    details: Optional[List[ErrorDetail]] = None
    trace_id: Optional[str] = None
```

### 6.3 Exception Handling

```python
from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler

class ErrorReportingException(Exception):
    def __init__(self, code: ErrorCode, message: str, details: List[ErrorDetail] = None):
        self.code = code
        self.message = message
        self.details = details or []

class ValidationException(ErrorReportingException):
    pass

class AuthenticationException(ErrorReportingException):
    pass

class ResourceNotFoundException(ErrorReportingException):
    pass

@app.exception_handler(ErrorReportingException)
async def error_reporting_exception_handler(request: Request, exc: ErrorReportingException):
    return JSONResponse(
        status_code=get_status_code(exc.code),
        content=ErrorResponse(
            error=ErrorInfo(
                code=exc.code,
                message=exc.message,
                details=exc.details
            ),
            timestamp=datetime.utcnow(),
            request_id=request.headers.get("X-Request-ID", str(uuid.uuid4())),
        ).dict()
    )
```

---

## 7. Technology Implementation

### 7.1 FastAPI Application Setup

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_database()
    await initialize_kafka_producer()
    await initialize_redis_client()
    yield
    # Shutdown
    await cleanup_resources()

app = FastAPI(
    title="Error Reporting Service",
    description="ASR Error Reporting System - Error Management Service",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.example.com"]
)
```

### 7.2 Dependency Injection

```python
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()

    # Database
    database = providers.Singleton(
        Database,
        url=config.database.url,
        pool_size=config.database.pool_size,
    )

    # Cache
    redis_client = providers.Singleton(
        RedisClient,
        url=config.redis.url,
    )

    # Message Queue
    kafka_producer = providers.Singleton(
        KafkaProducer,
        bootstrap_servers=config.kafka.bootstrap_servers,
    )

    # Repositories
    error_repository = providers.Factory(
        ErrorReportRepository,
        database=database,
    )

    # Services
    error_service = providers.Factory(
        ErrorReportService,
        repository=error_repository,
        event_publisher=kafka_producer,
        cache=redis_client,
    )
```

---

## 8. Custom Error Categorization

### 8.1 Custom Category Management

The Error Reporting Service supports user-defined error categories in addition to the predefined system categories. This allows organizations to create domain-specific categorization schemes that match their workflow requirements.

#### 8.1.1 Custom Category Features

**Category Creation:**
- User-defined category names and descriptions
- Category approval workflow for quality control
- Category versioning and lifecycle management
- Category sharing across teams and organizations

**Category Validation:**
- Duplicate category name prevention
- Category naming conventions enforcement
- Category description requirements
- Category usage analytics and recommendations

**Category Management:**
- Category search and filtering functionality
- Category usage statistics and analytics
- Category deprecation and migration support
- Category hierarchy and parent-child relationships

#### 8.1.2 Custom Category Data Model

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

class CategoryStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DEPRECATED = "deprecated"

class CategoryScope(str, Enum):
    PERSONAL = "personal"
    TEAM = "team"
    ORGANIZATION = "organization"
    GLOBAL = "global"

@dataclass
class CustomErrorCategory:
    id: UUID
    name: str
    description: str
    created_by: UUID
    organization_id: UUID
    status: CategoryStatus
    scope: CategoryScope
    parent_category_id: Optional[UUID] = None
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    replacement_category_id: Optional[UUID] = None
```

#### 8.1.3 Custom Category Database Schema

```sql
CREATE TABLE custom_error_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by UUID NOT NULL,
    organization_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN (
        'draft', 'pending_approval', 'approved', 'deprecated'
    )),
    scope VARCHAR(20) NOT NULL DEFAULT 'personal' CHECK (scope IN (
        'personal', 'team', 'organization', 'global'
    )),
    parent_category_id UUID REFERENCES custom_error_categories(id),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    deprecated_at TIMESTAMP WITH TIME ZONE,
    replacement_category_id UUID REFERENCES custom_error_categories(id),

    CONSTRAINT unique_category_name_per_org UNIQUE (name, organization_id, scope),
    CONSTRAINT no_self_reference CHECK (id != parent_category_id),
    CONSTRAINT no_self_replacement CHECK (id != replacement_category_id)
);

CREATE INDEX idx_custom_categories_org_status ON custom_error_categories(organization_id, status);
CREATE INDEX idx_custom_categories_created_by ON custom_error_categories(created_by);
CREATE INDEX idx_custom_categories_parent ON custom_error_categories(parent_category_id);
CREATE INDEX idx_custom_categories_name ON custom_error_categories(name);
```

#### 8.1.4 Custom Category API Endpoints

```python
# POST /api/v1/categories/custom
@router.post("/categories/custom", response_model=CustomCategoryResponse)
async def create_custom_category(
    request: CreateCustomCategoryRequest,
    current_user: User = Depends(get_current_user)
) -> CustomCategoryResponse:
    """Create a new custom error category"""

# GET /api/v1/categories/custom
@router.get("/categories/custom", response_model=PaginatedCustomCategories)
async def list_custom_categories(
    filters: CustomCategoryFilters = Depends(),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user)
) -> PaginatedCustomCategories:
    """List custom categories with filtering"""

# PUT /api/v1/categories/custom/{category_id}
@router.put("/categories/custom/{category_id}", response_model=CustomCategoryResponse)
async def update_custom_category(
    category_id: str,
    request: UpdateCustomCategoryRequest,
    current_user: User = Depends(get_current_user)
) -> CustomCategoryResponse:
    """Update a custom error category"""

# POST /api/v1/categories/custom/{category_id}/approve
@router.post("/categories/custom/{category_id}/approve", status_code=204)
async def approve_custom_category(
    category_id: str,
    current_user: User = Depends(require_category_approver)
) -> None:
    """Approve a custom category for organization use"""

# POST /api/v1/categories/custom/{category_id}/deprecate
@router.post("/categories/custom/{category_id}/deprecate", status_code=204)
async def deprecate_custom_category(
    category_id: str,
    request: DeprecateCustomCategoryRequest,
    current_user: User = Depends(require_category_manager)
) -> None:
    """Deprecate a custom category and optionally provide replacement"""
```

---

## 9. Directory Structure

```
error-reporting-service/
├── src/
│   ├── domain/                          # Business logic (pure, no dependencies)
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── error_report.py          # ErrorReport entity
│   │   │   ├── error_category.py        # ErrorCategory entity
│   │   │   └── audit_log.py             # AuditLog entity
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── severity_level.py        # SeverityLevel enum
│   │   │   ├── error_metadata.py        # ErrorMetadata value object
│   │   │   └── position_range.py        # PositionRange value object
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── error_repository.py      # Abstract repository interface
│   │   │   └── audit_repository.py      # Abstract audit repository
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── validation_service.py    # Business validation rules
│   │       ├── categorization_service.py # Error categorization logic
│   │       └── custom_category_service.py # Custom category management
│   ├── application/                     # Use cases and application services
│   │   ├── __init__.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── submit_error_report.py   # Submit error use case
│   │   │   ├── update_error_report.py   # Update error use case
│   │   │   ├── search_errors.py         # Search errors use case
│   │   │   └── delete_error_report.py   # Delete error use case
│   │   ├── dto/
│   │   │   ├── __init__.py
│   │   │   ├── requests.py              # Pydantic request models
│   │   │   ├── responses.py             # Pydantic response models
│   │   │   └── events.py                # Event schemas
│   │   └── ports/
│   │       ├── __init__.py
│   │       ├── error_reporting_port.py  # Primary port interface
│   │       ├── event_publishing_port.py # Event publishing interface
│   │       └── validation_port.py       # Validation interface
│   ├── infrastructure/                  # Adapters and external concerns
│   │   ├── __init__.py
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── database/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # SQLAlchemy models
│   │   │   │   ├── repositories.py      # Repository implementations
│   │   │   │   └── migrations/          # Alembic migrations
│   │   │   ├── http/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── controllers.py       # FastAPI controllers
│   │   │   │   ├── dependencies.py      # FastAPI dependencies
│   │   │   │   └── middleware.py        # Custom middleware
│   │   │   ├── messaging/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── kafka_producer.py    # Kafka event publisher
│   │   │   │   └── event_serializer.py  # Event serialization
│   │   │   ├── cache/
│   │   │   │   ├── __init__.py
│   │   │   │   └── redis_adapter.py     # Redis cache implementation
│   │   │   └── external/
│   │   │       ├── __init__.py
│   │   │       └── auth_client.py       # User Management Service client
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py              # Pydantic settings
│   │   │   └── container.py             # Dependency injection container
│   │   └── database/
│   │       ├── __init__.py
│   │       └── connection.py            # Database connection setup
│   ├── main.py                          # FastAPI app setup
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── unit/                            # Unit tests
│   │   ├── __init__.py
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/                     # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── fixtures/                        # Test fixtures
│       ├── __init__.py
│       └── error_data.py
├── alembic/                             # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── k8s/                                 # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── pyproject.toml                       # Poetry configuration
├── README.md
└── .env.example
```

---

## 9. Key Classes and Interfaces

### 9.1 Domain Entities

```python
# src/domain/entities/error_report.py
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from uuid import UUID

@dataclass
class ErrorReport:
    id: UUID
    job_id: str
    speaker_id: str
    original_text: str
    corrected_text: str
    start_position: int
    end_position: int
    severity_level: str
    categories: List[str]
    context_notes: Optional[str]
    metadata: dict
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    version: int

    def validate_positions(self) -> bool:
        """Validate that position range is valid"""
        return self.end_position > self.start_position >= 0

    def calculate_error_length(self) -> int:
        """Calculate the length of the error in characters"""
        return self.end_position - self.start_position

    def is_critical(self) -> bool:
        """Check if error is critical severity"""
        return self.severity_level == "critical"
```

### 9.2 Repository Interfaces

```python
# src/domain/repositories/error_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.error_report import ErrorReport

class ErrorRepositoryPort(ABC):
    @abstractmethod
    async def save(self, error_report: ErrorReport) -> ErrorReport:
        """Save an error report"""
        pass

    @abstractmethod
    async def find_by_id(self, error_id: UUID) -> Optional[ErrorReport]:
        """Find error report by ID"""
        pass

    @abstractmethod
    async def find_by_job_id(self, job_id: str, limit: int = 100, offset: int = 0) -> List[ErrorReport]:
        """Find error reports by job ID"""
        pass

    @abstractmethod
    async def find_by_speaker_id(self, speaker_id: str, limit: int = 100, offset: int = 0) -> List[ErrorReport]:
        """Find error reports by speaker ID"""
        pass

    @abstractmethod
    async def search(self, filters: dict, limit: int = 100, offset: int = 0) -> List[ErrorReport]:
        """Search error reports with filters"""
        pass

    @abstractmethod
    async def update(self, error_report: ErrorReport) -> ErrorReport:
        """Update an error report"""
        pass

    @abstractmethod
    async def delete(self, error_id: UUID) -> bool:
        """Delete an error report"""
        pass

    @abstractmethod
    async def count_by_filters(self, filters: dict) -> int:
        """Count error reports matching filters"""
        pass
```

### 9.3 Use Case Implementation

```python
# src/application/use_cases/submit_error_report.py
from dataclasses import dataclass
from typing import List
from uuid import uuid4
from datetime import datetime

from ..dto.requests import ErrorReportRequest
from ..dto.responses import ErrorReportResponse
from ..ports.error_reporting_port import ErrorReportingPort
from ..ports.event_publishing_port import EventPublishingPort
from ...domain.entities.error_report import ErrorReport
from ...domain.repositories.error_repository import ErrorRepositoryPort
from ...domain.services.validation_service import ValidationService

@dataclass
class SubmitErrorReportUseCase:
    error_repository: ErrorRepositoryPort
    event_publisher: EventPublishingPort
    validation_service: ValidationService

    async def execute(self, request: ErrorReportRequest, user_id: str) -> ErrorReportResponse:
        # Validate business rules
        await self.validation_service.validate_error_report(request)

        # Create domain entity
        error_report = ErrorReport(
            id=uuid4(),
            job_id=request.job_id,
            speaker_id=request.speaker_id,
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            start_position=request.start_position,
            end_position=request.end_position,
            severity_level=request.severity_level.value,
            categories=[cat.value for cat in request.error_categories],
            context_notes=request.context_notes,
            metadata=request.metadata.dict(),
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=user_id,
            version=1
        )

        # Save to repository
        saved_error = await self.error_repository.save(error_report)

        # Publish event
        await self.event_publisher.publish_error_reported(saved_error)

        # Return response
        return ErrorReportResponse.from_entity(saved_error)
```

### 9.4 FastAPI Controller

```python
# src/infrastructure/adapters/http/controllers.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from ....application.use_cases.submit_error_report import SubmitErrorReportUseCase
from ....application.dto.requests import ErrorReportRequest
from ....application.dto.responses import ErrorReportResponse, PaginatedErrorReports
from .dependencies import get_current_user, get_submit_error_use_case

router = APIRouter(prefix="/api/v1/errors", tags=["Error Reports"])

@router.post("/", response_model=ErrorReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_error_report(
    request: ErrorReportRequest,
    current_user: dict = Depends(get_current_user),
    use_case: SubmitErrorReportUseCase = Depends(get_submit_error_use_case)
) -> ErrorReportResponse:
    """Submit a new error report"""
    try:
        return await use_case.execute(request, current_user["user_id"])
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message, "details": e.details}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )
```

---

## 10. Configuration Management

### 10.1 Settings Configuration

```python
# src/infrastructure/config/settings.py
from pydantic import BaseSettings, Field
from typing import List, Optional

class DatabaseSettings(BaseSettings):
    url: str = Field(..., env="DATABASE_URL")
    pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    echo: bool = Field(False, env="DATABASE_ECHO")

class RedisSettings(BaseSettings):
    url: str = Field(..., env="REDIS_URL")
    max_connections: int = Field(10, env="REDIS_MAX_CONNECTIONS")
    retry_on_timeout: bool = Field(True, env="REDIS_RETRY_ON_TIMEOUT")

class KafkaSettings(BaseSettings):
    bootstrap_servers: List[str] = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    topic_prefix: str = Field("asr", env="KAFKA_TOPIC_PREFIX")
    producer_config: dict = Field(
        default_factory=lambda: {
            "acks": "all",
            "retries": 3,
            "compression_type": "snappy"
        }
    )

class AuthSettings(BaseSettings):
    user_management_service_url: str = Field(..., env="USER_MANAGEMENT_SERVICE_URL")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    token_expire_minutes: int = Field(30, env="TOKEN_EXPIRE_MINUTES")

class Settings(BaseSettings):
    app_name: str = "Error Reporting Service"
    app_version: str = "1.0.0"
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    kafka: KafkaSettings = KafkaSettings()
    auth: AuthSettings = AuthSettings()

    # API Configuration
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = Field(["*"], env="CORS_ORIGINS")
    trusted_hosts: List[str] = Field(["localhost"], env="TRUSTED_HOSTS")

    # Performance Configuration
    max_request_size: int = Field(1024 * 1024, env="MAX_REQUEST_SIZE")  # 1MB
    request_timeout: int = Field(30, env="REQUEST_TIMEOUT")  # 30 seconds

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

settings = Settings()
```

### 10.2 Environment Configuration

```bash
# .env.example
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/error_reporting
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=false

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=10
REDIS_RETRY_ON_TIMEOUT=true

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092,localhost:9093,localhost:9094
KAFKA_TOPIC_PREFIX=asr

# Authentication Configuration
USER_MANAGEMENT_SERVICE_URL=http://localhost:8001
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
TRUSTED_HOSTS=localhost,*.example.com

# Performance Configuration
MAX_REQUEST_SIZE=1048576
REQUEST_TIMEOUT=30
```

---

## 11. Dependency Management

### 11.1 Poetry Configuration

```toml
# pyproject.toml
[tool.poetry]
name = "error-reporting-service"
version = "1.0.0"
description = "ASR Error Reporting System - Error Management Service"
authors = ["Development Team <dev@example.com>"]
readme = "README.md"
packages = [{include = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = {extras = ["email"], version = "^2.4.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.0"}
asyncpg = "^0.29.0"
alembic = "^1.12.0"
redis = {extras = ["hiredis"], version = "^5.0.0"}
aiokafka = "^0.8.0"
httpx = "^0.25.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
dependency-injector = "^4.41.0"
prometheus-client = "^0.18.0"
opentelemetry-api = "^1.20.0"
opentelemetry-sdk = "^1.20.0"
opentelemetry-instrumentation-fastapi = "^0.41b0"
structlog = "^23.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-mock = "^3.12.0"
httpx = "^0.25.0"
pytest-postgresql = "^5.0.0"
testcontainers = "^3.7.0"
black = "^23.9.0"
isort = "^5.12.0"
flake8 = "^6.1.0"
mypy = "^1.6.0"
coverage = "^7.3.0"
pre-commit = "^3.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 100
known_first_party = ["src"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "slow: marks tests as slow running",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\bProtocol\):",
    "@(abc\.)?abstractmethod",
]
```

---

## 12. User Stories

### 12.1 Epic: Error Report Management

#### 12.1.1 User Story: Submit Error Report
**As a** QA personnel
**I want to** submit error reports for ASR transcription mistakes
**So that** the system can learn and improve future transcriptions

**Acceptance Criteria:**
- [ ] I can select text in the transcription interface
- [ ] I can provide corrected text for the selected error
- [ ] I can categorize the error type (substitution, insertion, deletion, etc.)
- [ ] I can set the severity level (low, medium, high, critical)
- [ ] I can add context notes explaining the error
- [ ] I can include metadata about audio quality and conditions
- [ ] The system validates my input before submission
- [ ] I receive confirmation when the error is successfully submitted
- [ ] The error is immediately available for search and analysis

**Story Points:** 8

**Technical Tasks:**
- [ ] Implement error report validation logic
- [ ] Create REST API endpoint for error submission
- [ ] Design database schema for error storage
- [ ] Implement event publishing for downstream services
- [ ] Add comprehensive error handling and validation

#### 12.1.2 User Story: View Error Report Details
**As a** QA personnel
**I want to** view detailed information about submitted error reports
**So that** I can review and verify the accuracy of reported errors

**Acceptance Criteria:**
- [ ] I can view all details of an error report including original and corrected text
- [ ] I can see the error categories and severity level
- [ ] I can view context notes and metadata
- [ ] I can see audit information (who created, when, last modified)
- [ ] I can see the current status of the error report
- [ ] The interface clearly highlights the error location in the text

**Story Points:** 3

**Technical Tasks:**
- [ ] Implement GET endpoint for error report retrieval
- [ ] Create response models with complete error information
- [ ] Add authorization checks for error access
- [ ] Implement caching for frequently accessed errors

#### 12.1.3 User Story: Update Error Report
**As a** QA personnel
**I want to** update error reports after submission
**So that** I can correct mistakes or add additional information

**Acceptance Criteria:**
- [ ] I can modify the corrected text of an error report
- [ ] I can update error categories and severity level
- [ ] I can add or modify context notes
- [ ] I can update metadata information
- [ ] The system tracks all changes with audit trail
- [ ] I cannot modify certain fields like original text or position
- [ ] The system prevents concurrent modifications with optimistic locking

**Story Points:** 5

**Technical Tasks:**
- [ ] Implement PUT endpoint for error report updates
- [ ] Add optimistic locking with version control
- [ ] Implement audit logging for all changes
- [ ] Add validation for updateable fields
- [ ] Publish update events to downstream services

#### 12.1.4 User Story: Delete Error Report
**As a** QA personnel with appropriate permissions
**I want to** delete error reports that were submitted in error
**So that** the system maintains data quality and accuracy

**Acceptance Criteria:**
- [ ] I can delete error reports that I created
- [ ] Supervisors can delete any error report
- [ ] The system asks for confirmation before deletion
- [ ] Deleted errors are soft-deleted and maintain audit trail
- [ ] Related data (categories, audit logs) are properly handled
- [ ] Downstream services are notified of the deletion

**Story Points:** 3

**Technical Tasks:**
- [ ] Implement DELETE endpoint with authorization
- [ ] Add soft delete functionality
- [ ] Implement cascade deletion for related entities
- [ ] Publish deletion events
- [ ] Add confirmation mechanisms

### 12.2 Epic: Error Search and Analysis

#### 12.2.1 User Story: Search Error Reports
**As a** QA personnel
**I want to** search and filter error reports
**So that** I can analyze patterns and find specific errors

**Acceptance Criteria:**
- [ ] I can search errors by job ID, speaker ID, or text content
- [ ] I can filter by error categories, severity, and date range
- [ ] I can filter by error status (active, resolved, archived)
- [ ] I can sort results by various fields (date, severity, etc.)
- [ ] The search results are paginated for performance
- [ ] I can export search results for external analysis
- [ ] The search is fast and responsive (< 2 seconds)

**Story Points:** 8

**Technical Tasks:**
- [ ] Implement advanced search endpoint with multiple filters
- [ ] Add database indexes for search performance
- [ ] Implement pagination and sorting
- [ ] Add caching for common search queries
- [ ] Create export functionality

#### 12.2.2 User Story: View Error Statistics
**As a** QA supervisor
**I want to** view statistics about error reports
**So that** I can understand error patterns and system performance

**Acceptance Criteria:**
- [ ] I can see total error counts by category and severity
- [ ] I can view error trends over time
- [ ] I can see error distribution by speaker and job
- [ ] I can filter statistics by date range and other criteria
- [ ] The statistics are updated in real-time
- [ ] I can export statistical reports

**Story Points:** 5

**Technical Tasks:**
- [ ] Implement statistics aggregation endpoints
- [ ] Add real-time statistics calculation
- [ ] Implement caching for statistical queries
- [ ] Create export functionality for reports

### 12.3 Epic: System Integration

#### 12.3.1 User Story: Event Publishing
**As a** system administrator
**I want** error events to be published to other services
**So that** the RAG system can process errors for pattern learning

**Acceptance Criteria:**
- [ ] Error reported events are published immediately upon submission
- [ ] Error updated events are published when errors are modified
- [ ] Error deleted events are published when errors are removed
- [ ] Events include all necessary data for downstream processing
- [ ] Event publishing is reliable with retry mechanisms
- [ ] Failed events are logged and can be replayed

**Story Points:** 5

**Technical Tasks:**
- [ ] Implement Kafka event publishing
- [ ] Design event schemas for all error operations
- [ ] Add retry mechanisms and error handling
- [ ] Implement event ordering and deduplication
- [ ] Add monitoring and alerting for event publishing

#### 12.3.2 User Story: Authentication Integration
**As a** system user
**I want** to authenticate using the central user management system
**So that** I have secure access to the error reporting functionality

**Acceptance Criteria:**
- [ ] I can authenticate using my existing credentials
- [ ] The system validates my permissions for each operation
- [ ] My session is maintained securely across requests
- [ ] I am automatically logged out after inactivity
- [ ] The system integrates seamlessly with the user management service

**Story Points:** 3

**Technical Tasks:**
- [ ] Implement JWT token validation
- [ ] Add authorization middleware
- [ ] Integrate with User Management Service
- [ ] Implement session management
- [ ] Add security headers and CORS configuration

### 12.4 Story Point Summary

| Epic | Stories | Total Story Points |
|------|---------|-------------------|
| Error Report Management | 4 stories | 19 points |
| Error Search and Analysis | 2 stories | 13 points |
| System Integration | 2 stories | 8 points |
| **Total** | **8 stories** | **40 points** |

**Estimated Development Time:** 6-8 weeks for 3-4 developers

---

**Document Status:** ✅ Complete
**Next Steps:** Begin implementation following the hexagonal architecture pattern
**Dependencies:** User Management Service for authentication
**Integration Points:** RAG Integration Service, Verification Service
```
```
```
