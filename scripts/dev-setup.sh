#!/bin/bash

# =====================================================
# RAG Interface - Development Environment Setup Script
# =====================================================
# This script sets up the complete development environment
# for the RAG Interface project with proper dependency management
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

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    local missing_deps=()
    
    # Check Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    else
        python_version=$(python3 --version | cut -d' ' -f2)
        log_info "Python version: $python_version"
        
        # Check if Python version is >= 3.11
        if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            log_error "Python 3.11+ is required. Current version: $python_version"
            exit 1
        fi
    fi
    
    # Check Node.js
    if ! command_exists node; then
        missing_deps+=("node")
    else
        node_version=$(node --version)
        log_info "Node.js version: $node_version"
    fi
    
    # Check npm
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    # Check Docker or Podman
    if ! command_exists docker && ! command_exists podman; then
        missing_deps+=("docker or podman")
    fi
    
    # Check Git
    if ! command_exists git; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and run this script again."
        exit 1
    fi
    
    log_success "All system requirements satisfied"
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python environment..."
    
    cd "$PROJECT_ROOT"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    
    # Install development tools
    log_info "Installing development tools..."
    pip install pre-commit black isort mypy flake8 bandit
    
    log_success "Python environment setup complete"
}

# Setup Node.js environment
setup_node_env() {
    log_info "Setting up Node.js environment..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    log_success "Node.js environment setup complete"
}

# Setup environment files
setup_env_files() {
    log_info "Setting up environment files..."
    
    cd "$PROJECT_ROOT"
    
    # Copy development environment file
    if [ ! -f ".env.local" ]; then
        log_info "Creating .env.local from .env.dev template..."
        cp .env.dev .env.local
        log_warning "Please edit .env.local with your actual API keys and configuration"
    else
        log_info ".env.local already exists, skipping..."
    fi
    
    log_success "Environment files setup complete"
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install pre-commit hooks
    pre-commit install
    
    log_success "Pre-commit hooks setup complete"
}

# Setup database
setup_database() {
    log_info "Setting up development database..."
    
    cd "$PROJECT_ROOT"
    
    # Check if Docker/Podman is running
    if command_exists docker; then
        CONTAINER_CMD="docker"
    elif command_exists podman; then
        CONTAINER_CMD="podman"
    else
        log_error "Neither Docker nor Podman is available"
        exit 1
    fi
    
    # Start database using Makefile
    log_info "Starting PostgreSQL database..."
    make db-up
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Initialize database schema
    log_info "Initializing database schema..."
    source venv/bin/activate
    make db-init
    
    log_success "Database setup complete"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    cd "$PROJECT_ROOT"
    
    # Check Python environment
    source venv/bin/activate
    python -c "import fastapi, uvicorn, pytest; print('Python dependencies OK')"
    
    # Check Node.js environment
    cd frontend
    npm run build > /dev/null 2>&1
    log_success "Frontend build test passed"
    
    cd "$PROJECT_ROOT"
    log_success "Installation verification complete"
}

# Main setup function
main() {
    log_info "Starting RAG Interface development environment setup..."
    
    check_requirements
    setup_python_env
    setup_node_env
    setup_env_files
    setup_pre_commit
    setup_database
    verify_installation
    
    log_success "Development environment setup complete!"
    log_info ""
    log_info "Next steps:"
    log_info "1. Edit .env.local with your API keys and configuration"
    log_info "2. Run 'scripts/dev-start.sh' to start the development environment"
    log_info "3. Visit http://localhost:3000 for the frontend"
    log_info "4. Visit http://localhost:8000/docs for the API documentation"
}

# Run main function
main "$@"
