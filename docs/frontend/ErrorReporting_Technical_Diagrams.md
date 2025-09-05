# Error Reporting Technical Architecture Diagrams

**Date:** December 19, 2024  
**Status:** Complete  
**Technology Stack:** React 18+ with TypeScript, Material-UI, FastAPI Backend  

---

## Component Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Application"
        A[App.tsx] --> B[ErrorReportingPage]
        B --> C[ErrorReportingForm]
        
        C --> D[TextSelection]
        C --> E[ErrorCategorization]
        C --> F[CorrectionInput]
        C --> G[MetadataInput]
        C --> H[ReviewSubmit]
        
        F --> I[VectorSimilarity]
        F --> J[VoiceInput]
        F --> K[TextToSpeech]
        
        G --> L[AudioQualityInput]
        G --> M[ContextualTags]
        G --> N[TechnicalFlags]
        
        D --> O[TouchSelectionHandles]
        D --> P[SelectionHighlight]
        
        E --> Q[CategoryHierarchy]
        E --> R[AICategorizationSuggestions]
    end
    
    subgraph "State Management"
        S[Redux Store]
        T[ErrorReportingSlice]
        U[UIStateSlice]
        V[APISlice]
    end
    
    subgraph "API Layer"
        W[RTK Query]
        X[ErrorReportingAPI]
        Y[SimilaritySearchAPI]
        Z[CategoryAPI]
    end
    
    C --> S
    S --> T
    S --> U
    S --> V
    
    X --> W
    Y --> W
    Z --> W
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style S fill:#e8f5e8
    style W fill:#fff3e0
```

## Backend Services Integration

```mermaid
graph LR
    subgraph "Frontend (Port 3001)"
        A[React App]
        B[ErrorReportingForm]
        C[API Client]
    end
    
    subgraph "Backend Services"
        D[Error Reporting Service<br/>Port 8010]
        E[User Management Service<br/>Port 8011]
        F[RAG Integration Service<br/>Port 8012]
        G[Correction Engine Service<br/>Port 8013]
        H[Verification Service<br/>Port 8014]
    end
    
    subgraph "Infrastructure"
        I[PostgreSQL<br/>Port 5433]
        J[Redis<br/>Port 6380]
        K[Vector Database]
    end
    
    A --> C
    B --> C
    
    C -->|Error Categories| D
    C -->|Submit Report| D
    C -->|Similarity Search| D
    
    C -->|Authentication| E
    C -->|User Validation| E
    
    D -->|Vector Search| F
    D -->|Correction Processing| G
    D -->|Data Validation| H
    
    D --> I
    D --> J
    F --> K
    
    style A fill:#e3f2fd
    style D fill:#f1f8e9
    style E fill:#f1f8e9
    style F fill:#f1f8e9
    style G fill:#f1f8e9
    style H fill:#f1f8e9
    style I fill:#fce4ec
    style J fill:#fce4ec
    style K fill:#fce4ec
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend UI
    participant Store as Redux Store
    participant API as API Layer
    participant ERS as Error Reporting Service
    participant RIS as RAG Integration Service
    participant DB as Database
    
    U->>UI: Select text "hypertension"
    UI->>Store: dispatch(setTextSelection)
    Store-->>UI: Update selection state
    
    U->>UI: Navigate to correction step
    UI->>API: searchSimilarPatterns("hypertension")
    API->>ERS: POST /api/v1/errors/similarity/search
    ERS->>RIS: Request vector similarity
    RIS->>DB: Query vector database
    DB-->>RIS: Return similar patterns
    RIS-->>ERS: Return similarity results
    ERS-->>API: Return suggestions
    API-->>Store: Update suggestions state
    Store-->>UI: Display AI suggestions
    
    U->>UI: Enter correction "high blood pressure"
    UI->>Store: dispatch(setCorrectionText)
    
    U->>UI: Submit error report
    UI->>API: submitErrorReport(reportData)
    API->>ERS: POST /api/v1/errors/report
    ERS->>DB: Store error report
    DB-->>ERS: Confirm storage
    ERS-->>API: Return report ID
    API-->>Store: Update submission state
    Store-->>UI: Show success message
    UI-->>U: Display confirmation
```

## Component State Management

```mermaid
stateDiagram-v2
    [*] --> Initial
    Initial --> TextSelection: Start Error Report
    
    state TextSelection {
        [*] --> NoSelection
        NoSelection --> Selecting: User starts selection
        Selecting --> Selected: Selection complete
        Selected --> MultipleSelections: Add more selections
        MultipleSelections --> Selected: Selection complete
        Selected --> Validated: Validation passed
    }
    
    TextSelection --> ErrorCategorization: Next Step
    
    state ErrorCategorization {
        [*] --> NoCategories
        NoCategories --> Selecting: User selects category
        Selecting --> Selected: Category selected
        Selected --> Validated: Validation passed
    }
    
    ErrorCategorization --> CorrectionInput: Next Step
    
    state CorrectionInput {
        [*] --> Empty
        Empty --> Typing: User types correction
        Typing --> LoadingSuggestions: Debounce timer
        LoadingSuggestions --> SuggestionsLoaded: API response
        LoadingSuggestions --> SuggestionsError: API error
        SuggestionsLoaded --> Validated: Text provided
        SuggestionsError --> Validated: Manual input
        Typing --> Validated: Manual completion
    }
    
    CorrectionInput --> MetadataInput: Next Step
    
    state MetadataInput {
        [*] --> BasicInfo
        BasicInfo --> AdvancedExpanded: Expand advanced
        AdvancedExpanded --> BasicInfo: Collapse advanced
        BasicInfo --> Validated: Basic info complete
        AdvancedExpanded --> Validated: Advanced info complete
    }
    
    MetadataInput --> ReviewSubmit: Next Step
    
    state ReviewSubmit {
        [*] --> Reviewing
        Reviewing --> Submitting: User submits
        Submitting --> Success: API success
        Submitting --> Error: API error
        Error --> Reviewing: Retry
        Success --> [*]
    }
