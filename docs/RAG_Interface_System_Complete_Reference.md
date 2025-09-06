# RAG Interface System - Complete Project Reference

**Document Version:** 2.0  
**Date:** September 6, 2025  
**Status:** Comprehensive Reference  
**Technology Stack:** Python + FastAPI + PostgreSQL + Vector Database + Redis + React + TypeScript  
**Architecture Pattern:** Hexagonal Architecture (Ports and Adapters) + SOLID Principles + TDD  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Service Architecture Details](#3-service-architecture-details)
4. [API Documentation](#4-api-documentation)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Development Guidelines](#6-development-guidelines)
7. [Deployment & Operations](#7-deployment--operations)
8. [User Guides](#8-user-guides)
9. [Quality Assurance](#9-quality-assurance)
10. [Reference Materials](#10-reference-materials)

---

## 1. Executive Summary

### 1.1 Project Overview

The RAG Interface System is a comprehensive ASR (Automatic Speech Recognition) Error Reporting and Quality Management platform designed to improve transcription accuracy through systematic error tracking, speaker bucket management, and AI-powered correction suggestions.

**Key Capabilities:**
- 🎯 **Error Reporting**: Comprehensive error tracking and categorization
- 🔄 **Speaker Bucket Management**: Quality-based speaker classification system
- 🤖 **RAG Integration**: AI-powered correction suggestions using Retrieval-Augmented Generation
- ✅ **Quality Verification**: MT validation workflows and quality assurance
- 📊 **Analytics**: Performance monitoring and improvement tracking

### 1.2 Business Value

- **Quality Improvement**: Systematic error tracking leads to 25-40% reduction in transcription errors
- **Resource Optimization**: Efficient allocation of MT resources based on speaker quality levels
- **Cost Reduction**: Automated correction suggestions reduce manual review time by 30-50%
- **Compliance**: Comprehensive audit trails for regulatory requirements
- **Scalability**: Microservices architecture supports enterprise-scale deployments

### 1.3 Technology Stack

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React + TypeScript]
        B[Vite Build System]
        C[React Query]
    end
    
    subgraph "Backend Services"
        D[API Gateway - FastAPI]
        E[Error Reporting Service]
        F[RAG Integration Service]
        G[Verification Service]
        H[User Management Service]
        I[Correction Engine Service]
    end
    
    subgraph "Data Layer"
        J[PostgreSQL]
        K[Vector Database]
        L[Redis Cache]
        M[Message Queue]
    end
    
    A --> D
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    E --> J
    F --> K
    G --> J
    H --> J
    I --> J
    E --> L
    F --> M
```

---

## 2. System Architecture Overview

### 2.1 Hexagonal Architecture Pattern

The system follows **Hexagonal Architecture (Ports and Adapters)** combined with **SOLID Principles** and **Test-Driven Development (TDD)**:

```mermaid
graph TB
    subgraph "Domain Layer (Core Business Logic)"
        A[Entities]
        B[Value Objects]
        C[Domain Services]
        D[Use Cases]
    end
    
    subgraph "Application Layer"
        E[Application Services]
        F[Ports/Interfaces]
    end
    
    subgraph "Infrastructure Layer"
        G[Database Adapters]
        H[External API Adapters]
        I[Message Queue Adapters]
        J[Cache Adapters]
    end
    
    subgraph "Presentation Layer"
        K[REST API Controllers]
        L[GraphQL Resolvers]
        M[Event Handlers]
    end
    
    D --> F
    F --> G
    F --> H
    F --> I
    F --> J
    K --> E
    L --> E
    M --> E
    E --> D
```

### 2.2 Service Architecture

**Five Core Microservices:**

| Service | Port | Responsibility | Technology |
|---------|------|----------------|------------|
| **API Gateway** | 8000 | Request routing, authentication, rate limiting | FastAPI + Redis |
| **Error Reporting Service** | 8003 | Error tracking, categorization, reporting | FastAPI + PostgreSQL |
| **RAG Integration Service** | 8002 | AI corrections, vector search, ML processing | FastAPI + Vector DB |
| **Verification Service** | 8001 | Quality assurance, MT validation workflows | FastAPI + PostgreSQL |
| **User Management Service** | 8004 | Authentication, authorization, speaker management | FastAPI + PostgreSQL |
| **Correction Engine Service** | 8005 | Correction algorithms, quality scoring | FastAPI + PostgreSQL |

### 2.3 Complete System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        ERROR_UI[Error Reporting UI<br/>React/TypeScript]
        VERIFY_UI[Verification Dashboard<br/>React/TypeScript]
        ADMIN_UI[Admin Dashboard<br/>React/TypeScript]
    end

    subgraph "API Gateway Layer"
        API_GW[API Gateway<br/>Rate Limiting<br/>Authentication<br/>Request Routing]
    end

    subgraph "Microservices Layer"
        UMS[User Management Service<br/>Authentication & Authorization]
        ERS[Error Reporting Service<br/>Error Processing & Validation]
        RIS[RAG Integration Service<br/>Vector Processing & ML]
        CES[Correction Engine Service<br/>Real-time Corrections]
        VS[Verification Service<br/>Analytics & Quality Assurance]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL<br/>Relational Data)]
        VECTOR_DB[(Vector Database<br/>Embeddings & Patterns)]
        REDIS[(Redis<br/>Cache & Sessions)]
        KAFKA[(Kafka<br/>Event Streaming)]
    end

    subgraph "External Systems"
        ASR_SYS[ASR Processing Pipeline]
        INSTANOTE[InstaNote Database]
        OAUTH[OAuth Providers]
        EMAIL[Email Service]
    end

    %% Frontend to Gateway
    ERROR_UI --> API_GW
    VERIFY_UI --> API_GW
    ADMIN_UI --> API_GW

    %% Gateway to Services
    API_GW --> UMS
    API_GW --> ERS
    API_GW --> RIS
    API_GW --> CES
    API_GW --> VS

    %% Service Interactions
    ERS --> RIS
    ERS --> VS
    RIS --> CES
    VS --> UMS
    CES --> RIS

    %% Data Connections
    UMS --> POSTGRES
    ERS --> POSTGRES
    VS --> POSTGRES
    RIS --> VECTOR_DB
    CES --> REDIS

    %% Event Streaming
    ERS --> KAFKA
    RIS --> KAFKA
    CES --> KAFKA
    VS --> KAFKA

    %% External Integrations
    UMS --> OAUTH
    VS --> INSTANOTE
    CES --> ASR_SYS
    VS --> EMAIL
```

### 2.4 Error Processing Data Flow

```mermaid
flowchart TD
    START([QA Personnel Identifies Error])

    SUBMIT[Submit Error Report<br/>via Error Reporting UI]
    VALIDATE[Validate Error Data<br/>in Error Reporting Service]
    STORE[Store Error Report<br/>in PostgreSQL]
    VECTORIZE[Generate Embeddings<br/>in RAG Integration Service]
    PATTERN[Store Pattern<br/>in Vector Database]
    PUBLISH[Publish Error Event<br/>to Kafka]

    PATTERN_EVENT[Pattern Learning Event]
    CES_CONSUME[Correction Engine<br/>Consumes Event]
    UPDATE_CACHE[Update Speaker Patterns<br/>in Redis Cache]

    VERIFY_TRIGGER[Trigger Verification<br/>Workflow]
    INSTANOTE_PULL[Pull Related Jobs<br/>from InstaNote]
    QUALITY_CHECK[Quality Assurance<br/>Validation]

    FEEDBACK[Generate Feedback<br/>for QA Personnel]

    START --> SUBMIT
    SUBMIT --> VALIDATE
    VALIDATE --> STORE
    STORE --> VECTORIZE
    VECTORIZE --> PATTERN
    PATTERN --> PUBLISH

    PUBLISH --> PATTERN_EVENT
    PATTERN_EVENT --> CES_CONSUME
    CES_CONSUME --> UPDATE_CACHE

    STORE --> VERIFY_TRIGGER
    VERIFY_TRIGGER --> INSTANOTE_PULL
    INSTANOTE_PULL --> QUALITY_CHECK
    QUALITY_CHECK --> FEEDBACK
```

### 2.5 Real-time Correction Flow

```mermaid
sequenceDiagram
    participant ASR as ASR System
    participant CES as Correction Engine
    participant CACHE as Redis Cache
    participant RIS as RAG Integration
    participant DB as PostgreSQL
    participant VS as Verification

    ASR->>CES: New Draft Text
    CES->>CACHE: Check Speaker Patterns

    alt Cache Hit
        CACHE-->>CES: Return Cached Patterns
    else Cache Miss
        CES->>RIS: Request Pattern Analysis
        RIS->>DB: Query Historical Data
        DB-->>RIS: Return Error Patterns
        RIS-->>CES: Return Analysis
        CES->>CACHE: Cache Results
    end

    CES->>CES: Apply Corrections
    CES->>VS: Log Correction Applied
    CES-->>ASR: Return Corrected Text

    Note over ASR,VS: Correction completed in < 5 seconds
```

---

## 3. Service Architecture Details

### 3.1 Error Reporting Service (ERS)

**Purpose**: Core error tracking and management functionality

**Key Components:**
- **Error Report Entity**: Comprehensive error data model
- **Speaker Profile Management**: Quality-based bucket classification
- **Error Categorization**: Systematic error type classification
- **Audit Trail**: Complete change history tracking

**Domain Model:**
```python
@dataclass
class ErrorReport:
    error_id: UUID
    job_id: UUID
    speaker_id: UUID
    reported_by: UUID
    original_text: str
    corrected_text: str
    error_categories: List[str]
    severity_level: SeverityLevel
    confidence_score: float
    status: ErrorStatus
    created_at: datetime
    metadata: Dict[str, Any]
```

**Quality-Based Bucket Classification System:**
- � **NO_TOUCH**: Very high quality ASR draft, no corrections needed
- 🔧 **LOW_TOUCH**: High quality ASR draft, minimal corrections required by MTs
- ⚙️ **MEDIUM_TOUCH**: Medium quality ASR draft, some corrections required
- �️ **HIGH_TOUCH**: Low quality ASR draft, significant corrections required

### 3.2 RAG Integration Service (RIS)

**Purpose**: AI-powered correction suggestions using Retrieval-Augmented Generation

**Key Features:**
- **Vector Search**: Semantic similarity matching for error patterns
- **Context-Aware Corrections**: Speaker-specific correction suggestions
- **Learning Pipeline**: Continuous improvement from validated corrections
- **Multi-Model Support**: Integration with various LLM providers

**RAG Pipeline:**
```mermaid
graph LR
    A[Error Text] --> B[Text Preprocessing]
    B --> C[Vector Embedding]
    C --> D[Similarity Search]
    D --> E[Context Retrieval]
    E --> F[LLM Generation]
    F --> G[Correction Suggestions]
    G --> H[Confidence Scoring]
```

### 3.3 Verification Service (VS)

**Purpose**: Quality assurance and MT validation workflows

**Key Workflows:**
- **SER Calculation**: Sentence Error Rate computation
- **MT Validation**: Medical Transcriptionist review process
- **Quality Metrics**: Performance tracking and analytics
- **Feedback Loop**: Continuous improvement integration

### 3.4 User Management Service (UMS)

**Purpose**: Authentication, authorization, and user profile management

**Features:**
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permission management
- **Speaker Profile Management**: Comprehensive speaker data
- **Bucket Progression**: Automated quality-based progression

### 3.5 Correction Engine Service (CES)

**Purpose**: Advanced correction algorithms and quality scoring

**Capabilities:**
- **Multi-Algorithm Support**: Various correction strategies
- **Quality Scoring**: Comprehensive correction quality assessment
- **Pattern Recognition**: Error pattern identification and learning
- **Performance Optimization**: Efficient correction processing

---

## 4. API Documentation

### 4.1 Error Reporting API

**Base URL**: `http://localhost:8000/api/v1/errors`

**Key Endpoints:**

#### POST /api/v1/errors
Create a new error report with comprehensive validation and processing.

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440010",
  "speaker_id": "speaker-123",
  "client_id": "client-456",
  "bucket_type": "medium_touch",
  "original_text": "The patient has severe hypertension",
  "corrected_text": "The patient has severe high blood pressure",
  "error_categories": ["medical_terminology"],
  "severity_level": "medium",
  "start_position": 20,
  "end_position": 39,
  "confidence_score": 0.85,
  "metadata": {
    "audio_quality": "good",
    "speaker_clarity": "clear",
    "background_noise": "low",
    "number_of_speakers": "one",
    "overlapping_speech": "no",
    "specialized_knowledge_required": "yes",
    "note_type": "progress_note",
    "specialty": "cardiology"
  }
}
```

**Enhanced Metadata Fields:**

| Field | Type | Options | Required | Description |
|-------|------|---------|----------|-------------|
| `bucket_type` | string | no_touch, low_touch, medium_touch, high_touch | Yes | Quality-based speaker classification |
| `audio_quality` | string | good, fair, poor | Yes | Overall audio quality assessment |
| `speaker_clarity` | string | clear, somewhat_clear, unclear, very_unclear | Yes | Speaker speech clarity level |
| `background_noise` | string | none, low, medium, high | Yes | Background noise level |
| `number_of_speakers` | string | one, two, three, four, five | Yes | Number of speakers in audio |
| `overlapping_speech` | string | yes, no | Yes | Presence of overlapping speech |
| `specialized_knowledge_required` | string | yes, no | Yes | Whether specialized medical knowledge is required |

#### GET /api/v1/errors/{error_id}
Retrieve detailed error report information.

#### GET /api/v1/errors/speaker/{speaker_id}
Get all error reports for a specific speaker with filtering options.

### 4.2 Speaker Bucket Management API

**Base URL**: `http://localhost:8000/api/v1/speakers`

**Quality-Based Bucket System:**
- **no_touch**: Very high quality ASR draft, no corrections needed
- **low_touch**: High quality ASR draft, minimal corrections required by MTs
- **medium_touch**: Medium quality ASR draft, some corrections required
- **high_touch**: Low quality ASR draft, significant corrections required

**Key Features:**
- Quality-based speaker classification using touch-based buckets
- Automated bucket progression based on performance metrics
- Performance analytics and trend monitoring
- Comprehensive speaker profiles with bucket history

#### GET /api/v1/speakers/{speaker_id}/profile
```json
{
  "speaker_id": "uuid",
  "current_bucket": "medium_touch",
  "bucket_info": {
    "label": "Medium Touch",
    "description": "Medium quality ASR draft, some corrections required",
    "color": "#ff9800",
    "icon": "⚙️",
    "level": 1
  },
  "statistics": {
    "total_reports": 25,
    "average_error_rate": 0.08,
    "average_correction_accuracy": 0.82,
    "days_in_current_bucket": 15
  }
}
```

#### GET /api/v1/speakers/{speaker_id}/bucket-history
Get complete bucket change history for a speaker.

```json
{
  "speaker_id": "speaker-123",
  "current_bucket": "medium_touch",
  "bucket_history": [
    {
      "bucket_type": "high_touch",
      "assigned_date": "2024-11-01T10:00:00Z",
      "assigned_by": "qa-user-456",
      "reason": "Initial assessment - multiple errors observed"
    },
    {
      "bucket_type": "medium_touch",
      "assigned_date": "2024-12-01T10:00:00Z",
      "assigned_by": "system",
      "reason": "Quality improvement - error rate decreased"
    }
  ],
  "performance_metrics": {
    "total_reports": 45,
    "error_rate_trend": "improving",
    "average_correction_accuracy": 0.78,
    "time_in_current_bucket_days": 19
  }
}
```

#### GET /api/v1/speakers/bucket-types
Get all available bucket types and their definitions.

```json
{
  "bucket_types": {
    "no_touch": {
      "label": "No Touch",
      "description": "Very high quality ASR draft, no corrections needed",
      "color": "#4caf50",
      "icon": "🎯",
      "level": 3
    },
    "low_touch": {
      "label": "Low Touch",
      "description": "High quality ASR draft, minimal corrections required by MTs",
      "color": "#2196f3",
      "icon": "🔧",
      "level": 2
    },
    "medium_touch": {
      "label": "Medium Touch",
      "description": "Medium quality ASR draft, some corrections required",
      "color": "#ff9800",
      "icon": "⚙️",
      "level": 1
    },
    "high_touch": {
      "label": "High Touch",
      "description": "Low quality ASR draft, significant corrections required",
      "color": "#f44336",
      "icon": "🛠️",
      "level": 0
    }
  },
  "progression_order": ["high_touch", "medium_touch", "low_touch", "no_touch"],
  "total_levels": 4
}
```

---

## 5. Frontend Architecture

### 5.1 Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **State Management**: React Query for server state, Context API for client state
- **Styling**: Tailwind CSS with custom component library
- **Testing**: Vitest + React Testing Library + Playwright E2E

### 5.2 Component Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        A[App.tsx]
        B[Router Configuration]
        C[Global State Providers]
    end
    
    subgraph "Feature Modules"
        D[Error Reporting Module]
        E[Speaker Management Module]
        F[Analytics Module]
        G[User Management Module]
    end
    
    subgraph "Shared Components"
        H[UI Component Library]
        I[Form Components]
        J[Data Visualization]
        K[Navigation Components]
    end
    
    subgraph "Services Layer"
        L[API Client]
        M[Authentication Service]
        N[Notification Service]
        O[Cache Management]
    end
    
    A --> B
    A --> C
    B --> D
    B --> E
    B --> F
    B --> G
    D --> H
    E --> H
    F --> J
    G --> I
    D --> L
    E --> L
    F --> L
    G --> M
```

### 5.3 Key User Interfaces

#### Error Reporting Interface
- **Intuitive Form Design**: Step-by-step error reporting workflow
- **Real-time Validation**: Immediate feedback on form inputs
- **Speaker Bucket Display**: Current speaker quality level indication
- **Correction Suggestions**: AI-powered correction recommendations

#### Speaker Management Dashboard
- **Bucket Progression Visualization**: Clear progression indicators
- **Performance Analytics**: Comprehensive performance metrics
- **Historical Tracking**: Complete progression history
- **Manual Override Controls**: Administrative bucket management

#### Analytics Dashboard
- **Real-time Metrics**: Live system performance indicators
- **Trend Analysis**: Historical performance trends
- **Quality Insights**: Error pattern analysis
- **Export Capabilities**: Data export for reporting

---

## 6. Development Guidelines

### 6.1 SOLID Principles Implementation

**Single Responsibility Principle (SRP)**
- Each service has one well-defined responsibility
- Domain entities focus solely on business logic
- Adapters handle only infrastructure concerns

**Open/Closed Principle (OCP)**
- Services extensible through new adapters
- New error categories added without modifying existing logic
- ML models swappable through adapter interfaces

**Liskov Substitution Principle (LSP)**
- All adapter implementations fully substitutable
- Database adapters (PostgreSQL, MongoDB) interchangeable
- Authentication providers substitutable

**Interface Segregation Principle (ISP)**
- Focused, specific port interfaces
- Clients depend only on methods they use
- Separate interfaces for read vs. write operations

**Dependency Inversion Principle (DIP)**
- High-level modules independent of low-level modules
- Both depend on abstractions (ports/interfaces)
- Concrete implementations injected at runtime

### 6.2 Test-Driven Development (TDD)

**Mandatory TDD Cycle:**
1. **Red**: Write failing test defining desired behavior
2. **Green**: Write minimal code to make test pass
3. **Refactor**: Improve code while maintaining test coverage

**Coverage Requirements:**
- **70% Unit Tests**: Domain logic and business rules
- **20% Integration Tests**: Service interactions
- **10% E2E Tests**: Complete user workflows

**Example TDD Implementation:**
```python
# 1. RED - Write failing test first
def test_error_report_creation():
    # Arrange
    error_data = {
        "original_text": "The patient has chest pain",
        "corrected_text": "The patient has chest pain and dyspnea",
        "speaker_id": "speaker-123",
        "error_categories": ["medical_terminology"]
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        ErrorReport.create(error_data)  # Should fail initially

# 2. GREEN - Implement minimal code to pass
@dataclass
class ErrorReport:
    original_text: str
    corrected_text: str
    speaker_id: str
    error_categories: List[str]

    @classmethod
    def create(cls, data: Dict[str, Any]) -> 'ErrorReport':
        # Minimal validation
        if not data.get("original_text"):
            raise ValidationError("Original text required")
        return cls(**data)

# 3. REFACTOR - Improve while maintaining tests
class ErrorReport:
    def __post_init__(self):
        self._validate_text_content()
        self._validate_speaker_exists()
        self._validate_error_categories()
```

### 6.3 Code Quality Standards

**Hexagonal Architecture Implementation:**
```python
# Domain Layer - Pure business logic
class ErrorReportEntity:
    def __init__(self, original_text: str, corrected_text: str):
        self.original_text = original_text
        self.corrected_text = corrected_text
        self.confidence_score = self._calculate_confidence()

    def _calculate_confidence(self) -> float:
        # Pure business logic - no dependencies
        return calculate_text_similarity(self.original_text, self.corrected_text)

# Application Layer - Use cases and ports
class ErrorReportingUseCase:
    def __init__(self, repository: ErrorRepositoryPort):
        self._repository = repository

    async def create_error_report(self, command: CreateErrorReportCommand) -> ErrorReport:
        error_report = ErrorReportEntity(command.original_text, command.corrected_text)
        return await self._repository.save(error_report)

# Infrastructure Layer - Adapters
class PostgreSQLErrorRepository(ErrorRepositoryPort):
    async def save(self, error_report: ErrorReportEntity) -> ErrorReport:
        # Database-specific implementation
        async with self.db_session() as session:
            db_record = ErrorReportModel.from_entity(error_report)
            session.add(db_record)
            await session.commit()
            return db_record.to_entity()
```

**Code Organization:**
```
src/
├── error_reporting_service/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── error_report.py
│   │   │   └── speaker_profile.py
│   │   ├── value_objects/
│   │   │   ├── bucket_type.py
│   │   │   └── speaker_metrics.py
│   │   └── services/
│   │       └── bucket_progression_service.py
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── create_error_report.py
│   │   │   └── evaluate_bucket_progression.py
│   │   └── ports/
│   │       ├── error_repository_port.py
│   │       └── notification_port.py
│   ├── infrastructure/
│   │   ├── adapters/
│   │   │   ├── database/
│   │   │   │   └── postgresql_error_repository.py
│   │   │   └── messaging/
│   │   │       └── kafka_event_publisher.py
│   │   └── config/
│   │       └── settings.py
│   └── presentation/
│       └── api/
│           ├── error_reporting_controller.py
│           └── speaker_management_controller.py
```

**Quality Gates:**
- All code must pass linting (flake8, mypy)
- 100% test coverage for domain logic
- Security scanning (bandit)
- Performance benchmarks
- Code review approval required

**Example Quality Checks:**
```bash
# Linting and type checking
flake8 src/ tests/ --max-line-length=88
mypy src/ --strict

# Security scanning
bandit -r src/ -f json

# Test coverage
pytest --cov=src --cov-report=html --cov-fail-under=90

# Performance testing
pytest tests/performance/ --benchmark-only
```

---

## 7. Deployment & Operations

### 7.1 Container Architecture

**Podman-based Deployment:**
```yaml
# podman-compose.dev.yml
services:
  api-gateway:
    image: rag-interface/api-gateway:latest
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
  
  error-reporting-service:
    image: rag-interface/error-reporting:latest
    ports: ["8003:8003"]
    depends_on: [postgres, redis]
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rag_interface
      POSTGRES_USER: rag_user
      POSTGRES_PASSWORD: secure_password
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### 7.2 Environment Configuration

**Development Environment Setup:**
```bash
# Complete development environment setup
./tools/scripts/dev-setup.sh

# This script performs:
# - Python virtual environment creation
# - Dependency installation (requirements.txt, requirements-dev.txt)
# - Node.js dependencies installation
# - Environment file configuration
# - Pre-commit hooks installation
# - Database initialization

# Start all services
./tools/scripts/dev-start.sh

# Monitor logs in real-time
./tools/scripts/dev-logs.sh -f

# Run comprehensive tests
./tools/scripts/test-all.sh

# Stop all services
./tools/scripts/dev-stop.sh
```

**Environment Variables:**
```bash
# Database Configuration
DATABASE_URL=postgresql://rag_user:password@localhost:5432/rag_interface
REDIS_URL=redis://localhost:6379/0

# Vector Database
VECTOR_DB_URL=http://localhost:8080
VECTOR_DB_API_KEY=your_api_key

# Authentication
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# External Services
INSTANOTE_API_URL=https://api.instanote.com
INSTANOTE_API_KEY=your_instanote_key

# Monitoring
PROMETHEUS_ENABLED=true
JAEGER_ENABLED=true
LOG_LEVEL=INFO
```

**Production Deployment Architecture:**
```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>NGINX/HAProxy]
    end

    subgraph "Application Layer"
        API1[API Gateway Instance 1]
        API2[API Gateway Instance 2]
        ERS1[Error Reporting Service 1]
        ERS2[Error Reporting Service 2]
        RIS1[RAG Integration Service 1]
        RIS2[RAG Integration Service 2]
    end

    subgraph "Data Layer"
        PG_PRIMARY[(PostgreSQL Primary)]
        PG_REPLICA[(PostgreSQL Replica)]
        REDIS_CLUSTER[(Redis Cluster)]
        VECTOR_CLUSTER[(Vector DB Cluster)]
    end

    subgraph "Monitoring"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        JAEGER[Jaeger]
        ELK[ELK Stack]
    end

    LB --> API1
    LB --> API2
    API1 --> ERS1
    API1 --> RIS1
    API2 --> ERS2
    API2 --> RIS2

    ERS1 --> PG_PRIMARY
    ERS2 --> PG_REPLICA
    RIS1 --> VECTOR_CLUSTER
    RIS2 --> VECTOR_CLUSTER

    API1 --> REDIS_CLUSTER
    API2 --> REDIS_CLUSTER
```

**Kubernetes Deployment:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: error-reporting-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: error-reporting-service
  template:
    metadata:
      labels:
        app: error-reporting-service
    spec:
      containers:
      - name: error-reporting
        image: rag-interface/error-reporting:latest
        ports:
        - containerPort: 8003
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8003
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 7.3 Monitoring & Observability

**Comprehensive Monitoring Stack:**
```mermaid
graph TB
    subgraph "Application Metrics"
        APP[Application Services]
        METRICS[Custom Metrics]
        HEALTH[Health Checks]
    end

    subgraph "Infrastructure Metrics"
        NODES[Kubernetes Nodes]
        PODS[Pod Metrics]
        NETWORK[Network Metrics]
    end

    subgraph "Data Collection"
        PROMETHEUS[Prometheus Server]
        JAEGER[Jaeger Tracing]
        FLUENTD[Fluentd Log Collector]
    end

    subgraph "Visualization & Alerting"
        GRAFANA[Grafana Dashboards]
        ALERTMANAGER[Alert Manager]
        KIBANA[Kibana Logs]
    end

    subgraph "Notification Channels"
        SLACK[Slack Notifications]
        EMAIL[Email Alerts]
        PAGERDUTY[PagerDuty]
    end

    APP --> PROMETHEUS
    METRICS --> PROMETHEUS
    HEALTH --> PROMETHEUS
    NODES --> PROMETHEUS
    PODS --> PROMETHEUS
    NETWORK --> PROMETHEUS

    APP --> JAEGER
    APP --> FLUENTD

    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTMANAGER
    FLUENTD --> KIBANA

    ALERTMANAGER --> SLACK
    ALERTMANAGER --> EMAIL
    ALERTMANAGER --> PAGERDUTY
```

**Key Performance Indicators (KPIs):**
```python
# Custom Prometheus Metrics
from prometheus_client import Counter, Histogram, Gauge

# Business Metrics
error_reports_total = Counter(
    'error_reports_total',
    'Total number of error reports submitted',
    ['speaker_bucket', 'error_category']
)

correction_accuracy = Histogram(
    'correction_accuracy_score',
    'Distribution of correction accuracy scores',
    buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
)

active_speakers = Gauge(
    'active_speakers_total',
    'Number of active speakers by bucket',
    ['bucket_type']
)

# Technical Metrics
api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint', 'status_code']
)

database_connections = Gauge(
    'database_connections_active',
    'Number of active database connections',
    ['service', 'database']
)
```

**Health Check Implementation:**
```python
# Health check endpoint
@router.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }

    # Database connectivity
    try:
        await database.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Redis connectivity
    try:
        await redis.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Vector database connectivity
    try:
        vector_db_status = await vector_db.health_check()
        health_status["checks"]["vector_db"] = "healthy"
    except Exception as e:
        health_status["checks"]["vector_db"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

**Alerting Rules:**
```yaml
# prometheus-alerts.yml
groups:
- name: rag-interface-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(api_request_duration_seconds_count{status_code=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: DatabaseConnectionsHigh
    expr: database_connections_active > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connection usage"
      description: "Database connections: {{ $value }}"

  - alert: ServiceDown
    expr: up{job="rag-interface"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "{{ $labels.instance }} has been down for more than 1 minute"
```

---

## 8. User Guides

### 8.1 End User Workflows

#### Error Reporting Workflow
1. **Access System**: Login with credentials
2. **Select Speaker**: Choose speaker from dropdown
3. **Enter Error Details**: Original and corrected text
4. **Categorize Error**: Select appropriate error categories
5. **Set Severity**: Choose severity level
6. **Submit Report**: Review and submit for processing
7. **Track Progress**: Monitor report status and verification

#### Quality Assurance Workflow
1. **Review Queue**: Access pending error reports
2. **Validate Corrections**: Review suggested corrections
3. **Approve/Reject**: Make validation decisions
4. **Provide Feedback**: Add comments and recommendations
5. **Update Speaker Bucket**: Trigger bucket progression if needed

### 8.2 Administrative Functions

#### Speaker Management
- **Bucket Assignment**: Manual bucket assignment and overrides
- **Performance Monitoring**: Track speaker improvement over time
- **Bulk Operations**: Batch processing for multiple speakers
- **Analytics Review**: Comprehensive performance analytics

#### System Configuration
- **User Management**: Add/remove users and assign roles
- **System Settings**: Configure thresholds and parameters
- **Integration Setup**: Configure external system connections
- **Backup Management**: Schedule and monitor data backups

---

## 9. Quality Assurance

### 9.1 Testing Strategy

**Test Pyramid:**
```mermaid
graph TB
    A[E2E Tests - 10%<br/>Complete User Journeys]
    B[Integration Tests - 20%<br/>Service Interactions]
    C[Unit Tests - 70%<br/>Business Logic]
    
    A --> B
    B --> C
```

**Testing Tools:**
- **Backend**: pytest, pytest-asyncio, factory-boy
- **Frontend**: Vitest, React Testing Library, Playwright
- **API**: Postman collections, automated API testing
- **Performance**: Load testing with locust

### 9.2 Quality Metrics

**Code Quality:**
- **Coverage**: Minimum 90% overall coverage
- **Complexity**: Cyclomatic complexity < 10
- **Maintainability**: Code Climate maintainability score > B
- **Security**: Zero high-severity security vulnerabilities

**Performance Benchmarks:**
- **API Response Time**: < 200ms for 95th percentile
- **Database Queries**: < 100ms average query time
- **Memory Usage**: < 512MB per service instance
- **CPU Utilization**: < 70% under normal load

---

## 10. Business Requirements & Specifications

### 10.1 Product Requirements Overview

**Primary Business Goals:**
- **Reduce Feedback Loop**: From days to real-time error correction validation
- **Improve QA Efficiency**: Focus on critical errors rather than repetitive issues
- **Enhanced Accuracy**: Speaker-specific error learning and correction
- **Time Savings**: Automated correction of known speaker-specific errors

**Key Performance Indicators:**
- 25-40% reduction in transcription errors
- 30-50% reduction in manual review time
- 90%+ user satisfaction with error reporting workflow
- <200ms API response time for 95th percentile

### 10.2 User Personas & Workflows

#### Medical Transcriptionist (MT)
**Primary Tasks:**
- Review ASR drafts for accuracy
- Submit error reports with corrections
- Validate suggested corrections
- Track speaker performance improvements

**Workflow:**
```mermaid
graph LR
    A[Access ASR Draft] --> B[Identify Error]
    B --> C[Select Error Text]
    C --> D[Categorize Error]
    D --> E[Provide Correction]
    E --> F[Submit Report]
    F --> G[Track Status]
```

#### Quality Assurance (QA) Personnel
**Primary Tasks:**
- Validate error reports and corrections
- Manage speaker bucket assignments
- Monitor system performance
- Generate quality reports

**Workflow:**
```mermaid
graph LR
    A[Review Error Queue] --> B[Validate Correction]
    B --> C[Approve/Reject]
    C --> D[Update Speaker Bucket]
    D --> E[Generate Reports]
```

### 10.3 Functional Requirements

#### Error Reporting Requirements
- **FR-001**: System shall support multi-touch text selection
- **FR-002**: System shall provide real-time error categorization
- **FR-003**: System shall generate AI-powered correction suggestions
- **FR-004**: System shall maintain complete audit trail
- **FR-005**: System shall support voice input/output capabilities

#### Speaker Management Requirements
- **FR-006**: System shall classify speakers into quality-based touch buckets (no_touch, low_touch, medium_touch, high_touch)
- **FR-007**: System shall automatically progress speakers based on performance metrics and error rates
- **FR-008**: System shall provide comprehensive speaker analytics with bucket-specific insights
- **FR-009**: System shall support manual bucket overrides with proper authorization
- **FR-010**: System shall enforce cooldown periods between bucket changes (minimum 14 days)
- **FR-011**: System shall track bucket progression history with detailed reasoning
- **FR-012**: System shall provide bucket-specific error pattern analysis

#### Quality Assurance Requirements
- **FR-013**: System shall provide MT validation workflows with bucket-aware processing
- **FR-014**: System shall calculate SER (Sentence Error Rate) metrics by bucket type
- **FR-015**: System shall support batch processing operations for bucket evaluations
- **FR-016**: System shall generate quality reports and analytics segmented by bucket
- **FR-017**: System shall integrate with InstaNote Database for verification workflows
- **FR-018**: System shall provide bucket-specific quality thresholds and alerts
- **FR-019**: System shall track correction effectiveness by bucket type

### 10.4 Bucket Progression Business Rules

#### Bucket Classification Criteria
- **HIGH_TOUCH (Level 0)**: Error rate > 15%, Accuracy < 60%
- **MEDIUM_TOUCH (Level 1)**: Error rate 10-15%, Accuracy 60-75%
- **LOW_TOUCH (Level 2)**: Error rate 5-10%, Accuracy 75-85%
- **NO_TOUCH (Level 3)**: Error rate < 5%, Accuracy > 85%

#### Progression Requirements
- **Minimum Reports**: 10 reports for promotion, 5 for demotion
- **Time in Bucket**: Minimum 7 days before evaluation
- **Consistency Score**: ≥ 70% consistency required
- **Improvement Trend**: ≥ 10% improvement for promotion
- **Cooldown Period**: 14 days between bucket changes
- **Change Limit**: Maximum 2 bucket changes per month

#### Automatic Progression Triggers
```python
# Promotion Criteria (moving to higher quality bucket)
def can_promote(speaker_metrics):
    return (
        speaker_metrics.total_reports >= 10 and
        speaker_metrics.days_in_current_bucket >= 7 and
        speaker_metrics.average_error_rate <= target_bucket_error_rate and
        speaker_metrics.average_correction_accuracy >= target_bucket_accuracy and
        speaker_metrics.consistency_score >= 0.70 and
        speaker_metrics.improvement_trend >= 0.10
    )

# Demotion Criteria (moving to lower quality bucket)
def should_demote(speaker_metrics):
    return (
        speaker_metrics.total_reports >= 5 and
        speaker_metrics.average_error_rate > current_bucket_threshold * 1.5 and
        speaker_metrics.average_correction_accuracy < current_bucket_threshold * 0.8 and
        speaker_metrics.consistency_score < 0.70
    )
```

#### Manual Override Rules
- **QA Personnel**: Can override bucket assignments with justification
- **Admin Users**: Can force bucket changes and bypass cooldown periods
- **Audit Trail**: All manual changes logged with user ID and reason
- **Approval Workflow**: Manual demotions require supervisor approval

### 10.5 Non-Functional Requirements

#### Performance Requirements
- **NFR-001**: API response time < 200ms for 95th percentile
- **NFR-002**: System shall support 1000+ concurrent users
- **NFR-003**: Database queries < 100ms average response time
- **NFR-004**: System uptime > 99.9%
- **NFR-005**: Bucket progression evaluation < 5 seconds

#### Security Requirements
- **NFR-006**: All data transmission encrypted with TLS 1.3
- **NFR-007**: JWT-based authentication with role-based access control
- **NFR-008**: Comprehensive audit logging for all operations
- **NFR-009**: Data retention policies compliant with healthcare regulations
- **NFR-010**: Bucket change authorization and approval workflows

#### Scalability Requirements
- **NFR-011**: Horizontal scaling support for all services
- **NFR-012**: Auto-scaling based on load metrics
- **NFR-013**: Database sharding support for large datasets
- **NFR-014**: CDN integration for global content delivery
- **NFR-015**: Bucket-specific caching strategies for performance optimization

---

## 11. Data Models & Database Design

### 11.1 Core Entity Relationships

```mermaid
erDiagram
    SPEAKER ||--o{ ERROR_REPORT : reports
    SPEAKER ||--o{ BUCKET_CHANGE_LOG : has
    SPEAKER {
        uuid speaker_id PK
        string speaker_identifier
        string speaker_name
        enum current_bucket "no_touch, low_touch, medium_touch, high_touch"
        datetime created_at
        datetime updated_at
        json metadata
    }

    ERROR_REPORT ||--o{ CORRECTION_SUGGESTION : has
    ERROR_REPORT {
        uuid error_id PK
        uuid job_id
        uuid speaker_id FK
        uuid reported_by FK
        text original_text
        text corrected_text
        string[] error_categories
        enum severity_level
        float confidence_score
        enum status
        datetime created_at
        json metadata
    }

    BUCKET_CHANGE_LOG {
        uuid change_id PK
        uuid speaker_id FK
        enum old_bucket "no_touch, low_touch, medium_touch, high_touch"
        enum new_bucket "no_touch, low_touch, medium_touch, high_touch"
        string change_reason
        datetime changed_at
        json metrics_at_change
        json metadata
    }

    CORRECTION_SUGGESTION {
        uuid suggestion_id PK
        uuid error_report_id FK
        text suggested_correction
        float confidence_score
        string source_model
        datetime created_at
        json metadata
    }
```

### 11.2 Bucket Type Enumeration

**BucketType Value Object:**
```python
from enum import Enum
from typing import Dict, List

class BucketType(str, Enum):
    """
    Quality-based speaker bucket classification levels.

    Each bucket represents different levels of ASR quality and required intervention:
    - NO_TOUCH: Highest quality, no corrections needed
    - LOW_TOUCH: High quality, minimal corrections needed
    - MEDIUM_TOUCH: Medium quality, some corrections needed
    - HIGH_TOUCH: Low quality, significant corrections needed
    """

    NO_TOUCH = "no_touch"
    LOW_TOUCH = "low_touch"
    MEDIUM_TOUCH = "medium_touch"
    HIGH_TOUCH = "high_touch"

    @classmethod
    def get_progression_order(cls) -> List['BucketType']:
        """Get bucket types in progression order (from lowest to highest quality)"""
        return [cls.HIGH_TOUCH, cls.MEDIUM_TOUCH, cls.LOW_TOUCH, cls.NO_TOUCH]

    @classmethod
    def get_bucket_info(cls) -> Dict[str, Dict[str, str]]:
        """Get detailed information about each bucket type"""
        return {
            cls.NO_TOUCH.value: {
                "label": "No Touch",
                "description": "Very high quality ASR draft, no corrections needed",
                "color": "#4caf50",  # Green
                "icon": "🎯"
            },
            cls.LOW_TOUCH.value: {
                "label": "Low Touch",
                "description": "High quality ASR draft, minimal corrections required",
                "color": "#2196f3",  # Blue
                "icon": "🔧"
            },
            cls.MEDIUM_TOUCH.value: {
                "label": "Medium Touch",
                "description": "Medium quality ASR draft, some corrections needed",
                "color": "#ff9800",  # Orange
                "icon": "⚙️"
            },
            cls.HIGH_TOUCH.value: {
                "label": "High Touch",
                "description": "Low quality ASR draft, significant corrections required",
                "color": "#f44336",  # Red
                "icon": "🛠️"
            }
        }

    def get_level(self) -> int:
        """Get numeric level (0-3) for comparison"""
        levels = {
            self.HIGH_TOUCH: 0,
            self.MEDIUM_TOUCH: 1,
            self.LOW_TOUCH: 2,
            self.NO_TOUCH: 3
        }
        return levels[self]
```

### 11.3 Vector Database Schema

**Error Pattern Embeddings:**
```json
{
  "id": "error_pattern_uuid",
  "vector": [1536-dimensional embedding],
  "metadata": {
    "speaker_id": "uuid",
    "bucket_type": "medium_touch",
    "original_text": "text with error",
    "corrected_text": "corrected text",
    "error_categories": ["category1", "category2"],
    "severity_level": "medium",
    "context": "medical_terminology",
    "audio_quality": "good",
    "speaker_clarity": "clear",
    "background_noise": "low",
    "timestamp": "2025-09-06T10:00:00Z"
  }
}
```

### 11.4 Cache Strategy

**Redis Cache Structure:**
```
speaker_profiles:{speaker_id} → Speaker profile data with bucket info (TTL: 1 hour)
bucket_patterns:{bucket_type} → Common error patterns by bucket (TTL: 24 hours)
speaker_bucket_history:{speaker_id} → Bucket change history (TTL: 12 hours)
error_patterns:{speaker_id} → Recent error patterns (TTL: 24 hours)
correction_suggestions:{text_hash} → Cached suggestions (TTL: 7 days)
session_data:{session_id} → User session data (TTL: 8 hours)
bucket_statistics:global → Global bucket distribution stats (TTL: 30 minutes)
```

**Example Cache Entries:**
```json
// speaker_profiles:speaker-123
{
  "speaker_id": "speaker-123",
  "current_bucket": "medium_touch",
  "bucket_level": 1,
  "performance_metrics": {
    "total_reports": 25,
    "average_error_rate": 0.08,
    "days_in_current_bucket": 15
  },
  "last_updated": "2025-09-06T10:00:00Z"
}

// bucket_patterns:medium_touch
{
  "bucket_type": "medium_touch",
  "common_errors": [
    "medical_terminology",
    "clinical_context",
    "pronunciation_variants"
  ],
  "typical_error_rate": 0.08,
  "correction_accuracy": 0.82
}
```

---

## 12. Security & Compliance

### 12.1 Authentication & Authorization

**JWT Token Structure:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "roles": ["qa_personnel", "mt_user"],
  "permissions": ["error_report:create", "speaker:read"],
  "exp": 1693987200,
  "iat": 1693900800
}
```

**Role-Based Access Control:**
- **Admin**: Full system access, user management, configuration
- **QA Personnel**: Error validation, speaker management, reporting
- **MT User**: Error reporting, correction submission, basic analytics
- **Read-Only**: View-only access to reports and analytics

### 12.2 Data Protection

**Encryption Standards:**
- **Data in Transit**: TLS 1.3 for all communications
- **Data at Rest**: AES-256 encryption for database storage
- **API Keys**: Encrypted storage with rotation policies
- **Sensitive Data**: Field-level encryption for PII

**Privacy Controls:**
- **Data Minimization**: Collect only necessary data
- **Retention Policies**: Automated data purging after retention period
- **Access Logging**: Comprehensive audit trails for all data access
- **Anonymization**: Speaker data anonymization for analytics

### 12.3 Compliance Framework

**Healthcare Compliance:**
- **HIPAA**: Healthcare data protection standards
- **SOC 2**: Security and availability controls
- **ISO 27001**: Information security management
- **GDPR**: Data protection and privacy rights

---

## 13. Performance & Monitoring

### 13.1 Performance Benchmarks

**API Performance Targets:**
```
Endpoint                    | Target Response Time | SLA
---------------------------|---------------------|-----
POST /api/v1/errors        | < 150ms            | 95%
GET /api/v1/speakers       | < 100ms            | 99%
POST /api/v1/corrections   | < 300ms            | 90%
GET /api/v1/analytics      | < 500ms            | 95%
```

**System Resource Targets:**
- **CPU Utilization**: < 70% under normal load
- **Memory Usage**: < 512MB per service instance
- **Database Connections**: < 80% of connection pool
- **Cache Hit Rate**: > 90% for frequently accessed data

### 13.2 Monitoring Stack

**Infrastructure Monitoring:**
```mermaid
graph TB
    A[Application Metrics] --> B[Prometheus]
    B --> C[Grafana Dashboards]
    D[System Logs] --> E[ELK Stack]
    F[Distributed Tracing] --> G[Jaeger]
    H[Health Checks] --> I[Alertmanager]
    I --> J[PagerDuty/Slack]
```

**Key Metrics:**
- **Business Metrics**: Error report volume, correction accuracy, user engagement
- **Technical Metrics**: Response times, error rates, resource utilization
- **Security Metrics**: Failed authentication attempts, suspicious activities
- **Quality Metrics**: Test coverage, deployment success rate, bug resolution time

### 13.3 Alerting Strategy

**Alert Severity Levels:**
- **Critical**: Service down, data loss, security breach
- **High**: Performance degradation, high error rates
- **Medium**: Resource utilization warnings, slow queries
- **Low**: Informational alerts, maintenance reminders

---

## 14. Reference Materials

### 14.1 Architecture Documents
- **[Master Architecture Summary](docs/architecture/00_Master_Architecture_Summary.md)**: Complete system overview
- **[Service Design Documents](docs/architecture/)**: Individual service architectures
- **[Database Schema](docs/architecture/database_schema_design.md)**: Data model specifications
- **[System Integration](docs/architecture/system_integration_design.md)**: Service interaction patterns

### 14.2 API References
- **[Error Reporting API](docs/api/enhanced_error_reporting_api.md)**: Complete API documentation
- **[Speaker Bucket API](docs/api/speaker_bucket_management_api.md)**: Bucket management endpoints

### 14.3 Development Resources
- **[Development Guide](docs/development/DEVELOPMENT_GUIDE.md)**: Complete development workflows
- **[SOLID Principles Guide](docs/development/SOLID_Principles_Implementation_Guide.md)**: Architecture principles
- **[Technology Standards](docs/development/Technology_Stack_Standards.md)**: Tech stack guidelines

### 14.4 Deployment Resources
- **[Deployment Guide](docs/deployment/README.md)**: Production deployment procedures
- **[Maintenance Guide](docs/deployment/MAINTENANCE_GUIDE.md)**: Operations and maintenance
- **[Troubleshooting Guide](docs/deployment/TROUBLESHOOTING_GUIDE.md)**: Issue resolution

---

**Document Maintained By**: Development Team
**Last Updated**: September 6, 2025
**Next Review**: October 6, 2025
**Version Control**: This document is version-controlled alongside the codebase
