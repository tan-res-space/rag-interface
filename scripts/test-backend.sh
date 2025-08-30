#!/bin/bash

# =====================================================
# RAG Interface - Backend Testing Script
# =====================================================
# This script runs backend-specific tests with detailed reporting
# =====================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Setup test environment
setup_test_env() {
    log_info "Setting up backend test environment..."
    
    cd "$PROJECT_ROOT"
    
    # Activate Python virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        log_error "Python virtual environment not found. Please run scripts/dev-setup.sh first"
        exit 1
    fi
    
    # Set test environment variables
    export PYTHONPATH="$PROJECT_ROOT"
    export TESTING=true
    export DATABASE_URL="sqlite:///./test.db"
    export REDIS_URL="redis://localhost:6379/15"
    export LOG_LEVEL="WARNING"  # Reduce log noise during tests
    
    # Create test results directory
    mkdir -p test-results
    
    log_success "Backend test environment setup complete"
}

# Run unit tests for specific service
run_service_tests() {
    local service="$1"
    local coverage_target="${2:-80}"
    
    log_info "Running unit tests for $service..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run pytest for specific service
    if pytest "tests/unit/$service/" \
        --cov="src/$service" \
        --cov-report=term-missing \
        --cov-report=html:"htmlcov/$service" \
        --cov-report=xml:"test-results/coverage-$service.xml" \
        --cov-fail-under="$coverage_target" \
        --junit-xml="test-results/$service-unit.xml" \
        -v \
        --tb=short; then
        log_success "$service unit tests passed"
        return 0
    else
        log_error "$service unit tests failed"
        return 1
    fi
}

# Run all backend unit tests
run_all_unit_tests() {
    log_info "Running all backend unit tests..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run pytest for all services
    if pytest tests/unit/ \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=xml:test-results/coverage.xml \
        --cov-fail-under=80 \
        --junit-xml=test-results/backend-unit.xml \
        -v \
        --tb=short \
        --durations=10; then
        log_success "All backend unit tests passed"
        return 0
    else
        log_error "Backend unit tests failed"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    log_info "Running backend integration tests..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Start test services if needed
    start_test_services
    
    # Run integration tests
    if pytest tests/integration/ \
        --junit-xml=test-results/backend-integration.xml \
        -v \
        --tb=short \
        --durations=10; then
        log_success "Backend integration tests passed"
        cleanup_test_services
        return 0
    else
        log_error "Backend integration tests failed"
        cleanup_test_services
        return 1
    fi
}

# Start test services
start_test_services() {
    log_info "Starting test services..."
    
    # Start test PostgreSQL
    if command -v docker >/dev/null 2>&1; then
        docker run -d --name test-postgres-$$ \
            -e POSTGRES_DB=test_db \
            -e POSTGRES_USER=test_user \
            -e POSTGRES_PASSWORD=test_pass \
            -p 5433:5432 \
            postgres:15-alpine >/dev/null 2>&1 || true
        
        # Wait for PostgreSQL to be ready
        sleep 5
        
        # Update DATABASE_URL for integration tests
        export DATABASE_URL="postgresql://test_user:test_pass@localhost:5433/test_db"
    fi
    
    log_success "Test services started"
}

# Cleanup test services
cleanup_test_services() {
    log_info "Cleaning up test services..."
    
    if command -v docker >/dev/null 2>&1; then
        docker stop test-postgres-$$ >/dev/null 2>&1 || true
        docker rm test-postgres-$$ >/dev/null 2>&1 || true
    fi
    
    log_success "Test services cleaned up"
}

# Run code quality checks
run_quality_checks() {
    log_info "Running backend code quality checks..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Create quality results directory
    mkdir -p test-results/quality
    
    # Linting with flake8
    log_info "Running flake8 linting..."
    flake8 src/ tests/ \
        --max-line-length=88 \
        --extend-ignore=E203,W503 \
        --format=json \
        --output-file=test-results/quality/flake8-report.json || true
    
    # Type checking with mypy
    log_info "Running mypy type checking..."
    mypy src/ \
        --ignore-missing-imports \
        --junit-xml=test-results/quality/mypy-report.xml || true
    
    # Security scanning with bandit
    log_info "Running bandit security scan..."
    bandit -r src/ \
        -f json \
        -o test-results/quality/bandit-report.json || true
    
    # Code formatting check with black
    log_info "Checking code formatting with black..."
    black --check --diff src/ tests/ > test-results/quality/black-report.txt || true
    
    # Import sorting check with isort
    log_info "Checking import sorting with isort..."
    isort --check-only --diff src/ tests/ > test-results/quality/isort-report.txt || true
    
    log_success "Code quality checks completed"
}