```

## API Integration Patterns

```mermaid
graph TD
    subgraph "Frontend API Layer"
        A[RTK Query Base API]
        B[Error Reporting API]
        C[Similarity Search API]
        D[Category API]
        E[User API]
    end
    
    subgraph "Middleware"
        F[Authentication Middleware]
        G[Error Handling Middleware]
        H[Retry Middleware]
        I[Cache Middleware]
    end
    
    subgraph "Backend Endpoints"
        J[POST /api/v1/errors/report]
        K[POST /api/v1/errors/similarity/search]
        L[GET /api/v1/errors/categories]
        M[GET /api/v1/users/validate]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    
    B --> F
    C --> F
    D --> F
    E --> F
    
    F --> G
    G --> H
    H --> I
    
    I --> J
    I --> K
    I --> L
    I --> M
    
    style A fill:#e8eaf6
    style F fill:#f3e5f5
    style J fill:#e8f5e8
```

## Real-time Features Architecture

```mermaid
graph TB
    subgraph "User Interactions"
        A[Text Input]
        B[Voice Input]
        C[Touch Selection]
    end
    
    subgraph "Debouncing Layer"
        D[useDebounce Hook]
        E[Debounce Timer: 500ms]
    end
    
    subgraph "API Calls"
        F[Similarity Search]
        G[Voice Recognition]
        H[Text-to-Speech]
    end
    
    subgraph "State Updates"
        I[Loading States]
        J[Success States]
        K[Error States]
    end
    
    subgraph "UI Updates"
        L[Show Suggestions]
        M[Update Progress]
        N[Display Errors]
    end
    
    A --> D
    B --> G
    C --> I
    
    D --> E
    E --> F
    
    F --> I
    G --> I
    H --> I
    
    I --> L
    J --> L
    K --> N
    
    L --> M
    N --> M
    
    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style F fill:#e8f5e8
    style I fill:#fff3e0
    style L fill:#fce4ec
```

## Error Handling Flow

```mermaid
flowchart TD
    A[User Action] --> B{Validation Check}
    B -->|Pass| C[Execute Action]
    B -->|Fail| D[Show Validation Error]
    
    C --> E{API Call Required?}
    E -->|No| F[Update Local State]
    E -->|Yes| G[Make API Call]
    
    G --> H{API Response}
    H -->|Success| I[Update State with Data]
    H -->|Error| J[Handle API Error]
    
    J --> K{Error Type}
    K -->|Network| L[Show Retry Option]
    K -->|Validation| M[Show Field Errors]
    K -->|Server| N[Show Generic Error]
    
    L --> O[User Retries]
    O --> G
    
    M --> P[Highlight Invalid Fields]
    P --> Q[User Corrects Input]
    Q --> A
    
    N --> R[Log Error Details]
    R --> S[Show Support Contact]
    
    D --> T[Focus Invalid Field]
    T --> U[User Corrects Input]
    U --> A
    
    F --> V[Success State]
    I --> V
    V --> W[Continue Workflow]
    
    style A fill:#e3f2fd
    style B fill:#f1f8e9
    style J fill:#ffebee
    style V fill:#e8f5e8
```

## Performance Optimization Strategy

```mermaid
graph LR
    subgraph "Code Splitting"
        A[App Shell]
        B[Route-based Splitting]
        C[Component Lazy Loading]
    end
    
    subgraph "Caching Strategy"
        D[API Response Cache]
        E[Component Memoization]
        F[Static Asset Cache]
    end
    
    subgraph "Bundle Optimization"
        G[Tree Shaking]
        H[Minification]
        I[Compression]
    end
    
    subgraph "Runtime Optimization"
        J[Virtual Scrolling]
        K[Debounced API Calls]
        L[Progressive Loading]
    end
    
    A --> B
    B --> C
    
    D --> E
    E --> F
    
    G --> H
    H --> I
    
    J --> K
    K --> L
    
    C --> D
    F --> G
    I --> J
    
    style A fill:#e8eaf6
    style D fill:#f3e5f5
    style G fill:#e8f5e8
    style J fill:#fff3e0
```

## Testing Architecture

```mermaid
graph TB
    subgraph "Unit Tests"
        A[Component Tests]
        B[Hook Tests]
        C[Utility Tests]
        D[API Tests]
    end
    
    subgraph "Integration Tests"
        E[Component Integration]
        F[API Integration]
        G[State Management]
        H[User Workflows]
    end
    
    subgraph "E2E Tests"
        I[Complete User Journeys]
        J[Cross-browser Testing]
        K[Mobile Testing]
        L[Accessibility Testing]
    end
    
    subgraph "Performance Tests"
        M[Load Testing]
        N[Stress Testing]
        O[Memory Profiling]
        P[Bundle Analysis]
    end
    
    A --> E
    B --> E
    C --> E
    D --> F
    
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> M
    J --> N
    K --> O
    L --> P
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style I fill:#e8f5e8
    style M fill:#fff3e0
```

---

These technical diagrams provide a comprehensive view of the Error Reporting system architecture, showing component relationships, data flow, state management, API integration patterns, and testing strategies. They serve as a technical reference for developers and architects working on the system.
