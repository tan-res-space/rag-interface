#!/bin/bash

# =====================================================
# RAG Interface - Comprehensive Testing Script
# =====================================================
# This script runs all tests for the RAG Interface project
# including backend, frontend, integration, and E2E tests
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

# Test results
BACKEND_TESTS_PASSED=false
FRONTEND_TESTS_PASSED=false
E2E_TESTS_PASSED=false
INTEGRATION_TESTS_PASSED=false

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup test environment
setup_test_env() {
    log_info "Setting up test environment..."
    
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
    export REDIS_URL="redis://localhost:6379/15"  # Use different Redis DB for tests
    
    log_success "Test environment setup complete"
}

# Run backend unit tests
run_backend_tests() {
    log_info "Running backend unit tests..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run pytest with coverage
    if pytest tests/unit/ \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        --cov-fail-under=80 \
        --junit-xml=test-results/backend-unit.xml \
        -v; then
        BACKEND_TESTS_PASSED=true
        log_success "Backend unit tests passed"
    else
        log_error "Backend unit tests failed"
        return 1
    fi
}

# Run backend integration tests
run_integration_tests() {
    log_info "Running backend integration tests..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start test database if needed
    if command_exists docker; then
        docker run -d --name test-postgres \
            -e POSTGRES_DB=test_db \
            -e POSTGRES_USER=test_user \
            -e POSTGRES_PASSWORD=test_pass \
            -p 5433:5432 \
            postgres:15-alpine || true
        sleep 5
    fi
    
    # Run integration tests
    if pytest tests/integration/ \
        --junit-xml=test-results/backend-integration.xml \
        -v; then
        INTEGRATION_TESTS_PASSED=true
        log_success "Backend integration tests passed"
    else
        log_error "Backend integration tests failed"
        return 1
    fi
    
    # Cleanup test database
    if command_exists docker; then
        docker stop test-postgres || true
        docker rm test-postgres || true
    fi
}

# Run frontend tests
run_frontend_tests() {
    log_info "Running frontend tests..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_error "Frontend dependencies not found. Please run scripts/dev-setup.sh first"
        return 1
    fi
    
    # Run unit tests with coverage
    if npm run test:coverage -- --reporter=junit --outputFile=../test-results/frontend-unit.xml; then
        FRONTEND_TESTS_PASSED=true
        log_success "Frontend tests passed"
    else
        log_error "Frontend tests failed"
        return 1
    fi
}

# Run E2E tests
run_e2e_tests() {
    log_info "Running E2E tests..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if services are running
    if ! curl -s http://localhost:3000 >/dev/null 2>&1; then
        log_warning "Frontend not running. Starting development environment..."
        cd "$PROJECT_ROOT"
        scripts/dev-start.sh
        sleep 30
    fi
    
    # Run Playwright tests
    if npm run test:e2e -- --reporter=junit --output-dir=../test-results/e2e; then
        E2E_TESTS_PASSED=true
        log_success "E2E tests passed"
    else
        log_error "E2E tests failed"
        return 1
    fi
}

# Run code quality checks
run_quality_checks() {
    log_info "Running code quality checks..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Python code quality
    log_info "Running Python linting..."
    flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
    
    log_info "Running Python type checking..."
    mypy src/ --ignore-missing-imports
    
    log_info "Running Python security checks..."
    bandit -r src/ -f json -o test-results/bandit-report.json || true
    
    # Frontend code quality
    cd frontend
    log_info "Running frontend linting..."
    npm run lint
    
    log_success "Code quality checks completed"
}

# Generate test report
generate_report() {
    log_info "Generating test report..."
    
    cd "$PROJECT_ROOT"
    
    # Create test results directory
    mkdir -p test-results
    
    # Generate summary report
    cat > test-results/summary.md << EOF
# Test Results Summary

## Test Status
- Backend Unit Tests: $([ "$BACKEND_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED")
- Backend Integration Tests: $([ "$INTEGRATION_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED")
- Frontend Tests: $([ "$FRONTEND_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED")
- E2E Tests: $([ "$E2E_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED")

## Coverage Reports
- Backend Coverage: [HTML Report](htmlcov/index.html)
- Frontend Coverage: [Coverage Report](frontend/coverage/index.html)

## Test Artifacts
- Backend Unit Results: test-results/backend-unit.xml
- Backend Integration Results: test-results/backend-integration.xml
- Frontend Results: test-results/frontend-unit.xml
- E2E Results: test-results/e2e/
- Security Report: test-results/bandit-report.json

Generated on: $(date)
EOF
    
    log_success "Test report generated: test-results/summary.md"
}

# Main function
main() {
    local run_e2e=false
    local run_integration=false
    local quick_mode=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --e2e)
                run_e2e=true
                shift
                ;;
            --integration)
                run_integration=true
                shift
                ;;
            --quick)
                quick_mode=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --e2e          Run E2E tests"
                echo "  --integration  Run integration tests"
                echo "  --quick        Run only unit tests"
                echo "  --help         Show this help"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    log_info "Starting comprehensive test suite..."
    
    setup_test_env
    
    # Create test results directory
    mkdir -p test-results
    
    # Run tests based on options
    if [ "$quick_mode" = true ]; then
        run_backend_tests
        run_frontend_tests
    else
        run_backend_tests
        run_frontend_tests
        run_quality_checks
        
        if [ "$run_integration" = true ]; then
            run_integration_tests
        fi
        
        if [ "$run_e2e" = true ]; then
            run_e2e_tests
        fi
    fi
    
    generate_report
    
    # Final status
    if [ "$BACKEND_TESTS_PASSED" = true ] && [ "$FRONTEND_TESTS_PASSED" = true ]; then
        log_success "All tests passed!"
        exit 0
    else
        log_error "Some tests failed. Check the reports for details."
        exit 1
    fi
}

# Run main function
main "$@"
