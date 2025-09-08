#!/bin/bash

# =====================================================
# RAG Interface - Local Development Setup Script
# =====================================================
# This script sets up the local development environment
# using Podman and podman-compose exclusively
# =====================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_system_requirements() {
    log_step "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Operating System: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "Operating System: macOS"
    else
        log_warning "Operating System: $OSTYPE (may not be fully supported)"
    fi
    
    # Check architecture
    local arch=$(uname -m)
    log_info "Architecture: $arch"
    
    # Check available memory
    if command_exists free; then
        local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$mem_gb" -ge 4 ]; then
            log_success "Memory: ${mem_gb}GB (sufficient)"
        else
            log_warning "Memory: ${mem_gb}GB (minimum 4GB recommended)"
        fi
    fi
    
    # Check available disk space
    local disk_gb=$(df -BG "$PROJECT_ROOT" | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$disk_gb" -ge 10 ]; then
        log_success "Disk Space: ${disk_gb}GB available (sufficient)"
    else
        log_warning "Disk Space: ${disk_gb}GB available (minimum 10GB recommended)"
    fi
}

# Install or check Podman
setup_podman() {
    log_step "Setting up Podman..."
    
    if command_exists podman; then
        local podman_version=$(podman --version | cut -d' ' -f3)
        log_success "Podman is already installed: $podman_version"
        
        # Test Podman
        if podman info >/dev/null 2>&1; then
            log_success "Podman is working correctly"
        else
            log_warning "Podman is installed but not working properly"
            log_info "You may need to start the Podman service or configure rootless mode"
        fi
    else
        log_warning "Podman is not installed"
        log_info "Please install Podman for your system:"
        echo ""
        echo "  Ubuntu/Debian: sudo apt-get install podman"
        echo "  RHEL/CentOS:   sudo dnf install podman"
        echo "  macOS:         brew install podman"
        echo ""
        echo "After installation, run this script again."
        exit 1
    fi
    
    # Check podman-compose
    if command_exists podman-compose; then
        local compose_version=$(podman-compose --version | cut -d' ' -f3)
        log_success "podman-compose is installed: $compose_version"
    else
        log_warning "podman-compose is not installed"
        log_info "Installing podman-compose..."
        
        if command_exists pip3; then
            pip3 install --user podman-compose
            log_success "podman-compose installed via pip3"
        else
            log_error "pip3 not found. Please install podman-compose manually:"
            echo "  pip3 install podman-compose"
            exit 1
        fi
    fi
}

