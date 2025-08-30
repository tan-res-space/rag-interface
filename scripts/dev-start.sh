#!/bin/bash

# =====================================================
# RAG Interface - Development Environment Start Script
# =====================================================
# This script starts the complete development environment
# using Docker Compose with hot-reload capabilities
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

# Determine container command
get_container_cmd() {
    if command_exists docker && docker info >/dev/null 2>&1; then
        echo "docker"
    elif command_exists podman && podman info >/dev/null 2>&1; then
        echo "podman"
    else
        log_error "Neither Docker nor Podman is available or running"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    cd "$PROJECT_ROOT"
    
    # Check if .env.local exists
    if [ ! -f ".env.local" ]; then
        log_warning ".env.local not found. Creating from .env.dev template..."
        cp .env.dev .env.local
        log_warning "Please edit .env.local with your actual configuration before continuing"
        read -p "Press Enter to continue after editing .env.local..."
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_error "Python virtual environment not found. Please run scripts/dev-setup.sh first"
        exit 1
    fi
    
    # Check if node_modules exists
    if [ ! -d "frontend/node_modules" ]; then
        log_error "Node.js dependencies not found. Please run scripts/dev-setup.sh first"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Start services
start_services() {
    log_info "Starting development services..."
    
    cd "$PROJECT_ROOT"
    
    # Load environment variables
    set -a
    source .env.local
    set +a
    
    # Determine container command
    CONTAINER_CMD=$(get_container_cmd)
    
    # Start services with Docker Compose
    log_info "Starting services with $CONTAINER_CMD compose..."
    
    if [ "$CONTAINER_CMD" = "docker" ]; then
        docker compose -f docker-compose.dev.yml up -d --build
    else
        podman-compose -f docker-compose.dev.yml up -d --build
    fi
    
    log_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for database
    log_info "Waiting for PostgreSQL..."
    timeout=60
    while ! nc -z localhost ${DB_PORT:-5432} 2>/dev/null; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            log_error "Timeout waiting for PostgreSQL"
            exit 1
        fi
    done
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    timeout=60
    while ! nc -z localhost ${REDIS_PORT:-6379} 2>/dev/null; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            log_error "Timeout waiting for Redis"
            exit 1
        fi
    done
    
    # Wait for backend services
    services=("${ERS_PORT:-8000}" "${UMS_PORT:-8001}" "${RIS_PORT:-8002}")
    for port in "${services[@]}"; do
        log_info "Waiting for service on port $port..."
        timeout=120
        while ! curl -s http://localhost:$port/health >/dev/null 2>&1; do
            sleep 3
            timeout=$((timeout - 3))
            if [ $timeout -le 0 ]; then
                log_warning "Timeout waiting for service on port $port"
                break
            fi
        done
    done
    
    # Wait for frontend
    log_info "Waiting for frontend..."
    timeout=120
    while ! curl -s http://localhost:${FRONTEND_PORT:-3000} >/dev/null 2>&1; do
        sleep 3
        timeout=$((timeout - 3))
        if [ $timeout -le 0 ]; then
            log_warning "Timeout waiting for frontend"
            break
        fi
    done
    
    log_success "Services are ready"
}

# Show service status
show_status() {
    log_info "Development environment is running!"
    echo ""
    echo "🌐 Frontend:              http://localhost:${FRONTEND_PORT:-3000}"
    echo "📚 API Documentation:    http://localhost:${ERS_PORT:-8000}/docs"
    echo "👥 User Management:      http://localhost:${UMS_PORT:-8001}/docs"
    echo "🤖 RAG Integration:      http://localhost:${RIS_PORT:-8002}/docs"
    echo "🔧 Correction Engine:    http://localhost:${CES_PORT:-8003}/docs"
    echo "✅ Verification Service: http://localhost:${VS_PORT:-8004}/docs"
    echo ""
    echo "🛠️  Development Tools:"
    echo "📧 MailHog:              http://localhost:${MAILHOG_WEB_PORT:-8025}"
    echo "🗄️  Adminer (DB):        http://localhost:${ADMINER_PORT:-8080}"
    echo "📊 Redis Commander:     http://localhost:${REDIS_COMMANDER_PORT:-8081}"
    echo ""
    echo "📝 Logs: Use 'scripts/dev-logs.sh' to view service logs"
    echo "🛑 Stop: Use 'scripts/dev-stop.sh' to stop all services"
}

# Main function
main() {
    log_info "Starting RAG Interface development environment..."
    
    check_prerequisites
    start_services
    wait_for_services
    show_status
    
    log_success "Development environment started successfully!"
}

# Handle script arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 [start|status]"
        exit 1
        ;;
esac
