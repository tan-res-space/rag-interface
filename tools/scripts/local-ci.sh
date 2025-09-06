#!/bin/bash

# =====================================================
# RAG Interface - Local CI Testing Script
# =====================================================
# This script allows testing GitHub Actions workflows locally
# using the 'act' tool or simulating CI environment
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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install act if not present
install_act() {
    log_info "Installing act (GitHub Actions local runner)..."
    
    if command_exists act; then
        log_info "act is already installed"
        return 0
    fi
    
    # Install act using curl
    if command_exists curl; then
        curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
    else
        log_error "curl is required to install act"
        return 1
    fi
    
    log_success "act installed successfully"
}

# Setup local CI environment
setup_local_ci() {
    log_info "Setting up local CI environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create .actrc file for act configuration
    cat > .actrc << EOF
# act configuration file
--container-architecture linux/amd64
--artifact-server-path /tmp/artifacts
--env-file .env.ci
--secret-file .secrets
EOF
    
    # Create CI environment file
    cat > .env.ci << EOF
# CI Environment Variables
CI=true
GITHUB_ACTIONS=true
RUNNER_OS=Linux
RUNNER_ARCH=X64
PYTHON_VERSION=3.11
NODE_VERSION=18
POETRY_VERSION=1.6.1
EOF
    
    # Create secrets file template
    if [ ! -f ".secrets" ]; then
        cat > .secrets << EOF
# GitHub Secrets (replace with actual values)
GITHUB_TOKEN=your_github_token_here
CODECOV_TOKEN=your_codecov_token_here
SLACK_WEBHOOK_URL=your_slack_webhook_here
EOF
        log_warning "Please edit .secrets file with your actual secret values"
    fi
    
    log_success "Local CI environment setup complete"
}

# Run specific workflow job
run_workflow_job() {
    local workflow="$1"
    local job="$2"
    
    log_info "Running workflow: $workflow, job: $job"
    
    cd "$PROJECT_ROOT"
    
    if command_exists act; then
        act -j "$job" -W ".github/workflows/$workflow.yml" --verbose
    else
        log_error "act is not installed. Please install it first or run with --install-act"
        return 1
    fi
}

# Simulate CI environment locally
simulate_ci() {
    log_info "Simulating CI environment locally..."
    
    cd "$PROJECT_ROOT"
    
    # Set CI environment variables
    export CI=true
    export GITHUB_ACTIONS=true
    export RUNNER_OS=Linux
    
    # Run the same checks as CI
    log_info "Running backend tests..."
    scripts/test-backend.sh --all || log_error "Backend tests failed"
    
    log_info "Running frontend tests..."
    scripts/test-frontend.sh --all || log_error "Frontend tests failed"
    
    log_info "Running quality checks..."
    scripts/quality-check.sh --all || log_error "Quality checks failed"
    
    log_success "Local CI simulation completed"
}

# Test specific components
test_component() {
    local component="$1"
    
    case "$component" in
        "backend")
            log_info "Testing backend component..."
            scripts/test-backend.sh --all
            ;;
        "frontend")
            log_info "Testing frontend component..."
            scripts/test-frontend.sh --all
            ;;
        "quality")
            log_info "Testing code quality..."
            scripts/quality-check.sh --all
            ;;
        "integration")
            log_info "Testing integration..."
            scripts/test-all.sh --integration
            ;;
        "e2e")
            log_info "Testing E2E..."
            scripts/test-all.sh --e2e
            ;;
        *)
            log_error "Unknown component: $component"
            return 1
            ;;
    esac
}

# List available workflows and jobs
list_workflows() {
    log_info "Available workflows and jobs:"
    echo ""
    echo "CI Workflow (.github/workflows/ci.yml):"
    echo "  - backend-tests"
    echo "  - backend-quality"
    echo "  - frontend-tests"
    echo "  - e2e-tests"
    echo "  - security-scan"
    echo "  - build"
    echo ""
    echo "CD Workflow (.github/workflows/cd.yml):"
    echo "  - build-and-push"
    echo "  - deploy-staging"
    echo "  - deploy-production"
    echo "  - security-scan-images"
    echo "  - performance-test"
    echo ""
    echo "Usage examples:"
    echo "  $0 --job backend-tests"
    echo "  $0 --workflow ci --job frontend-tests"
    echo "  $0 --simulate"
    echo "  $0 --component backend"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --install-act           Install act tool for local GitHub Actions testing"
    echo "  --setup                 Setup local CI environment"
    echo "  --simulate              Simulate CI environment without act"
    echo "  --workflow WORKFLOW     Specify workflow (ci or cd)"
    echo "  --job JOB              Run specific job"
    echo "  --component COMPONENT   Test specific component (backend|frontend|quality|integration|e2e)"
    echo "  --list                  List available workflows and jobs"
    echo "  --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --setup                          # Setup local CI environment"
    echo "  $0 --job backend-tests              # Run backend tests job"
    echo "  $0 --workflow ci --job build        # Run build job from CI workflow"
    echo "  $0 --simulate                       # Simulate CI without act"
    echo "  $0 --component backend              # Test backend component"
    echo "  $0 --install-act                    # Install act tool"
}

# Main function
main() {
    local workflow="ci"
    local job=""
    local component=""
    local install_act_flag=false
    local setup_flag=false
    local simulate_flag=false
    local list_flag=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-act)
                install_act_flag=true
                shift
                ;;
            --setup)
                setup_flag=true
                shift
                ;;
            --simulate)
                simulate_flag=true
                shift
                ;;
            --workflow)
                workflow="$2"
                shift 2
                ;;
            --job)
                job="$2"
                shift 2
                ;;
            --component)
                component="$2"
                shift 2
                ;;
            --list)
                list_flag=true
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
    
    # Execute based on flags
    if [ "$install_act_flag" = true ]; then
        install_act
    elif [ "$setup_flag" = true ]; then
        setup_local_ci
    elif [ "$simulate_flag" = true ]; then
        simulate_ci
    elif [ "$list_flag" = true ]; then
        list_workflows
    elif [ -n "$component" ]; then
        test_component "$component"
    elif [ -n "$job" ]; then
        run_workflow_job "$workflow" "$job"
    else
        log_info "No specific action requested. Running full CI simulation..."
        simulate_ci
    fi
}

# Run main function
main "$@"
