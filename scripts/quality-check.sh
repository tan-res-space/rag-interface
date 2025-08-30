#!/bin/bash

# =====================================================
# RAG Interface - Code Quality Check Script
# =====================================================
# This script runs comprehensive code quality checks
# for both backend and frontend components
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

# Quality check results
BACKEND_QUALITY_PASSED=true
FRONTEND_QUALITY_PASSED=true

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

# Setup environment
setup_env() {
    log_info "Setting up quality check environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create quality results directory
    mkdir -p quality-reports
    
    # Activate Python virtual environment if available
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    log_success "Environment setup complete"
}

# Run backend quality checks
run_backend_quality() {
    log_info "Running backend code quality checks..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate 2>/dev/null || true
    
    local backend_failed=false
    
    # Black formatting check
    log_info "Checking Python code formatting with Black..."
    if black --check --diff src/ tests/ > quality-reports/black-report.txt 2>&1; then
        log_success "Black formatting check passed"
    else
        log_warning "Black formatting issues found"
        backend_failed=true
    fi
    
    # isort import sorting check
    log_info "Checking import sorting with isort..."
    if isort --check-only --diff src/ tests/ > quality-reports/isort-report.txt 2>&1; then
        log_success "isort check passed"
    else
        log_warning "Import sorting issues found"
        backend_failed=true
    fi
    
    # Flake8 linting
    log_info "Running Flake8 linting..."
    if flake8 src/ tests/ \
        --max-line-length=88 \
        --extend-ignore=E203,W503 \
        --format=json \
        --output-file=quality-reports/flake8-report.json; then
        log_success "Flake8 linting passed"
    else
        log_warning "Flake8 linting issues found"
        backend_failed=true
    fi
    
    # MyPy type checking
    log_info "Running MyPy type checking..."
    if mypy src/ \
        --ignore-missing-imports \
        --junit-xml=quality-reports/mypy-report.xml \
        > quality-reports/mypy-output.txt 2>&1; then
        log_success "MyPy type checking passed"
    else
        log_warning "MyPy type checking issues found"
        backend_failed=true
    fi
    
    # Bandit security scanning
    log_info "Running Bandit security scan..."
    if bandit -r src/ \
        -f json \
        -o quality-reports/bandit-report.json \
        > quality-reports/bandit-output.txt 2>&1; then
        log_success "Bandit security scan passed"
    else
        log_warning "Bandit security issues found"
        backend_failed=true
    fi
    
    # Autoflake unused imports check
    log_info "Checking for unused imports with autoflake..."
    if autoflake --check --recursive src/ tests/ > quality-reports/autoflake-report.txt 2>&1; then
        log_success "Autoflake check passed"
    else
        log_warning "Unused imports found"
        backend_failed=true
    fi
    
    if [ "$backend_failed" = true ]; then
        BACKEND_QUALITY_PASSED=false
        log_error "Backend quality checks failed"
    else
        log_success "All backend quality checks passed"
    fi
}

# Run frontend quality checks
run_frontend_quality() {
    log_info "Running frontend code quality checks..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_error "Frontend dependencies not found. Please run scripts/dev-setup.sh first"
        FRONTEND_QUALITY_PASSED=false
        return 1
    fi
    
    local frontend_failed=false
    
    # ESLint
    log_info "Running ESLint..."
    if npm run lint -- \
        --format=json \
        --output-file=../quality-reports/eslint-report.json \
        > ../quality-reports/eslint-output.txt 2>&1; then
        log_success "ESLint check passed"
    else
        log_warning "ESLint issues found"
        frontend_failed=true
    fi
    
    # TypeScript compilation check
    log_info "Running TypeScript compilation check..."
    if npx tsc --noEmit --pretty false > ../quality-reports/typescript-report.txt 2>&1; then
        log_success "TypeScript compilation check passed"
    else
        log_warning "TypeScript compilation issues found"
        frontend_failed=true
    fi
    
    # Prettier formatting check
    log_info "Checking code formatting with Prettier..."
    if npx prettier --check src/ > ../quality-reports/prettier-report.txt 2>&1; then
        log_success "Prettier formatting check passed"
    else
        log_warning "Prettier formatting issues found"
        frontend_failed=true
    fi
    
    # Package audit
    log_info "Running npm audit..."
    if npm audit --audit-level=moderate --json > ../quality-reports/npm-audit.json 2>&1; then
        log_success "npm audit passed"
    else
        log_warning "npm audit found vulnerabilities"
        frontend_failed=true
    fi
    
    if [ "$frontend_failed" = true ]; then
        FRONTEND_QUALITY_PASSED=false
        log_error "Frontend quality checks failed"
    else
        log_success "All frontend quality checks passed"
    fi
}

# Fix backend issues automatically
fix_backend_issues() {
    log_info "Fixing backend code quality issues..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate 2>/dev/null || true
    
    # Auto-fix with Black
    log_info "Formatting code with Black..."
    black src/ tests/
    
    # Auto-fix with isort
    log_info "Sorting imports with isort..."
    isort src/ tests/
    
    # Auto-fix with autoflake
    log_info "Removing unused imports with autoflake..."
    autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src/ tests/
    
    # Auto-fix with pyupgrade
    log_info "Upgrading Python syntax with pyupgrade..."
    find src/ tests/ -name "*.py" -exec pyupgrade --py311-plus {} \;
    
    log_success "Backend auto-fixes applied"
}

