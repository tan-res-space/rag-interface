#!/bin/bash
# Development Environment Setup Script
# Sets up the complete development environment for the RAG Interface System

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    log_success "Python $python_version found"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    node_version=$(node --version)
    log_success "Node.js $node_version found"
    
    # Check container runtime
    if command -v podman &> /dev/null; then
        CONTAINER_CMD="podman"
        log_success "Podman found"
    elif command -v docker &> /dev/null; then
        CONTAINER_CMD="docker"
        log_success "Docker found"
    else
        log_error "Either Podman or Docker is required"
        exit 1
    fi
    
    # Check PostgreSQL client
    if ! command -v psql &> /dev/null; then
        log_warning "PostgreSQL client not found - database operations may be limited"
    else
        log_success "PostgreSQL client found"
    fi
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment
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
    pip install -r requirements-dev.txt
    pip install -r requirements-test.txt
    
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

# Setup environment configuration
setup_env_config() {
    log_info "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Copy environment template
    if [ ! -f ".env.local" ]; then
        log_info "Creating .env.local from development template..."
        cp config/environments/development.env .env.local
        log_success "Environment configuration created"
        log_warning "Please review and update .env.local with your specific settings"
    else
        log_info "Environment configuration already exists"
    fi
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    cd "$PROJECT_ROOT"
    
    # Start database with container
    log_info "Starting PostgreSQL database..."
    make db-up
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Initialize database schema
    log_info "Initializing database schema..."
    make db-init
    
    log_success "Database setup complete"
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Install pre-commit
    pip install pre-commit
    
    # Install hooks
    pre-commit install
    
    log_success "Pre-commit hooks setup complete"
}

# Run tests to verify setup
verify_setup() {
    log_info "Verifying setup..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run validation script
    if [ -f "validate_setup.py" ]; then
        log_info "Running setup validation..."
        python validate_setup.py
    fi
    
    # Run quick tests
    log_info "Running quick test suite..."
    pytest tests/unit/shared/ -v
    
    log_success "Setup verification complete"
}

# Main setup function
main() {
    log_info "Starting RAG Interface System development setup..."
    
    check_prerequisites
    setup_python_env
    setup_node_env
    setup_env_config
    setup_database
    setup_pre_commit
    verify_setup
    
    log_success "Development environment setup complete!"
    echo
    log_info "Next steps:"
    echo "  1. Review and update .env.local with your settings"
    echo "  2. Start the development environment: make dev-start"
    echo "  3. Access the application at http://localhost:3000"
    echo "  4. View API documentation at http://localhost:8000/docs"
}

# Run main function
main "$@"
