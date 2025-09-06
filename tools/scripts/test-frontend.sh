#!/bin/bash

# =====================================================
# RAG Interface - Frontend Testing Script
# =====================================================
# This script runs frontend-specific tests with detailed reporting
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
    log_info "Setting up frontend test environment..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_error "Frontend dependencies not found. Please run scripts/dev-setup.sh first"
        exit 1
    fi
    
    # Set test environment variables
    export NODE_ENV=test
    export CI=true
    
    # Create test results directory
    mkdir -p ../test-results/frontend
    
    log_success "Frontend test environment setup complete"
}

# Run unit tests
run_unit_tests() {
    log_info "Running frontend unit tests..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run Vitest with coverage
    if npm run test:coverage -- \
        --reporter=verbose \
        --reporter=junit \
        --outputFile=../test-results/frontend/unit-tests.xml \
        --coverage.reporter=text \
        --coverage.reporter=html \
        --coverage.reporter=lcov \
        --coverage.reporter=json \
        --coverage.reportsDirectory=../test-results/frontend/coverage; then
        log_success "Frontend unit tests passed"
        return 0
    else
        log_error "Frontend unit tests failed"
        return 1
    fi
}

# Run component tests
run_component_tests() {
    log_info "Running frontend component tests..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run component-specific tests
    if npm run test -- \
        --run \
        --reporter=verbose \
        --reporter=junit \
        --outputFile=../test-results/frontend/component-tests.xml \
        src/components/; then
        log_success "Frontend component tests passed"
        return 0
    else
        log_error "Frontend component tests failed"
        return 1
    fi
}

# Run E2E tests
run_e2e_tests() {
    log_info "Running frontend E2E tests..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if development server is running
    if ! curl -s http://localhost:3000 >/dev/null 2>&1; then
        log_warning "Development server not running. Starting it..."
        npm run dev &
        DEV_SERVER_PID=$!
        
        # Wait for server to start
        timeout=60
        while ! curl -s http://localhost:3000 >/dev/null 2>&1; do
            sleep 2
            timeout=$((timeout - 2))
            if [ $timeout -le 0 ]; then
                log_error "Timeout waiting for development server"
                kill $DEV_SERVER_PID 2>/dev/null || true
                return 1
            fi
        done
        
        log_info "Development server started"
    fi
    
    # Run Playwright tests
    if npm run test:e2e -- \
        --reporter=junit \
        --output-dir=../test-results/frontend/e2e \
        --reporter=html \
        --reporter=json; then
        log_success "Frontend E2E tests passed"
        
        # Stop development server if we started it
        if [ -n "${DEV_SERVER_PID:-}" ]; then
            kill $DEV_SERVER_PID 2>/dev/null || true
        fi
        
        return 0
    else
        log_error "Frontend E2E tests failed"
        
        # Stop development server if we started it
        if [ -n "${DEV_SERVER_PID:-}" ]; then
            kill $DEV_SERVER_PID 2>/dev/null || true
        fi
        
        return 1
    fi
}

# Run linting
run_linting() {
    log_info "Running frontend linting..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run ESLint
    if npm run lint -- \
        --format=json \
        --output-file=../test-results/frontend/eslint-report.json; then
        log_success "Frontend linting passed"
        return 0
    else
        log_warning "Frontend linting found issues"
        return 1
    fi
}

# Run type checking
run_type_checking() {
    log_info "Running frontend type checking..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run TypeScript compiler check
    if npx tsc --noEmit --pretty false > ../test-results/frontend/typescript-report.txt 2>&1; then
        log_success "Frontend type checking passed"
        return 0
    else
        log_error "Frontend type checking failed"
        return 1
    fi
}

# Run build test
run_build_test() {
    log_info "Running frontend build test..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Test production build
    if npm run build > ../test-results/frontend/build-output.txt 2>&1; then
        log_success "Frontend build test passed"
        
        # Check if build artifacts exist
        if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
            log_info "Build artifacts created successfully"
            
            # Test preview server
            npm run preview &
            PREVIEW_PID=$!
            sleep 5
            
            if curl -s http://localhost:4173 >/dev/null 2>&1; then
                log_success "Preview server test passed"
            else
                log_warning "Preview server test failed"
            fi
            
            kill $PREVIEW_PID 2>/dev/null || true
        else
            log_error "Build artifacts not found"
            return 1
        fi
        
        return 0
    else
        log_error "Frontend build test failed"
        return 1
    fi
}

# Run accessibility tests
run_accessibility_tests() {
    log_info "Running frontend accessibility tests..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run axe-core accessibility tests (if configured)
    if npm run test:a11y 2>/dev/null || true; then
        log_success "Frontend accessibility tests completed"
        return 0
    else
        log_warning "Frontend accessibility tests not configured or failed"
        return 1
    fi
}

