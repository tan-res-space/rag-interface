#!/bin/bash

# =====================================================
# RAG Interface - Local Development Startup Script
# =====================================================
# This script starts all services for local development
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

# Configuration
STARTUP_TIMEOUT=300  # 5 minutes total timeout
SERVICE_WAIT_TIMEOUT=60  # 1 minute per service
HEALTH_CHECK_INTERVAL=5  # 5 seconds between health checks

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

log_service() {
    echo -e "${CYAN}[SERVICE]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Podman availability
check_podman() {
    if ! command_exists podman; then
        log_error "Podman is not installed or not in PATH"
        log_info "Please install Podman and try again"
        exit 1
    fi
    
    if ! podman info >/dev/null 2>&1; then
        log_error "Podman is not running or not accessible"
        log_info "Please start Podman service and try again"
        exit 1
    fi
    
    if ! command_exists podman-compose; then
        log_error "podman-compose is not installed or not in PATH"
        log_info "Please install podman-compose and try again"
        exit 1
    fi
    
    log_success "Podman runtime is available"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    cd "$PROJECT_ROOT"
    
    # Check Podman
    check_podman
    
    # Check if .env.local exists
    if [ ! -f ".env.local" ]; then
        log_warning ".env.local not found. Creating from development template..."
        if [ -f "config/environments/development.env" ]; then
            cp config/environments/development.env .env.local
        else
            log_error "No environment template found. Please create .env.local manually."
            exit 1
        fi
        log_warning "Please edit .env.local with your actual configuration"
    fi
    
    # Load environment variables
    set -a
    source .env.local
    set +a
    
    # Check if Python virtual environment exists
    if [ ! -d "venv" ]; then
        log_warning "Python virtual environment not found. Creating..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
    
    # Check if frontend dependencies exist
    if [ ! -d "frontend/node_modules" ]; then
        log_warning "Frontend dependencies not found. Installing..."
        cd frontend
        npm install
        cd "$PROJECT_ROOT"
    fi
    
    log_success "Prerequisites check completed"
}

# Start infrastructure services (PostgreSQL, Redis)
start_infrastructure() {
    log_step "Starting infrastructure services..."
    
    cd "$PROJECT_ROOT"
    
    # Start infrastructure services first
    podman-compose -f podman-compose.dev.yml up -d --force-recreate postgres redis
    
    # Wait for PostgreSQL
    log_service "Waiting for PostgreSQL to be ready..."
    local timeout=$SERVICE_WAIT_TIMEOUT
    while ! nc -z localhost "${DB_PORT:-5433}" 2>/dev/null; do
        sleep $HEALTH_CHECK_INTERVAL
        timeout=$((timeout - HEALTH_CHECK_INTERVAL))
        if [ $timeout -le 0 ]; then
            log_error "Timeout waiting for PostgreSQL"
            return 1
        fi
        echo -n "."
    done
    echo
    log_success "PostgreSQL is ready"
    
    # Wait for Redis
    log_service "Waiting for Redis to be ready..."
    timeout=$SERVICE_WAIT_TIMEOUT
    while ! nc -z localhost "${REDIS_PORT:-6380}" 2>/dev/null; do
        sleep $HEALTH_CHECK_INTERVAL
        timeout=$((timeout - HEALTH_CHECK_INTERVAL))
        if [ $timeout -le 0 ]; then
            log_error "Timeout waiting for Redis"
            return 1
        fi
        echo -n "."
    done
    echo
    log_success "Redis is ready"
    
    log_success "Infrastructure services started successfully"
}

# Start backend services
start_backend_services() {
    log_step "Starting backend services..."
    
    cd "$PROJECT_ROOT"
    
    # Start backend services (including API Gateway)
    podman-compose -f podman-compose.dev.yml up -d --force-recreate api-gateway error-reporting-service user-management-service rag-integration-service correction-engine-service verification-service
    
    # Wait for backend services
    local services=("${GATEWAY_PORT:-8000}" "${ERS_PORT:-8010}" "${UMS_PORT:-8011}" "${RIS_PORT:-8012}" "${CES_PORT:-8013}" "${VS_PORT:-8014}")
    local service_names=("API Gateway" "Error Reporting Service" "User Management Service" "RAG Integration Service" "Correction Engine Service" "Verification Service")
    
    for i in "${!services[@]}"; do
        local port="${services[$i]}"
        local name="${service_names[$i]}"
        
        log_service "Waiting for $name on port $port..."
        local timeout=$SERVICE_WAIT_TIMEOUT
        while ! curl -s "http://localhost:$port/health" >/dev/null 2>&1; do
            sleep $HEALTH_CHECK_INTERVAL
            timeout=$((timeout - HEALTH_CHECK_INTERVAL))
            if [ $timeout -le 0 ]; then
                log_warning "Timeout waiting for $name on port $port"
                break
            fi
            echo -n "."
        done
        echo
        
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            log_success "$name is ready"
        else
            log_warning "$name may not be fully ready"
        fi
    done
    
    log_success "Backend services started"
}

# Start frontend service
start_frontend() {
    log_step "Starting frontend service..."
    
    cd "$PROJECT_ROOT"
    
    # Start frontend
    podman-compose -f podman-compose.dev.yml up -d --force-recreate frontend
    
    # Wait for frontend
    log_service "Waiting for frontend on port ${FRONTEND_PORT:-3001}..."
    local timeout=$SERVICE_WAIT_TIMEOUT
    while ! curl -s "http://localhost:${FRONTEND_PORT:-3001}" >/dev/null 2>&1; do
        sleep $HEALTH_CHECK_INTERVAL
        timeout=$((timeout - HEALTH_CHECK_INTERVAL))
        if [ $timeout -le 0 ]; then
            log_warning "Timeout waiting for frontend"
            break
        fi
        echo -n "."
    done
    echo
    
    if curl -s "http://localhost:${FRONTEND_PORT:-3001}" >/dev/null 2>&1; then
        log_success "Frontend is ready"
    else
        log_warning "Frontend may not be fully ready"
    fi
}

# Start development tools (optional)
start_dev_tools() {
    log_step "Starting development tools..."
    
    cd "$PROJECT_ROOT"
    
    # Start development tools
    podman-compose -f podman-compose.dev.yml up -d --force-recreate mailhog adminer redis-commander
    
    log_success "Development tools started"
}

# Show service status and URLs
show_status() {
    log_step "RAG Interface Local Development Status"
    echo ""
    echo "🌐 Frontend Application:"
    echo "   http://localhost:${FRONTEND_PORT:-3001}"
    echo ""
    echo "🔧 Backend Services:"
    echo "   API Gateway:          http://localhost:${GATEWAY_PORT:-8000}"
    echo "   Error Reporting:       http://localhost:${ERS_PORT:-8010}"
    echo "   User Management:       http://localhost:${UMS_PORT:-8011}"
    echo "   RAG Integration:       http://localhost:${RIS_PORT:-8012}"
    echo "   Correction Engine:     http://localhost:${CES_PORT:-8013}"
    echo "   Verification:          http://localhost:${VS_PORT:-8014}"
    echo ""
    echo "📚 API Documentation:"
    echo "   Error Reporting Docs:  http://localhost:${ERS_PORT:-8010}/docs"
    echo "   User Management Docs:  http://localhost:${UMS_PORT:-8011}/docs"
    echo "   RAG Integration Docs:  http://localhost:${RIS_PORT:-8012}/docs"
    echo "   Correction Engine Docs: http://localhost:${CES_PORT:-8013}/docs"
    echo "   Verification Docs:     http://localhost:${VS_PORT:-8014}/docs"
    echo ""
    echo "🛠️ Development Tools:"
    echo "   MailHog (Email):       http://localhost:${MAILHOG_WEB_PORT:-8025}"
    echo "   Adminer (Database):    http://localhost:${ADMINER_PORT:-8080}"
    echo "   Redis Commander:       http://localhost:${REDIS_COMMANDER_PORT:-8081}"
    echo ""
    echo "📝 Management Commands:"
    echo "   View logs:             ./tools/scripts/local-logs.sh"
    echo "   Stop services:         ./tools/scripts/local-stop.sh"
}

# Main function
main() {
    local command="${1:-all}"
    local start_time=$(date +%s)
    
    log_info "Starting RAG Interface Local Development Environment..."
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    case "$command" in
        "all")
            check_prerequisites
            start_infrastructure
            start_backend_services
            start_frontend
            start_dev_tools
            ;;
        "infrastructure")
            check_prerequisites
            start_infrastructure
            ;;
        "backend")
            start_backend_services
            ;;
        "frontend")
            start_frontend
            ;;
        "tools")
            start_dev_tools
            ;;
        *)
            echo "Usage: $0 [all|infrastructure|backend|frontend|tools]"
            echo ""
            echo "Commands:"
            echo "  all            - Start all services (default)"
            echo "  infrastructure - Start only infrastructure (PostgreSQL, Redis)"
            echo "  backend        - Start only backend services"
            echo "  frontend       - Start only frontend"
            echo "  tools          - Start only development tools"
            exit 1
            ;;
    esac
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    log_success "RAG Interface Local Development started successfully in ${duration}s!"
    echo ""
    show_status
}

# Run main function
main "$@"
