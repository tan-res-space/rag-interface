#!/bin/bash
# Comprehensive Test Runner Script
# Runs all test suites with coverage reporting and quality checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Configuration
COVERAGE_THRESHOLD=90
PARALLEL_WORKERS=auto
TEST_TIMEOUT=300

# Parse command line arguments
UNIT_ONLY=false
INTEGRATION_ONLY=false
E2E_ONLY=false
COVERAGE_ONLY=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            UNIT_ONLY=true
            shift
            ;;
        --integration-only)
            INTEGRATION_ONLY=true
            shift
            ;;
        --e2e-only)
            E2E_ONLY=true
            shift
            ;;
        --coverage-only)
            COVERAGE_ONLY=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --threshold)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --workers)
            PARALLEL_WORKERS="$2"
            shift 2
            ;;
        --timeout)
            TEST_TIMEOUT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --unit-only        Run only unit tests"
            echo "  --integration-only Run only integration tests"
            echo "  --e2e-only         Run only end-to-end tests"
            echo "  --coverage-only    Run only coverage analysis"
            echo "  --verbose, -v      Verbose output"
            echo "  --threshold N      Coverage threshold (default: 90)"
            echo "  --workers N        Number of parallel workers (default: auto)"
            echo "  --timeout N        Test timeout in seconds (default: 300)"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Setup test environment
setup_test_env() {
    log_info "Setting up test environment..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        log_error "Virtual environment not found. Run setup-dev.sh first."
        exit 1
    fi
    
    # Load test environment
    export ENVIRONMENT=testing
    if [ -f "config/environments/testing.env" ]; then
        set -a
        source config/environments/testing.env
        set +a
    fi
    
    # Create test results directory
    mkdir -p reports/test-results
    mkdir -p reports/quality
    
    log_success "Test environment ready"
}

# Run unit tests
run_unit_tests() {
    log_info "Running unit tests..."
    
    local pytest_args=()
    
    if [ "$VERBOSE" = true ]; then
        pytest_args+=("-v")
    fi
    
    if [ "$PARALLEL_WORKERS" != "auto" ]; then
        pytest_args+=("-n" "$PARALLEL_WORKERS")
    else
        pytest_args+=("-n" "auto")
    fi
    
    pytest_args+=(
        "tests/unit/"
        "--cov=src"
        "--cov-report=html:reports/coverage-unit"
        "--cov-report=xml:reports/test-results/coverage-unit.xml"
        "--cov-report=term-missing"
        "--junit-xml=reports/test-results/unit-tests.xml"
        "--timeout=$TEST_TIMEOUT"
    )
    
    if pytest "${pytest_args[@]}"; then
        log_success "Unit tests passed"
        return 0
    else
        log_error "Unit tests failed"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    # Start test services if needed
    log_info "Starting test services..."
    make test-services-up
    
    local pytest_args=()
    
    if [ "$VERBOSE" = true ]; then
        pytest_args+=("-v")
    fi
    
    pytest_args+=(
        "tests/integration/"
        "--cov=src"
        "--cov-append"
        "--cov-report=html:reports/coverage-integration"
        "--cov-report=xml:reports/test-results/coverage-integration.xml"
        "--junit-xml=reports/test-results/integration-tests.xml"
        "--timeout=$TEST_TIMEOUT"
    )
    
    local result=0
    if pytest "${pytest_args[@]}"; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        result=1
    fi
    
    # Stop test services
    log_info "Stopping test services..."
    make test-services-down
    
    return $result
}

# Run end-to-end tests
run_e2e_tests() {
    log_info "Running end-to-end tests..."
    
    # Start full application stack
    log_info "Starting application stack..."
    make test-stack-up
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    local result=0
    
    # Run API E2E tests
    log_info "Running API E2E tests..."
    if pytest tests/e2e/api/ -v --junit-xml=test-results/e2e-api-tests.xml; then
        log_success "API E2E tests passed"
    else
        log_error "API E2E tests failed"
        result=1
    fi
    
    # Run Frontend E2E tests
    log_info "Running Frontend E2E tests..."
    cd frontend
    if npm run test:e2e; then
        log_success "Frontend E2E tests passed"
    else
        log_error "Frontend E2E tests failed"
        result=1
    fi
    cd ..
    
    # Stop application stack
    log_info "Stopping application stack..."
    make test-stack-down
    
    return $result
}

# Generate coverage report
generate_coverage_report() {
    log_info "Generating comprehensive coverage report..."
    
    # Combine coverage data
    coverage combine
    
    # Generate reports
    coverage html -d reports/coverage-combined
    coverage xml -o reports/test-results/coverage-combined.xml
    coverage report --show-missing
    
    # Check coverage threshold
    local coverage_percent=$(coverage report | tail -1 | awk '{print $4}' | sed 's/%//')
    
    if (( $(echo "$coverage_percent >= $COVERAGE_THRESHOLD" | bc -l) )); then
        log_success "Coverage threshold met: ${coverage_percent}% >= ${COVERAGE_THRESHOLD}%"
        return 0
    else
        log_error "Coverage threshold not met: ${coverage_percent}% < ${COVERAGE_THRESHOLD}%"
        return 1
    fi
}

# Run code quality checks
run_quality_checks() {
    log_info "Running code quality checks..."
    
    local result=0
    
    # Run linting
    log_info "Running linting checks..."
    if flake8 src/ tests/ --output-file=reports/quality/flake8-report.txt; then
        log_success "Linting checks passed"
    else
        log_warning "Linting issues found (see reports/quality/flake8-report.txt)"
    fi

    # Run type checking
    log_info "Running type checking..."
    if mypy src/ --html-report reports/quality/mypy-report; then
        log_success "Type checking passed"
    else
        log_warning "Type checking issues found (see reports/quality/mypy-report)"
    fi

    # Run security checks
    log_info "Running security checks..."
    if bandit -r src/ -f json -o reports/quality/bandit-report.json; then
        log_success "Security checks passed"
    else
        log_warning "Security issues found (see reports/quality/bandit-report.json)"
    fi
    
    return $result
}

# Main test execution
main() {
    log_info "Starting comprehensive test suite..."
    
    setup_test_env
    
    local overall_result=0
    
    # Run tests based on options
    if [ "$COVERAGE_ONLY" = true ]; then
        generate_coverage_report || overall_result=1
    elif [ "$UNIT_ONLY" = true ]; then
        run_unit_tests || overall_result=1
    elif [ "$INTEGRATION_ONLY" = true ]; then
        run_integration_tests || overall_result=1
    elif [ "$E2E_ONLY" = true ]; then
        run_e2e_tests || overall_result=1
    else
        # Run all tests
        log_info "Running complete test suite..."
        
        run_unit_tests || overall_result=1
        run_integration_tests || overall_result=1
        run_e2e_tests || overall_result=1
        generate_coverage_report || overall_result=1
    fi
    
    # Run quality checks
    run_quality_checks
    
    # Summary
    echo
    if [ $overall_result -eq 0 ]; then
        log_success "All tests completed successfully!"
    else
        log_error "Some tests failed. Check the reports in reports/"
    fi

    log_info "Test reports available in:"
    echo "  - reports/test-results/: JUnit XML and coverage reports"
    echo "  - reports/quality/: HTML coverage and quality reports"
    
    exit $overall_result
}

# Run main function
main "$@"