# Generate test report
generate_backend_report() {
    log_info "Generating backend test report..."
    
    cd "$PROJECT_ROOT"
    
    # Generate detailed report
    cat > test-results/backend-report.md << EOF
# Backend Test Results

## Test Summary
- Test Run Date: $(date)
- Python Version: $(python --version)
- Test Framework: pytest

## Coverage Reports
$([ -f "test-results/coverage.xml" ] && echo "- Overall Coverage: [XML Report](coverage.xml)" || echo "- Overall Coverage: Not available")
$([ -d "htmlcov" ] && echo "- HTML Coverage Report: [View Report](../htmlcov/index.html)" || echo "- HTML Coverage: Not available")

## Test Results
$([ -f "test-results/backend-unit.xml" ] && echo "- Unit Tests: [JUnit XML](backend-unit.xml)" || echo "- Unit Tests: Not run")
$([ -f "test-results/backend-integration.xml" ] && echo "- Integration Tests: [JUnit XML](backend-integration.xml)" || echo "- Integration Tests: Not run")

## Code Quality
$([ -f "test-results/quality/flake8-report.json" ] && echo "- Linting Report: [Flake8 JSON](quality/flake8-report.json)" || echo "- Linting: Not run")
$([ -f "test-results/quality/mypy-report.xml" ] && echo "- Type Checking: [MyPy XML](quality/mypy-report.xml)" || echo "- Type Checking: Not run")
$([ -f "test-results/quality/bandit-report.json" ] && echo "- Security Scan: [Bandit JSON](quality/bandit-report.json)" || echo "- Security Scan: Not run")

## Service-Specific Coverage
$(find test-results -name "coverage-*.xml" | while read file; do
    service=$(basename "$file" | sed 's/coverage-\(.*\)\.xml/\1/')
    echo "- $service: [Coverage XML]($file)"
done)

EOF
    
    log_success "Backend test report generated: test-results/backend-report.md"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [SERVICE]"
    echo ""
    echo "Options:"
    echo "  --unit          Run unit tests only (default)"
    echo "  --integration   Run integration tests"
    echo "  --quality       Run code quality checks"
    echo "  --all           Run all tests and checks"
    echo "  --service NAME  Run tests for specific service"
    echo "  --help          Show this help message"
    echo ""
    echo "Services:"
    echo "  error_reporting_service"
    echo "  user_management_service"
    echo "  rag_integration_service"
    echo "  correction_engine_service"
    echo "  verification_service"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all unit tests"
    echo "  $0 --integration                      # Run integration tests"
    echo "  $0 --service error_reporting_service  # Test specific service"
    echo "  $0 --all                              # Run everything"
}

# Main function
main() {
    local run_unit=true
    local run_integration=false
    local run_quality=false
    local specific_service=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --unit)
                run_unit=true
                run_integration=false
                run_quality=false
                shift
                ;;
            --integration)
                run_integration=true
                run_unit=false
                run_quality=false
                shift
                ;;
            --quality)
                run_quality=true
                run_unit=false
                run_integration=false
                shift
                ;;
            --all)
                run_unit=true
                run_integration=true
                run_quality=true
                shift
                ;;
            --service)
                specific_service="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    log_info "Starting backend tests..."
    
    setup_test_env
    
    local exit_code=0
    
    # Run tests based on options
    if [ -n "$specific_service" ]; then
        run_service_tests "$specific_service" || exit_code=1
    else
        if [ "$run_unit" = true ]; then
            run_all_unit_tests || exit_code=1
        fi
        
        if [ "$run_integration" = true ]; then
            run_integration_tests || exit_code=1
        fi
        
        if [ "$run_quality" = true ]; then
            run_quality_checks || exit_code=1
        fi
    fi
    
    generate_backend_report
    
    if [ $exit_code -eq 0 ]; then
        log_success "Backend tests completed successfully!"
    else
        log_error "Backend tests failed. Check the reports for details."
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