# Fix frontend issues automatically
fix_frontend_issues() {
    log_info "Fixing frontend code quality issues..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Auto-fix with Prettier
    log_info "Formatting code with Prettier..."
    npx prettier --write src/
    
    # Auto-fix with ESLint
    log_info "Auto-fixing ESLint issues..."
    npm run lint -- --fix || true
    
    log_success "Frontend auto-fixes applied"
}

# Generate quality report
generate_quality_report() {
    log_info "Generating code quality report..."
    
    cd "$PROJECT_ROOT"
    
    # Generate comprehensive report
    cat > quality-reports/quality-summary.md << EOF
# Code Quality Report

## Summary
- Report Generated: $(date)
- Backend Quality: $([ "$BACKEND_QUALITY_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED")
- Frontend Quality: $([ "$FRONTEND_QUALITY_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED")

## Backend Quality Reports
$([ -f "quality-reports/black-report.txt" ] && echo "- [Black Formatting Report](black-report.txt)" || echo "- Black: Not run")
$([ -f "quality-reports/isort-report.txt" ] && echo "- [isort Import Sorting Report](isort-report.txt)" || echo "- isort: Not run")
$([ -f "quality-reports/flake8-report.json" ] && echo "- [Flake8 Linting Report](flake8-report.json)" || echo "- Flake8: Not run")
$([ -f "quality-reports/mypy-report.xml" ] && echo "- [MyPy Type Checking Report](mypy-report.xml)" || echo "- MyPy: Not run")
$([ -f "quality-reports/bandit-report.json" ] && echo "- [Bandit Security Report](bandit-report.json)" || echo "- Bandit: Not run")
$([ -f "quality-reports/autoflake-report.txt" ] && echo "- [Autoflake Unused Imports Report](autoflake-report.txt)" || echo "- Autoflake: Not run")

## Frontend Quality Reports
$([ -f "quality-reports/eslint-report.json" ] && echo "- [ESLint Report](eslint-report.json)" || echo "- ESLint: Not run")
$([ -f "quality-reports/typescript-report.txt" ] && echo "- [TypeScript Compilation Report](typescript-report.txt)" || echo "- TypeScript: Not run")
$([ -f "quality-reports/prettier-report.txt" ] && echo "- [Prettier Formatting Report](prettier-report.txt)" || echo "- Prettier: Not run")
$([ -f "quality-reports/npm-audit.json" ] && echo "- [npm Audit Report](npm-audit.json)" || echo "- npm audit: Not run")

## Recommendations
$([ "$BACKEND_QUALITY_PASSED" = false ] && echo "- Run \`scripts/quality-check.sh --fix-backend\` to auto-fix backend issues" || echo "- Backend code quality is excellent")
$([ "$FRONTEND_QUALITY_PASSED" = false ] && echo "- Run \`scripts/quality-check.sh --fix-frontend\` to auto-fix frontend issues" || echo "- Frontend code quality is excellent")

EOF
    
    log_success "Quality report generated: quality-reports/quality-summary.md"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backend       Run backend quality checks only"
    echo "  --frontend      Run frontend quality checks only"
    echo "  --fix-backend   Auto-fix backend quality issues"
    echo "  --fix-frontend  Auto-fix frontend quality issues"
    echo "  --fix-all       Auto-fix all quality issues"
    echo "  --all           Run all quality checks (default)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all quality checks"
    echo "  $0 --backend          # Run backend checks only"
    echo "  $0 --fix-all          # Auto-fix all issues"
    echo "  $0 --fix-backend      # Auto-fix backend issues only"
}

# Main function
main() {
    local run_backend=true
    local run_frontend=true
    local fix_backend=false
    local fix_frontend=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend)
                run_backend=true
                run_frontend=false
                shift
                ;;
            --frontend)
                run_frontend=true
                run_backend=false
                shift
                ;;
            --fix-backend)
                fix_backend=true
                run_backend=false
                run_frontend=false
                shift
                ;;
            --fix-frontend)
                fix_frontend=true
                run_backend=false
                run_frontend=false
                shift
                ;;
            --fix-all)
                fix_backend=true
                fix_frontend=true
                run_backend=false
                run_frontend=false
                shift
                ;;
            --all)
                run_backend=true
                run_frontend=true
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
    
    log_info "Starting code quality checks..."
    
    setup_env
    
    # Run fixes if requested
    if [ "$fix_backend" = true ]; then
        fix_backend_issues
    fi
    
    if [ "$fix_frontend" = true ]; then
        fix_frontend_issues
    fi
    
    # Run quality checks
    if [ "$run_backend" = true ]; then
        run_backend_quality
    fi
    
    if [ "$run_frontend" = true ]; then
        run_frontend_quality
    fi
    
    # Generate report if checks were run
    if [ "$run_backend" = true ] || [ "$run_frontend" = true ]; then
        generate_quality_report
    fi
    
    # Final status
    if [ "$BACKEND_QUALITY_PASSED" = true ] && [ "$FRONTEND_QUALITY_PASSED" = true ]; then
        log_success "All code quality checks passed!"
        exit 0
    else
        log_error "Some quality checks failed. Check the reports for details."
        exit 1
    fi
}

# Run main function
main "$@"
