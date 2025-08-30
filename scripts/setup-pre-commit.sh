#!/bin/bash

# =====================================================
# RAG Interface - Pre-commit Setup Script
# =====================================================
# This script sets up pre-commit hooks for code quality enforcement
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

# Setup pre-commit
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."
    
    cd "$PROJECT_ROOT"
    
    # Activate Python virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        log_error "Python virtual environment not found. Please run scripts/dev-setup.sh first"
        exit 1
    fi
    
    # Install pre-commit if not already installed
    if ! command_exists pre-commit; then
        log_info "Installing pre-commit..."
        pip install pre-commit
    fi
    
    # Install pre-commit hooks
    log_info "Installing pre-commit hooks..."
    pre-commit install
    
    # Install commit-msg hook for conventional commits
    pre-commit install --hook-type commit-msg
    
    log_success "Pre-commit hooks installed successfully"
}

# Install additional tools
install_tools() {
    log_info "Installing additional code quality tools..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Python tools
    pip install \
        black \
        isort \
        flake8 \
        mypy \
        bandit \
        autoflake \
        pyupgrade \
        detect-secrets
    
    # Frontend tools (if frontend directory exists)
    if [ -d "frontend" ]; then
        cd frontend
        
        # Check if package.json exists
        if [ -f "package.json" ]; then
            log_info "Installing frontend code quality tools..."
            
            # Install prettier and eslint if not already in package.json
            npm install --save-dev \
                prettier \
                eslint \
                @typescript-eslint/eslint-plugin \
                @typescript-eslint/parser \
                eslint-plugin-react \
                eslint-plugin-react-hooks \
                eslint-config-prettier \
                eslint-plugin-prettier
        fi
    fi
    
    log_success "Additional tools installed"
}

# Create secrets baseline
create_secrets_baseline() {
    log_info "Creating secrets baseline..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Create secrets baseline
    detect-secrets scan --baseline .secrets.baseline
    
    log_success "Secrets baseline created"
}

# Test pre-commit hooks
test_pre_commit() {
    log_info "Testing pre-commit hooks..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run pre-commit on all files
    if pre-commit run --all-files; then
        log_success "All pre-commit hooks passed"
    else
        log_warning "Some pre-commit hooks failed. This is normal for the first run."
        log_info "Pre-commit hooks will auto-fix many issues. Run again to see remaining issues."
    fi
}

# Update pre-commit hooks
update_pre_commit() {
    log_info "Updating pre-commit hooks..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Update hooks to latest versions
    pre-commit autoupdate
    
    log_success "Pre-commit hooks updated"
}

# Show pre-commit status
show_status() {
    log_info "Pre-commit status:"
    
    cd "$PROJECT_ROOT"
    
    if [ -f ".git/hooks/pre-commit" ]; then
        log_success "Pre-commit hooks are installed"
    else
        log_warning "Pre-commit hooks are not installed"
    fi
    
    if [ -f ".pre-commit-config.yaml" ]; then
        log_success "Pre-commit configuration exists"
        echo ""
        echo "Configured hooks:"
        grep -E "^\s*-\s*id:" .pre-commit-config.yaml | sed 's/.*id: /  - /'
    else
        log_warning "Pre-commit configuration not found"
    fi
    
    if [ -f ".secrets.baseline" ]; then
        log_success "Secrets baseline exists"
    else
        log_warning "Secrets baseline not found"
    fi
}

# Uninstall pre-commit hooks
uninstall_pre_commit() {
    log_info "Uninstalling pre-commit hooks..."
    
    cd "$PROJECT_ROOT"
    
    if command_exists pre-commit; then
        pre-commit uninstall
        pre-commit uninstall --hook-type commit-msg
        log_success "Pre-commit hooks uninstalled"
    else
        log_warning "Pre-commit not found"
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --install       Install pre-commit hooks (default)"
    echo "  --install-tools Install additional code quality tools"
    echo "  --test          Test pre-commit hooks on all files"
    echo "  --update        Update pre-commit hooks to latest versions"
    echo "  --status        Show pre-commit installation status"
    echo "  --uninstall     Uninstall pre-commit hooks"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Install pre-commit hooks"
    echo "  $0 --install-tools    # Install additional tools"
    echo "  $0 --test             # Test hooks on all files"
    echo "  $0 --update           # Update hooks"
    echo "  $0 --status           # Show status"
}

# Main function
main() {
    local action="install"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install)
                action="install"
                shift
                ;;
            --install-tools)
                action="install-tools"
                shift
                ;;
            --test)
                action="test"
                shift
                ;;
            --update)
                action="update"
                shift
                ;;
            --status)
                action="status"
                shift
                ;;
            --uninstall)
                action="uninstall"
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
    
    # Execute action
    case "$action" in
        "install")
            setup_pre_commit
            create_secrets_baseline
            ;;
        "install-tools")
            install_tools
            ;;
        "test")
            test_pre_commit
            ;;
        "update")
            update_pre_commit
            ;;
        "status")
            show_status
            ;;
        "uninstall")
            uninstall_pre_commit
            ;;
        *)
            log_error "Unknown action: $action"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