# Setup Python environment
setup_python() {
    log_step "Setting up Python environment..."
    
    cd "$PROJECT_ROOT"
    
    # Check Python version
    if command_exists python3; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python is installed: $python_version"
        
        # Check if version is 3.11+
        local major=$(echo "$python_version" | cut -d'.' -f1)
        local minor=$(echo "$python_version" | cut -d'.' -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; then
            log_success "Python version is compatible (3.11+)"
        else
            log_warning "Python version $python_version may not be fully compatible (3.11+ recommended)"
        fi
    else
        log_error "Python 3 is not installed"
        log_info "Please install Python 3.11+ and try again"
        exit 1
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment and install dependencies
    log_info "Installing Python dependencies..."
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_warning "requirements.txt not found"
    fi
    
    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        log_success "Development dependencies installed"
    fi
    
    deactivate
}

# Setup Node.js environment
setup_nodejs() {
    log_step "Setting up Node.js environment..."
    
    # Check Node.js version
    if command_exists node; then
        local node_version=$(node --version)
        log_success "Node.js is installed: $node_version"
        
        # Check if version is 18+
        local major=$(echo "$node_version" | sed 's/v//' | cut -d'.' -f1)
        
        if [ "$major" -ge 18 ]; then
            log_success "Node.js version is compatible (18+)"
        else
            log_warning "Node.js version $node_version may not be fully compatible (18+ recommended)"
        fi
    else
        log_error "Node.js is not installed"
        log_info "Please install Node.js 18+ and try again"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        local npm_version=$(npm --version)
        log_success "npm is installed: $npm_version"
    else
        log_error "npm is not installed"
        exit 1
    fi
    
    # Install frontend dependencies
    if [ -d "frontend" ]; then
        log_info "Installing frontend dependencies..."
        cd "$PROJECT_ROOT/frontend"
        
        npm install
        log_success "Frontend dependencies installed"
        
        cd "$PROJECT_ROOT"
    else
        log_warning "Frontend directory not found"
    fi
}

# Setup environment configuration
setup_environment() {
    log_step "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Create .env.local if it doesn't exist
    if [ ! -f ".env.local" ]; then
        log_info "Creating .env.local from template..."
        
        if [ -f "config/environments/development.env" ]; then
            cp config/environments/development.env .env.local
            log_success ".env.local created from development template"
        else
            # Create a basic .env.local
            cat > .env.local << 'EOF'
# RAG Interface Local Development Configuration

# Database Configuration
DATABASE_NAME=rag_interface_dev
DB_USER=rag_user
DB_PASSWORD=dev_password_2025
DB_PORT=5433

# Redis Configuration
REDIS_PASSWORD=dev_redis_2025
REDIS_PORT=6380

# Service Ports
ERS_PORT=8010
UMS_PORT=8011
RIS_PORT=8012
CES_PORT=8013
VS_PORT=8014
FRONTEND_PORT=3001

# Development Tools Ports
MAILHOG_SMTP_PORT=1025
MAILHOG_WEB_PORT=8025
ADMINER_PORT=8080
REDIS_COMMANDER_PORT=8081

# Debug Ports
ERS_DEBUG_PORT=5678
UMS_DEBUG_PORT=5679
RIS_DEBUG_PORT=5680
CES_DEBUG_PORT=5681
VS_DEBUG_PORT=5682

# Logging
LOG_LEVEL=DEBUG
EOF
            log_success ".env.local created with default values"
        fi
        
        log_warning "Please review and edit .env.local with your specific configuration"
    else
        log_info ".env.local already exists"
    fi
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_step "Setting up pre-commit hooks..."
    
    cd "$PROJECT_ROOT"
    
    # Check if pre-commit is installed
    if command_exists pre-commit; then
        log_success "pre-commit is already installed"
    else
        log_info "Installing pre-commit..."
        source venv/bin/activate
        pip install pre-commit
        deactivate
        log_success "pre-commit installed"
    fi
    
    # Install pre-commit hooks
    if [ -f ".pre-commit-config.yaml" ]; then
        log_info "Installing pre-commit hooks..."
        source venv/bin/activate
        pre-commit install
        deactivate
        log_success "Pre-commit hooks installed"
    else
        log_warning ".pre-commit-config.yaml not found, skipping pre-commit setup"
    fi
}

# Verify setup
verify_setup() {
    log_step "Verifying setup..."
    
    cd "$PROJECT_ROOT"
    
    local issues=0
    
    # Check Podman
    if command_exists podman && podman info >/dev/null 2>&1; then
        log_success "✓ Podman is working"
    else
        log_error "✗ Podman is not working"
        issues=$((issues + 1))
    fi
    
    # Check podman-compose
    if command_exists podman-compose; then
        log_success "✓ podman-compose is available"
    else
        log_error "✗ podman-compose is not available"
        issues=$((issues + 1))
    fi
    
    # Check Python virtual environment
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        log_success "✓ Python virtual environment is ready"
    else
        log_error "✗ Python virtual environment is not ready"
        issues=$((issues + 1))
    fi
    
    # Check frontend dependencies
    if [ -d "frontend/node_modules" ]; then
        log_success "✓ Frontend dependencies are installed"
    else
        log_error "✗ Frontend dependencies are not installed"
        issues=$((issues + 1))
    fi
    
    # Check environment configuration
    if [ -f ".env.local" ]; then
        log_success "✓ Environment configuration exists"
    else
        log_error "✗ Environment configuration is missing"
        issues=$((issues + 1))
    fi
    
    echo ""
    if [ $issues -eq 0 ]; then
        log_success "Setup verification completed successfully!"
        log_info "You can now start the local development environment with:"
        echo "  ./tools/scripts/local-start.sh"
    else
        log_error "Setup verification found $issues issue(s)"
        log_info "Please resolve the issues above and run this script again"
        exit 1
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup          - Complete setup (default)"
    echo "  podman         - Setup Podman only"
    echo "  python         - Setup Python environment only"
    echo "  nodejs         - Setup Node.js environment only"
    echo "  environment    - Setup environment configuration only"
    echo "  pre-commit     - Setup pre-commit hooks only"
    echo "  verify         - Verify setup only"
    echo ""
    echo "Examples:"
    echo "  $0             # Complete setup"
    echo "  $0 verify      # Verify current setup"
    echo "  $0 python      # Setup Python environment only"
}

# Main function
main() {
    local command="${1:-setup}"
    
    log_info "RAG Interface Local Development Setup"
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    case "$command" in
        "setup")
            check_system_requirements
            setup_podman
            setup_python
            setup_nodejs
            setup_environment
            setup_pre_commit
            verify_setup
            ;;
        "podman")
            setup_podman
            ;;
        "python")
            setup_python
            ;;
        "nodejs")
            setup_nodejs
            ;;
        "environment")
            setup_environment
            ;;
        "pre-commit")
            setup_pre_commit
            ;;
        "verify")
            verify_setup
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