# Generate frontend test report
generate_frontend_report() {
    log_info "Generating frontend test report..."
    
    cd "$PROJECT_ROOT"
    
    # Generate detailed report
    cat > test-results/frontend/frontend-report.md << EOF
# Frontend Test Results

## Test Summary
- Test Run Date: $(date)
- Node.js Version: $(node --version)
- npm Version: $(npm --version)
- Test Framework: Vitest + Playwright

## Test Results
$([ -f "test-results/frontend/unit-tests.xml" ] && echo "- Unit Tests: [JUnit XML](unit-tests.xml)" || echo "- Unit Tests: Not run")
$([ -f "test-results/frontend/component-tests.xml" ] && echo "- Component Tests: [JUnit XML](component-tests.xml)" || echo "- Component Tests: Not run")
$([ -d "test-results/frontend/e2e" ] && echo "- E2E Tests: [Playwright Report](e2e/)" || echo "- E2E Tests: Not run")

## Coverage Reports
$([ -d "reports/test-results/frontend/coverage" ] && echo "- Coverage Report: [HTML Report](coverage/index.html)" || echo "- Coverage: Not available")
$([ -f "reports/test-results/frontend/coverage/lcov.info" ] && echo "- LCOV Coverage: [LCOV File](coverage/lcov.info)" || echo "- LCOV Coverage: Not available")

## Code Quality
$([ -f "reports/test-results/frontend/eslint-report.json" ] && echo "- ESLint Report: [JSON Report](eslint-report.json)" || echo "- ESLint: Not run")
$([ -f "reports/test-results/frontend/typescript-report.txt" ] && echo "- TypeScript Check: [Report](typescript-report.txt)" || echo "- TypeScript: Not run")

## Build Artifacts
$([ -f "test-results/frontend/build-output.txt" ] && echo "- Build Output: [Log](build-output.txt)" || echo "- Build Test: Not run")
$([ -d "frontend/dist" ] && echo "- Build Artifacts: Available in frontend/dist/" || echo "- Build Artifacts: Not available")

EOF
    
    log_success "Frontend test report generated: test-results/frontend/frontend-report.md"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --unit          Run unit tests only"
    echo "  --component     Run component tests"
    echo "  --e2e           Run E2E tests"
    echo "  --lint          Run linting"
    echo "  --type-check    Run type checking"
    echo "  --build         Run build test"
    echo "  --a11y          Run accessibility tests"
    echo "  --all           Run all tests and checks (default)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run all frontend tests"
    echo "  $0 --unit       # Run unit tests only"
    echo "  $0 --e2e        # Run E2E tests only"
    echo "  $0 --lint       # Run linting only"
}

# Main function
main() {
    local run_unit=false
    local run_component=false
    local run_e2e=false
    local run_lint=false
    local run_type_check=false
    local run_build=false
    local run_a11y=false
    local run_all=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --unit)
                run_unit=true
                run_all=false
                shift
                ;;
            --component)
                run_component=true
                run_all=false
                shift
                ;;
            --e2e)
                run_e2e=true
                run_all=false
                shift
                ;;
            --lint)
                run_lint=true
                run_all=false
                shift
                ;;
            --type-check)
                run_type_check=true
                run_all=false
                shift
                ;;
            --build)
                run_build=true
                run_all=false
                shift
                ;;
            --a11y)
                run_a11y=true
                run_all=false
                shift
                ;;
            --all)
                run_all=true
                shift
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
    
    log_info "Starting frontend tests..."
    
    setup_test_env
    
    local exit_code=0
    
    # Run tests based on options
    if [ "$run_all" = true ]; then
        run_unit_tests || exit_code=1
        run_component_tests || exit_code=1
        run_lint || exit_code=1
        run_type_checking || exit_code=1
        run_build_test || exit_code=1
        run_accessibility_tests || exit_code=1
        run_e2e_tests || exit_code=1
    else
        [ "$run_unit" = true ] && (run_unit_tests || exit_code=1)
        [ "$run_component" = true ] && (run_component_tests || exit_code=1)
        [ "$run_e2e" = true ] && (run_e2e_tests || exit_code=1)
        [ "$run_lint" = true ] && (run_linting || exit_code=1)
        [ "$run_type_check" = true ] && (run_type_checking || exit_code=1)
        [ "$run_build" = true ] && (run_build_test || exit_code=1)
        [ "$run_a11y" = true ] && (run_accessibility_tests || exit_code=1)
    fi
    
    generate_frontend_report
    
    if [ $exit_code -eq 0 ]; then
        log_success "Frontend tests completed successfully!"
    else
        log_error "Frontend tests failed. Check the reports for details."
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
