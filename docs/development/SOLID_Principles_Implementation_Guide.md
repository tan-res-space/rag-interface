# SOLID Principles + TDD Implementation Guide
## ASR Error Reporting System

**Document Version:** 1.1
**Date:** August 19, 2025
**Purpose:** Comprehensive guide for implementing SOLID principles with Test-Driven Development across all system modules
**Scope:** All services, classes, and interfaces in the ASR Error Reporting System
**Methodology:** Test-Driven Development (TDD) mandatory for all implementations

---

## Table of Contents

1. [Overview](#overview)
2. [TDD + SOLID Integration](#tdd--solid-integration)
3. [Single Responsibility Principle (SRP) with TDD](#single-responsibility-principle-srp-with-tdd)
4. [Open/Closed Principle (OCP) with TDD](#openclosed-principle-ocp-with-tdd)
5. [Liskov Substitution Principle (LSP) with TDD](#liskov-substitution-principle-lsp-with-tdd)
6. [Interface Segregation Principle (ISP) with TDD](#interface-segregation-principle-isp-with-tdd)
7. [Dependency Inversion Principle (DIP) with TDD](#dependency-inversion-principle-dip-with-tdd)
8. [Service-Specific TDD + SOLID Examples](#service-specific-tdd--solid-examples)
9. [TDD + SOLID Code Review Checklist](#tdd--solid-code-review-checklist)
10. [Common Anti-Patterns to Avoid](#common-anti-patterns-to-avoid)
11. [TDD Testing Strategies for SOLID Code](#tdd-testing-strategies-for-solid-code)

---

## Overview

### Why SOLID Principles + TDD Matter

The ASR Error Reporting System implements SOLID principles with Test-Driven Development as core architectural guidelines to ensure:

- **Maintainability**: Code that is easy to understand, modify, and extend, with tests that document behavior
- **Testability**: Components that can be tested in isolation with clear dependencies, designed test-first
- **Flexibility**: System that can adapt to changing requirements without major rewrites, validated by comprehensive tests
- **Scalability**: Architecture that supports growth and evolution, with tests that prevent regressions
- **Team Productivity**: Clear boundaries that enable parallel development, with tests that define contracts
- **Quality Assurance**: TDD ensures high code quality and comprehensive test coverage from the start

### Integration with Hexagonal Architecture + TDD

SOLID principles and TDD complement the Hexagonal Architecture pattern:

- **Ports (Interfaces)**: Designed following ISP and DIP, tested first to define clear contracts
- **Core Domain**: Implements SRP and OCP, with business logic tested before implementation
- **Adapters**: Follow LSP and can be substituted seamlessly, with tests ensuring contract compliance
- **Use Cases**: Single responsibility with clear dependencies, tested first to validate workflows

### TDD Red-Green-Refactor Cycle

Every component follows the mandatory TDD cycle:

1. **Red Phase**: Write a failing test that defines the desired behavior
2. **Green Phase**: Write minimal code to make the test pass
3. **Refactor Phase**: Improve code design while keeping all tests green

This cycle ensures that SOLID principles are validated through tests and that all code is thoroughly tested.

---

## TDD + SOLID Integration

### How TDD Validates SOLID Principles

Test-Driven Development serves as a validation mechanism for SOLID principle compliance:

**SRP Validation through TDD:**
- If a class is hard to test, it likely has multiple responsibilities
- Tests should focus on a single behavior, indicating single responsibility
- Multiple test classes for one production class suggests SRP violation

**OCP Validation through TDD:**
- New functionality should be addable by writing new tests, not modifying existing ones
- Existing tests should continue to pass when extending functionality
- Test suites should grow, not change, when adding features

**LSP Validation through TDD:**
- All implementations should pass the same test suite
- Substituting implementations should not break existing tests
- Contract tests validate that all implementations honor the same agreements

**ISP Validation through TDD:**
- Tests should only mock the interfaces they actually use
- If tests require mocking unused methods, interfaces are too broad
- Focused tests indicate focused interfaces

**DIP Validation through TDD:**
- High-level modules should be testable with mocked dependencies
- If mocking is difficult, dependencies are too concrete
- Tests should validate abstractions, not implementations

### TDD Workflow for SOLID Code

**Step 1: Write Interface Tests (Red Phase)**
```python
# Test the interface contract first
class TestErrorRepositoryPort:
    def test_save_returns_valid_id(self):
        # This test defines the interface contract
        repository = MockErrorRepository()  # Will fail until interface exists
        error_report = create_test_error_report()

        error_id = repository.save(error_report)

        assert error_id is not None
        assert isinstance(error_id, str)
```

**Step 2: Create Interface (Green Phase)**
```python
# Create minimal interface to make test pass
class ErrorRepositoryPort(ABC):
    @abstractmethod
    def save(self, error_report: ErrorReport) -> str:
        pass
```

**Step 3: Write Implementation Tests (Red Phase)**
```python
# Test concrete implementation
class TestPostgreSQLErrorRepository:
    def test_save_persists_to_database(self):
        repository = PostgreSQLErrorRepository(test_db)
        error_report = create_test_error_report()

        error_id = repository.save(error_report)

        # Verify persistence
        saved_report = repository.get_by_id(error_id)
        assert saved_report.original_text == error_report.original_text
```

**Step 4: Implement Concrete Class (Green Phase)**
```python
# Implement to make tests pass
class PostgreSQLErrorRepository(ErrorRepositoryPort):
    def save(self, error_report: ErrorReport) -> str:
        # Minimal implementation to pass tests
        pass
```

**Step 5: Refactor for SOLID Compliance**
```python
# Improve design while keeping tests green
class PostgreSQLErrorRepository(ErrorRepositoryPort):
    def __init__(self, connection: DatabaseConnection):
        self._connection = connection  # DIP: Depend on abstraction

    def save(self, error_report: ErrorReport) -> str:
        # SRP: Only handles persistence
        # Implementation details...
        pass
```

---

## Single Responsibility Principle (SRP) with TDD

### Definition
*A class should have only one reason to change.*

### TDD Implementation Strategy

**Test-First SRP Validation:**
TDD helps identify SRP violations early by making testing difficult when classes have multiple responsibilities.

**TDD Red Phase - Define Single Responsibility:**
```python
# Test defines a single responsibility
class TestErrorValidator:
    def test_validates_required_fields_only(self):
        # Red: This test will fail until ErrorValidator exists
        validator = ErrorValidator()
        error_report = ErrorReport(job_id="", speaker_id="123")

        result = validator.validate(error_report)

        assert not result.is_valid
        assert "job_id is required" in result.errors
        # Test focuses on validation only, not persistence or events
```

**TDD Green Phase - Implement Single Responsibility:**
```python
# Green: Minimal implementation with single responsibility
class ErrorValidator:
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        """Only validates error reports - single responsibility"""
        errors = []
        if not error_report.job_id:
            errors.append("job_id is required")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

**TDD Refactor Phase - Maintain Single Responsibility:**
```python
# Refactor: Improve design while maintaining single responsibility
class ErrorValidator:
    def __init__(self, validation_rules: List[ValidationRule]):
        self._validation_rules = validation_rules  # DIP: Depend on abstraction

    def validate(self, error_report: ErrorReport) -> ValidationResult:
        """Still only validates - responsibility unchanged"""
        errors = []
        for rule in self._validation_rules:
            rule_result = rule.validate(error_report)
            if not rule_result.is_valid:
                errors.extend(rule_result.errors)

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

### Traditional Implementation Strategy

**Service Level:**
- Each microservice has a single business responsibility
- Error Reporting Service: Only handles error submission and management
- RAG Integration Service: Only handles vector processing and ML operations
- Correction Engine Service: Only handles real-time correction application

**Class Level:**
```python
# ✅ GOOD: Single responsibility
class ErrorValidator:
    def validate_error_report(self, error_report: ErrorReport) -> ValidationResult:
        """Only validates error reports"""
        pass

class ErrorRepository:
    def save_error_report(self, error_report: ErrorReport) -> str:
        """Only handles data persistence"""
        pass

class ErrorEventPublisher:
    def publish_error_created(self, error_report: ErrorReport) -> None:
        """Only handles event publishing"""
        pass

# ❌ BAD: Multiple responsibilities
class ErrorHandler:
    def validate_and_save_and_publish(self, error_report: ErrorReport):
        """Violates SRP - does validation, persistence, and event publishing"""
        pass
```

**Method Level:**
```python
# ✅ GOOD: Single responsibility methods
class ErrorReportService:
    def validate_error_format(self, error_report: ErrorReport) -> bool:
        """Only validates format"""
        pass
    
    def validate_error_business_rules(self, error_report: ErrorReport) -> bool:
        """Only validates business rules"""
        pass
    
    def save_error_report(self, error_report: ErrorReport) -> str:
        """Only saves to database"""
        pass

# ❌ BAD: Multiple responsibilities in one method
class ErrorReportService:
    def process_error_report(self, error_report: ErrorReport):
        """Violates SRP - validates, saves, publishes events, sends notifications"""
        pass
```

### Benefits
- Easier to understand and maintain
- Changes to one responsibility don't affect others
- Simpler unit testing
- Better code reusability

---

## Open/Closed Principle (OCP)

### Definition
*Software entities should be open for extension, closed for modification.*

### Implementation Strategy

**Strategy Pattern for Extensibility:**
```python
# Abstract base for extensible validation
class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        pass

# Existing validation strategies (closed for modification)
class SeverityValidationStrategy(ValidationStrategy):
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        # Severity validation logic
        pass

class ContextValidationStrategy(ValidationStrategy):
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        # Context validation logic
        pass

# New validation can be added without modifying existing code (open for extension)
class CustomFieldValidationStrategy(ValidationStrategy):
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        # New custom field validation logic
        pass

# Validator that uses strategies
class ErrorValidator:
    def __init__(self, strategies: List[ValidationStrategy]):
        self._strategies = strategies
    
    def validate(self, error_report: ErrorReport) -> ValidationResult:
        for strategy in self._strategies:
            result = strategy.validate(error_report)
            if not result.is_valid:
                return result
        return ValidationResult.success()
```

**Factory Pattern for Extensible Object Creation:**
```python
class EmbeddingModelFactory:
    _models = {
        'openai': OpenAIEmbeddingModel,
        'sentence_transformers': SentenceTransformerModel,
        'custom': CustomEmbeddingModel
    }
    
    @classmethod
    def create_model(cls, model_type: str) -> EmbeddingModelPort:
        if model_type not in cls._models:
            raise ValueError(f"Unknown model type: {model_type}")
        return cls._models[model_type]()
    
    @classmethod
    def register_model(cls, model_type: str, model_class: Type[EmbeddingModelPort]):
        """Extend with new models without modifying existing code"""
        cls._models[model_type] = model_class
```

### Benefits
- New functionality can be added without changing existing code
- Reduces risk of introducing bugs in stable code
- Supports plugin architectures
- Enables A/B testing of new algorithms

---

## Liskov Substitution Principle (LSP)

### Definition
*Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.*

### Implementation Strategy

**Database Adapter Substitutability:**
```python
class ErrorRepositoryPort(ABC):
    @abstractmethod
    async def save(self, error_report: ErrorReport) -> str:
        """Save error report and return ID"""
        pass
    
    @abstractmethod
    async def get_by_id(self, error_id: str) -> Optional[ErrorReport]:
        """Retrieve error report by ID"""
        pass

# All implementations must honor the same contracts
class PostgreSQLErrorRepository(ErrorRepositoryPort):
    async def save(self, error_report: ErrorReport) -> str:
        # PostgreSQL implementation
        # Must return valid ID, handle errors consistently
        pass
    
    async def get_by_id(self, error_id: str) -> Optional[ErrorReport]:
        # Must return None for non-existent IDs, not raise exceptions
        pass

class MongoDBErrorRepository(ErrorRepositoryPort):
    async def save(self, error_report: ErrorReport) -> str:
        # MongoDB implementation
        # Must behave identically to PostgreSQL version
        pass
    
    async def get_by_id(self, error_id: str) -> Optional[ErrorReport]:
        # Must behave identically to PostgreSQL version
        pass

# Client code works with any implementation
class ErrorService:
    def __init__(self, repository: ErrorRepositoryPort):
        self._repository = repository  # Can be any implementation
    
    async def process_error(self, error_report: ErrorReport):
        error_id = await self._repository.save(error_report)
        # This works regardless of which repository implementation is used
```

**Contract Guarantees:**
- Pre-conditions cannot be strengthened in derived classes
- Post-conditions cannot be weakened in derived classes
- Invariants must be preserved
- Exception behavior must be consistent

### Benefits
- Implementations can be swapped without code changes
- Enables easy testing with mock implementations
- Supports multiple deployment configurations
- Facilitates technology migration

---

## Interface Segregation Principle (ISP)

### Definition
*No client should be forced to depend on methods it does not use.*

### Implementation Strategy

**Segregated Repository Interfaces:**
```python
# ❌ BAD: Fat interface forces clients to depend on unused methods
class ErrorRepositoryPort(ABC):
    @abstractmethod
    async def save(self, error_report: ErrorReport) -> str: pass
    @abstractmethod
    async def update(self, error_id: str, updates: dict) -> None: pass
    @abstractmethod
    async def delete(self, error_id: str) -> None: pass
    @abstractmethod
    async def get_by_id(self, error_id: str) -> Optional[ErrorReport]: pass
    @abstractmethod
    async def search(self, filters: dict) -> List[ErrorReport]: pass
    @abstractmethod
    async def get_analytics(self, time_range: TimeRange) -> Analytics: pass

# ✅ GOOD: Segregated interfaces
class ErrorReaderPort(ABC):
    @abstractmethod
    async def get_by_id(self, error_id: str) -> Optional[ErrorReport]: pass
    @abstractmethod
    async def search(self, filters: dict) -> List[ErrorReport]: pass

class ErrorWriterPort(ABC):
    @abstractmethod
    async def save(self, error_report: ErrorReport) -> str: pass
    @abstractmethod
    async def update(self, error_id: str, updates: dict) -> None: pass
    @abstractmethod
    async def delete(self, error_id: str) -> None: pass

class ErrorAnalyticsPort(ABC):
    @abstractmethod
    async def get_analytics(self, time_range: TimeRange) -> Analytics: pass

# Clients depend only on what they need
class ErrorSearchService:
    def __init__(self, reader: ErrorReaderPort):  # Only needs reading
        self._reader = reader

class ErrorCreationService:
    def __init__(self, writer: ErrorWriterPort):  # Only needs writing
        self._writer = writer

class ErrorDashboardService:
    def __init__(self, reader: ErrorReaderPort, analytics: ErrorAnalyticsPort):
        self._reader = reader      # Needs reading
        self._analytics = analytics # Needs analytics
        # Doesn't depend on writing capabilities
```

### Benefits
- Clients have minimal dependencies
- Changes to unused methods don't affect clients
- Easier to implement and test
- Better separation of concerns

---

## Dependency Inversion Principle (DIP)

### Definition
*Depend on abstractions, not concretions.*

### Implementation Strategy

**High-Level Modules Depend on Abstractions:**
```python
# ✅ GOOD: High-level module depends on abstractions
class SubmitErrorReportUseCase:
    def __init__(
        self,
        error_repository: ErrorRepositoryPort,      # Abstraction
        event_publisher: EventPublishingPort,       # Abstraction
        validator: ErrorValidatorPort,              # Abstraction
        cache: CachePort                            # Abstraction
    ):
        self._error_repository = error_repository
        self._event_publisher = event_publisher
        self._validator = validator
        self._cache = cache

    async def execute(self, error_report: ErrorReport) -> str:
        # Business logic depends only on abstractions
        validation_result = await self._validator.validate(error_report)
        if not validation_result.is_valid:
            raise ValidationError(validation_result.errors)

        error_id = await self._error_repository.save(error_report)
        await self._event_publisher.publish_error_created(error_report)
        await self._cache.invalidate_pattern("errors:*")

        return error_id

# ❌ BAD: High-level module depends on concretions
class SubmitErrorReportUseCase:
    def __init__(self):
        self._postgres_repo = PostgreSQLErrorRepository()  # Concrete dependency
        self._kafka_publisher = KafkaEventPublisher()      # Concrete dependency
        self._redis_cache = RedisCache()                   # Concrete dependency
```

**Dependency Injection Container:**
```python
class DIContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register_singleton(self, interface: Type, implementation: Type):
        self._services[interface] = (implementation, True)

    def register_transient(self, interface: Type, implementation: Type):
        self._services[interface] = (implementation, False)

    def get(self, interface: Type):
        if interface not in self._services:
            raise ValueError(f"Service {interface} not registered")

        implementation, is_singleton = self._services[interface]

        if is_singleton:
            if interface not in self._singletons:
                self._singletons[interface] = implementation()
            return self._singletons[interface]

        return implementation()

# Configuration
def configure_container() -> DIContainer:
    container = DIContainer()

    # Register abstractions with concrete implementations
    container.register_singleton(ErrorRepositoryPort, PostgreSQLErrorRepository)
    container.register_singleton(EventPublishingPort, KafkaEventPublisher)
    container.register_singleton(CachePort, RedisCache)
    container.register_transient(ErrorValidatorPort, ErrorValidator)

    return container
```

### Benefits
- Business logic is independent of infrastructure
- Easy to test with mock implementations
- Technology can be swapped without code changes
- Supports multiple deployment configurations

---

## Service-Specific Implementation Examples

### Error Reporting Service (ERS)

**SRP Implementation:**
```python
# Each class has a single responsibility
class ErrorReportDomain:
    """Only contains business logic for error reports"""
    def __init__(self, job_id: str, speaker_id: str, original_text: str, corrected_text: str):
        self.job_id = job_id
        self.speaker_id = speaker_id
        self.original_text = original_text
        self.corrected_text = corrected_text

    def calculate_severity(self) -> SeverityLevel:
        """Business logic for severity calculation"""
        pass

class ErrorReportValidator:
    """Only validates error reports"""
    def validate(self, error_report: ErrorReportDomain) -> ValidationResult:
        pass

class ErrorReportRepository:
    """Only handles data persistence"""
    def save(self, error_report: ErrorReportDomain) -> str:
        pass
```

**OCP Implementation:**
```python
# Extensible validation without modifying existing code
class ValidationRule(ABC):
    @abstractmethod
    def validate(self, error_report: ErrorReportDomain) -> ValidationResult:
        pass

class RequiredFieldsRule(ValidationRule):
    def validate(self, error_report: ErrorReportDomain) -> ValidationResult:
        # Check required fields
        pass

class TextLengthRule(ValidationRule):
    def validate(self, error_report: ErrorReportDomain) -> ValidationResult:
        # Check text length limits
        pass

# New rules can be added without modifying existing code
class CustomBusinessRule(ValidationRule):
    def validate(self, error_report: ErrorReportDomain) -> ValidationResult:
        # Custom validation logic
        pass
```

### RAG Integration Service (RIS)

**DIP Implementation for ML Models:**
```python
# High-level ML logic depends on abstractions
class EmbeddingGenerationUseCase:
    def __init__(
        self,
        embedding_model: EmbeddingModelPort,        # Abstraction
        vector_store: VectorStoragePort,            # Abstraction
        quality_calculator: QualityCalculatorPort   # Abstraction
    ):
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._quality_calculator = quality_calculator

    async def generate_and_store_embedding(self, text: str) -> str:
        embedding = await self._embedding_model.generate_embedding(text)
        quality_score = await self._quality_calculator.calculate_quality(embedding)

        if quality_score < 0.8:
            raise LowQualityEmbeddingError()

        vector_id = await self._vector_store.store_vector(embedding)
        return vector_id

# Concrete implementations can be swapped
class OpenAIEmbeddingModel(EmbeddingModelPort):
    async def generate_embedding(self, text: str) -> List[float]:
        # OpenAI implementation
        pass

class SentenceTransformerModel(EmbeddingModelPort):
    async def generate_embedding(self, text: str) -> List[float]:
        # Sentence Transformers implementation
        pass
```

### Correction Engine Service (CES)

**LSP Implementation:**
```python
# All correction algorithms are substitutable
class CorrectionAlgorithmPort(ABC):
    @abstractmethod
    async def apply_correction(self, text: str, patterns: List[Pattern]) -> CorrectionResult:
        pass

class RuleBasedCorrection(CorrectionAlgorithmPort):
    async def apply_correction(self, text: str, patterns: List[Pattern]) -> CorrectionResult:
        # Rule-based implementation
        # Must honor the same contracts as other implementations
        pass

class MLBasedCorrection(CorrectionAlgorithmPort):
    async def apply_correction(self, text: str, patterns: List[Pattern]) -> CorrectionResult:
        # ML-based implementation
        # Must behave consistently with rule-based version
        pass

# Client code works with any implementation
class CorrectionService:
    def __init__(self, algorithm: CorrectionAlgorithmPort):
        self._algorithm = algorithm  # Can be any implementation

    async def correct_text(self, text: str, patterns: List[Pattern]) -> CorrectionResult:
        return await self._algorithm.apply_correction(text, patterns)
```

---

## Code Review Checklist

### Single Responsibility Principle (SRP)
- [ ] Does each class have only one reason to change?
- [ ] Are methods focused on a single task?
- [ ] Can you describe what the class does in one sentence?
- [ ] Are there any "and" or "or" words in the class description?

### Open/Closed Principle (OCP)
- [ ] Can new functionality be added without modifying existing code?
- [ ] Are extension points clearly defined?
- [ ] Is the strategy pattern used for variable algorithms?
- [ ] Are factory patterns used for object creation?

### Liskov Substitution Principle (LSP)
- [ ] Can derived classes be substituted for base classes?
- [ ] Do all implementations honor the same contracts?
- [ ] Are pre-conditions not strengthened in derived classes?
- [ ] Are post-conditions not weakened in derived classes?

### Interface Segregation Principle (ISP)
- [ ] Are interfaces focused and cohesive?
- [ ] Do clients depend only on methods they use?
- [ ] Are large interfaces broken down into smaller ones?
- [ ] Is there a clear separation between read and write operations?

### Dependency Inversion Principle (DIP)
- [ ] Do high-level modules depend on abstractions?
- [ ] Are dependencies injected rather than created?
- [ ] Is there a clear separation between business logic and infrastructure?
- [ ] Can implementations be easily mocked for testing?

---

## Common Anti-Patterns to Avoid

### SRP Violations
```python
# ❌ BAD: God class with multiple responsibilities
class ErrorProcessor:
    def validate_error(self): pass
    def save_to_database(self): pass
    def send_notification(self): pass
    def generate_report(self): pass
    def calculate_metrics(self): pass
```

### OCP Violations
```python
# ❌ BAD: Modification required for extension
class ErrorValidator:
    def validate(self, error_report: ErrorReport, validation_type: str):
        if validation_type == "basic":
            # Basic validation
        elif validation_type == "advanced":
            # Advanced validation
        elif validation_type == "custom":  # Requires modification
            # Custom validation
```

### LSP Violations
```python
# ❌ BAD: Derived class changes expected behavior
class DatabaseRepository(ErrorRepositoryPort):
    def save(self, error_report: ErrorReport) -> str:
        if error_report.severity == "low":
            raise NotImplementedError("Low severity errors not supported")
        # This violates LSP - clients expect all errors to be saveable
```

### ISP Violations
```python
# ❌ BAD: Fat interface forces unnecessary dependencies
class AllInOnePort(ABC):
    @abstractmethod
    def read_data(self): pass
    @abstractmethod
    def write_data(self): pass
    @abstractmethod
    def send_email(self): pass
    @abstractmethod
    def generate_pdf(self): pass
    # Read-only clients are forced to depend on write/email/pdf methods
```

### DIP Violations
```python
# ❌ BAD: High-level module depends on concrete implementation
class ErrorService:
    def __init__(self):
        self._repository = PostgreSQLRepository()  # Concrete dependency
        self._cache = RedisCache()                 # Concrete dependency
```

---

## Testing Strategies for SOLID Code

### Unit Testing with SOLID Principles

**SRP Enables Focused Testing:**
```python
class TestErrorValidator:
    def test_validates_required_fields(self):
        validator = ErrorValidator()
        error_report = ErrorReport(job_id="", speaker_id="123")  # Missing job_id

        result = validator.validate(error_report)

        assert not result.is_valid
        assert "job_id is required" in result.errors
```

**DIP Enables Easy Mocking:**
```python
class TestSubmitErrorReportUseCase:
    def test_successful_submission(self):
        # Arrange
        mock_repository = Mock(spec=ErrorRepositoryPort)
        mock_publisher = Mock(spec=EventPublishingPort)
        mock_validator = Mock(spec=ErrorValidatorPort)

        mock_validator.validate.return_value = ValidationResult.success()
        mock_repository.save.return_value = "error-123"

        use_case = SubmitErrorReportUseCase(
            mock_repository, mock_publisher, mock_validator
        )

        # Act
        error_id = await use_case.execute(error_report)

        # Assert
        assert error_id == "error-123"
        mock_repository.save.assert_called_once_with(error_report)
        mock_publisher.publish_error_created.assert_called_once_with(error_report)
```

**LSP Enables Contract Testing:**
```python
class TestErrorRepositoryContract:
    """Test that all repository implementations honor the same contract"""

    @pytest.mark.parametrize("repository_class", [
        PostgreSQLErrorRepository,
        MongoDBErrorRepository,
        InMemoryErrorRepository
    ])
    def test_save_returns_valid_id(self, repository_class):
        repository = repository_class()
        error_report = create_valid_error_report()

        error_id = await repository.save(error_report)

        assert error_id is not None
        assert len(error_id) > 0
        assert isinstance(error_id, str)
```

---

**Document Status:** ✅ Implementation Ready
**Compliance Level:** All modules must follow SOLID principles
**Review Required:** Architecture Review Board approval for any SOLID principle violations
**Next Review Date:** Monthly SOLID compliance audits
